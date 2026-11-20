"""
RIESGO DE DESASTRES EN CIUDADES: pérdidas reales y gasto municipal en gestión del riesgo.

Sirve para validar los scorecards UNDRR de las 16 ciudades latinoamericanas (15 con más de
2 millones de habitantes + CABA) que están en /mnt/project-files/consultas/scorecard_undrr/.
La unidad es el GOBIERNO LOCAL (municipio, distrito o entidad con gobierno propio), igual que
en los scorecards.

Fuentes (todas públicas):
  - DesInventar Sendai (UNDRR): un registro por evento y municipio. Colombia, Ecuador, Perú,
    México, Venezuela y Argentina. Cada país cubre años distintos (ver cobertura en el resumen).
  - Atlas Digital de Desastres en Brasil (MIDR, base S2iD, 1991-2025; se toma la versión más nueva): solo los desastres que
    el municipio registró ante el gobierno federal, así que cuenta menos eventos chicos que
    DesInventar (que también usa prensa).
  - Emergencias UNGRD (datos.gov.co, 2019-2025): Colombia, completa los años que DesInventar no tiene.
  - SICONFI (Tesoro Nacional de Brasil), DCA Anexo I-E: gasto municipal en la subfunción
    06.182 "Defesa Civil" y gasto total, 2015-2024.
  - CUIPO (Contaduría, datos.gov.co): gasto de Bogotá, Medellín y Cali en el programa MGA 4503
    "Prevención y atención de desastres y emergencias" (incluye bomberos), 2023-2025.

Qué genera (en esta carpeta):
  perdidas_ciudad_eventos.csv     un evento por fila, ya filtrado a las 16 ciudades
  perdidas_ciudad_anual.csv       ciudad + año + tipo (socionatural u otro): eventos, muertos,
                                  heridos, desaparecidos, damnificados, viviendas destruidas y afectadas
  perdidas_ciudad_resumen.csv     ciudad: tasas anuales por 100.000 habitantes en la ventana
                                  común 2000-2013 y en todo el período disponible desde 2000
  eventos_2026_documentados.csv   terremotos y lluvias de 2026 que todavía no están en las bases
                                  (cifras de prensa, con fuente; no entran en las tasas)
  gasto_riesgo_ciudad_anual.csv   ciudad + año: gasto en gestión del riesgo, total y por habitante
La explicación paso a paso está en GUIA_RIESGO_CIUDADES.md.

Los archivos originales quedan en crudos/. Si un archivo ya está ahí, no se vuelve a bajar
(borralo, o corré con ETL_REFRESCAR=1, para traer la versión más nueva).

Cómo ejecutarlo (desde la carpeta etl/):
    python riesgo_ciudades/extraer_riesgo_ciudades.py
"""

import csv
import json
import os
import time
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pandas as pd
import requests

CARPETA = Path(__file__).resolve().parent
CRUDOS = CARPETA / "crudos"
REFRESCAR = os.environ.get("ETL_REFRESCAR") == "1"
SESION = requests.Session()
SESION.headers["User-Agent"] = "word-data-etl/1.0"

# id, nombre, iso3, población de referencia (la de los scorecards), fuente de pérdidas y códigos
CIUDADES = [
    # Brasil: código IBGE de 7 dígitos (atlas y SICONFI); Brasília en SICONFI es el ente 53 (DF)
    dict(id="sao_paulo", nombre="São Paulo", iso3="BRA", pob=11451999, ibge="3550308", siconfi="3550308"),
    dict(id="rio", nombre="Rio de Janeiro", iso3="BRA", pob=6211423, ibge="3304557", siconfi="3304557"),
    dict(id="brasilia", nombre="Brasília (Distrito Federal)", iso3="BRA", pob=2817381, ibge="5300108", siconfi="53"),
    dict(id="salvador", nombre="Salvador", iso3="BRA", pob=2418005, ibge="2927408", siconfi="2927408"),
    dict(id="fortaleza", nombre="Fortaleza", iso3="BRA", pob=2428678, ibge="2304400", siconfi="2304400"),
    dict(id="belo_horizonte", nombre="Belo Horizonte", iso3="BRA", pob=2315560, ibge="3106200", siconfi="3106200"),
    dict(id="manaus", nombre="Manaus", iso3="BRA", pob=2063547, ibge="1302603", siconfi="1302603"),
    # DesInventar: (código de país, nivel geográfico, código)
    dict(id="cdmx", nombre="Ciudad de México", iso3="MEX", pob=9209944, di=("mex", "level0", "09")),
    dict(id="lima", nombre="Lima Metropolitana", iso3="PER", pob=10292408, di=("per", "level1", "1501")),
    dict(id="bogota", nombre="Bogotá D.C.", iso3="COL", pob=7918660, di=("col", "level1", "11001"), divipola="11001", cuipo="210111001"),
    dict(id="medellin", nombre="Medellín", iso3="COL", pob=2524747, di=("col", "level1", "05001"), divipola="05001", cuipo="210105001"),
    dict(id="cali", nombre="Santiago de Cali", iso3="COL", pob=2283846, di=("col", "level1", "76001"), divipola="76001", cuipo="210176001"),
    dict(id="guayaquil", nombre="Guayaquil", iso3="ECU", pob=2650288, di=("ecu", "level1", "0901")),
    dict(id="quito", nombre="Quito (Distrito Metropolitano)", iso3="ECU", pob=2679722, di=("ecu", "level1", "1701")),
    dict(id="caracas", nombre="Caracas (Municipio Libertador)", iso3="VEN", pob=2091452, di=("ven", "level0", "01")),
    dict(id="caba", nombre="Buenos Aires (CABA)", iso3="ARG", pob=3121707, di=("arg", "level0", "02")),
]
VENTANA_COMUN = (2000, 2013)  # años que cubren todas las fuentes (México termina en 2013)
DESDE = 2000
ANIO_MAXIMO = 2026

# Eventos naturales o socionaturales (lo que mide el scorecard). Lo demás (accidentes,
# incendios estructurales, epidemias, explosiones, contaminación) queda como "otro".
CLAVES_NATURALES = [
    "INUNDA", "DESLIZ", "MOVIMIENTO EN MASA", "MOVIMIENTO DE MASA", "MOVIMENTO DE MASSA", "REMOCION", "AVENIDA", "CRECIENTE", "DESBORD",
    "VENDAVAL", "SISMO", "TERREMOTO", "SEQU", "DEFICIT HIDRICO", "ESTIAGEM", "INCENDIO FORESTAL", "INCENDIO DE COBERTURA",
    "INCENDIO FLORESTAL", "TORMENTA", "TEMPESTAD", "GRANIZ", "EROSI", "EROSAO", "HELADA", "CALOR", "VOLCAN", "LLUVIA",
    "CHUVA", "TSUNAMI", "HURACAN", "MAREJADA", "TORNADO", "CICLON", "LAHAR", "LICUA", "HUNDIM", "SOCAV", "OLEAJE",
    "DETRIT", "NEVADA", "ALUD", "ALUVI", "ENXURRADA", "ALAGAMENTO", "INUNDACOES", "GRANIZO", "VENDAVAIS", "ONDA FRIA",
    "OLA DE FRIO", "FRIO", "NEBLINA", "SEDIMENTA", "CAMBIO LINEA DE COSTA", "EROSAO COSTEIRA", "BAIXA UMIDADE",
]
EXCLUIR_BR = {"Doenças infecciosas", "Rompimento/Colapso de barragens", "Outros"}

COLUMNAS = ["muertos", "heridos", "desaparecidos", "damnificados", "afectados", "viv_destruidas", "viv_afectadas"]


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode()
    return texto.upper().strip()


def es_natural(evento):
    e = normalizar(evento)
    if "INCENDIO" in e and not any(k in e for k in ("FORESTAL", "FLORESTAL", "COBERTURA")):
        return False
    return any(k in e for k in CLAVES_NATURALES)


def bajar(url, destino, timeout=1800, intentos=3):
    """Baja url a destino si no existe (o si ETL_REFRESCAR=1). Si falla y hay copia, usa la copia."""
    if destino.exists() and destino.stat().st_size > 0 and not REFRESCAR:
        return destino
    for i in range(intentos):
        try:
            r = SESION.get(url, timeout=timeout, stream=True)
            r.raise_for_status()
            tmp = destino.with_suffix(destino.suffix + ".tmp")
            with open(tmp, "wb") as f:
                for parte in r.iter_content(1 << 20):
                    f.write(parte)
            if destino.suffix == ".zip" and not zipfile.is_zipfile(tmp):
                raise ValueError(f"descarga cortada: {url}")
            tmp.replace(destino)
            return destino
        except Exception as e:  # noqa: BLE001
            if i == intentos - 1:
                if destino.exists():
                    print(f"AVISO_FUENTE {url}: {e}; uso la copia anterior")
                    return destino
                raise
            time.sleep(5 * (i + 1))


def socrata(dataset, params, timeout=300):
    url = f"https://www.datos.gov.co/resource/{dataset}.json"
    for i in range(3):
        try:
            r = SESION.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception:  # noqa: BLE001
            if i == 2:
                raise
            time.sleep(5 * (i + 1))


def num(x):
    return pd.to_numeric(x, errors="coerce").fillna(0)


# ------------------------------------------------------------------ DesInventar
def fichas_desinventar(pais):
    """Lee las fichas del XML de DesInventar (un evento por fila)."""
    cache = CRUDOS / f"di_{pais}_fichas.csv"
    zp = bajar(f"https://www.desinventar.net/DesInventar/download/DI_export_{pais}.zip", CRUDOS / f"DI_export_{pais}.zip")
    if cache.exists() and cache.stat().st_mtime >= zp.stat().st_mtime:
        return pd.read_csv(cache, dtype=str)
    campos = ["serial", "level0", "level1", "level2", "name0", "name1", "name2", "evento", "lugar", "fechano", "fechames",
              "fechadia", "muertos", "heridos", "desaparece", "afectados", "damnificados", "vivdest", "vivafec", "fuentes"]
    filas, seccion = [], None
    with zipfile.ZipFile(zp) as z, z.open(f"DI_export_{pais}.xml") as f:
        for ev, el in ET.iterparse(f, events=("start", "end")):
            if ev == "start":
                if el.tag in ("fichas", "regiones", "lev0", "lev1", "lev2", "eventos", "causas"):
                    seccion = el.tag
                continue
            if el.tag == "TR":
                if seccion == "fichas":
                    filas.append([(el.findtext(c) or "").strip() for c in campos])
                el.clear()
    df = pd.DataFrame(filas, columns=campos)
    df.to_csv(cache, index=False)
    return df


def perdidas_desinventar():
    salida = []
    for c in CIUDADES:
        if "di" not in c:
            continue
        pais, nivel, codigo = c["di"]
        df = fichas_desinventar(pais)
        df = df[df[nivel] == codigo]
        if c["iso3"] == "COL":
            df = df[num(df.fechano) <= 2018]  # desde 2019 se usa UNGRD (más completa)
        salida.append(pd.DataFrame({
            "ciudad_id": c["id"], "fuente": "DesInventar", "anio": num(df.fechano).astype(int),
            "fecha": df.fechano + "-" + df.fechames.str.zfill(2) + "-" + df.fechadia.str.zfill(2),
            "evento": df.evento, "lugar": df.lugar,
            "muertos": num(df.muertos), "heridos": num(df.heridos), "desaparecidos": num(df.desaparece),
            "damnificados": num(df.damnificados), "afectados": num(df.afectados),
            "viv_destruidas": num(df.vivdest), "viv_afectadas": num(df.vivafec),
        }))
    return pd.concat(salida, ignore_index=True)


# ------------------------------------------------------------------ Brasil (Atlas S2iD)
URL_ATLAS = "https://atlasdigital.mdr.gov.br/arquivos/2026/BD_Atlas_1991_2025_v1.1_2026.08.06_Consolidado.csv"


def url_atlas():
    """El nombre del archivo cambia con cada versión: se toma el link de la página de descargas."""
    try:
        import re
        html = SESION.get("https://atlasdigital.mdr.gov.br/paginas/downloads.xhtml", timeout=60).text
        links = re.findall(r'href="(/arquivos/[^"]+Consolidado\.csv)"', html)
        if links:
            return "https://atlasdigital.mdr.gov.br" + links[0]
    except Exception as e:  # noqa: BLE001
        print(f"AVISO_FUENTE atlas (página de descargas): {e}")
    return URL_ATLAS


def perdidas_brasil():
    ruta = CRUDOS / "atlas_br_consolidado.csv"
    viejo = CRUDOS / "atlas_br_1991_2025.csv"
    if viejo.exists() and not ruta.exists():
        viejo.rename(ruta)
    ruta = bajar(url_atlas() if (REFRESCAR or not ruta.exists()) else URL_ATLAS, ruta)
    df = pd.read_csv(ruta, sep=";", encoding="latin1", dtype=str)
    cod = {c["ibge"]: c["id"] for c in CIUDADES if "ibge" in c}
    df = df[df.Cod_IBGE_Mun.isin(cod)]
    fecha = pd.to_datetime(df.Data_Evento, format="%d/%m/%Y", errors="coerce")
    tipo = df.descricao_tipologia.fillna("")
    return pd.DataFrame({
        "ciudad_id": df.Cod_IBGE_Mun.map(cod), "fuente": "Atlas Digital de Desastres (S2iD)",
        "anio": fecha.dt.year.astype("Int64"), "fecha": fecha.dt.strftime("%Y-%m-%d"),
        "evento": tipo.where(~tipo.isin(EXCLUIR_BR), "Otro: " + tipo), "lugar": "",
        "muertos": num(df.DH_MORTOS), "heridos": num(df.DH_FERIDOS), "desaparecidos": num(df.DH_DESAPARECIDOS),
        "damnificados": num(df.DH_DESABRIGADOS) + num(df.DH_DESALOJADOS), "afectados": num(df["DH_OUTROS AFETADOS"]),
        "viv_destruidas": num(df["DM_Uni Habita Destruidas"]), "viv_afectadas": num(df["DM_Uni Habita Danificadas"]),
    })


# ------------------------------------------------------------------ Colombia (UNGRD)
UNGRD = [  # dataset, columna del código DIVIPOLA, nombres de columnas de cada versión
    ("wwkg-r6te", "divipola", dict(muertos="fallecidos", heridos="heridos", desaparecidos="desaparecidos", personas="personas",
                                   viv_destruidas="viviendas_destruidas", viv_afectadas="viviendas_averiadas")),
    ("rgre-6ak4", "codificaci_n_segun_divipola", dict(muertos="fallecidos", heridos="heridos", desaparecidos="desaparecidos",
                                                      personas="personas", viv_destruidas="viviendas_destruidas",
                                                      viv_afectadas="viviendas_averiadas")),
    ("2343-nuqp", "codificaci_n_segun_divipola", dict(muertos="muertos", heridos="heridos", desaparecidos="desapa",
                                                      personas="personas", viv_destruidas="viv_destru", viv_afectadas="viv_aver")),
]


def perdidas_colombia_ungrd():
    salida = []
    cods = {c["divipola"]: c["id"] for c in CIUDADES if "divipola" in c}
    for ds, col_cod, m in UNGRD:
        cache = CRUDOS / f"ungrd_{ds}.json"
        if cache.exists() and not REFRESCAR:
            datos = json.loads(cache.read_text())
        else:
            variantes = set(cods) | {k.lstrip("0") for k in cods}
            filtro = f"{col_cod} in(" + ",".join(f"'{v}'" for v in sorted(variantes)) + ")"
            datos = socrata(ds, {"$where": filtro, "$limit": 50000})
            cache.write_text(json.dumps(datos, ensure_ascii=False))
        df = pd.DataFrame(datos)
        if df.empty:
            continue
        df["ciudad_id"] = df[col_cod].astype(str).str.zfill(5).map(cods)
        fecha = pd.to_datetime(df.fecha, errors="coerce")
        salida.append(pd.DataFrame({
            "ciudad_id": df.ciudad_id, "fuente": "UNGRD (datos.gov.co)", "anio": fecha.dt.year.astype("Int64"),
            "fecha": fecha.dt.strftime("%Y-%m-%d"), "evento": df.evento, "lugar": "",
            "muertos": num(df[m["muertos"]]), "heridos": num(df[m["heridos"]]),
            "desaparecidos": num(df[m["desaparecidos"]]), "damnificados": 0, "afectados": num(df[m["personas"]]),
            "viv_destruidas": num(df[m["viv_destruidas"]]), "viv_afectadas": num(df[m["viv_afectadas"]]),
        }))
    return pd.concat(salida, ignore_index=True)


# ------------------------------------------------------------------ Eventos de 2026 (prensa)
EVENTOS_2026 = [
    dict(ciudad_id="cali", fecha="2026-08-10", evento="Sismo (M7,4, epicentro en San José del Palmar, Chocó)", muertos=154,
         heridos=1517, viv_destruidas=None, viv_afectadas=12000, damnificados_familias=45139,
         nota="26 estructuras colapsadas; 765 edificaciones inhabitables; cerca de 200 IPS afectadas",
         fuente="Alcaldía de Cali (repositorio oficial del terremoto), El País Cali 5-sep-2026, Publimetro 10-sep-2026"),
    dict(ciudad_id="medellin", fecha="2026-08-10", evento="Sismo (M7,4, Chocó)", muertos=0, heridos=None, viv_destruidas=0,
         viv_afectadas=None, damnificados_familias=None, nota="Daños leves; 16 viviendas evacuadas; metro suspendido unas horas",
         fuente="Publimetro Medellín 14-ago-2026, Asocapitales"),
    dict(ciudad_id="bogota", fecha="2026-08-10", evento="Sismo (M7,4, Chocó)", muertos=None, heridos=None, viv_destruidas=None,
         viv_afectadas=None, damnificados_familias=None, nota="Daños menores reportados", fuente="Asocapitales, prensa"),
    dict(ciudad_id="caracas", fecha="2026-06-24", evento="Doble sismo (Mw 7,2 y 7,5, centro-norte de Venezuela)", muertos=None,
         heridos=None, viv_destruidas=None, viv_afectadas=None, damnificados_familias=None,
         nota="Edificios colapsados en San Bernardino (Marama) y Chacao; más de 2.600 muertes en el país (Reuters, 3-jul-2026); sin cifra oficial para el Municipio Libertador",
         fuente="CNN en Español, France 24, Reuters, Wikipedia (Terremotos de Venezuela de 2026)"),
    dict(ciudad_id="caracas", fecha="2026-08-23", evento="Lluvias intensas (dos semanas)", muertos=5, heridos=None,
         viv_destruidas=None, viv_afectadas=None, damnificados_familias=None,
         nota="29 deslizamientos y 45 vías inundadas", fuente="El Diario (Caracas) 28-ago-2026, NTN24"),
]


# Dónde el dato de gasto no mide lo mismo que en el resto
NOTAS_GASTO = {
    "brasilia": "No comparable: la Defensa Civil y los bomberos del DF se pagan con el Fondo Constitucional (federal), fuera de este presupuesto",
    "salvador": "No comparable: Codesal no registra gasto en la subfunción 06.182 (lo imputa a administración general u obras)",
    "bogota": "Incluye IDIGER y bomberos (Bogotá informa consolidado); 2024 sube por obras de reducción del riesgo",
}

# ------------------------------------------------------------------ Gasto: Brasil (SICONFI)
def gasto_brasil(anios=range(2015, 2025)):
    filas = []
    for c in CIUDADES:
        if "siconfi" not in c:
            continue
        for a in anios:
            cache = CRUDOS / f"siconfi_dca_IE_{c['siconfi']}_{a}.json"
            if cache.exists() and not REFRESCAR:
                items = json.loads(cache.read_text())
            else:
                url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/dca"
                try:
                    r = SESION.get(url, params={"an_exercicio": a, "no_anexo": "DCA-Anexo I-E", "id_ente": c["siconfi"]},
                                   timeout=180)
                    r.raise_for_status()
                    items = r.json().get("items", [])
                except Exception as e:  # noqa: BLE001
                    print(f"AVISO_FUENTE SICONFI {c['id']} {a}: {e}")
                    continue
                cache.write_text(json.dumps(items, ensure_ascii=False))
                time.sleep(1)
            if not items:
                continue
            d = pd.DataFrame(items)
            d = d[d.coluna == "Despesas Liquidadas"]
            def valor(pref):
                v = d[d.conta.str.startswith(pref)].valor
                return float(v.sum()) if len(v) else 0.0
            total = d[d.cod_conta == "TotalDespesas"].valor
            filas.append(dict(ciudad_id=c["id"], anio=a, moneda="BRL", fuente="SICONFI DCA Anexo I-E (liquidado)",
                              concepto="Subfunción 06.182 Defesa Civil", gasto_riesgo=valor("06.182"),
                              gasto_total=float(total.iloc[0]) if len(total) else None,
                              poblacion=int(d.populacao.iloc[0]) if "populacao" in d and len(d) else None))
    return pd.DataFrame(filas)


# ------------------------------------------------------------------ Gasto: Colombia (CUIPO)
def gasto_colombia(anios=(2023, 2024, 2025)):
    filas = []
    for c in CIUDADES:
        if "cuipo" not in c:
            continue
        for a in anios:
            cache = CRUDOS / f"cuipo_{c['cuipo']}_{a}.json"
            if cache.exists() and not REFRESCAR:
                datos = json.loads(cache.read_text())
            else:
                base = f"codigo_entidad='{c['cuipo']}' and periodo='{a}1201' and cod_vigencia_del_gasto='1'"
                try:
                    riesgo = socrata("4f7r-epif", {"$select": "sum(obligaciones) as v", "$where": base + " and cod_programatico_mga like '4503%'"})
                    total = socrata("4f7r-epif", {"$select": "sum(obligaciones) as v", "$where": base})
                except Exception as e:  # noqa: BLE001
                    print(f"AVISO_FUENTE CUIPO {c['id']} {a}: {e}")
                    continue
                datos = {"riesgo": riesgo[0].get("v"), "total": total[0].get("v")}
                cache.write_text(json.dumps(datos))
            if datos.get("total") in (None, "0"):
                continue
            filas.append(dict(ciudad_id=c["id"], anio=a, moneda="COP", fuente="CUIPO ejecución de gastos (obligaciones, vigencia actual)",
                              concepto="Programa MGA 4503 Prevención y atención de desastres y emergencias",
                              gasto_riesgo=float(datos["riesgo"] or 0), gasto_total=float(datos["total"]), poblacion=c["pob"]))
    return pd.DataFrame(filas)


# ------------------------------------------------------------------ Armado
def main():
    CRUDOS.mkdir(exist_ok=True)
    nombres = {c["id"]: c for c in CIUDADES}

    ev = pd.concat([perdidas_desinventar(), perdidas_brasil(), perdidas_colombia_ungrd()], ignore_index=True)
    ev = ev.dropna(subset=["anio"])
    ev["anio"] = ev.anio.astype(int)
    ev = ev[ev.anio <= ANIO_MAXIMO]  # DesInventar Venezuela tiene años mal cargados (2102-2104)
    ev["tipo"] = ev.evento.map(lambda e: "socionatural" if es_natural(e) and not str(e).startswith("Otro:") else "otro")
    ev.insert(1, "ciudad", ev.ciudad_id.map(lambda i: nombres[i]["nombre"]))
    ev.insert(2, "iso3", ev.ciudad_id.map(lambda i: nombres[i]["iso3"]))
    ev.sort_values(["ciudad_id", "fecha"]).to_csv(CARPETA / "perdidas_ciudad_eventos.csv", index=False)

    anual = (ev.groupby(["ciudad_id", "ciudad", "iso3", "anio", "tipo", "fuente"])
               .agg(eventos=("evento", "size"), **{k: (k, "sum") for k in COLUMNAS}).reset_index())
    anual.to_csv(CARPETA / "perdidas_ciudad_anual.csv", index=False)

    # Resumen: solo eventos socionaturales, tasas anuales por 100.000 habitantes
    nat = anual[(anual.tipo == "socionatural") & (anual.anio >= DESDE)]
    filas = []
    for c in CIUDADES:
        d = nat[nat.ciudad_id == c["id"]]
        cob = ev[(ev.ciudad_id == c["id"]) & (ev.anio >= DESDE)].anio
        a0, a1 = (int(cob.min()), int(cob.max())) if len(cob) else (None, None)
        fila = dict(ciudad_id=c["id"], ciudad=c["nombre"], iso3=c["iso3"], poblacion_ref=c["pob"],
                    fuentes=" + ".join(sorted(d.fuente.unique())), cobertura_desde=a0, cobertura_hasta=a1)
        for etiqueta, (y0, y1) in (("comun", VENTANA_COMUN), ("todo", (a0, a1))):
            if y0 is None:
                continue
            w = d[(d.anio >= y0) & (d.anio <= y1)]
            n_anios = y1 - y0 + 1
            fila[f"anios_{etiqueta}"] = n_anios
            fila[f"eventos_por_anio_{etiqueta}"] = round(w.eventos.sum() / n_anios, 2)
            for k in ("muertos", "viv_destruidas", "viv_afectadas"):
                fila[f"{k}_x100mil_anio_{etiqueta}"] = round(w[k].sum() / n_anios / c["pob"] * 1e5, 3)
            fila[f"muertos_total_{etiqueta}"] = int(w.muertos.sum())
        filas.append(fila)
    pd.DataFrame(filas).to_csv(CARPETA / "perdidas_ciudad_resumen.csv", index=False)

    e26 = pd.DataFrame(EVENTOS_2026)
    e26.insert(1, "ciudad", e26.ciudad_id.map(lambda i: nombres[i]["nombre"]))
    e26.to_csv(CARPETA / "eventos_2026_documentados.csv", index=False)

    gasto = pd.concat([gasto_brasil(), gasto_colombia()], ignore_index=True)
    if not gasto.empty:
        gasto.insert(1, "ciudad", gasto.ciudad_id.map(lambda i: nombres[i]["nombre"]))
        gasto["pct_gasto_total"] = (gasto.gasto_riesgo / gasto.gasto_total * 100).round(3)
        gasto["gasto_riesgo_por_hab"] = (gasto.gasto_riesgo / gasto.poblacion).round(2)
        gasto["nota"] = gasto.ciudad_id.map(NOTAS_GASTO).fillna("")
        gasto.to_csv(CARPETA / "gasto_riesgo_ciudad_anual.csv", index=False)

    print(f"eventos: {len(ev)}; filas anuales: {len(anual)}; gasto: {len(gasto)}")


if __name__ == "__main__":
    main()
