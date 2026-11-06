"""
ACTUALIZACIÓN MENSUAL: vuelve a correr todo el ETL, compara con la versión anterior
y solo reemplaza los datos que salieron bien.

Cómo funciona (paso a paso):
  1. Copia la carpeta etl/ a una carpeta temporal ("staging"). Ahí se trabaja; los datos
     publicados no se tocan hasta el final.
  2. Corre los scripts en orden, con ETL_REFRESCAR=1 para que vuelvan a bajar las fuentes:
       panel de países (paso 1 + paso 2) -> maestros -> alianzas -> Argentina por provincia
       -> Latinoamérica por subdivisión -> modelo unificado (SQLite) -> bases regionales -> base absoluta
  3. Si un paso falla (fuente caída, dominio bloqueado, cambio de formato), ese paso vuelve
     a su versión anterior y los siguientes siguen con ella. Nunca se pisan datos buenos.
  4. Controla cada archivo nuevo contra el anterior: si desaparece un archivo, se pierden
     columnas o caen más de 5 % las filas, el paso se rechaza y queda la versión anterior.
  5. Copia a etl/ solo los archivos que cambiaron, guardando antes la versión vieja en
     etl/historial/<fecha>/ (se conservan las últimas 3 actualizaciones).
  6. Prueba si cada fuente sigue respondiendo (chequear_fuentes.py) y avisa el porcentaje de
     fuentes posiblemente discontinuadas.
  7. Escribe el resumen en etl/actualizaciones/<fecha>_resumen.md y suma una fila por paso
     a etl/actualizaciones/historial.csv.

Uso:
    python actualizar_mensual.py            # actualiza y publica
    python actualizar_mensual.py --prueba   # corre y compara, pero no publica nada
    (--conservar deja la copia de trabajo en /tmp para revisarla)
"""

import hashlib
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

ETL = Path(__file__).resolve().parent
SALIDA_RESUMEN = ETL / "actualizaciones"
HISTORIAL = ETL / "historial"
BACKUPS_A_CONSERVAR = 3
CAIDA_MAXIMA_FILAS = 0.05  # más de 5 % menos filas = sospechoso
# Tablas que salen de Wikidata (editada por voluntarios) varían más de un mes a otro
CAIDA_MAXIMA_POR_ARCHIVO = {"latam_subnacional/gobernantes_subdivision.csv": 0.20}
# Una columna que pierde más de 20 % de sus datos = descarga cortada (p. ej. Wikidata con timeout)
CAIDA_MAXIMA_DATOS = 0.20
LIMITE_SEGUNDOS_PASO = 3 * 3600
NO_COPIAR = shutil.ignore_patterns("__pycache__", "historial", "actualizaciones")

# nombre, descripción, comandos (relativos a etl/), carpetas que el paso escribe
PASOS = [
    ("panel_paises", "Panel de países (Banco Mundial, OMS, ILOSTAT, WHR)",
     [["paso1_extraer_banco_mundial.py"], ["paso2_distribucion_precios_bienestar.py"]],
     ["datos_procesados", "datos_crudos"]),
    ("maestros", "Maestros de países y subdivisiones",
     [["maestros/crear_maestros.py", "--descargar"]], ["maestros"]),
    ("alianzas", "Alianzas y tratados internacionales",
     [["alianzas/extraer_alianzas_internacionales.py"]], ["alianzas"]),
    ("argentina", "Argentina por provincia",
     [["argentina_provincias/extraer_argentina_provincias.py"]], ["argentina_provincias"]),
    ("latam", "Latinoamérica por subdivisión",  # lee maestros/ y argentina_provincias/
     [["latam_subnacional/extraer_latam_subnacional.py"]], ["latam_subnacional"]),
    ("dimensiones_nuevas", "Migración, clima, capital social, gobernanza, deuda y federalismo fiscal",
     [["fuentes_nuevas/extraer_dimensiones_nuevas.py"]], ["fuentes_nuevas"]),  # lee maestros/ y argentina_provincias/
    ("panel_paso3", "Dimensiones nuevas sumadas al panel de países",  # después de panel_paises y dimensiones_nuevas
     [["paso3_dimensiones_nuevas.py"]], ["datos_procesados"]),
    ("indicadores_sociales", "Educación, redes, videojuegos, construcción, cultura, apuestas y medallero",
     [["indicadores_sociales_digitales/extraer_indicadores_sociales.py"]], ["indicadores_sociales_digitales"]),
    ("modelo_unificado", "Modelo unificado (SQLite)",
     [["modelo_unificado/construir_master.py"]], ["modelo_unificado"]),
    ("bases_regionales", "Bases Argentina, Latinoamérica y mundial (SQLite)",  # lee el master
     [["bases_regionales/construir_bases_regionales.py"]], ["bases_regionales"]),
    ("base_absoluta", "Base absoluta: país, provincia, variable y una columna por año",  # lee el master
     [["base_absoluta/construir_base_absoluta.py"]], ["base_absoluta"]),
]

PISTAS_ERROR = [
    (r"403|407|Tunnel connection failed|ProxyError", "posible dominio bloqueado por la red del entorno"),
    (r"ConnectionError|Max retries|timed out|ReadTimeout|50[0-9] Server Error", "la fuente no respondió (caída o lenta)"),
    (r"404 Client Error", "la fuente cambió la dirección del archivo (404)"),
    (r"KeyError|ValueError|ParserError|XLRDError|BadZipFile", "la fuente cambió el formato del archivo"),
    (r"ModuleNotFoundError", "falta instalar una librería (pip install -r requirements.txt)"),
]


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def es_dato(ruta: Path) -> bool:
    """Archivos de datos que se publican (no código ni guías, que se editan a mano)."""
    return ruta.is_file() and ruta.suffix not in (".py", ".pyc", ".md") and "__pycache__" not in ruta.parts


def foto(ruta: Path):
    """Tamaño y fecha de modificación, para saber si alguien tocó el archivo mientras corríamos."""
    return (ruta.stat().st_size, ruta.stat().st_mtime_ns) if ruta.exists() else None


def huella(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def archivos_de(base: Path, carpetas):
    for carpeta in carpetas:
        raiz = base / carpeta
        if raiz.exists():
            for r in sorted(raiz.rglob("*")):
                if es_dato(r):
                    yield r.relative_to(base)


def es_tabla(rel) -> bool:
    return rel.name.endswith((".csv", ".csv.gz"))


def pista(texto):
    return "; ".join(desc for patron, desc in PISTAS_ERROR if re.search(patron, texto)) or "ver el log"


def leer_tabla(ruta: Path):
    try:
        return pd.read_csv(ruta, low_memory=False, keep_default_na=False, na_values=[""])
    except Exception:
        return None


def filas_sqlite(ruta: Path):
    con = sqlite3.connect(ruta)
    try:
        tablas = [t for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        return {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tablas}
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Controles y comparación
# ---------------------------------------------------------------------------
def controlar(rel, viejo: Path, nuevo: Path):
    """Devuelve una lista de problemas que impiden publicar el archivo nuevo."""
    problemas = []
    if not nuevo.exists():
        return [f"{rel}: el archivo desapareció"]
    if es_tabla(nuevo):
        a, b = leer_tabla(viejo), leer_tabla(nuevo)
        if b is None or b.empty:
            return [f"{rel}: el archivo nuevo está vacío o no se puede leer"]
        if a is not None:
            # una columna que ya estaba vacía (p. ej. felicidad_fuente) puede desaparecer sin problema
            perdidas = [c for c in a.columns if c not in b.columns and a[c].notna().any()]
            if perdidas:
                problemas.append(f"{rel}: se perdieron columnas {perdidas[:8]}")
            if len(b) < len(a) * (1 - CAIDA_MAXIMA_POR_ARCHIVO.get(rel.as_posix(), CAIDA_MAXIMA_FILAS)):
                problemas.append(f"{rel}: bajó de {len(a):,} a {len(b):,} filas")
            vacias = []
            for c in [c for c in a.columns if c in b.columns]:
                na, nb = int(a[c].notna().sum()), int(b[c].notna().sum())
                if na >= 50 and nb < na * (1 - CAIDA_MAXIMA_DATOS):
                    vacias.append(f"{c} ({na:,} → {nb:,})")
            if vacias:
                problemas.append(f"{rel}: columnas que perdieron más de {CAIDA_MAXIMA_DATOS:.0%} de sus datos: "
                                 + ", ".join(vacias[:5]) + ("…" if len(vacias) > 5 else ""))
    elif nuevo.suffix == ".sqlite":
        a, b = filas_sqlite(viejo), filas_sqlite(nuevo)
        for t, n in a.items():
            if t not in b:
                problemas.append(f"{rel}: desapareció la tabla {t}")
            elif b[t] < n * (1 - CAIDA_MAXIMA_FILAS):
                problemas.append(f"{rel}: la tabla {t} bajó de {n:,} a {b[t]:,} filas")
    return problemas


def comparar_csv(viejo: Path, nuevo: Path):
    a, b = leer_tabla(viejo), leer_tabla(nuevo)
    if a is None or b is None:
        return "no se pudo leer para comparar"
    partes = [f"filas {len(a):,} → {len(b):,}"]
    nuevas = [c for c in b.columns if c not in a.columns]
    quitadas = [c for c in a.columns if c not in b.columns]
    if nuevas:
        partes.append(f"columnas nuevas: {', '.join(nuevas[:6])}{'…' if len(nuevas) > 6 else ''}")
    if quitadas:
        partes.append(f"columnas quitadas: {', '.join(quitadas[:6])}")
    if "anio" in a.columns and "anio" in b.columns:
        ra = f"{a.anio.min()}–{a.anio.max()}"
        rb = f"{b.anio.min()}–{b.anio.max()}"
        if ra != rb:
            partes.append(f"años {ra} → {rb}")
    comunes = [c for c in a.columns if c in b.columns]
    ha = set(pd.util.hash_pandas_object(a[comunes].astype(str), index=False))
    hb = pd.util.hash_pandas_object(b[comunes].astype(str), index=False)
    cambiadas = int((~hb.isin(ha)).sum())
    partes.append(f"{cambiadas:,} filas nuevas o con algún valor distinto")
    con_dato_a, con_dato_b = a[comunes].notna().sum(), b[comunes].notna().sum()
    delta = (con_dato_b - con_dato_a).sort_values(key=abs, ascending=False)
    delta = delta[delta != 0]
    total = int(con_dato_b.sum() - con_dato_a.sum())
    if total:
        partes.append(f"celdas con dato {total:+,}")
    if len(delta):
        top = ", ".join(f"{c} {int(v):+,}" for c, v in delta.head(4).items())
        partes.append(f"(más cambio: {top})")
    return "; ".join(partes)


def comparar_sqlite(viejo: Path, nuevo: Path):
    a, b = filas_sqlite(viejo), filas_sqlite(nuevo)
    cambios = [f"{t} {a.get(t, 0):,} → {n:,}" for t, n in b.items() if a.get(t) != n]
    nuevas = [t for t in b if t not in a]
    texto = f"{len(cambios)} tablas cambiaron de tamaño"
    if cambios:
        texto += ": " + ", ".join(cambios[:8]) + ("…" if len(cambios) > 8 else "")
    if nuevas:
        texto += f"; tablas nuevas: {', '.join(nuevas)}"
    return texto


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def correr_paso(staging: Path, nombre, comandos, carpeta_logs: Path):
    log = carpeta_logs / f"{nombre}.log"
    entorno = {**os.environ, "ETL_REFRESCAR": "1", "PYTHONUNBUFFERED": "1"}
    inicio = time.time()
    with open(log, "w") as salida:
        for comando in comandos:
            script = staging / comando[0]
            salida.write(f"\n$ python {' '.join(comando)}\n")
            salida.flush()
            try:
                r = subprocess.run([sys.executable, str(script), *comando[1:]], cwd=script.parent,
                                   stdout=salida, stderr=subprocess.STDOUT, env=entorno,
                                   timeout=LIMITE_SEGUNDOS_PASO)
                codigo = r.returncode
            except subprocess.TimeoutExpired:
                salida.write(f"\nERROR: superó {LIMITE_SEGUNDOS_PASO // 60} minutos\n")
                codigo = -1
            if codigo != 0:
                return False, time.time() - inicio, log
    return True, time.time() - inicio, log


def main():
    prueba = "--prueba" in sys.argv
    fecha = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%Y-%m-%d %H:%M")
    trabajo = Path(tempfile.mkdtemp(prefix="etl_actualizacion_"))
    staging = trabajo / "etl"
    resguardo = trabajo / "antes_de_cada_paso"
    carpeta_logs = SALIDA_RESUMEN / "logs" / fecha
    carpeta_logs.mkdir(parents=True, exist_ok=True)

    print(f"Copiando etl/ a {staging} ...")
    todas = [c for _, _, _, carpetas in PASOS for c in carpetas]
    al_empezar = {rel: foto(ETL / rel) for rel in archivos_de(ETL, todas)}
    shutil.copytree(ETL, staging, ignore=NO_COPIAR)

    # Algunas carpetas las escriben dos pasos (datos_procesados: paso 1-2 y paso 3). El control se
    # hace en el último que la escribe, y si ese falla se vuelve a la versión de antes del primero.
    def primero_que_escribe(carpeta):
        return next(n for n, _, _, cs in PASOS if carpeta in cs)

    def escrita_despues(i, carpeta):
        return any(carpeta in cs for _, _, _, cs in PASOS[i + 1:])

    resultados = []
    for i, (nombre, descripcion, comandos, carpetas) in enumerate(PASOS):
        print(f"\n=== {descripcion} ===", flush=True)
        # Copia del paso antes de correrlo, para volver atrás si falla
        for c in carpetas:
            if (staging / c).exists():
                shutil.copytree(staging / c, resguardo / nombre / c, ignore=NO_COPIAR)
        ok, segundos, log = correr_paso(staging, nombre, comandos, carpeta_logs)
        texto_log = log.read_text(errors="replace")
        avisos = sorted(set(re.findall(r"AVISO_FUENTE (.+)", texto_log)))
        estado, detalle = "actualizado", []
        if not ok:
            estado = "falló"
            ultimas = [l for l in texto_log.strip().splitlines() if l.strip()][-3:]
            detalle = [f"causa probable: {pista(texto_log[-4000:])}", *ultimas]
        else:
            for rel in archivos_de(ETL, carpetas):
                if "crudos" not in rel.parts and "datos_crudos" not in rel.parts \
                        and not escrita_despues(i, rel.parts[0]):
                    detalle += controlar(rel, ETL / rel, staging / rel)
            if detalle:
                estado = "rechazado"
        if estado != "actualizado":
            for c in carpetas:
                shutil.rmtree(staging / c, ignore_errors=True)
                origen = resguardo / primero_que_escribe(c) / c
                if origen.exists():
                    shutil.copytree(origen, staging / c)
                for r in resultados:  # pasos anteriores que escribieron esa carpeta vuelven atrás también
                    if c in r["carpetas"] and r["estado"] == "actualizado":
                        r["estado"] = "rechazado"
                        r["detalle"].append(f"se volvió atrás porque «{descripcion}» no se pudo actualizar")
            print(f"   {estado.upper()}: se mantiene la versión anterior", flush=True)
        else:
            print(f"   OK en {segundos / 60:.1f} min", flush=True)
        resultados.append(dict(paso=nombre, descripcion=descripcion, estado=estado,
                               minutos=round(segundos / 60, 1), detalle=detalle, avisos=avisos, carpetas=carpetas))

    # Qué archivos cambiaron, comparados con lo publicado
    cambios, vistos = [], set()
    for res in resultados:
        if res["estado"] != "actualizado":
            continue
        for rel in archivos_de(staging, res["carpetas"]):
            nuevo, viejo = staging / rel, ETL / rel
            if rel in vistos or (viejo.exists() and huella(nuevo) == huella(viejo)):
                continue
            vistos.add(rel)
            if not viejo.exists():
                resumen = "archivo nuevo"
            elif es_tabla(rel) and "crudos" not in rel.parts:
                resumen = comparar_csv(viejo, nuevo)
            elif rel.suffix == ".sqlite":
                resumen = comparar_sqlite(viejo, nuevo)
            else:
                resumen = None  # crudos y otros: solo se cuentan
            cambios.append((res["paso"], rel, resumen))

    # Si otro proceso modificó un archivo publicado mientras corríamos, gana su versión
    pisados = [rel for _, rel, _ in cambios if foto(ETL / rel) != al_empezar.get(rel)]
    cambios = [c for c in cambios if c[1] not in pisados]

    # Publicar: guardar lo viejo en historial/ y copiar lo nuevo
    if not prueba and cambios:
        destino_backup = HISTORIAL / fecha
        for _, rel, _ in cambios:
            if (ETL / rel).exists():
                (destino_backup / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ETL / rel, destino_backup / rel)
        for _, rel, _ in cambios:
            (ETL / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(staging / rel, ETL / rel)
        viejos = sorted(p for p in HISTORIAL.iterdir() if p.is_dir())[:-BACKUPS_A_CONSERVAR]
        for p in viejos:
            shutil.rmtree(p, ignore_errors=True)

    # Estado de cada fuente (¿alguna se dio de baja?). Si el chequeo mismo falla, no frena nada.
    try:
        sys.path.insert(0, str(ETL))
        from chequear_fuentes import chequear
        _, lineas_fuentes = chequear(guardar=not prueba)
    except Exception as error:
        lineas_fuentes = ["## Estado de las fuentes", f"- No se pudo hacer el chequeo: {error!r}"]

    # Resumen
    fallos = [r for r in resultados if r["estado"] != "actualizado"]
    lineas = [f"# Actualización mensual {hora}" + (" (PRUEBA: no se publicó nada)" if prueba else ""), ""]
    if fallos:
        lineas.append(f"**{len(fallos)} de {len(resultados)} pasos no se actualizaron; "
                      "esos datos quedan como estaban.**")
    else:
        lineas.append(f"Todos los pasos se actualizaron. {len(cambios)} archivos cambiaron.")
    lineas += ["", "| Paso | Estado | Minutos |", "|---|---|---|"]
    lineas += [f"| {r['descripcion']} | {r['estado']} | {r['minutos']} |" for r in resultados]
    lineas += ["", *lineas_fuentes]
    for r in resultados:
        if r["detalle"]:
            lineas += ["", f"## {r['descripcion']}: {r['estado']}", *[f"- {d}" for d in r["detalle"]],
                       f"- log: actualizaciones/logs/{fecha}/{r['paso']}.log"]
    avisos = [(r["descripcion"], a) for r in resultados for a in r["avisos"]]
    if avisos:
        lineas += ["", "## Fuentes que no respondieron (se usó la copia anterior de ese archivo)"]
        lineas += [f"- {d}: {a}" for d, a in avisos]
    tablas = [(p, rel, s) for p, rel, s in cambios if s]
    crudos = [rel for _, rel, s in cambios if not s]
    lineas += ["", "## Qué cambió"]
    if tablas:
        lineas += [f"- **{rel}**: {s}" for _, rel, s in tablas]
    else:
        lineas.append("- Ninguna tabla procesada cambió.")
    if crudos:
        lineas.append(f"- Además cambiaron {len(crudos)} archivos crudos o auxiliares.")
    if pisados:
        lineas += ["", "## No se publicaron porque alguien los modificó durante la actualización",
                   *[f"- {rel}" for rel in pisados], "Se renuevan en la próxima corrida."]
    if not prueba and cambios:
        lineas += ["", f"Versión anterior de los archivos reemplazados: etl/historial/{fecha}/"]
    texto = "\n".join(lineas) + "\n"

    sufijo = "_prueba" if prueba else ""
    (SALIDA_RESUMEN / f"{fecha}_resumen{sufijo}.md").write_text(texto)
    historial = SALIDA_RESUMEN / "historial.csv"
    filas = pd.DataFrame([{"fecha": hora, "prueba": int(prueba), "paso": r["paso"], "estado": r["estado"],
                           "minutos": r["minutos"], "archivos_cambiados": sum(p == r["paso"] for p, _, _ in cambios),
                           "avisos_fuentes": len(r["avisos"])} for r in resultados])
    filas.to_csv(historial, mode="a", header=not historial.exists(), index=False)
    if "--conservar" in sys.argv:
        print(f"Copia de trabajo conservada en {trabajo}")
    else:
        shutil.rmtree(trabajo, ignore_errors=True)

    print("\n" + texto)
    print(f"Resumen: {SALIDA_RESUMEN / f'{fecha}_resumen{sufijo}.md'}")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
