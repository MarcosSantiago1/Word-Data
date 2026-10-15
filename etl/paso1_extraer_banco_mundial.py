"""
PASO 1 DEL ETL: EXTRAER datos de países desde la API del Banco Mundial.

Qué hace este script, en orden:
  1. Descarga la lista oficial de países (con su código ISO Alpha-3, región
     y nivel de ingreso) y descarta los "agregados" (Mundo, Unión Europea...).
  2. Para cada indicador de la tabla INDICADORES, descarga todos los valores
     de todos los países entre ANIO_INICIO y ANIO_FIN.
  3. Guarda dos archivos:
       datos_crudos/banco_mundial_largo.csv  -> formato "largo": una fila por
                                                país + año + indicador.
       datos_procesados/paises_anual.csv     -> formato "ancho": una fila por
                                                país + año, una columna por
                                                indicador. Es la tabla base
                                                del dashboard.

Cómo ejecutarlo (desde una terminal, dentro de la carpeta etl/):
    pip install -r requirements.txt
    python paso1_extraer_banco_mundial.py

No necesita clave ni registro: la API del Banco Mundial es abierta.
Documentación de la API: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
"""

import time
from pathlib import Path

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# 1. CONFIGURACIÓN: lo único que normalmente querrás cambiar
# ---------------------------------------------------------------------------

ANIO_INICIO = 2000
ANIO_FIN = 2024

# Código del Banco Mundial  ->  nombre corto de la columna en nuestro dataset.
# Cada código se puede consultar en https://data.worldbank.org/indicator/<CÓDIGO>
INDICADORES = {
    # Demografía y economía (base)
    "SP.POP.TOTL": "poblacion",
    "NY.GDP.PCAP.PP.KD": "pib_pc_ppp",              # US$ internacionales constantes
    # Salud pública
    "SP.DYN.LE00.IN": "esperanza_vida",              # años
    "SP.DYN.IMRT.IN": "mortalidad_infantil",         # por 1.000 nacidos vivos
    "SH.MED.BEDS.ZS": "camas_hospital_x1000",
    "SH.MED.PHYS.ZS": "medicos_x1000",
    # Salud mental (el Banco Mundial republica estos datos de la OMS)
    "SH.STA.SUIC.P5": "suicidio_total_x100k",
    "SH.STA.SUIC.MA.P5": "suicidio_hombres_x100k",
    "SH.STA.SUIC.FE.P5": "suicidio_mujeres_x100k",
    # Inversión pública
    "SH.XPD.GHED.GD.ZS": "gasto_salud_pct_pib",      # gasto del gobierno en salud
    "SH.XPD.GHED.GE.ZS": "gasto_salud_pct_gasto_pub",
    "SE.XPD.TOTL.GD.ZS": "gasto_educacion_pct_pib",
}

URL_BASE = "https://api.worldbank.org/v2"

CARPETA = Path(__file__).resolve().parent
CARPETA_CRUDOS = CARPETA / "datos_crudos"
CARPETA_PROCESADOS = CARPETA / "datos_procesados"


# ---------------------------------------------------------------------------
# 2. FUNCIONES DE AYUDA
# ---------------------------------------------------------------------------

def pedir_a_la_api(ruta, parametros, intentos=4):
    """Hace una petición a la API y devuelve todas las filas, página a página.

    La API responde siempre una lista de dos elementos:
        [ {información de paginación}, [filas de datos] ]
    Si hay más de una página, las pedimos todas y las juntamos.
    """
    parametros = {"format": "json", "per_page": 20000, **parametros}
    filas = []
    pagina = 1
    while True:
        parametros["page"] = pagina
        respuesta = None
        for intento in range(1, intentos + 1):
            try:
                respuesta = requests.get(f"{URL_BASE}/{ruta}", params=parametros, timeout=60)
                respuesta.raise_for_status()
                break
            except requests.RequestException as error:
                if intento == intentos:
                    raise RuntimeError(
                        f"No se pudo conectar con la API del Banco Mundial ({ruta}).\n"
                        f"Revisa tu conexión a internet. Detalle: {error}"
                    ) from error
                espera = 2 ** intento
                print(f"   Fallo de conexión, reintento en {espera} s...")
                time.sleep(espera)

        contenido = respuesta.json()
        # Cuando algo va mal (p. ej. un código de indicador inexistente) la API
        # devuelve un solo elemento con un mensaje en vez de [paginación, datos].
        if len(contenido) < 2:
            raise ValueError(f"La API devolvió un error para '{ruta}': {contenido}")

        paginacion, datos = contenido
        filas.extend(datos or [])
        if pagina >= int(paginacion["pages"]):
            return filas
        pagina += 1


def descargar_paises():
    """Devuelve una tabla con los países reales (sin agregados regionales)."""
    filas = pedir_a_la_api("country", {})
    paises = pd.DataFrame(
        {
            "iso3": fila["id"],
            "pais": fila["name"],
            "region": fila["region"]["value"],
            "nivel_ingreso": fila["incomeLevel"]["value"],
        }
        for fila in filas
    )
    # Algunos nombres traen espacios sobrantes al final; los limpiamos.
    paises["region"] = paises["region"].str.strip()
    # Los agregados ("World", "Latin America & Caribbean", "High income"...)
    # tienen la región "Aggregates". No son países, así que los quitamos.
    return paises[paises["region"] != "Aggregates"].reset_index(drop=True)


def descargar_indicador(codigo):
    """Devuelve una tabla larga: iso3, anio, indicador, valor."""
    filas = pedir_a_la_api(
        f"country/all/indicator/{codigo}",
        {"date": f"{ANIO_INICIO}:{ANIO_FIN}"},
    )
    return pd.DataFrame(
        {
            "iso3": fila["countryiso3code"],
            "anio": int(fila["date"]),
            "indicador": codigo,
            "valor": fila["value"],
        }
        for fila in filas
    )


def a_formato_ancho(largo, paises):
    """Pasa de una fila por indicador a una fila por país y año."""
    largo = largo.assign(variable=largo["indicador"].map(INDICADORES))
    ancho = largo.pivot_table(
        index=["iso3", "anio"], columns="variable", values="valor", aggfunc="first"
    ).reset_index()
    ancho.columns.name = None
    # Aseguramos que existan todas las columnas, aunque un indicador venga vacío.
    for columna in INDICADORES.values():
        if columna not in ancho.columns:
            ancho[columna] = pd.NA
    # Unimos con la tabla de países usando el código ISO3 como clave (JOIN).
    # how="inner" deja fuera los agregados, que no están en `paises`.
    ancho = paises.merge(ancho, on="iso3", how="inner")
    columnas = ["iso3", "pais", "region", "nivel_ingreso", "anio", *INDICADORES.values()]
    return ancho[columnas].sort_values(["iso3", "anio"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3. PROGRAMA PRINCIPAL
# ---------------------------------------------------------------------------

def main():
    CARPETA_CRUDOS.mkdir(exist_ok=True)
    CARPETA_PROCESADOS.mkdir(exist_ok=True)

    print("1/3 Descargando la lista de países...")
    paises = descargar_paises()
    print(f"    {len(paises)} países (sin agregados regionales)")

    print(f"2/3 Descargando {len(INDICADORES)} indicadores ({ANIO_INICIO}-{ANIO_FIN})...")
    tablas = []
    for codigo, nombre in INDICADORES.items():
        tabla = descargar_indicador(codigo)
        con_dato = tabla["valor"].notna().sum()
        print(f"    {nombre:<28} {con_dato:>6} valores")
        tablas.append(tabla)
    largo = pd.concat(tablas, ignore_index=True)

    # Guardamos los datos crudos tal como llegaron (útil para auditar).
    largo.to_csv(CARPETA_CRUDOS / "banco_mundial_largo.csv", index=False)
    paises.to_csv(CARPETA_CRUDOS / "paises.csv", index=False)

    print("3/3 Construyendo la tabla país-año...")
    ancho = a_formato_ancho(largo.dropna(subset=["valor"]), paises)
    salida = CARPETA_PROCESADOS / "paises_anual.csv"
    ancho.to_csv(salida, index=False)

    print(f"\nListo: {len(ancho)} filas, {ancho['iso3'].nunique()} países -> {salida}")
    print("\nPorcentaje de datos disponibles por variable:")
    cobertura = ancho[list(INDICADORES.values())].notna().mean().mul(100).round(1)
    print(cobertura.sort_values(ascending=False).to_string())


if __name__ == "__main__":
    main()
