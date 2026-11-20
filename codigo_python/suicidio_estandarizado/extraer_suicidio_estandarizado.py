"""
TASA DE SUICIDIO ESTANDARIZADA POR EDAD Y TASA POR GRUPO DE EDAD (OMS),
por país, año y sexo.

Por qué hace falta: el paso 1 trae del Banco Mundial la tasa CRUDA de suicidio
(SH.STA.SUIC.P5 = muertes / población x 100.000, "not age-adjusted"). La tasa
cruda depende de cuántos viejos y cuántos jóvenes tiene cada país, así que no
sirve para comparar países con pirámides distintas (Japón vs. Níger, por
ejemplo). La tasa ESTANDARIZADA aplica las tasas de cada grupo de edad del país
a una misma población de referencia (la población estándar mundial de la OMS),
así las diferencias que quedan son de riesgo y no de estructura de edades.

Qué hace este script, en orden:
  1. Descarga de la API del Global Health Observatory (OMS):
       MH_12       -> tasa estandarizada por edad (con intervalo de incertidumbre)
       SDGSUICIDE  -> tasa cruda (para compararla) y, solo para 2021, la tasa
                      de cada grupo de edad (10-19, 20-29 ... 70 y más)
     Las dos vienen por sexo: ambos, hombres, mujeres.
     La tasa de un grupo de edad no necesita estandarizarse: ya compara gente
     de la misma edad entre países.
  2. Se queda solo con países (descarta regiones y el mundo) y les pone el
     nombre en español del maestro de países.
  3. Guarda en esta carpeta:
       suicidio_estandarizado_largo.csv      una fila por país + año + sexo
       suicidio_estandarizado_pais_anual.csv una fila por país + año (para unir
                                             con paises_anual.csv por iso3+anio)
       tabla_suicidio_<último año>.csv/.xlsx ranking del último año disponible
       suicidio_por_edad_largo.csv           una fila por país + año + sexo + grupo de edad
       tabla_suicidio_por_edad_<año>.csv/.xlsx  una fila por país y sexo, una columna
                                             por grupo de edad de 10 años

Cómo ejecutarlo (desde la carpeta etl/):
    python suicidio_estandarizado/extraer_suicidio_estandarizado.py

Necesita acceso a ghoapi.azureedge.net. La OMS anunció que esta API OData se
reemplaza; si deja de responder, el error lo dice y hay que cambiar URL_BASE.
"""

from pathlib import Path

import gzip
import json

import pandas as pd
import requests

URL_BASE = "https://ghoapi.azureedge.net/api"

INDICADORES = {
    "MH_12": "estandarizada",
    "SDGSUICIDE": "cruda",
}

SEXOS = {"SEX_BTSX": "total", "SEX_MLE": "hombres", "SEX_FMLE": "mujeres"}

# Grupos de edad de la OMS. Se superponen (15-29 incluye 15-19 y 20-29), por eso
# la tabla ancha usa solo los de 10 años, que juntos cubren de 10 años en adelante.
TODAS_LAS_EDADES = "AGEGROUP_YEARSALL"
GRUPOS_10_ANIOS = ["10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70+"]

CARPETA = Path(__file__).resolve().parent
MAESTRO_PAISES = CARPETA.parent / "maestros" / "paises_maestro.csv"
CRUDOS = CARPETA / "crudos"


def descargar(codigo):
    """Devuelve el indicador de la OMS como tabla, solo filas de países.

    Cada descarga se guarda tal cual en crudos/<código>.json.gz. Si la API no
    responde (o la OMS la da de baja), se usa esa copia propia y se avisa.
    """
    copia = CRUDOS / f"{codigo}.json.gz"
    try:
        respuesta = requests.get(f"{URL_BASE}/{codigo}", timeout=120)
        respuesta.raise_for_status()
        filas = respuesta.json()["value"]
        CRUDOS.mkdir(exist_ok=True)
        with gzip.open(copia, "wt", encoding="utf-8") as f:
            json.dump(filas, f)
    except (requests.RequestException, ValueError, KeyError) as error:
        if not copia.exists():
            raise
        print(f"  AVISO_FUENTE {copia.name}: falló la descarga ({error}); se usa la copia anterior")
        with gzip.open(copia, "rt", encoding="utf-8") as f:
            filas = json.load(f)
    df = pd.DataFrame(filas)
    df = df[df["SpatialDimType"] == "COUNTRY"]
    return pd.DataFrame({
        "iso3": df["SpatialDim"],
        "anio": df["TimeDim"].astype(int),
        "sexo": df["Dim1"].map(SEXOS),
        "grupo_edad": df["Dim2"].fillna(TODAS_LAS_EDADES),
        "valor": df["NumericValue"],
        "ic_bajo": df["Low"],
        "ic_alto": df["High"],
    })


def main():
    tablas = {}
    for codigo, tipo in INDICADORES.items():
        print(f"Descargando {codigo} ({tipo})...")
        tablas[tipo] = descargar(codigo)
        print(f"  {len(tablas[tipo]):,} filas de países")

    # La cruda trae también filas por grupo de edad: se separan, y las de "todas las
    # edades" son las que se comparan con la estandarizada
    cruda = tablas["cruda"]
    por_edad = cruda[cruda["grupo_edad"] != TODAS_LAS_EDADES].copy()
    tablas["cruda"] = cruda[cruda["grupo_edad"] == TODAS_LAS_EDADES]
    tablas["estandarizada"] = tablas["estandarizada"].drop(columns="grupo_edad")

    largo = tablas["estandarizada"].rename(columns={
        "valor": "tasa_estandarizada_x100k",
        "ic_bajo": "ic_bajo_estandarizada",
        "ic_alto": "ic_alto_estandarizada",
    }).merge(
        tablas["cruda"][["iso3", "anio", "sexo", "valor"]]
        .rename(columns={"valor": "tasa_cruda_x100k"}),
        on=["iso3", "anio", "sexo"], how="outer",
    )

    paises = pd.read_csv(MAESTRO_PAISES, usecols=["iso3", "nombre_es", "region_bm_es"])
    largo = paises.merge(largo, on="iso3", how="right")
    sin_nombre = largo.loc[largo["nombre_es"].isna(), "iso3"].unique()
    if len(sin_nombre):
        print(f"  Aviso: códigos sin nombre en el maestro: {', '.join(sin_nombre)}")
    largo = largo.sort_values(["iso3", "anio", "sexo"])
    largo.to_csv(CARPETA / "suicidio_estandarizado_largo.csv", index=False)

    # Formato ancho por país-año, con los mismos nombres que usa el panel.
    ancho = largo.pivot_table(
        index=["iso3", "anio"], columns="sexo",
        values=["tasa_estandarizada_x100k", "tasa_cruda_x100k"],
    )
    ancho.columns = [
        f"suicidio_{'estandarizado' if medida.startswith('tasa_est') else 'crudo_oms'}_{sexo}_x100k"
        for medida, sexo in ancho.columns
    ]
    ancho = ancho.reset_index()
    ancho.to_csv(CARPETA / "suicidio_estandarizado_pais_anual.csv", index=False)

    # Tabla resumen del último año: ranking por tasa estandarizada total.
    ultimo = int(largo["anio"].max())
    tabla = (
        largo[largo["anio"] == ultimo]
        .pivot_table(index=["iso3", "nombre_es", "region_bm_es"], columns="sexo",
                     values=["tasa_estandarizada_x100k", "tasa_cruda_x100k"])
    )
    tabla.columns = [f"{m}_{s}" for m, s in tabla.columns]
    tabla = tabla.reset_index()
    tabla = tabla.rename(columns={
        "nombre_es": "pais",
        "region_bm_es": "region",
        "tasa_estandarizada_x100k_total": "estandarizada_total",
        "tasa_estandarizada_x100k_hombres": "estandarizada_hombres",
        "tasa_estandarizada_x100k_mujeres": "estandarizada_mujeres",
        "tasa_cruda_x100k_total": "cruda_total",
    })
    # Con tasa de mujeres 0 la razón no se puede calcular: queda vacía.
    tabla["razon_hombres_mujeres"] = (
        tabla["estandarizada_hombres"] / tabla["estandarizada_mujeres"].where(tabla["estandarizada_mujeres"] > 0)
    ).round(1)
    tabla["diferencia_cruda_menos_estandarizada"] = (
        tabla["cruda_total"] - tabla["estandarizada_total"]
    ).round(1)
    tabla = tabla.sort_values("estandarizada_total", ascending=False)
    tabla.insert(0, "ranking", range(1, len(tabla) + 1))
    columnas = ["ranking", "iso3", "pais", "region", "estandarizada_total",
                "estandarizada_hombres", "estandarizada_mujeres",
                "razon_hombres_mujeres", "cruda_total",
                "diferencia_cruda_menos_estandarizada"]
    tabla = tabla[columnas]
    tabla.to_csv(CARPETA / f"tabla_suicidio_{ultimo}.csv", index=False)
    try:
        tabla.to_excel(CARPETA / f"tabla_suicidio_{ultimo}.xlsx", index=False)
    except ImportError:
        print("  (sin openpyxl: no se generó el .xlsx, el .csv tiene lo mismo)")

    # Tasas por grupo de edad (la OMS las publica solo para 2021)
    por_edad["grupo_edad"] = por_edad["grupo_edad"].str.replace("AGEGROUP_YEARS", "").str.replace("PLUS", "+")
    por_edad = (paises.merge(por_edad, on="iso3", how="right")
                .rename(columns={"valor": "tasa_x100k"})
                .drop(columns=["ic_bajo", "ic_alto"])
                .sort_values(["iso3", "anio", "sexo", "grupo_edad"]))
    por_edad.to_csv(CARPETA / "suicidio_por_edad_largo.csv", index=False)
    anio_edad = int(por_edad["anio"].max())
    edad = (por_edad[(por_edad["anio"] == anio_edad) & por_edad["grupo_edad"].isin(GRUPOS_10_ANIOS)]
            .pivot_table(index=["iso3", "nombre_es", "region_bm_es", "sexo"], columns="grupo_edad",
                         values="tasa_x100k")
            .round(1)[GRUPOS_10_ANIOS].reset_index())
    edad.columns.name = None
    edad = edad.rename(columns={"nombre_es": "pais", "region_bm_es": "region"})
    edad["sexo"] = pd.Categorical(edad["sexo"], ["total", "hombres", "mujeres"])
    edad = edad.sort_values(["pais", "sexo"])
    edad.to_csv(CARPETA / f"tabla_suicidio_por_edad_{anio_edad}.csv", index=False)
    try:
        edad.to_excel(CARPETA / f"tabla_suicidio_por_edad_{anio_edad}.xlsx", index=False)
    except ImportError:
        pass
    print(f"Por edad: {edad['iso3'].nunique()} países, {anio_edad}, grupos {', '.join(GRUPOS_10_ANIOS)}")

    print(f"Listo: {largo['iso3'].nunique()} países, "
          f"{largo['anio'].min()}-{ultimo}. Tabla de {ultimo}: {len(tabla)} países.")


if __name__ == "__main__":
    main()
