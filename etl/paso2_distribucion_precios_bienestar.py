"""
PASO 2 DEL ETL: sumar al dataset país-año variables de PRECIOS, DESIGUALDAD,
SALARIOS y FELICIDAD.

Parte del archivo que dejó el paso 1 (datos_procesados/paises_anual.csv) y le
agrega columnas nuevas usando la misma clave: iso3 + anio.

Variables nuevas y de dónde salen:
  Tipo de cambio          Banco Mundial (WDI)  PA.NUS.FCRF  moneda local por US$
  Paridad de poder        Banco Mundial (WDI)  PA.NUS.PPP   moneda local por $ PPA
    adquisitivo (PPA)
  Índice de Gini          Banco Mundial (WDI)  SI.POV.GINI  0 = igualdad total
  Curva de Lorenz         Banco Mundial (WDI)  SI.DST.*     % del ingreso de cada
                                                            quintil y decil
  "Canasta básica"        Banco Mundial        Food Prices for Nutrition 5.0:
                                               costo de una dieta saludable
                                               (no existe una canasta básica
                                               comparable entre países)
  Salario promedio        ILOSTAT (OIT)        ingreso promedio mensual de
                                               los asalariados, en moneda
                                               local, US$ y US$ PPA
  Felicidad               World Happiness Report 2025 (promedio de 3 años)

Cómo ejecutarlo (desde la carpeta etl/, después del paso 1):
    python paso2_distribucion_precios_bienestar.py

Se puede volver a ejecutar las veces que quieras: antes de unir, borra las
columnas que él mismo agregó la vez anterior.
"""

import io
import time
from pathlib import Path

import pandas as pd
import requests

from paso1_extraer_banco_mundial import ANIO_FIN, ANIO_INICIO, URL_BASE

CARPETA = Path(__file__).resolve().parent
CARPETA_CRUDOS = CARPETA / "datos_crudos"
ARCHIVO_PANEL = CARPETA / "datos_procesados" / "paises_anual.csv"

# Indicadores de la base principal del Banco Mundial (WDI, fuente 2).
INDICADORES_WDI = {
    "PA.NUS.FCRF": "tipo_cambio_lcu_por_usd",       # promedio del año, oficial
    "PA.NUS.PPP": "ppa_lcu_por_usd_intl",           # factor de conversión PPA
    "SI.POV.GINI": "gini",                           # 0-100
    "SI.DST.FRST.10": "ingreso_decil1_pct",          # 10 % más pobre
    "SI.DST.FRST.20": "ingreso_quintil1_pct",        # 20 % más pobre
    "SI.DST.02ND.20": "ingreso_quintil2_pct",
    "SI.DST.03RD.20": "ingreso_quintil3_pct",
    "SI.DST.04TH.20": "ingreso_quintil4_pct",
    "SI.DST.05TH.20": "ingreso_quintil5_pct",        # 20 % más rico
    "SI.DST.10TH.10": "ingreso_decil10_pct",         # 10 % más rico
}

# Food Prices for Nutrition (fuente 88): costo diario por persona de la dieta
# saludable más barata posible en cada país.
INDICADORES_DIETA = {
    "CoHD_LCU": "dieta_saludable_lcu_dia",
    "CoHD_PPP": "dieta_saludable_ppa_dia",
    "CoHD_headcount": "pct_no_puede_pagar_dieta_saludable",
}

DIAS_POR_MES = 30.4  # 365 / 12

# Columnas que agrega este paso (las usamos para que el script sea re-ejecutable).
COLUMNAS_NUEVAS = [
    *INDICADORES_WDI.values(),
    "lorenz_acum_10", "lorenz_acum_20", "lorenz_acum_40", "lorenz_acum_60",
    "lorenz_acum_80", "lorenz_acum_90",
    "gini_aprox_desde_lorenz", "ratio_quintil5_quintil1", "ratio_palma",
    *INDICADORES_DIETA.values(),
    "dieta_saludable_usd_mes", "dieta_saludable_lcu_mes",
    "salario_promedio_mensual_lcu", "salario_promedio_mensual_usd",
    "salario_promedio_mensual_ppa",
    "felicidad", "felicidad_ranking",
]


# ---------------------------------------------------------------------------
# 1. EXTRAER
# ---------------------------------------------------------------------------

def pedir_json(url, parametros=None, intentos=4):
    """GET con reintentos; devuelve el JSON."""
    for intento in range(1, intentos + 1):
        try:
            respuesta = requests.get(url, params=parametros, timeout=120)
            respuesta.raise_for_status()
            return respuesta.json()
        except requests.RequestException as error:
            if intento == intentos:
                raise RuntimeError(f"No se pudo descargar {url}: {error}") from error
            time.sleep(2 ** intento)


def descargar_banco_mundial(codigos, fuente):
    """Tabla larga iso3, anio, variable, valor para indicadores de la API v2.

    Si countryiso3code viene vacío (pasa en algunas fuentes) usamos country["id"].
    """
    filas = []
    for codigo, nombre in codigos.items():
        contenido = pedir_json(
            f"{URL_BASE}/country/all/indicator/{codigo}",
            {"format": "json", "per_page": 30000, "source": fuente,
             "date": f"{ANIO_INICIO}:{ANIO_FIN}"},
        )
        if len(contenido) < 2:
            raise ValueError(f"La API devolvió un error para {codigo}: {contenido}")
        datos = [d for d in contenido[1] or [] if d["value"] is not None]
        print(f"    {nombre:<36} {len(datos):>6} valores")
        filas += [
            {"iso3": d["countryiso3code"] or d["country"]["id"], "anio": int(d["date"]),
             "variable": nombre, "valor": d["value"]}
            for d in datos
        ]
    return pd.DataFrame(filas)


def descargar_dieta_saludable():
    """Food Prices for Nutrition usa la API "avanzada" (por dimensiones).

    La URL tiene la forma /sources/88/country/all/series/A;B;C/time/all y cada
    dato trae una lista de variables (País, Clasificación, Serie, Año).
    """
    series = ";".join(INDICADORES_DIETA)
    contenido = pedir_json(
        f"{URL_BASE}/sources/88/country/all/series/{series}/time/all",
        {"format": "json", "per_page": 30000},
    )
    filas = []
    for dato in contenido["source"]["data"]:
        dims = {v["concept"]: v["id"] for v in dato["variable"]}
        if dato["value"] is None:
            continue
        filas.append({
            "iso3": dims["Country"],
            "anio": int(dims["Time"].removeprefix("YR")),
            "variable": INDICADORES_DIETA[dims["Series"]],
            "valor": dato["value"],
            "version": dims["Classification"],
        })
    tabla = pd.DataFrame(filas)
    print(f"    dieta saludable ({', '.join(sorted(tabla['version'].unique()))})"
          f"             {len(tabla):>6} valores")
    return tabla.drop(columns="version")


# Salario promedio (ILOSTAT) y felicidad (World Happiness Report) vienen de
# servidores distintos del Banco Mundial.

URL_ILOSTAT = (
    "https://rplumber.ilo.org/data/indicator/?id=EAR_EMTA_SEX_CUR_NB_A"
    f"&timefrom={ANIO_INICIO}&timeto={ANIO_FIN}&type=code&format=.csv"
)
URL_FELICIDAD = "https://files.worldhappiness.report/WHR25_Data_Figure_2.1v3.xlsx"

# El servidor de la OIT rechaza (403) las peticiones sin un User-Agent de navegador.
CABECERAS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"}

# ILOSTAT usa KOS para Kosovo; el Banco Mundial, XKX.
ISO3_ILO_A_BANCO_MUNDIAL = {"KOS": "XKX"}

# El World Happiness Report identifica a los países por nombre, no por código.
# Los que se escriben distinto que en el Banco Mundial los traducimos a mano.
# Taiwán, Chipre del Norte y Somalilandia no están en la lista del Banco Mundial
# y quedan afuera.
NOMBRES_WHR_A_ISO3 = {
    "Congo": "COG", "DR Congo": "COD", "Côte d’Ivoire": "CIV", "Egypt": "EGY",
    "Gambia": "GMB", "Hong Kong SAR of China": "HKG", "Iran": "IRN",
    "Kyrgyzstan": "KGZ", "Puerto Rico": "PRI", "Republic of Korea": "KOR",
    "Republic of Moldova": "MDA", "Slovakia": "SVK", "Somalia": "SOM",
    "State of Palestine": "PSE", "Swaziland": "SWZ", "Syria": "SYR",
    "Türkiye": "TUR", "Venezuela": "VEN", "Yemen": "YEM",
}


def descargar(url):
    """Descarga un archivo con reintentos y devuelve sus bytes."""
    for intento in range(1, 5):
        try:
            respuesta = requests.get(url, headers=CABECERAS, timeout=180)
            respuesta.raise_for_status()
            return respuesta.content
        except requests.RequestException as error:
            if intento == 4:
                raise RuntimeError(f"No se pudo descargar {url}: {error}") from error
            time.sleep(2 ** intento)


def descargar_salario_ilostat():
    """Ingreso promedio mensual de los asalariados, ambos sexos (OIT).

    ILOSTAT ya publica cada valor en tres monedas: local, dólares al tipo de
    cambio del año y dólares PPA de 2021. Elige una sola fuente (encuesta de
    hogares, de empresas o registro administrativo) por país y año, pero la
    fuente puede cambiar entre países: compara con cuidado.
    """
    contenido = descargar(URL_ILOSTAT)
    (CARPETA_CRUDOS / "ilostat_salario_promedio_mensual.csv").write_bytes(contenido)
    ilo = pd.read_csv(io.BytesIO(contenido), encoding="utf-8-sig")
    ilo = ilo[ilo["sex"] == "SEX_T"]
    ilo["iso3"] = ilo["ref_area"].replace(ISO3_ILO_A_BANCO_MUNDIAL)
    ilo["anio"] = ilo["time"].astype(int)
    ilo["variable"] = ilo["classif1"].map({
        "CUR_TYPE_LCU": "salario_promedio_mensual_lcu",
        "CUR_TYPE_USD": "salario_promedio_mensual_usd",
        "CUR_TYPE_PPP": "salario_promedio_mensual_ppa",
    })
    tabla = ilo.pivot_table(index=["iso3", "anio"], columns="variable",
                            values="obs_value", aggfunc="first").reset_index()
    tabla.columns.name = None
    # Limpieza: algunos años vienen en otra unidad (Malta 2000-2008 da unas
    # 2-7 monedas por MES, Egipto 2008 unos 13 dólares). Regla: si un valor en
    # dólares es menos del 10 % de la mediana de ese país, lo dejamos vacío.
    mediana = tabla.groupby("iso3")["salario_promedio_mensual_usd"].transform("median")
    sospechoso = tabla["salario_promedio_mensual_usd"] < 0.1 * mediana
    descartados = tabla.loc[sospechoso, ["iso3", "anio"]].astype(str).agg(" ".join, axis=1)
    print(f"    (valores de salario descartados por sospechosos: {', '.join(descartados)})")
    tabla.loc[sospechoso, tabla.columns[2:]] = None
    print(f"    salario promedio (ILOSTAT)             {len(tabla):>6} país-año, "
          f"{tabla['iso3'].nunique()} países")
    return tabla


def descargar_felicidad(paises):
    """Puntaje de felicidad del World Happiness Report 2025 (0 a 10).

    Es la "escalera de Cantril" de la encuesta Gallup: cada persona ubica su
    vida entre 0 (la peor posible) y 10 (la mejor posible). El informe publica
    el promedio de 3 años: el valor de 2024 promedia 2022, 2023 y 2024.
    """
    contenido = descargar(URL_FELICIDAD)
    (CARPETA_CRUDOS / "whr2025_figura_2_1.xlsx").write_bytes(contenido)
    whr = pd.read_excel(io.BytesIO(contenido))
    nombre_a_iso3 = dict(zip(paises["pais"], paises["iso3"])) | NOMBRES_WHR_A_ISO3
    whr["iso3"] = whr["Country name"].map(nombre_a_iso3)
    sin_codigo = sorted(whr.loc[whr["iso3"].isna(), "Country name"].unique())
    if sin_codigo:
        print(f"    (sin código ISO3, se descartan: {', '.join(sin_codigo)})")
    tabla = whr.dropna(subset=["iso3"]).rename(columns={
        "Year": "anio",
        "Life evaluation (3-year average)": "felicidad",
        "Rank": "felicidad_ranking",
    })[["iso3", "anio", "felicidad", "felicidad_ranking"]]
    tabla["felicidad_ranking"] = tabla["felicidad_ranking"].astype("Int64")
    print(f"    felicidad (WHR 2025)                   {len(tabla):>6} país-año, "
          f"{tabla['iso3'].nunique()} países")
    return tabla


# ---------------------------------------------------------------------------
# 2. TRANSFORMAR: KPIs derivados
# ---------------------------------------------------------------------------

def calcular_lorenz(df):
    """Puntos de la curva de Lorenz y medidas de desigualdad.

    La curva de Lorenz dice qué % del ingreso total acumula el x % más pobre.
    Con igualdad perfecta, el 40 % más pobre tendría el 40 % del ingreso.
    El índice de Gini es el área entre esa diagonal y la curva, por 2.
    """
    q = [df[f"ingreso_quintil{i}_pct"] for i in range(1, 6)]
    df["lorenz_acum_10"] = df["ingreso_decil1_pct"]
    df["lorenz_acum_20"] = q[0]
    df["lorenz_acum_40"] = q[0] + q[1]
    df["lorenz_acum_60"] = q[0] + q[1] + q[2]
    df["lorenz_acum_80"] = q[0] + q[1] + q[2] + q[3]
    df["lorenz_acum_90"] = 100 - df["ingreso_decil10_pct"]
    puntos = [f"lorenz_acum_{p}" for p in (10, 20, 40, 60, 80, 90)]
    df[puntos] = df[puntos].round(1)

    # Gini aproximado con la regla del trapecio sobre los 8 puntos conocidos.
    # Siempre da un poco MENOS que el Gini oficial porque supone igualdad
    # dentro de cada tramo; sirve para entender de dónde sale el número.
    x = [0, 10, 20, 40, 60, 80, 90, 100]
    y = [0, df["lorenz_acum_10"], df["lorenz_acum_20"], df["lorenz_acum_40"],
         df["lorenz_acum_60"], df["lorenz_acum_80"], df["lorenz_acum_90"], 100]
    area = sum((x[i] - x[i - 1]) / 100 * (y[i] + y[i - 1]) / 2 / 100 for i in range(1, 8))
    df["gini_aprox_desde_lorenz"] = ((1 - 2 * area) * 100).round(1)

    df["ratio_quintil5_quintil1"] = (q[4] / q[0]).round(2)          # S80/S20
    df["ratio_palma"] = (df["ingreso_decil10_pct"] / (q[0] + q[1])).round(2)
    return df


def convertir_monedas(df):
    """Pasa montos en moneda local a dólares con el tipo de cambio del año."""
    df["dieta_saludable_lcu_mes"] = (df["dieta_saludable_lcu_dia"] * DIAS_POR_MES).round(2)
    df["dieta_saludable_usd_mes"] = (
        df["dieta_saludable_lcu_mes"] / df["tipo_cambio_lcu_por_usd"]).round(2)
    return df


# ---------------------------------------------------------------------------
# 3. CARGAR: unir al panel del paso 1
# ---------------------------------------------------------------------------

def main():
    CARPETA_CRUDOS.mkdir(exist_ok=True)
    panel = pd.read_csv(ARCHIVO_PANEL)
    panel["poblacion"] = panel["poblacion"].astype("Int64")  # entero aunque falte algún dato
    panel = panel.drop(columns=[c for c in COLUMNAS_NUEVAS if c in panel.columns])
    print(f"Panel del paso 1: {len(panel)} filas, {panel['iso3'].nunique()} países")

    print("1/3 Tipo de cambio, PPA, Gini y reparto del ingreso (WDI)...")
    largo = [descargar_banco_mundial(INDICADORES_WDI, 2)]
    print("2/3 Costo de una dieta saludable (Food Prices for Nutrition)...")
    largo.append(descargar_dieta_saludable())
    largo = pd.concat(largo, ignore_index=True)
    largo.to_csv(CARPETA_CRUDOS / "paso2_banco_mundial_largo.csv", index=False)

    nuevo = largo.pivot_table(index=["iso3", "anio"], columns="variable",
                              values="valor", aggfunc="first").reset_index()
    nuevo.columns.name = None

    print("3/3 Salario promedio (ILOSTAT) y felicidad (World Happiness Report)...")
    paises = panel[["iso3", "pais"]].drop_duplicates()
    for extra in (descargar_salario_ilostat(), descargar_felicidad(paises)):
        nuevo = nuevo.merge(extra, on=["iso3", "anio"], how="outer")

    # LEFT JOIN: conservamos exactamente las filas del panel (217 países x años).
    panel = panel.merge(nuevo, on=["iso3", "anio"], how="left")
    for columna in COLUMNAS_NUEVAS:
        if columna not in panel.columns:
            panel[columna] = pd.NA
    panel = convertir_monedas(calcular_lorenz(panel))
    panel["felicidad_ranking"] = panel["felicidad_ranking"].astype("Int64")

    columnas_paso1 = [c for c in panel.columns if c not in COLUMNAS_NUEVAS]
    panel = panel[columnas_paso1 + COLUMNAS_NUEVAS]
    panel.to_csv(ARCHIVO_PANEL, index=False)

    print(f"\nListo: {len(panel)} filas x {panel.shape[1]} columnas -> {ARCHIVO_PANEL}")
    print("\nPaíses con al menos un dato, por variable nueva:")
    print(panel.groupby("iso3")[COLUMNAS_NUEVAS].count().gt(0).sum().to_string())


if __name__ == "__main__":
    main()
