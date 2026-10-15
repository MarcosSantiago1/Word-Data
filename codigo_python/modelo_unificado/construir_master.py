"""
Master unificado de países y provincias/estados (base relacional normalizada).

Junta en UNA base SQLite todo lo que el proyecto fue construyendo por separado:

    maestros/paises_maestro.csv            251 países y territorios (códigos ISO, nombres, capital)
    maestros/subdivisiones_maestro.csv     3.590 subdivisiones ISO 3166-2 de primer nivel
    datos_procesados/paises_anual.csv      panel país-año (pasos 1 y 2)
    alianzas/*.csv                          membresías, tratados, pactos militares
    argentina_provincias/*.csv              20 tablas provincia-año (o provincia-año-rama, etc.)
    factbook/*.csv                          CIA World Factbook (foto de enero 2026): perfil, fronteras,
                                            religiones/etnias/idiomas y socios comerciales

Las maestras son la base de las dimensiones; acá se les agrega lo que faltaba para un modelo
relacional: ids numéricos, la jerarquía de regiones de la ONU (M49: continente > subregión),
el tipo de entidad (Estado, territorio dependiente...) con su soberano, reclamos territoriales,
regiones EPH de Argentina y tablas de equivalencias (cómo llama cada fuente a cada país).

Orden de ejecución: pasos 1 y 2, alianzas, argentina_provincias, maestros y por último este
(factbook/extraer_factbook.py se corre una sola vez: el Factbook ya no se publica):

    cd etl/modelo_unificado
    python construir_master.py

Salidas (en esta carpeta):
    master_paises_provincias.sqlite   la base completa (dimensiones + hechos + vistas)
    esquema.sql                       el DDL (CREATE TABLE / VIEW) para llevarlo a otro motor
    tablas/*.csv                      dimensiones, tablas puente, catálogo y diccionario

Los identificadores son estables entre corridas: pais_id = código ISO numérico (900+ para
Kosovo e Islas del Canal, que no tienen); subdivision_id se guarda en tablas/dim_subdivision.csv
y se reutiliza, así que una subdivisión nueva recibe un id nuevo sin mover los anteriores.
"""

import json
import os
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path

import pandas as pd
import pycountry
import pyreadr
import requests

MASTER = Path(__file__).resolve().parent
ETL = MASTER.parent
CRUDOS = MASTER / "crudos"
TABLAS = MASTER / "tablas"
BASE = MASTER / "master_paises_provincias.sqlite"
PROV = ETL / "argentina_provincias"
MAESTROS = ETL / "maestros"
ALI = ETL / "alianzas"
FB = ETL / "factbook"
NUEVAS = ETL / "fuentes_nuevas"
SOCIALES = ETL / "indicadores_sociales_digitales"

# Reutilizamos los diccionarios que ya viven en los otros scripts (una sola fuente de verdad)
sys.dont_write_bytecode = True  # no dejar __pycache__ en las carpetas de los otros pasos
sys.path[:0] = [str(ETL), str(PROV), str(ALI)]
from extraer_alianzas_internacionales import COW_CCODE_ISO3, iso3_por_nombre  # noqa: E402
from extraer_argentina_provincias import (CODIGO_CCKP, CODIGO_INDEC,  # noqa: E402
                                          REGION_DE_PROVINCIA, REGION_EPH)
from paso2_distribucion_precios_bienestar import (ISO3_ILO_A_BANCO_MUNDIAL,  # noqa: E402
                                                  NOMBRES_WHR_A_ISO3)

# Namibia es "NA": sin keep_default_na pandas lo lee como dato faltante
LEER = dict(keep_default_na=False, na_values=[""])

URL_BM_PAISES = "https://api.worldbank.org/v2/country?format=json&per_page=400"
URL_M49 = ("https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/"
           "master/all/all.csv")

# ---------------------------------------------------------------------------
# Convenciones de nombres
# ---------------------------------------------------------------------------
# Tablas: dim_ (catálogos), hecho_ (medidas por año), rel_ (relaciones muchos a muchos),
#         ref_ (documentación), v_ (vistas listas para el dashboard).
# Columnas: snake_case, en español, sin tildes ni espacios; la unidad va al final
#           (_pct, _x1000, _mill_pesos_2004, _usd, ...). El año siempre es "anio".


def snake(texto):
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")


# ---------------------------------------------------------------------------
# Traducciones y casos especiales cargados a mano
# ---------------------------------------------------------------------------
REGION_M49_ES = {
    "Africa": "África", "Americas": "América", "Asia": "Asia", "Europe": "Europa",
    "Oceania": "Oceanía",
    "Northern Africa": "Norte de África", "Sub-Saharan Africa": "África subsahariana",
    "Latin America and the Caribbean": "América Latina y el Caribe",
    "Northern America": "América del Norte (EE. UU., Canadá y otros)",
    "Central Asia": "Asia Central", "Eastern Asia": "Asia Oriental",
    "South-eastern Asia": "Sudeste Asiático", "Southern Asia": "Asia Meridional",
    "Western Asia": "Asia Occidental", "Eastern Europe": "Europa Oriental",
    "Northern Europe": "Europa del Norte", "Southern Europe": "Europa del Sur",
    "Western Europe": "Europa Occidental", "Australia and New Zealand": "Australia y Nueva Zelanda",
    "Melanesia": "Melanesia", "Micronesia": "Micronesia", "Polynesia": "Polinesia",
    "Caribbean": "Caribe", "Central America": "América Central", "South America": "América del Sur",
    "Eastern Africa": "África Oriental", "Middle Africa": "África Central",
    "Southern Africa": "África Austral", "Western Africa": "África Occidental",
}
REGION_BM_ES = {
    "EAS": "Asia Oriental y el Pacífico", "ECS": "Europa y Asia Central",
    "LCN": "América Latina y el Caribe",
    "MEA": "Oriente Medio, Norte de África, Afganistán y Pakistán",
    "NAC": "América del Norte", "SAS": "Asia Meridional", "SSF": "África subsahariana",
}
NIVEL_INGRESO = [  # código, nombre_en, nombre_es, orden
    ("LIC", "Low income", "Ingreso bajo", 1),
    ("LMC", "Lower middle income", "Ingreso mediano bajo", 2),
    ("UMC", "Upper middle income", "Ingreso mediano alto", 3),
    ("HIC", "High income", "Ingreso alto", 4),
]

# Códigos del Banco Mundial que no existen en ISO 3166-1: id en el rango 900-999 (reservado por ISO
# para uso propio). Tampoco están en M49, igual que Taiwán: se ubican a mano para poder agrupar.
ID_NO_ISO = {"XKX": 901, "CHI": 902}
REGION_M49_MANUAL = {"TWN": "Eastern Asia", "XKX": "Southern Europe", "CHI": "Northern Europe"}

# Territorios que no son Estados: tipo de entidad y quién ejerce la soberanía
DEPENDENCIAS = {
    # territorio: (soberano, tipo)
    "ABW": ("NLD", "pais_constituyente"), "CUW": ("NLD", "pais_constituyente"),
    "SXM": ("NLD", "pais_constituyente"), "BES": ("NLD", "municipio_especial"),
    "AIA": ("GBR", "territorio_dependiente"), "BMU": ("GBR", "territorio_dependiente"),
    "CYM": ("GBR", "territorio_dependiente"), "FLK": ("GBR", "territorio_dependiente"),
    "GIB": ("GBR", "territorio_dependiente"), "IOT": ("GBR", "territorio_dependiente"),
    "MSR": ("GBR", "territorio_dependiente"), "PCN": ("GBR", "territorio_dependiente"),
    "SGS": ("GBR", "territorio_dependiente"), "SHN": ("GBR", "territorio_dependiente"),
    "TCA": ("GBR", "territorio_dependiente"), "VGB": ("GBR", "territorio_dependiente"),
    "GGY": ("GBR", "dependencia_de_la_corona"), "JEY": ("GBR", "dependencia_de_la_corona"),
    "IMN": ("GBR", "dependencia_de_la_corona"), "CHI": ("GBR", "agrupacion_estadistica"),
    "ASM": ("USA", "territorio_dependiente"), "GUM": ("USA", "territorio_dependiente"),
    "MNP": ("USA", "territorio_dependiente"), "PRI": ("USA", "territorio_dependiente"),
    "VIR": ("USA", "territorio_dependiente"), "UMI": ("USA", "territorio_dependiente"),
    "GLP": ("FRA", "departamento_de_ultramar"), "GUF": ("FRA", "departamento_de_ultramar"),
    "MTQ": ("FRA", "departamento_de_ultramar"), "REU": ("FRA", "departamento_de_ultramar"),
    "MYT": ("FRA", "departamento_de_ultramar"), "BLM": ("FRA", "territorio_dependiente"),
    "MAF": ("FRA", "territorio_dependiente"), "NCL": ("FRA", "territorio_dependiente"),
    "PYF": ("FRA", "territorio_dependiente"), "SPM": ("FRA", "territorio_dependiente"),
    "WLF": ("FRA", "territorio_dependiente"), "ATF": ("FRA", "territorio_dependiente"),
    "CCK": ("AUS", "territorio_dependiente"), "CXR": ("AUS", "territorio_dependiente"),
    "HMD": ("AUS", "territorio_dependiente"), "NFK": ("AUS", "territorio_dependiente"),
    "TKL": ("NZL", "territorio_dependiente"), "COK": ("NZL", "estado_libre_asociado"),
    "NIU": ("NZL", "estado_libre_asociado"), "BVT": ("NOR", "territorio_dependiente"),
    "SJM": ("NOR", "territorio_dependiente"), "FRO": ("DNK", "pais_constituyente"),
    "GRL": ("DNK", "pais_constituyente"), "ALA": ("FIN", "region_autonoma"),
    "HKG": ("CHN", "region_administrativa_especial"), "MAC": ("CHN", "region_administrativa_especial"),
}
OTROS_TIPOS = {
    "VAT": "estado_observador_onu", "PSE": "estado_observador_onu",
    "TWN": "estado_reconocimiento_limitado", "XKX": "estado_reconocimiento_limitado",
    "ESH": "territorio_en_disputa", "ATA": "territorio_internacional",
}
# Reclamos de soberanía que conviene tener a mano (sobre todo los argentinos)
RECLAMOS = [
    # territorio, reclamante, subdivisión del reclamante, descripción
    ("FLK", "ARG", "AR-V", "Islas Malvinas: Argentina las considera parte de Tierra del Fuego, "
                           "Antártida e Islas del Atlántico Sur"),
    ("SGS", "ARG", "AR-V", "Islas Georgias del Sur y Sandwich del Sur"),
    ("ATA", "ARG", "AR-V", "Antártida Argentina (sector 25° O - 74° O)"),
    ("ATA", "CHL", "CL-MA", "Territorio Chileno Antártico (región de Magallanes)"),
    ("ATA", "GBR", None, "Territorio Antártico Británico"),
    ("ATA", "AUS", None, "Territorio Antártico Australiano"),
    ("ATA", "NZL", None, "Dependencia Ross"),
    ("ATA", "NOR", None, "Tierra de la Reina Maud e isla Pedro I"),
    ("ATA", "FRA", None, "Tierra Adelia"),
    ("ESH", "MAR", None, "Sahara Occidental: administrado mayormente por Marruecos; "
                         "la RASD lo reclama como Estado"),
    ("TWN", "CHN", "CN-TW", "La República Popular China lo considera una provincia (CN-TW en ISO 3166-2)"),
]
# Nombres con que cada fuente argentina escribe algunas provincias (para la tabla de equivalencias)
ALIAS_PROVINCIA = {
    "AR-C": ["CABA", "Capital Federal", "Ciudad Autónoma de Buenos Aires"],
    "AR-V": ["Tierra del Fuego, Antártida e Islas del Atlántico Sur"],
}


# ---------------------------------------------------------------------------
# Descargas de referencia (una sola vez)
# ---------------------------------------------------------------------------
def bajar(url, nombre):
    # Con ETL_REFRESCAR=1 (actualizar_mensual.py) se baja de nuevo; si falla, queda la copia anterior
    destino = CRUDOS / nombre
    if not destino.exists() or os.environ.get("ETL_REFRESCAR") == "1":
        CRUDOS.mkdir(parents=True, exist_ok=True)
        print(f"Descargando {nombre} ...")
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
        except requests.RequestException as error:
            if not destino.exists():
                raise
            print(f"  AVISO_FUENTE {nombre}: falló la descarga ({error}); se usa la copia anterior")
            return destino
        destino.write_bytes(r.content)
    return destino


# ---------------------------------------------------------------------------
# 1. Dimensiones geográficas
# ---------------------------------------------------------------------------
def regiones_m49():
    m49 = pd.read_csv(bajar(URL_M49, "iso3166_regiones_m49.csv"), dtype=str, **LEER)
    m49.columns = [snake(c) for c in m49.columns]
    filas, hoja = {}, {}  # hoja: alfa-3 -> región más específica
    for r in m49.itertuples():
        padre = None
        for nivel, (nombre, codigo) in enumerate([(r.region, r.region_code), (r.sub_region, r.sub_region_code),
                                                  (r.intermediate_region, r.intermediate_region_code)], start=1):
            if isinstance(nombre, str):
                filas[int(codigo)] = dict(region_geografica_id=int(codigo), nombre_es=REGION_M49_ES[nombre],
                                          nombre_en=nombre, nivel=nivel, region_padre_id=padre)
                padre = hoja[r.alpha_3] = int(codigo)
    tabla = pd.DataFrame(filas.values()).sort_values(["nivel", "region_geografica_id"])
    por_nombre = dict(zip(tabla.nombre_en, tabla.region_geografica_id))
    for iso3, nombre in REGION_M49_MANUAL.items():
        hoja[iso3] = por_nombre[nombre]
    return tabla, hoja


def paises_banco_mundial():
    datos = json.loads(bajar(URL_BM_PAISES, "bm_paises.json").read_text())[1]
    bm = pd.json_normalize(datos)
    bm = bm[bm["region.id"] != "NA"]  # fuera los agregados (regiones, grupos de ingreso)
    return bm.assign(**{c: bm[c].str.strip() for c in ["name", "region.value", "capitalCity"]})


def dim_pais(region_hoja, bm):
    """Parte de maestros/paises_maestro.csv y le agrega ids, M49, tipo de entidad y soberano."""
    m = pd.read_csv(MAESTROS / "paises_maestro.csv", dtype={"iso_numerico": str}, **LEER)
    oficial = {c.alpha_3: getattr(c, "official_name", c.name) for c in pycountry.countries}
    codigo_region = dict(zip(bm["region.value"], bm["region.id"]))
    codigo_ingreso = dict(zip(bm["incomeLevel.value"], bm["incomeLevel.id"]))
    pais = pd.DataFrame({
        "pais_id": [int(n) if isinstance(n, str) else ID_NO_ISO[i] for i, n in zip(m.iso3, m.iso_numerico)],
        "iso3": m.iso3, "iso2": m.iso2, "iso_numerico": m.iso_numerico,
        "codigo_banco_mundial": m.iso3.where(m.iso3.isin(bm.id)),
        "nombre_es": m.nombre_es, "nombre_en": m.nombre_en,
        "nombre_oficial_en": m.nombre_oficial_en.fillna(m.iso3.map(oficial)).fillna(m.nombre_en),
        "nombre_es_banco_mundial": m.nombre_es_banco_mundial,
        "region_geografica_id": m.iso3.map(region_hoja).astype("Int64"),
        "region_bm_codigo": m.region_bm.str.strip().map(codigo_region),
        "nivel_ingreso_codigo": m.nivel_ingreso_bm.map(codigo_ingreso),
        "capital": m.capital, "latitud_capital": m.latitud_capital, "longitud_capital": m.longitud_capital,
    })
    tipo = {iso3: t for iso3, (_, t) in DEPENDENCIAS.items()} | OTROS_TIPOS
    pais["tipo_entidad"] = pais.iso3.map(tipo).fillna("estado_miembro_onu")
    pais["es_miembro_onu"] = (pais.tipo_entidad == "estado_miembro_onu").astype(int)
    id_de = dict(zip(pais.iso3, pais.pais_id))
    pais["pais_soberano_id"] = pais.iso3.map({t: id_de[s] for t, (s, _) in DEPENDENCIAS.items()}).astype("Int64")
    pais["en_panel_bm"] = m.en_panel.astype(int)
    assert pais.es_miembro_onu.sum() == 193, pais.es_miembro_onu.sum()
    assert pais.pais_id.is_unique and pais.iso3.is_unique
    assert pais.region_bm_codigo.notna().sum() == m.region_bm.notna().sum()
    return pais.sort_values("iso3").reset_index(drop=True)


def dim_subdivision(pais):
    """Parte de maestros/subdivisiones_maestro.csv (primer nivel ISO 3166-2) y agrega ids y región EPH."""
    m = pd.read_csv(MAESTROS / "subdivisiones_maestro.csv", **LEER)
    id_de = dict(zip(pais.iso3, pais.pais_id))
    sub = pd.DataFrame({
        "codigo": m.subdivision_iso, "pais_id": m.iso3.map(id_de), "nombre": m.nombre,
        "nombre_iso": m.nombre_iso, "nombre_es": m.nombre_es, "nombre_en": m.nombre_en,
        "tipo_iso": m.tipo_iso, "tipo_es": m.tipo_es, "nivel": 1,
        "latitud": m.latitud, "longitud": m.longitud, "wikidata_id": m.wikidata_id,
        "es_iso_3166_2": 1, "pais_equivalente_id": m.tambien_pais_iso3.map(id_de).astype("Int64"),
    })
    # La producción de hidrocarburos en el mar figura como "Estado Nacional": no es una provincia
    offshore = dict(codigo="AR-offshore", pais_id=id_de["ARG"], nombre="Plataforma continental (Estado Nacional)",
                    tipo_es="zona marítima de jurisdicción nacional", nivel=1, es_iso_3166_2=0)
    sub = pd.concat([sub, pd.DataFrame([offshore])], ignore_index=True)
    region_id = {nombre: codigo for codigo, nombre in REGION_EPH.items()}
    sub["region_subnacional_id"] = sub.nombre.where(sub.pais_id == id_de["ARG"]).map(
        REGION_DE_PROVINCIA).map(region_id).astype("Int64")
    assert sub.region_subnacional_id.notna().sum() == 24

    # IDs estables: se reutilizan los de la corrida anterior; una subdivisión nueva recibe el siguiente
    registro = TABLAS / "dim_subdivision.csv"
    previos = {}
    if registro.exists():
        r = pd.read_csv(registro, usecols=["codigo", "subdivision_id"], **LEER)
        previos = dict(zip(r.codigo, r.subdivision_id.astype(int)))
    sub = sub.sort_values(["pais_id", "codigo"]).reset_index(drop=True)
    siguiente = max(previos.values(), default=0) + 1
    ids = []
    for codigo in sub.codigo:
        if codigo not in previos:
            previos[codigo], siguiente = siguiente, siguiente + 1
        ids.append(previos[codigo])
    sub["subdivision_id"] = ids
    sub["subdivision_padre_id"] = pd.array([None] * len(sub), dtype="Int64")  # para un futuro 2.º nivel
    columnas = ["subdivision_id", "pais_id", "codigo", "nombre", "nombre_iso", "nombre_es", "nombre_en",
                "tipo_iso", "tipo_es", "nivel", "subdivision_padre_id", "region_subnacional_id",
                "latitud", "longitud", "wikidata_id", "es_iso_3166_2", "pais_equivalente_id"]
    assert sub.codigo.is_unique and sub.pais_id.notna().all()
    return sub[columnas]


def equivalencias_pais(pais, bm):
    filas = []
    for r in pais.itertuples():
        for sistema, valor in [("nombre_en", r.nombre_en), ("nombre_oficial_en", r.nombre_oficial_en),
                               ("nombre_es_banco_mundial", r.nombre_es_banco_mundial), ("nombre_es", r.nombre_es)]:
            if isinstance(valor, str):
                filas.append((r.pais_id, sistema, "nombre", valor))
    id_de = dict(zip(pais.iso3, pais.pais_id))
    for r in bm.itertuples():  # nombre en inglés del panel (columna "pais" de paises_anual.csv)
        filas.append((id_de[r.id], "nombre_banco_mundial_en", "nombre", r.name))
    for nombre, iso3 in NOMBRES_WHR_A_ISO3.items():
        filas.append((id_de[iso3], "nombre_world_happiness_report", "nombre", nombre))
    for codigo, iso3 in ISO3_ILO_A_BANCO_MUNDIAL.items():
        filas.append((id_de[iso3], "codigo_ilostat", "codigo", codigo))
    for r in bm.itertuples():  # iso2 del Banco Mundial (difiere de ISO en Kosovo e Islas del Canal)
        filas.append((id_de[r.id], "iso2_banco_mundial", "codigo", r.iso2Code))
    fb = pd.read_csv(FB / "factbook_entidades.csv", **LEER).dropna(subset=["iso3"])
    for r in fb.itertuples():  # código y nombre de la CIA (Palestina tiene dos: Cisjordania y Gaza)
        filas.append((id_de[r.iso3], "codigo_gec_cia_factbook", "codigo", r.codigo_gec))
        filas.append((id_de[r.iso3], "nombre_cia_factbook", "nombre", r.nombre_factbook))
    estados = pyreadr.read_r(ALI / "crudos" / "cow_estados.rda")["cow_states"].drop_duplicates("ccode")
    for r in estados.itertuples():
        cc = int(r.ccode)
        iso3 = COW_CCODE_ISO3[cc] if cc in COW_CCODE_ISO3 else iso3_por_nombre(r.statenme)
        if iso3 in id_de:
            filas.append((id_de[iso3], "codigo_correlates_of_war", "codigo", str(cc)))
            filas.append((id_de[iso3], "abreviatura_correlates_of_war", "codigo", r.stateabb))
    eq = pd.DataFrame(filas, columns=["pais_id", "sistema", "tipo", "valor"]).drop_duplicates()
    return eq.drop_duplicates(["sistema", "valor"]).sort_values(["pais_id", "sistema"])


def equivalencias_subdivision(sub):
    ar = sub[sub.region_subnacional_id.notna()].set_index("nombre").subdivision_id
    filas = [(ar[n], "codigo_indec", "codigo", f"{c:02d}") for c, n in CODIGO_INDEC.items()]
    filas += [(ar[n], "codigo_gaul1_cckp", "codigo", f"ARG.12{c}") for n, c in CODIGO_CCKP.items()]
    por_codigo = dict(zip(sub.codigo, sub.subdivision_id))
    for codigo, alias in ALIAS_PROVINCIA.items():
        filas += [(por_codigo[codigo], "nombre_en_fuentes", "nombre", a) for a in alias]
    filas.append((por_codigo["AR-offshore"], "nombre_en_fuentes", "nombre", "Estado Nacional"))
    return pd.DataFrame(filas, columns=["subdivision_id", "sistema", "tipo", "valor"]).sort_values(
        ["subdivision_id", "sistema"])


# ---------------------------------------------------------------------------
# 2. Hechos: se leen los CSV de los pasos anteriores y se cambian los códigos por ids
# ---------------------------------------------------------------------------
# archivo -> (tabla, columnas de la clave además de subdivision_id, renombres)
TABLAS_PROVINCIA = {
    "poblacion_provincia_anual.csv": ("hecho_subdivision_poblacion", ["anio"], {}),
    "indicadores_provincia_anual.csv": ("hecho_subdivision_economia", ["anio"],
                                        {"poblacion": "poblacion_implicita_vab"}),
    "vab_provincia_sector_largo.csv": ("hecho_subdivision_vab_rama", ["anio", "rama_nro"], {}),
    "petroleo_gas_provincia_anual.csv": ("hecho_subdivision_hidrocarburos", ["anio"], {}),
    "agricultura_provincia_anual.csv": ("hecho_subdivision_agricultura", ["anio_cosecha", "cultivo"], {}),
    "ganaderia_bovinos_provincia_anual.csv": ("hecho_subdivision_ganaderia", ["anio"], {}),
    "censo_vivienda_servicios_educacion.csv": ("hecho_subdivision_censo", ["anio_censo"], {}),
    "turismo_hoteles_provincia_anual.csv": ("hecho_subdivision_turismo", ["anio"], {}),
    "temperatura_provincia_anual.csv": ("hecho_subdivision_clima", ["anio"], {}),
    "salud_provincia_anual.csv": ("hecho_subdivision_salud", ["anio"], {}),
    "empresas_con_empleados_provincia_anual.csv": ("hecho_subdivision_empresas", ["anio"], {}),
    "pymes_provincia.csv": ("hecho_subdivision_pymes", ["anio"], {}),
    "carga_impositiva_provincia_anual.csv": ("hecho_subdivision_fiscal", ["anio"], {}),
    "alicuotas_ingresos_brutos_provincia.csv": ("hecho_subdivision_alicuota_iibb", ["anio", "actividad"], {}),
    "salarios_provincia_anual.csv": ("hecho_subdivision_salarios", ["anio"], {}),
    "canastas_provincia_anual.csv": ("hecho_subdivision_canastas", ["anio"], {}),
    "pobreza_gini_provincia_anual.csv": ("hecho_subdivision_pobreza", ["anio"], {}),
    "gobierno_provincial_anual.csv": ("hecho_subdivision_gobierno", ["anio"], {}),
    "gobernadores_elecciones.csv": ("hecho_subdivision_eleccion_gobernador", ["anio_eleccion"], {}),
    "legisladores_nacionales_provincia_anual.csv": ("hecho_subdivision_legisladores", ["anio", "camara"], {}),
}
FUENTE_PROVINCIA = {
    "hecho_subdivision_poblacion": "INDEC, proyecciones de población base Censo 2010",
    "hecho_subdivision_economia": "CEPAL-MECON (VAB 52 ramas) y Argendata (PBG per cápita)",
    "hecho_subdivision_vab_rama": "CEPAL-MECON, VAB por jurisdicción y 52 ramas",
    "hecho_subdivision_hidrocarburos": "Secretaría de Energía (SESCO + Capítulo IV)",
    "hecho_subdivision_agricultura": "MAGyP, estimaciones agrícolas",
    "hecho_subdivision_ganaderia": "MAGyP / SENASA, stock bovino al 31-12",
    "hecho_subdivision_censo": "INDEC, censos 2010 y 2022",
    "hecho_subdivision_turismo": "INDEC-Turismo, Encuesta de Ocupación Hotelera (piso, no total provincial)",
    "hecho_subdivision_clima": "Banco Mundial CCKP, ERA5",
    "hecho_subdivision_salud": "Ministerio de Salud (vacunación SRP, médicos matriculados)",
    "hecho_subdivision_empresas": "OEDE Ministerio de Trabajo y CEP XXI",
    "hecho_subdivision_pymes": "Registro MiPyME (foto al 23-12-2024)",
    "hecho_subdivision_fiscal": "DNAP Ministerio de Economía (recaudación propia) + cálculo propio",
    "hecho_subdivision_alicuota_iibb": "DNAP, alícuotas teóricas de Ingresos Brutos",
    "hecho_subdivision_salarios": "OEDE Ministerio de Trabajo (SIPA, privados registrados)",
    "hecho_subdivision_canastas": "INDEC CBA/CBT por región EPH (estimado por región)",
    "hecho_subdivision_pobreza": "Cálculo propio con microdatos EPH-INDEC (31 aglomerados)",
    "hecho_subdivision_gobierno": "electorAr + carga manual",
    "hecho_subdivision_eleccion_gobernador": "electorAr (Atlas Electoral) + carga manual",
    "hecho_subdivision_legisladores": "HCDN (diputados) y Senado de la Nación",
}


# Seis dimensiones nuevas (fuentes_nuevas/extraer_dimensiones_nuevas.py): archivo -> (tabla, clave extra, fuente)
TABLAS_PAIS_NUEVAS = {
    "pais_migracion_anual.csv": ("hecho_pais_migracion_anual", ["anio"],
                                 "Banco Mundial (ONU WPP 2024; remesas de balanza de pagos FMI)"),
    "pais_emisiones_energia_anual.csv": ("hecho_pais_emisiones", ["anio"],
                                         "Banco Mundial (EDGAR, SE4All), OWID (Ember/Energy Institute, EM-DAT)"),
    "pais_capital_social_anual.csv": ("hecho_pais_capital_social", ["anio"],
                                      "CEPALSTAT (Latinobarómetro), OWID (World Values Survey), V-Dem v16"),
    "pais_diversidad_cultural_anual.csv": ("hecho_pais_diversidad_cultural", ["anio"],
                                           "Comparative Constitutions Project v5"),
    "pais_poblacion_indigena.csv": ("hecho_pais_poblacion_indigena", ["decada_censal"],
                                    "CEPALSTAT / CELADE, censos de población"),
    "pais_gobernanza_anual.csv": ("hecho_pais_institucional_gobernanza", ["anio"],
                                  "Banco Mundial WGI, V-Dem v16, BID DPI 2020"),
    "pais_financiero_deuda_anual.csv": ("hecho_pais_financiero_deuda", ["anio"],
                                        "Banco Mundial (IDS, QEDS al 4.º trimestre), BCRP (EMBIG de J.P. Morgan)"),
    "pais_salud_cronica_anual.csv": ("hecho_pais_salud_cronica", ["anio"],
                                     "Banco Mundial, OMS GHO, OMS GHE 2021 vía OWID (AVAD)"),
    "pais_tecnologia_anual.csv": ("hecho_pais_tecnologia", ["anio"], "Banco Mundial (UIT, UNESCO), OCDE ICT hogares"),
}
# Indicadores sociales y digitales (indicadores_sociales_digitales/extraer_indicadores_sociales.py)
TABLAS_PAIS_SOCIALES = {
    "pais_educacion_anual.csv": ("hecho_pais_educacion", ["anio"],
                                 "Banco Mundial (UNESCO-UIS: alfabetización, nivel alcanzado; Índice de Capital Humano)"),
    "pais_digital_ocio_anual.csv": ("hecho_pais_digital_ocio", ["anio"],
                                    "OCDE, ICT Access and Usage by Individuals (16-74 y 16-24 años)"),
    "pais_empleo_sectorial_anual.csv": ("hecho_pais_empleo_sectorial", ["anio"],
                                        "OIT (estimaciones modeladas; encuestas de hogares a 2 dígitos CIIU rev. 4)"),
    "pais_gasto_cultura_anual.csv": ("hecho_pais_gasto_cultura", ["anio"],
                                     "FMI GFS COFOG; OCDE Government at a Glance (Chile, Colombia y US$ PPA)"),
    "pais_deporte_olimpico.csv": ("hecho_pais_deporte_olimpico", ["anio"],
                                  "Olympedia: medallero y atletas por edición (verano en años pares de JJ. OO., "
                                  "invierno en los otros; Tokio 2020 se jugó en 2021)"),
    "pais_consolas_comercio_anual.csv": ("hecho_pais_consolas_comercio", ["anio"],
                                         "UN Comtrade, consolas de videojuegos HS 950450 (HS 950410 hasta 2011)"),
}
TABLAS_SUBDIVISION_NUEVAS = {
    "subdivision_deuda_anual.csv": ("hecho_subdivision_financiero", ["anio"],
                                    "Coordinación Fiscal Provincial, stock al 31-12 y servicios devengados"),
    "subdivision_finanzas_publicas_anual.csv": ("hecho_subdivision_finanzas_publicas", ["anio"],
                                                "Coordinación Fiscal Provincial, esquema Ahorro-Inversión-Financiamiento"),
    "subdivision_emisiones_anual.csv": ("hecho_subdivision_ambiental", ["anio"],
                                        "OCDE, emisiones regionales (TL2) de 6 países de América Latina"),
    "subdivision_internet_anual.csv": ("hecho_subdivision_tecnologia", ["anio"],
                                       "ENACOM, accesos a internet fijo (último trimestre del año)"),
}
# Columnas que en el CSV quedan como decimales por los vacíos pero son conteos o 0/1
ENTEROS = ("es_", "saldo_", "medallas_", "atletas_", "personas_", "muertes_", "veto_", "avad_total", "spread_embi_meses",
           "internet_fijo_trimestre", "decada_censal")


def enteros(d):
    for c in d.columns:
        if c.startswith(ENTEROS) and pd.api.types.is_float_dtype(d[c]):
            d[c] = d[c].round().astype("Int64")
    return d


def leer_subdivisiones_nuevas(sub):
    id_sub = dict(zip(sub.codigo, sub.subdivision_id))
    hechos = {}
    for archivo, (tabla, clave, _) in TABLAS_SUBDIVISION_NUEVAS.items():
        d = enteros(pd.read_csv(NUEVAS / archivo))
        faltan = set(d.subdivision_iso) - set(id_sub)
        assert not faltan, (archivo, faltan)
        d.insert(0, "subdivision_id", d.pop("subdivision_iso").map(id_sub))
        assert not d.duplicated(["subdivision_id"] + clave).any(), tabla
        hechos[tabla] = (d, ["subdivision_id"] + clave)
    return hechos


def leer_provincias(sub):
    id_sub = dict(zip(sub.codigo, sub.subdivision_id))
    hechos, extra = {}, {}
    for archivo, (tabla, clave, renombres) in TABLAS_PROVINCIA.items():
        d = pd.read_csv(PROV / archivo)
        faltan = set(d.provincia_iso) - set(id_sub)
        assert not faltan, (archivo, faltan)
        d.insert(0, "subdivision_id", d.provincia_iso.map(id_sub))
        d = d.drop(columns=["provincia_iso", "provincia"]).rename(columns=renombres)
        d.columns = [snake(c) for c in d.columns]
        if tabla == "hecho_subdivision_canastas":
            # la región ya está en dim_subdivision: se controla y se borra la copia
            region = sub.set_index("subdivision_id").region_subnacional_id.map(REGION_EPH)
            assert (d.subdivision_id.map(region) == d.region).all()
            d = d.drop(columns="region")
        if tabla == "hecho_subdivision_vab_rama":
            extra["dim_rama_cepal"] = (d[["rama_nro", "rama", "grupo"]].drop_duplicates()
                                       .sort_values("rama_nro").rename(columns={"grupo": "grupo_sector"}))
            assert extra["dim_rama_cepal"].rama_nro.is_unique
            d = d.drop(columns=["rama", "grupo"])
        assert not d.duplicated(["subdivision_id"] + clave).any(), tabla
        hechos[tabla] = (d, ["subdivision_id"] + clave)
    return hechos, extra


def leer_paises(pais):
    id_de = dict(zip(pais.iso3, pais.pais_id))
    hechos, extra = {}, {}

    panel = pd.read_csv(ETL / "datos_procesados" / "paises_anual.csv")
    vacias = [c for c in panel.columns if panel[c].isna().all()]  # p. ej. felicidad_fuente
    panel = panel.drop(columns=["pais", "region", "nivel_ingreso"] + vacias)
    panel.insert(0, "pais_id", panel.pop("iso3").map(id_de))
    hechos["hecho_pais_anual"] = (panel, ["pais_id", "anio"])
    extra["columnas_vacias_descartadas"] = vacias

    # Membresías: catálogo de organizaciones + relación país-organización
    mem = pd.read_csv(ALI / "membresias_organizaciones.csv")
    org = (mem[["organizacion", "organizacion_nombre", "tipo"]].drop_duplicates()
           .rename(columns={"organizacion": "organizacion_codigo", "organizacion_nombre": "nombre"}))
    assert org.organizacion_codigo.is_unique
    extra["dim_organizacion"] = org.sort_values("organizacion_codigo")
    rel = mem.drop(columns=["pais", "organizacion_nombre", "tipo", "en_panel"]).rename(
        columns={"organizacion": "organizacion_codigo"})
    rel.insert(0, "pais_id", rel.pop("iso3").map(id_de))
    hechos["rel_pais_organizacion"] = (rel, ["pais_id", "organizacion_codigo", "anio_ingreso"])

    # Tratados: los datos del acuerdo van a su catálogo; el año de adhesión de cada país, a la relación
    tra = pd.read_csv(ALI / "tratados_comerciales_pais.csv")
    acu = (tra[["acuerdo_id", "acuerdo", "tipo", "region", "listado_omc"]].drop_duplicates()
           .rename(columns={"acuerdo": "nombre", "region": "region_acuerdo"}))
    assert acu.acuerdo_id.is_unique
    extra["dim_acuerdo_comercial"] = acu.sort_values("acuerdo_id")
    rel = tra[["iso3", "acuerdo_id", "via", "anio_firma", "anio_entrada_vigor", "anio_salida"]].copy()
    rel.insert(0, "pais_id", rel.pop("iso3").map(id_de))
    hechos["rel_pais_acuerdo_comercial"] = (rel, ["pais_id", "acuerdo_id"])

    dia = pd.read_csv(ALI / "alianzas_militares_diadas.csv").drop(columns=["pais_a", "pais_b"])
    dia.insert(0, "pais_a_id", dia.pop("iso3_a").map(id_de))
    dia.insert(1, "pais_b_id", dia.pop("iso3_b").map(id_de))
    hechos["rel_alianza_militar_anual"] = (dia, ["pais_a_id", "pais_b_id", "anio"])

    # Del país-año de alianzas guardamos solo lo que NO se puede recalcular desde las membresías
    ali = pd.read_csv(ALI / "alianzas_pais_anual.csv")
    extra["alianzas_pais_anual_original"] = ali
    propios = ["n_igos_cow_total", "n_acuerdos_comerciales_en_vigor", "n_aliados_defensa",
               "n_aliados_cualquier_pacto"]
    rel_anual = ali[["iso3", "anio"] + propios].copy()
    rel_anual.insert(0, "pais_id", rel_anual.pop("iso3").map(id_de))
    hechos["hecho_pais_relaciones_anual"] = (rel_anual, ["pais_id", "anio"])

    # CIA World Factbook: foto del 22-01-2026. La clave lleva codigo_gec porque Palestina son dos
    # entidades en el Factbook (Cisjordania "we" y Gaza "gz")
    a_id = lambda serie: serie.map(id_de).astype("Int64")  # noqa: E731
    perfil = pd.read_csv(FB / "factbook_perfil_pais.csv", **LEER)
    perfil.insert(0, "pais_id", a_id(perfil.pop("iso3")))
    perfil = perfil.astype({"edad_minima_voto": "Int64", "es_voto_obligatorio": "Int64"})
    hechos["hecho_pais_perfil_factbook"] = (perfil, ["pais_id", "codigo_gec"])
    fro = pd.read_csv(FB / "factbook_fronteras.csv", **LEER)
    fro.insert(0, "pais_id", a_id(fro.pop("iso3")))
    fro.insert(2, "vecino_pais_id", a_id(fro.pop("vecino_iso3")))
    hechos["rel_pais_frontera"] = (fro, ["pais_id", "codigo_gec", "vecino_nombre_factbook"])
    com = pd.read_csv(FB / "factbook_composicion.csv", **LEER)
    com.insert(0, "pais_id", a_id(com.pop("iso3")))
    com = com.astype({"es_cota_superior": "Int64", "es_oficial": "Int64"})
    hechos["rel_pais_composicion"] = (com, ["pais_id", "codigo_gec", "dimension", "orden"])
    soc = pd.read_csv(FB / "factbook_socios_comerciales.csv", **LEER)
    soc.insert(0, "pais_id", a_id(soc.pop("iso3")))
    soc.insert(5, "socio_pais_id", a_id(soc.pop("socio_iso3")))
    hechos["rel_pais_socio_comercial"] = (soc, ["pais_id", "codigo_gec", "flujo", "rango"])
    assert fro.vecino_pais_id.notna().all() and soc.socio_pais_id.notna().all()

    for archivo, (tabla, clave, _) in ({NUEVAS / a: v for a, v in TABLAS_PAIS_NUEVAS.items()}
                                       | {SOCIALES / a: v for a, v in TABLAS_PAIS_SOCIALES.items()}).items():
        d = enteros(pd.read_csv(archivo))
        faltan = set(d.iso3) - set(id_de)
        assert not faltan, (archivo, faltan)
        d.insert(0, "pais_id", d.pop("iso3").map(id_de))
        hechos[tabla] = (d, ["pais_id"] + clave)

    for tabla, (d, clave) in hechos.items():
        for c in clave:
            assert d[c].notna().all(), (tabla, c)
        assert not d.duplicated(clave).any(), tabla
    return hechos, extra


# ---------------------------------------------------------------------------
# 3. Escritura en SQLite con claves primarias y foráneas
# ---------------------------------------------------------------------------
def tipo_sql(serie):
    if pd.api.types.is_bool_dtype(serie) or pd.api.types.is_integer_dtype(serie):
        return "INTEGER"
    if pd.api.types.is_float_dtype(serie):
        no_nulos = serie.dropna()
        return "INTEGER" if len(no_nulos) and (no_nulos == no_nulos.round()).all() and serie.name.startswith(
            ("anio", "n_", "rama_nro")) else "REAL"
    return "TEXT"


FK = {
    "pais_id": "dim_pais(pais_id)", "pais_a_id": "dim_pais(pais_id)", "pais_b_id": "dim_pais(pais_id)",
    "vecino_pais_id": "dim_pais(pais_id)", "socio_pais_id": "dim_pais(pais_id)",
    "subdivision_id": "dim_subdivision(subdivision_id)", "rama_nro": "dim_rama_cepal(rama_nro)",
    "organizacion_codigo": "dim_organizacion(organizacion_codigo)",
    "acuerdo_id": "dim_acuerdo_comercial(acuerdo_id)",
}

DDL_DIMENSIONES = """
CREATE TABLE dim_region_geografica (       -- jerarquía M49 de la ONU: continente > subregión > región intermedia
    region_geografica_id INTEGER PRIMARY KEY,   -- código M49 (19 = América, 419 = América Latina y el Caribe...)
    nombre_es            TEXT NOT NULL,
    nombre_en            TEXT NOT NULL,
    nivel                INTEGER NOT NULL CHECK (nivel IN (1, 2, 3)),
    region_padre_id      INTEGER REFERENCES dim_region_geografica(region_geografica_id)
);
CREATE TABLE dim_region_bm (               -- regiones del Banco Mundial
    region_bm_codigo TEXT PRIMARY KEY,     -- LCN, ECS, ...
    nombre_en        TEXT NOT NULL,
    nombre_es        TEXT NOT NULL
);
CREATE TABLE dim_nivel_ingreso (           -- clasificación vigente del Banco Mundial
    nivel_ingreso_codigo TEXT PRIMARY KEY, -- LIC, LMC, UMC, HIC
    nombre_en            TEXT NOT NULL,
    nombre_es            TEXT NOT NULL,
    orden                INTEGER NOT NULL UNIQUE
);
CREATE TABLE dim_pais (
    pais_id               INTEGER PRIMARY KEY,   -- = ISO 3166-1 numérico (901 Kosovo, 902 Islas del Canal)
    iso3                  TEXT NOT NULL UNIQUE CHECK (length(iso3) = 3),
    iso2                  TEXT NOT NULL UNIQUE CHECK (length(iso2) = 2),
    iso_numerico          TEXT UNIQUE,           -- '032'; NULL si no es ISO
    codigo_banco_mundial  TEXT UNIQUE,           -- NULL si el BM no publica datos del territorio
    nombre_es             TEXT NOT NULL,
    nombre_en             TEXT NOT NULL,
    nombre_oficial_en     TEXT NOT NULL,
    nombre_es_banco_mundial TEXT,
    region_geografica_id  INTEGER REFERENCES dim_region_geografica(region_geografica_id),
    region_bm_codigo      TEXT REFERENCES dim_region_bm(region_bm_codigo),
    nivel_ingreso_codigo  TEXT REFERENCES dim_nivel_ingreso(nivel_ingreso_codigo),
    capital               TEXT,
    latitud_capital       REAL,
    longitud_capital      REAL,
    tipo_entidad          TEXT NOT NULL,
    es_miembro_onu        INTEGER NOT NULL CHECK (es_miembro_onu IN (0, 1)),
    pais_soberano_id      INTEGER REFERENCES dim_pais(pais_id),
    en_panel_bm           INTEGER NOT NULL CHECK (en_panel_bm IN (0, 1))
);
CREATE TABLE dim_region_subnacional (      -- agrupaciones de provincias (regiones EPH del INDEC)
    region_subnacional_id INTEGER PRIMARY KEY,   -- código de región de la EPH
    pais_id               INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    sistema               TEXT NOT NULL,
    nombre                TEXT NOT NULL,
    UNIQUE (pais_id, sistema, nombre)
);
CREATE TABLE dim_subdivision (             -- provincias, estados, regiones... (ISO 3166-2)
    subdivision_id        INTEGER PRIMARY KEY,
    pais_id               INTEGER NOT NULL REFERENCES dim_pais(pais_id),     -- relación 1:N
    codigo                TEXT NOT NULL UNIQUE,  -- 'AR-B' (ISO 3166-2)
    nombre                TEXT NOT NULL,         -- nombre corto, el mismo que usan las tablas del proyecto
    nombre_iso            TEXT,                  -- nombre oficial ISO, en el idioma local
    nombre_es             TEXT,                  -- etiqueta de Wikidata en español
    nombre_en             TEXT,
    tipo_iso              TEXT,
    tipo_es               TEXT,
    nivel                 INTEGER NOT NULL CHECK (nivel >= 1),          -- hoy solo primer nivel
    subdivision_padre_id  INTEGER REFERENCES dim_subdivision(subdivision_id),
    region_subnacional_id INTEGER REFERENCES dim_region_subnacional(region_subnacional_id),
    latitud               REAL,
    longitud              REAL,
    wikidata_id           TEXT,
    es_iso_3166_2         INTEGER NOT NULL CHECK (es_iso_3166_2 IN (0, 1)),
    pais_equivalente_id   INTEGER REFERENCES dim_pais(pais_id)  -- US-PR -> PRI: no sumar dos veces
);
CREATE TABLE pais_equivalencia (           -- cómo llama cada fuente a cada país
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    sistema TEXT NOT NULL,
    tipo    TEXT NOT NULL CHECK (tipo IN ('codigo', 'nombre')),
    valor   TEXT NOT NULL,
    PRIMARY KEY (sistema, valor)
);
CREATE TABLE subdivision_equivalencia (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    sistema        TEXT NOT NULL,
    tipo           TEXT NOT NULL CHECK (tipo IN ('codigo', 'nombre')),
    valor          TEXT NOT NULL,
    PRIMARY KEY (sistema, valor)
);
CREATE TABLE rel_reclamo_territorial (
    pais_id                    INTEGER NOT NULL REFERENCES dim_pais(pais_id),      -- territorio
    pais_reclamante_id         INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    subdivision_reclamante_id  INTEGER REFERENCES dim_subdivision(subdivision_id),
    descripcion                TEXT NOT NULL,
    PRIMARY KEY (pais_id, pais_reclamante_id)
);
CREATE TABLE dim_organizacion (
    organizacion_codigo TEXT PRIMARY KEY,  -- 'MERCOSUR', 'OTAN', ...
    nombre              TEXT NOT NULL,
    tipo                TEXT NOT NULL
);
CREATE TABLE dim_acuerdo_comercial (
    acuerdo_id     INTEGER PRIMARY KEY,    -- número DESTA
    nombre         TEXT NOT NULL,
    tipo           TEXT,
    region_acuerdo TEXT,
    listado_omc    INTEGER
);
CREATE TABLE dim_rama_cepal (
    rama_nro     INTEGER PRIMARY KEY,
    rama         TEXT NOT NULL,
    grupo_sector TEXT NOT NULL
);
CREATE TABLE ref_catalogo_tabla (
    tabla        TEXT PRIMARY KEY,
    tipo         TEXT NOT NULL,
    grano        TEXT NOT NULL,
    fuente       TEXT,
    archivo_origen TEXT,
    filas        INTEGER,
    anio_min     INTEGER,
    anio_max     INTEGER
);
CREATE TABLE ref_diccionario_columna (
    tabla    TEXT NOT NULL REFERENCES ref_catalogo_tabla(tabla),
    columna  TEXT NOT NULL,
    tipo_sql TEXT NOT NULL,
    unidad   TEXT,
    pct_nulos REAL,
    PRIMARY KEY (tabla, columna)
);
"""


GRANO_DIM = {
    "dim_region_geografica": "region_geografica_id (código M49)", "dim_region_bm": "region_bm_codigo",
    "dim_nivel_ingreso": "nivel_ingreso_codigo", "dim_pais": "pais_id (también único: iso3, iso2)",
    "dim_region_subnacional": "region_subnacional_id", "dim_subdivision": "subdivision_id (también único: codigo)",
    "pais_equivalencia": "sistema, valor", "subdivision_equivalencia": "sistema, valor",
    "rel_reclamo_territorial": "pais_id, pais_reclamante_id", "dim_organizacion": "organizacion_codigo",
    "dim_acuerdo_comercial": "acuerdo_id", "dim_rama_cepal": "rama_nro",
}


def ddl_hecho(tabla, d, clave):
    lineas = []
    for c in d.columns:
        linea = f"    {c} {tipo_sql(d[c])}"
        if c in clave:
            linea += " NOT NULL"
        if c in FK:
            linea += f" REFERENCES {FK[c]}"
        lineas.append(linea)
    lineas.append(f"    PRIMARY KEY ({', '.join(clave)})")
    if tabla == "rel_alianza_militar_anual":
        lineas.append("    CHECK (pais_a_id <> pais_b_id)")
    return f"CREATE TABLE {tabla} (\n" + ",\n".join(lineas) + "\n);"


def insertar(con, tabla, d):
    d = d.astype(object).where(d.notna(), None)
    marcas = ", ".join("?" * len(d.columns))
    con.executemany(f"INSERT INTO {tabla} ({', '.join(d.columns)}) VALUES ({marcas})",
                    d.itertuples(index=False, name=None))


UNIDADES = [  # sufijo -> unidad (se usa la primera que coincide)
    ("_miles_personas", "miles de personas"), ("_usd_ppa_millones", "millones de US$ PPA"),
    ("_lcu_millones", "millones de moneda local"), ("_anios", "años"), ("_pct_gasto_publico", "% del gasto público"),
    ("_pct_pib", "% del PIB"), ("_pct_pbg_estimado", "% del PBG (estimado)"), ("_pct", "%"),
    ("_x1000", "por 1.000 hab."), ("_x100k", "por 100.000 hab."), ("_cada_1000_hab", "por 1.000 hab."),
    ("_cada_10000_hab", "por 10.000 hab."), ("_mill_pesos_2004", "millones de $ de 2004"),
    ("_mill_pesos", "millones de $ corrientes"), ("_pesos_2024", "$ de 2024"), ("_pesos_2004", "$ de 2004"),
    ("_pesos", "$ corrientes"), ("_usd_mes", "US$ por mes"), ("_usd", "US$"), ("_lcu_dia", "moneda local por día"),
    ("_lcu_mes", "moneda local por mes"), ("_lcu", "moneda local"), ("_ppa_dia", "US$ PPA por día"),
    ("_ppa", "US$ PPA"), ("_ha", "hectáreas"), ("_tn", "toneladas"), ("_kg_ha", "kg por hectárea"),
    ("_m3", "m³"), ("_miles_m3", "miles de m³"), ("_c", "°C"), ("_km2", "km²"), ("_km", "km"),
    ("_m", "metros"), ("_mtco2e", "millones de t de CO2 equivalente"), ("_tco2e", "t de CO2 equivalente"),
    ("_pb", "puntos básicos"), ("_x100_hogares", "por 100 hogares"), ("_x100_hab", "por 100 hab."),
    ("_x100", "por 100 hab."), ("_0_100", "índice 0-100"), ("_0_1", "índice 0-1"),
]


def unidad(columna):
    for sufijo, u in UNIDADES:
        if columna.endswith(sufijo) or f"{sufijo}_" in columna:
            return u
    if columna.startswith(("pct_", "participacion")):
        return "%" if columna.startswith("pct_") else "proporción (0-1)"
    if columna.startswith(("latitud", "longitud")):
        return "grados decimales"
    if columna.startswith(("miembro_", "es_", "en_")):
        return "0/1"
    return None


VISTAS = """
CREATE VIEW v_pais AS
SELECT p.pais_id, p.iso3, p.iso2, p.iso_numerico, p.nombre_es, p.nombre_en, p.nombre_oficial_en,
       COALESCE(r1.nombre_es, r2.nombre_es, r3.nombre_es) AS continente,
       CASE WHEN r3.nivel = 2 THEN r3.nombre_es WHEN r2.nivel = 2 THEN r2.nombre_es END AS subregion,
       CASE WHEN r3.nivel = 3 THEN r3.nombre_es END AS region_intermedia,
       b.nombre_es AS region_bm, i.nombre_es AS nivel_ingreso, p.capital, p.latitud_capital, p.longitud_capital,
       p.tipo_entidad, p.es_miembro_onu, s.iso3 AS soberano_iso3, p.en_panel_bm,
       (SELECT COUNT(*) FROM dim_subdivision d WHERE d.pais_id = p.pais_id AND d.nivel = 1 AND d.es_iso_3166_2 = 1) AS n_subdivisiones_nivel1
FROM dim_pais p
LEFT JOIN dim_region_geografica r3 ON r3.region_geografica_id = p.region_geografica_id
LEFT JOIN dim_region_geografica r2 ON r2.region_geografica_id = r3.region_padre_id
LEFT JOIN dim_region_geografica r1 ON r1.region_geografica_id = r2.region_padre_id
LEFT JOIN dim_region_bm b ON b.region_bm_codigo = p.region_bm_codigo
LEFT JOIN dim_nivel_ingreso i ON i.nivel_ingreso_codigo = p.nivel_ingreso_codigo
LEFT JOIN dim_pais s ON s.pais_id = p.pais_soberano_id;

CREATE VIEW v_subdivision AS
SELECT d.subdivision_id, p.iso3, p.nombre_es AS pais, d.codigo, d.nombre, d.nombre_es, d.tipo_es, d.nivel,
       padre.codigo AS codigo_padre, r.nombre AS region_subnacional, d.latitud, d.longitud,
       d.es_iso_3166_2, eq.iso3 AS tambien_es_pais_iso3
FROM dim_subdivision d
JOIN dim_pais p ON p.pais_id = d.pais_id
LEFT JOIN dim_subdivision padre ON padre.subdivision_id = d.subdivision_padre_id
LEFT JOIN dim_region_subnacional r ON r.region_subnacional_id = d.region_subnacional_id
LEFT JOIN dim_pais eq ON eq.pais_id = d.pais_equivalente_id;

-- Membresía por año (formato largo) recalculada desde los episodios: reemplaza las 48 columnas miembro_*
CREATE VIEW v_pais_membresia_anual AS
WITH RECURSIVE anios(anio) AS (SELECT 1945 UNION ALL SELECT anio + 1 FROM anios WHERE anio < 2025)
SELECT m.pais_id, a.anio, m.organizacion_codigo, o.tipo, m.estado
FROM rel_pais_organizacion m
JOIN dim_organizacion o ON o.organizacion_codigo = m.organizacion_codigo
JOIN anios a ON a.anio >= m.anio_ingreso AND (m.anio_salida IS NULL OR a.anio < m.anio_salida);

CREATE VIEW v_vab_provincia_grupo AS
SELECT v.subdivision_id, v.anio, v.estado_dato, r.grupo_sector,
       SUM(v.vab_mill_pesos_2004) AS vab_mill_pesos_2004,
       ROUND(SUM(v.participacion_en_provincia), 4) AS participacion_en_provincia
FROM hecho_subdivision_vab_rama v JOIN dim_rama_cepal r ON r.rama_nro = v.rama_nro
GROUP BY v.subdivision_id, v.anio, v.estado_dato, r.grupo_sector;

-- Control de coherencia: la suma de las provincias contra el dato nacional del Banco Mundial
CREATE VIEW v_control_poblacion_pais_vs_subdivisiones AS
SELECT p.iso3, h.anio, h.poblacion AS poblacion_banco_mundial, SUM(s.habitantes) AS suma_subdivisiones,
       ROUND(100.0 * SUM(s.habitantes) / h.poblacion - 100, 2) AS diferencia_pct
FROM hecho_subdivision_poblacion s
JOIN dim_subdivision d ON d.subdivision_id = s.subdivision_id
JOIN dim_pais p ON p.pais_id = d.pais_id
JOIN hecho_pais_anual h ON h.pais_id = p.pais_id AND h.anio = s.anio
GROUP BY p.iso3, h.anio, h.poblacion;

-- ===== Seis dimensiones nuevas: cocientes que no se guardan =====
CREATE VIEW v_pais_migracion_anual AS
SELECT p.iso3, m.pais_id, m.anio, m.saldo_migratorio_neto, h.poblacion,
       ROUND(1000.0 * m.saldo_migratorio_neto / h.poblacion, 3) AS tasa_migracion_neta_x1000,
       m.stock_migrantes_pct_poblacion, m.remesas_recibidas_usd, m.remesas_recibidas_pct_pib,
       m.remesas_enviadas_usd, ROUND(100.0 * m.remesas_enviadas_usd / f.pib_usd, 4) AS remesas_enviadas_pct_pib,
       m.remesas_recibidas_usd - m.remesas_enviadas_usd AS remesas_netas_usd
FROM hecho_pais_migracion_anual m
JOIN dim_pais p ON p.pais_id = m.pais_id
LEFT JOIN hecho_pais_anual h ON h.pais_id = m.pais_id AND h.anio = m.anio
LEFT JOIN hecho_pais_financiero_deuda f ON f.pais_id = m.pais_id AND f.anio = m.anio;

-- deuda_externa_usd es la QEDS (todos los países); deuda_externa_ids_usd, la de IDS (países en desarrollo)
CREATE VIEW v_pais_financiero_deuda AS
SELECT p.iso3, f.*,
       ROUND(100.0 * COALESCE(f.deuda_externa_usd, f.deuda_externa_ids_usd) / f.pib_usd, 2) AS deuda_externa_pct_pib,
       ROUND(100.0 * f.reservas_internacionales_usd / COALESCE(f.deuda_externa_usd, f.deuda_externa_ids_usd), 2)
           AS reservas_pct_deuda_externa
FROM hecho_pais_financiero_deuda f
JOIN dim_pais p ON p.pais_id = f.pais_id;

-- Latinobarómetro publica desconfianza en jueces y en partidos/congreso: se promedian las dos
CREATE VIEW v_pais_capital_social AS
SELECT p.iso3, c.*,
       ROUND((c.desconfianza_poder_judicial_pct + c.desconfianza_partidos_congreso_pct) / 2.0, 1)
           AS desconfianza_instituciones_pct
FROM hecho_pais_capital_social c
JOIN dim_pais p ON p.pais_id = c.pais_id;

-- Fragmentación = 1 - suma de las participaciones al cuadrado (probabilidad de que dos personas al azar
-- sean de grupos distintos). Si los porcentajes suman más de 101 (idiomas que se superponen) queda NULL.
CREATE VIEW v_pais_diversidad_cultural AS
WITH grupos AS (
    SELECT pais_id, codigo_gec, dimension, SUM(poblacion_pct) AS pct_cubierta,
           1 - SUM(poblacion_pct * poblacion_pct) / 10000.0 AS fragmentacion
    FROM rel_pais_composicion
    WHERE poblacion_pct IS NOT NULL
    GROUP BY pais_id, codigo_gec, dimension
), indices AS (
    SELECT pais_id, codigo_gec,
           MAX(CASE WHEN dimension = 'etnia' AND pct_cubierta <= 101 THEN ROUND(fragmentacion, 4) END)
               AS indice_fragmentacion_etnica_0_1,
           MAX(CASE WHEN dimension = 'idioma' AND pct_cubierta <= 101 THEN ROUND(fragmentacion, 4) END)
               AS indice_fragmentacion_linguistica_0_1,
           MAX(CASE WHEN dimension = 'religion' AND pct_cubierta <= 101 THEN ROUND(fragmentacion, 4) END)
               AS indice_fragmentacion_religiosa_0_1,
           MAX(CASE WHEN dimension = 'etnia' THEN ROUND(pct_cubierta, 1) END) AS pct_composicion_etnica_cubierta,
           MAX(CASE WHEN dimension = 'idioma' THEN ROUND(pct_cubierta, 1) END) AS pct_composicion_linguistica_cubierta
    FROM grupos GROUP BY pais_id, codigo_gec
), constitucion AS (
    SELECT * FROM hecho_pais_diversidad_cultural c
    WHERE anio = (SELECT MAX(anio) FROM hecho_pais_diversidad_cultural x WHERE x.pais_id = c.pais_id)
), indigena AS (
    SELECT * FROM hecho_pais_poblacion_indigena i
    WHERE decada_censal = (SELECT MAX(decada_censal) FROM hecho_pais_poblacion_indigena x WHERE x.pais_id = i.pais_id)
)
SELECT p.iso3, p.pais_id, i.codigo_gec, i.indice_fragmentacion_etnica_0_1, i.indice_fragmentacion_linguistica_0_1,
       i.indice_fragmentacion_religiosa_0_1, i.pct_composicion_etnica_cubierta,
       i.pct_composicion_linguistica_cubierta, c.anio AS anio_constitucion_ccp,
       c.es_proteccion_lenguas_constitucion, c.es_derechos_indigenas_constitucion,
       c.es_derechos_culturales_constitucion, ind.decada_censal, ind.poblacion_indigena_pct
FROM dim_pais p
LEFT JOIN indices i ON i.pais_id = p.pais_id
LEFT JOIN constitucion c ON c.pais_id = p.pais_id
LEFT JOIN indigena ind ON ind.pais_id = p.pais_id
WHERE i.pais_id IS NOT NULL OR c.pais_id IS NOT NULL OR ind.pais_id IS NOT NULL;

CREATE VIEW v_pais_salud_cronica AS
SELECT p.iso3, s.*, ROUND(100000.0 * s.avad_total / h.poblacion, 0) AS avad_x100k
FROM hecho_pais_salud_cronica s
JOIN dim_pais p ON p.pais_id = s.pais_id
LEFT JOIN hecho_pais_anual h ON h.pais_id = s.pais_id AND h.anio = s.anio;

-- ===== Indicadores sociales y digitales: participaciones que no se guardan =====
-- Cada participación usa el total de su misma fuente: construcción con el empleo modelado,
-- cultura y apuestas con el total de la misma encuesta.
CREATE VIEW v_pais_indicadores_sociales AS
WITH claves AS (
    SELECT pais_id, anio FROM hecho_pais_educacion UNION SELECT pais_id, anio FROM hecho_pais_digital_ocio
    UNION SELECT pais_id, anio FROM hecho_pais_empleo_sectorial UNION SELECT pais_id, anio FROM hecho_pais_gasto_cultura
    UNION SELECT pais_id, anio FROM hecho_pais_deporte_olimpico UNION SELECT pais_id, anio FROM hecho_pais_consolas_comercio
)
SELECT p.iso3, p.nombre_es AS pais, k.anio,
       e.alfabetizacion_adultos_pct, e.alfabetizacion_jovenes_15_24_pct,
       ROUND(e.alfabetizacion_adultos_hombres_pct - e.alfabetizacion_adultos_mujeres_pct, 2)
           AS brecha_alfabetizacion_hombres_menos_mujeres_pp,
       e.nivel_alcanzado_secundaria_alta_pct, e.nivel_alcanzado_licenciatura_pct,
       e.escolaridad_promedio_25mas_anios, e.escolaridad_esperada_anios,
       d.usa_redes_sociales_16_74_pct, d.compro_online_videojuegos_software_16_74_pct,
       ROUND(100.0 * s.empleo_construccion_modelado_miles_personas / s.empleo_total_modelado_miles_personas, 3)
           AS empleo_construccion_pct,
       CASE WHEN COALESCE(s.empleo_artes_espectaculos_miles_personas,
                          s.empleo_bibliotecas_museos_patrimonio_miles_personas) IS NOT NULL
            THEN ROUND(100.0 * (COALESCE(s.empleo_artes_espectaculos_miles_personas, 0)
                                + COALESCE(s.empleo_bibliotecas_museos_patrimonio_miles_personas, 0))
                       / s.empleo_total_encuesta_miles_personas, 3) END AS empleo_cultura_pct,
       ROUND(100.0 * s.empleo_juegos_azar_apuestas_miles_personas / s.empleo_total_encuesta_miles_personas, 3)
           AS empleo_juegos_azar_apuestas_pct,
       g.gasto_recreacion_cultura_religion_pct_pib, g.gasto_servicios_culturales_pct_pib,
       g.gasto_servicios_culturales_gob_central_pct_pib, g.fuente_gobierno_general,
       o.juegos_olimpicos, o.atletas_participantes, o.medallas_oro + o.medallas_plata + o.medallas_bronce AS medallas_total,
       ROUND(1e6 * (o.medallas_oro + o.medallas_plata + o.medallas_bronce) / h.poblacion, 3) AS medallas_por_millon_hab,
       ROUND(100.0 * o.atletas_mujeres / o.atletas_participantes, 1) AS atletas_mujeres_pct,
       c.importaciones_consolas_usd, ROUND(c.importaciones_consolas_usd / h.poblacion, 3) AS importaciones_consolas_usd_por_hab,
       c.importaciones_consolas_usd - COALESCE(c.exportaciones_consolas_usd, 0) AS importaciones_netas_consolas_usd
FROM claves k
JOIN dim_pais p ON p.pais_id = k.pais_id
LEFT JOIN hecho_pais_educacion e ON e.pais_id = k.pais_id AND e.anio = k.anio
LEFT JOIN hecho_pais_digital_ocio d ON d.pais_id = k.pais_id AND d.anio = k.anio
LEFT JOIN hecho_pais_empleo_sectorial s ON s.pais_id = k.pais_id AND s.anio = k.anio
LEFT JOIN hecho_pais_gasto_cultura g ON g.pais_id = k.pais_id AND g.anio = k.anio
LEFT JOIN hecho_pais_deporte_olimpico o ON o.pais_id = k.pais_id AND o.anio = k.anio
LEFT JOIN hecho_pais_consolas_comercio c ON c.pais_id = k.pais_id AND c.anio = k.anio
LEFT JOIN hecho_pais_anual h ON h.pais_id = k.pais_id AND h.anio = k.anio;

CREATE VIEW v_subdivision_financiero AS
SELECT s.codigo, s.nombre, d.*,
       ROUND(100.0 * (d.servicio_deuda_amortizacion_mill_pesos + d.servicio_deuda_intereses_mill_pesos)
             / f.ingresos_corrientes_mill_pesos, 2) AS servicio_deuda_pct_ingresos_corrientes,
       ROUND(100.0 * f.intereses_deuda_mill_pesos / f.ingresos_corrientes_mill_pesos, 2)
           AS intereses_pct_ingresos_corrientes,
       ROUND(100.0 * d.deuda_stock_mill_pesos / f.ingresos_totales_mill_pesos, 1) AS deuda_pct_ingresos_totales
FROM hecho_subdivision_financiero d
JOIN dim_subdivision s ON s.subdivision_id = d.subdivision_id
LEFT JOIN hecho_subdivision_finanzas_publicas f ON f.subdivision_id = d.subdivision_id AND f.anio = d.anio;

-- Transferencias automáticas = coparticipación y demás tributos de origen nacional;
-- discrecionales = transferencias corrientes y de capital que manda la Nación (y otros)
CREATE VIEW v_subdivision_federalismo_fiscal AS
SELECT s.codigo, s.nombre, f.subdivision_id, f.anio,
       ROUND(100.0 * f.tributarios_origen_nacional_mill_pesos / f.ingresos_totales_mill_pesos, 1)
           AS pct_ingresos_por_transferencias_automaticas,
       ROUND(100.0 * f.tributarios_origen_provincial_mill_pesos / f.gasto_total_mill_pesos, 1)
           AS indice_autonomia_financiera_subnacional,
       ROUND(100.0 * (f.transferencias_corrientes_recibidas_mill_pesos + f.transferencias_capital_recibidas_mill_pesos)
             / f.gasto_total_mill_pesos, 1) AS transferencias_discrecionales_pct_gasto,
       ROUND(100.0 * f.regalias_mill_pesos / f.ingresos_totales_mill_pesos, 1) AS regalias_pct_ingresos,
       ROUND(100.0 * f.resultado_financiero_mill_pesos / f.ingresos_totales_mill_pesos, 1)
           AS resultado_financiero_pct_ingresos
FROM hecho_subdivision_finanzas_publicas f
JOIN dim_subdivision s ON s.subdivision_id = f.subdivision_id;
"""


def vista_pais_anual(hechos):
    cols_h = [c for c in hechos["hecho_pais_anual"][0].columns if c not in ("pais_id", "anio")]
    cols_r = [c for c in hechos["hecho_pais_relaciones_anual"][0].columns if c not in ("pais_id", "anio")]
    sel = ", ".join([f"h.{c}" for c in cols_h] + [f"r.{c}" for c in cols_r])
    return f"""
CREATE VIEW v_pais_anual AS
SELECT v.iso3, v.nombre_es AS pais, v.continente, v.region_bm, v.nivel_ingreso, h.anio, {sel},
       (SELECT COUNT(*) FROM v_pais_membresia_anual m
         WHERE m.pais_id = h.pais_id AND m.anio = h.anio AND m.estado = 'pleno') AS n_organizaciones_clave
FROM hecho_pais_anual h
JOIN v_pais v ON v.pais_id = h.pais_id
LEFT JOIN hecho_pais_relaciones_anual r ON r.pais_id = h.pais_id AND r.anio = h.anio;"""


def vista_subdivision_anual(hechos):
    """Une todas las tablas provincia-año (las de una fila por subdivisión y año) en una vista ancha."""
    anuales = [t for t, (d, clave) in hechos.items() if t.startswith("hecho_subdivision") and clave == ["subdivision_id", "anio"]]
    # una columna que aparece en dos tablas (p. ej. meses_con_dato) lleva el tema como prefijo en ambas
    repetidas = pd.Series([c for t in anuales for c in hechos[t][0].columns]).value_counts()
    selects, joins = [], []
    for i, t in enumerate(anuales):
        alias = f"t{i}"
        prefijo = t.replace("hecho_subdivision_", "")
        for c in hechos[t][0].columns:
            if c in ("subdivision_id", "anio"):
                continue
            nombre = c if repetidas[c] == 1 else f"{prefijo}_{c}"
            selects.append(f"{alias}.{c} AS {nombre}")
        joins.append(f"LEFT JOIN {t} {alias} ON {alias}.subdivision_id = e.subdivision_id AND {alias}.anio = e.anio")
    union = "\n    UNION ".join(f"SELECT subdivision_id, anio FROM {t}" for t in anuales)
    return (f"CREATE VIEW v_subdivision_anual AS\nWITH esqueleto AS (\n    {union}\n)\n"
            f"SELECT s.iso3, s.codigo, s.nombre AS subdivision, s.region_subnacional, e.anio,\n       "
            + ",\n       ".join(selects)
            + "\nFROM esqueleto e\nJOIN v_subdivision s ON s.subdivision_id = e.subdivision_id\n"
            + "\n".join(joins) + ";")


def validar_membresias(con, pais, original):
    """La vista larga tiene que reproducir exactamente las columnas miembro_* de alianzas_pais_anual.csv."""
    larga = pd.read_sql("SELECT pais_id, anio, organizacion_codigo FROM v_pais_membresia_anual "
                        "WHERE estado = 'pleno' AND anio >= 2000", con)
    larga["iso3"] = larga.pais_id.map(dict(zip(pais.pais_id, pais.iso3)))
    larga = larga[larga.iso3.isin(original.iso3)]
    miembro = [c for c in original.columns if c.startswith("miembro_")]
    ancha = original.melt(id_vars=["iso3", "anio"], value_vars=miembro, var_name="org", value_name="v")
    ancha = ancha[ancha.v == 1]
    org_de_col = {f"miembro_{snake(o)}": o for o in larga.organizacion_codigo.unique()}
    ancha["organizacion_codigo"] = ancha.org.map(org_de_col)
    assert ancha.organizacion_codigo.notna().all(), set(ancha[ancha.organizacion_codigo.isna()].org)
    a = set(zip(ancha.iso3, ancha.anio, ancha.organizacion_codigo))
    b = set(zip(larga.iso3, larga.anio, larga.organizacion_codigo))
    return len(a), len(a - b), len(b - a)


def main():
    TABLAS.mkdir(exist_ok=True)
    print("1. Dimensiones geográficas")
    regiones, region_hoja = regiones_m49()
    bm = paises_banco_mundial()
    pais = dim_pais(region_hoja, bm)
    sub = dim_subdivision(pais)
    region_bm = (bm[["region.id", "region.value"]].drop_duplicates()
                 .rename(columns={"region.id": "region_bm_codigo", "region.value": "nombre_en"}))
    region_bm["nombre_es"] = region_bm.region_bm_codigo.map(REGION_BM_ES)
    ingreso = pd.DataFrame(NIVEL_INGRESO, columns=["nivel_ingreso_codigo", "nombre_en", "nombre_es", "orden"])
    id_ar = int(pais.loc[pais.iso3 == "ARG", "pais_id"].iloc[0])
    region_sub = pd.DataFrame([dict(region_subnacional_id=c, pais_id=id_ar, sistema="Regiones EPH (INDEC)",
                                    nombre=n) for c, n in REGION_EPH.items()])
    id_de = dict(zip(pais.iso3, pais.pais_id))
    id_sub = dict(zip(sub.codigo, sub.subdivision_id))
    reclamos = pd.DataFrame([dict(pais_id=id_de[t], pais_reclamante_id=id_de[r],
                                  subdivision_reclamante_id=id_sub.get(s), descripcion=d)
                             for t, r, s, d in RECLAMOS])
    eq_pais = equivalencias_pais(pais, bm)
    eq_sub = equivalencias_subdivision(sub)
    print(f"   {len(pais)} países/territorios, {len(sub)} subdivisiones, {len(eq_pais)} equivalencias de país")

    print("2. Hechos")
    hechos_p, extra_p = leer_paises(pais)
    hechos_s, extra_s = leer_provincias(sub)
    hechos = hechos_p | hechos_s | leer_subdivisiones_nuevas(sub)

    print("3. Base SQLite")
    BASE.unlink(missing_ok=True)
    con = sqlite3.connect(BASE)
    con.execute("PRAGMA foreign_keys = ON")
    ddl_hechos = [ddl_hecho(t, d, clave) for t, (d, clave) in hechos.items()]
    con.executescript(DDL_DIMENSIONES + "\n".join(ddl_hechos))
    dims = {
        "dim_region_geografica": regiones, "dim_region_bm": region_bm, "dim_nivel_ingreso": ingreso,
        "dim_pais": pais, "dim_region_subnacional": region_sub, "dim_subdivision": sub,
        "pais_equivalencia": eq_pais, "subdivision_equivalencia": eq_sub, "rel_reclamo_territorial": reclamos,
        "dim_organizacion": extra_p["dim_organizacion"], "dim_acuerdo_comercial": extra_p["dim_acuerdo_comercial"],
        "dim_rama_cepal": extra_s["dim_rama_cepal"],
    }
    # dim_pais y dim_subdivision se apuntan a sí mismas: se cargan sin chequeo y se valida al final
    con.execute("PRAGMA foreign_keys = OFF")
    for t, d in dims.items():
        insertar(con, t, d)
    for t, (d, _) in hechos.items():
        insertar(con, t, d)
    con.executescript(VISTAS + vista_pais_anual(hechos) + "\n" + vista_subdivision_anual(hechos))
    errores = con.execute("PRAGMA foreign_key_check").fetchall()
    assert not errores, errores[:10]

    # Catálogo y diccionario
    archivos = {v[0]: f"argentina_provincias/{k}" for k, v in TABLAS_PROVINCIA.items()} | {
        "hecho_pais_anual": "datos_procesados/paises_anual.csv",
        "rel_pais_organizacion": "alianzas/membresias_organizaciones.csv",
        "rel_pais_acuerdo_comercial": "alianzas/tratados_comerciales_pais.csv",
        "rel_alianza_militar_anual": "alianzas/alianzas_militares_diadas.csv",
        "hecho_pais_relaciones_anual": "alianzas/alianzas_pais_anual.csv",
        "hecho_pais_perfil_factbook": "factbook/factbook_perfil_pais.csv",
        "rel_pais_frontera": "factbook/factbook_fronteras.csv",
        "rel_pais_composicion": "factbook/factbook_composicion.csv",
        "rel_pais_socio_comercial": "factbook/factbook_socios_comerciales.csv",
    } | {t: f"fuentes_nuevas/{a}" for a, (t, _, _) in (TABLAS_PAIS_NUEVAS | TABLAS_SUBDIVISION_NUEVAS).items()} | {
        t: f"indicadores_sociales_digitales/{a}" for a, (t, _, _) in TABLAS_PAIS_SOCIALES.items()}
    fuentes = FUENTE_PROVINCIA | {
        "hecho_pais_anual": "Banco Mundial, OMS, ILOSTAT, World Happiness Report (pasos 1 y 2)",
        "rel_pais_organizacion": "COW IGO v3 + carga manual verificada con Wikidata",
        "rel_pais_acuerdo_comercial": "DESTA 2.0", "rel_alianza_militar_anual": "ATOP 5.1",
        "hecho_pais_relaciones_anual": "COW IGO, DESTA, ATOP (conteos)",
        "hecho_pais_perfil_factbook": "CIA World Factbook, foto del 22-01-2026 (factbook/factbook.json en GitHub)",
        "rel_pais_frontera": "CIA World Factbook, foto del 22-01-2026",
        "rel_pais_composicion": "CIA World Factbook, foto del 22-01-2026 (religiones, etnias, idiomas)",
        "rel_pais_socio_comercial": "CIA World Factbook, foto del 22-01-2026 (5 principales socios)",
        "dim_pais": "maestros/paises_maestro.csv (ISO 3166-1, Banco Mundial, Wikidata) + dependencias a mano",
        "dim_subdivision": "maestros/subdivisiones_maestro.csv (ISO 3166-2, Wikidata) + regiones EPH",
        "dim_region_geografica": "ONU M49 (lukes/ISO-3166-Countries-with-Regional-Codes)",
        "dim_region_bm": "Banco Mundial API", "dim_nivel_ingreso": "Banco Mundial API",
        "dim_organizacion": "alianzas/membresias_organizaciones.csv",
        "dim_acuerdo_comercial": "DESTA 2.0", "dim_rama_cepal": "CEPAL-MECON",
        "dim_region_subnacional": "INDEC, regiones de la EPH",
        "pais_equivalencia": "maestros, Banco Mundial, WHR (paso 2), ILOSTAT (paso 2), Correlates of War, "
                             "CIA World Factbook",
        "subdivision_equivalencia": "códigos INDEC y GAUL del script de provincias + nombres en las fuentes",
        "rel_reclamo_territorial": "carga manual",
    } | {t: f for t, _, f in (TABLAS_PAIS_NUEVAS | TABLAS_SUBDIVISION_NUEVAS | TABLAS_PAIS_SOCIALES).values()}
    catalogo, diccionario = [], []
    for t in list(dims) + list(hechos):
        d = dims[t] if t in dims else hechos[t][0]
        tipo = t.split("_")[0] if t.split("_")[0] in ("dim", "hecho", "rel") else "puente"
        grano = ", ".join(hechos[t][1]) if t in hechos else GRANO_DIM[t]
        anio = next((c for c in ("anio", "decada_censal", "anio_cosecha", "anio_censo", "anio_eleccion", "anio_ingreso",
                                 "anio_entrada_vigor") if c in d), None)
        catalogo.append(dict(tabla=t, tipo=tipo, grano=grano, fuente=fuentes.get(t), archivo_origen=archivos.get(t),
                             filas=len(d), anio_min=int(d[anio].min()) if anio else None,
                             anio_max=int(d[anio].max()) if anio else None))
        for c in d.columns:
            diccionario.append(dict(tabla=t, columna=c, tipo_sql=tipo_sql(d[c]), unidad=unidad(c),
                                    pct_nulos=round(100 * d[c].isna().mean(), 1)))
    insertar(con, "ref_catalogo_tabla", pd.DataFrame(catalogo))
    insertar(con, "ref_diccionario_columna", pd.DataFrame(diccionario))
    con.commit()

    print("4. Controles")
    total, faltan, sobran = validar_membresias(con, pais, extra_p["alianzas_pais_anual_original"])
    print(f"   membresías país-año recalculadas: {total} en el CSV; faltan {faltan}, sobran {sobran}")
    assert faltan == 0 and sobran == 0
    ali = extra_p["alianzas_pais_anual_original"]
    n = pd.read_sql("SELECT iso3, anio, n_organizaciones_clave FROM v_pais_anual", con)
    m = ali[["iso3", "anio", "n_organizaciones_clave"]].merge(n, on=["iso3", "anio"], suffixes=("", "_vista"))
    assert (m.n_organizaciones_clave == m.n_organizaciones_clave_vista).all()
    grupos = pd.read_csv(PROV / "vab_provincia_grupos_largo.csv")
    vista = pd.read_sql("SELECT d.codigo AS provincia_iso, g.anio, g.grupo_sector AS grupo, g.vab_mill_pesos_2004 "
                        "FROM v_vab_provincia_grupo g JOIN dim_subdivision d USING (subdivision_id)", con)
    m = grupos.merge(vista, on=["provincia_iso", "anio", "grupo"], suffixes=("", "_vista"))
    assert len(m) == len(grupos) and (m.vab_mill_pesos_2004 - m.vab_mill_pesos_2004_vista).abs().max() < 1e-3
    print("   VAB por grupo recalculado desde las 52 ramas: coincide con vab_provincia_grupos_largo.csv")
    print(pd.read_sql("SELECT * FROM v_control_poblacion_pais_vs_subdivisiones WHERE anio IN (2010, 2022, 2024)", con)
          .to_string(index=False))
    # Dimensiones nuevas: tres cruces entre fuentes independientes
    c = pd.read_sql("""SELECT f.anio, SUM(f.tributarios_origen_provincial_mill_pesos) AS aif,
                              SUM(r.recaudacion_propia_mill_pesos) AS dnap
                       FROM hecho_subdivision_finanzas_publicas f
                       JOIN hecho_subdivision_fiscal r USING (subdivision_id, anio) GROUP BY f.anio""", con)
    print("   recaudación propia, AIF / DNAP: entre "
          f"{(c.aif / c.dnap).min():.3f} y {(c.aif / c.dnap).max():.3f} ({c.anio.min()}-{c.anio.max()})")
    c = pd.read_sql("""SELECT d.anio, SUM(d.servicio_deuda_intereses_mill_pesos) AS deuda,
                              SUM(f.intereses_deuda_mill_pesos) AS aif
                       FROM hecho_subdivision_financiero d
                       JOIN hecho_subdivision_finanzas_publicas f USING (subdivision_id, anio)
                       WHERE d.servicio_deuda_intereses_mill_pesos IS NOT NULL GROUP BY d.anio""", con)
    print("   intereses de deuda provincial, planilla de servicios / AIF: entre "
          f"{(c.deuda / c.aif).min():.3f} y {(c.deuda / c.aif).max():.3f}")
    assert ((c.deuda / c.aif - 1).abs() < 0.05).all()
    c = pd.read_sql("""SELECT p.iso3, a.anio, SUM(a.emisiones_gei_total_tco2e) / 1e6 AS regiones,
                              e.emisiones_gei_total_mtco2e AS nacional
                       FROM hecho_subdivision_ambiental a
                       JOIN dim_subdivision d USING (subdivision_id) JOIN dim_pais p ON p.pais_id = d.pais_id
                       JOIN hecho_pais_emisiones e ON e.pais_id = p.pais_id AND e.anio = a.anio
                       WHERE a.anio = 2022 GROUP BY p.iso3, a.anio""", con)
    c["regiones_sobre_nacional"] = (c.regiones / c.nacional).round(3)
    print("   emisiones 2022, suma de regiones OCDE / dato nacional BM:",
          dict(zip(c.iso3, c.regiones_sobre_nacional)))
    if extra_p["columnas_vacias_descartadas"]:
        print("   columnas vacías descartadas del panel:", extra_p["columnas_vacias_descartadas"])

    print("5. Exportando")
    (MASTER / "esquema.sql").write_text(
        "-- Generado por construir_master.py\n\n" + "\n\n".join(
            r[0] + ";" for r in con.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY "
                                            "CASE type WHEN 'table' THEN 0 ELSE 1 END, rowid")))
    for t, d in dims.items():
        d.to_csv(TABLAS / f"{t}.csv", index=False)
    pd.read_sql("SELECT * FROM v_pais", con).to_csv(TABLAS / "v_pais.csv", index=False)
    pd.read_sql("SELECT * FROM ref_catalogo_tabla", con).to_csv(TABLAS / "ref_catalogo_tabla.csv", index=False)
    pd.read_sql("SELECT * FROM ref_diccionario_columna", con).to_csv(TABLAS / "ref_diccionario_columna.csv", index=False)
    con.execute("VACUUM")
    con.close()
    print(f"   {BASE.name}: {BASE.stat().st_size / 1e6:.1f} MB, {len(dims) + len(hechos) + 2} tablas")


if __name__ == "__main__":
    main()
