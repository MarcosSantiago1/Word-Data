"""
Indicadores sociales y digitales por país: alfabetización, nivel educativo alcanzado, redes sociales,
compra de videojuegos, construcción, inversión en cultura, rendimiento deportivo (medallero olímpico)
y empleo en juegos de azar y apuestas.

Qué se pudo conseguir y qué no (y por qué) está en FUENTES_INDICADORES_SOCIALES.md.
Este script baja los datos, los limpia y deja una tabla CSV por tema en esta carpeta (clave iso3 + anio):

    pais_educacion_anual.csv          Banco Mundial (UNESCO-UIS, Índice de Capital Humano)
    pais_digital_ocio_anual.csv       OCDE, encuesta de uso de TIC por personas (redes sociales, videojuegos)
    pais_empleo_sectorial_anual.csv   OIT (construcción, cultura, juegos de azar y apuestas)
    pais_gasto_cultura_anual.csv      FMI y OCDE, gasto público por función (COFOG 08 y 08.2)
    pais_deporte_olimpico.csv         Olympedia, medallero y atletas por edición de los Juegos Olímpicos
    pais_consolas_comercio_anual.csv  UN Comtrade, importaciones y exportaciones de consolas (HS 950450)

Las participaciones que se pueden calcular con otras columnas (empleo en construcción / empleo
total, gasto en servicios culturales / PIB...) NO se guardan: las arma construir_master.py en la
vista v_pais_indicadores_sociales.

    cd etl/indicadores_sociales_digitales
    python extraer_indicadores_sociales.py               # todo
    python extraer_indicadores_sociales.py educacion     # un solo paso

Dominios que tiene que permitir el entorno: api.worldbank.org rplumber.ilo.org sdmx.oecd.org api.imf.org
www.olympedia.org comtradeapi.un.org

Requiere: requests, pandas, lxml (para leer las tablas de Olympedia)
"""
import io
import re
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

CARPETA = Path(__file__).resolve().parent
CRUDOS = CARPETA / "crudos"
ETL = CARPETA.parent

ANIO_INICIO = 2000
# El servidor de la OIT rechaza (403) los pedidos sin un User-Agent de navegador.
NAVEGADOR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
# ILOSTAT usa KOS para Kosovo; el Banco Mundial y el maestro, XKX.
ISO3_OIT = {"KOS": "XKX"}

PAISES = set(pd.read_csv(ETL / "maestros" / "paises_maestro.csv", keep_default_na=False).iso3)


# ---------------------------------------------------------------------------
# Utilidades (las mismas ideas que fuentes_nuevas/extraer_dimensiones_nuevas.py)
# ---------------------------------------------------------------------------
def descargar(url, archivo, params=None, cabeceras=None, intentos=4):
    """Baja url a crudos/archivo y devuelve la ruta."""
    destino = CRUDOS / archivo
    for intento in range(intentos):
        try:
            r = requests.get(url, params=params, headers=NAVEGADOR | (cabeceras or {}), timeout=600)
            r.raise_for_status()
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(r.content)
            return destino
        except requests.RequestException as error:
            if intento == intentos - 1:
                raise
            print(f"   reintento {intento + 1} ({error.__class__.__name__}) {url[:80]}")
            time.sleep(2 ** (intento + 1))


def solo_paises(d):
    """Deja afuera agregados regionales (WLD, OECD, EU27...) y códigos que no son países del maestro."""
    return d[d.iso3.isin(PAISES)]


def ancho(largo, columnas):
    """De largo (iso3, anio, variable, valor) a una columna por variable, en el orden de `columnas`."""
    t = largo.pivot_table(index=["iso3", "anio"], columns="variable", values="valor", aggfunc="first").reset_index()
    t.columns.name = None
    for c in columnas:
        if c not in t:
            t[c] = pd.NA
    return t[["iso3", "anio"] + list(columnas)]


def guardar(t, archivo):
    t = t.dropna(how="all", subset=[c for c in t.columns if c not in ("iso3", "anio")])
    t = t.sort_values(["iso3", "anio"]).reset_index(drop=True)
    assert not t.duplicated(["iso3", "anio"]).any(), archivo
    t.to_csv(CARPETA / archivo, index=False)
    print(f"   {archivo}: {len(t)} filas, {t.iso3.nunique()} países, {t.anio.min()}-{t.anio.max()}")
    for c in t.columns[2:]:
        n = t.dropna(subset=[c])
        print(f"      {c:<55} {n.iso3.nunique():>3} países  {n.anio.min()}-{n.anio.max()}")
    return t


def banco_mundial(codigos, fuente=None):
    """Indicadores del Banco Mundial en formato largo (iso3, anio, variable, valor)."""
    partes = []
    for codigo, variable in codigos.items():
        params = {"format": "json", "per_page": 20000, "date": f"{ANIO_INICIO}:2030"}
        if fuente:
            params["source"] = fuente
        for intento in range(4):  # la API a veces devuelve 400/502 sueltos que se resuelven solos
            r = requests.get(f"https://api.worldbank.org/v2/country/all/indicator/{codigo}", params=params,
                             headers=NAVEGADOR, timeout=300)
            if r.ok or intento == 3:
                break
            print(f"   reintento {intento + 1} ({r.status_code}) {codigo}")
            time.sleep(2 ** (intento + 1))
        r.raise_for_status()
        cabecera, filas = r.json()[0], (r.json() + [None])[1]
        assert filas, (codigo, cabecera)
        assert cabecera["pages"] == 1, codigo
        partes.append(pd.DataFrame({"iso3": f["countryiso3code"], "anio": int(f["date"][:4]),
                                    "variable": variable, "valor": f["value"]}
                                   for f in filas if f["value"] is not None))
    largo = pd.concat(partes, ignore_index=True)
    largo.to_csv(CRUDOS / f"banco_mundial_{list(codigos.values())[0]}.csv.gz", index=False)
    return solo_paises(largo)


def ocde(flujo, clave, archivo):
    """Un flujo SDMX de la OCDE como CSV con etiquetas."""
    ruta = descargar(f"https://sdmx.oecd.org/public/rest/data/{flujo}/{clave}"
                     f"?startPeriod={ANIO_INICIO}&format=csvfilewithlabels", archivo)
    return pd.read_csv(ruta, low_memory=False)


def oit(indicador, archivo):
    """Un indicador de ILOSTAT (ambos sexos) en formato largo con classif1."""
    ruta = descargar("https://rplumber.ilo.org/data/indicator/", archivo,
                     params={"id": indicador, "sex": "SEX_T", "timefrom": ANIO_INICIO, "type": "code",
                             "format": ".csv"})
    d = pd.read_csv(ruta, low_memory=False)
    d["iso3"] = d.ref_area.replace(ISO3_OIT)
    return solo_paises(d.rename(columns={"time": "anio", "obs_value": "valor"}))


# ---------------------------------------------------------------------------
# 1. Alfabetización y nivel de estudios alcanzado (Banco Mundial, que republica UNESCO-UIS)
# ---------------------------------------------------------------------------
ALFABETIZACION = {
    "SE.ADT.LITR.ZS": "alfabetizacion_adultos_pct",              # 15 años o más
    "SE.ADT.LITR.FE.ZS": "alfabetizacion_adultos_mujeres_pct",
    "SE.ADT.LITR.MA.ZS": "alfabetizacion_adultos_hombres_pct",
    "SE.ADT.1524.LT.ZS": "alfabetizacion_jovenes_15_24_pct",
}
# Población de 25 años o más que completó AL MENOS ese nivel (cada nivel incluye a los de arriba)
NIVEL_ALCANZADO = {
    "SE.PRM.CUAT.ZS": "nivel_alcanzado_primaria_pct",
    "SE.SEC.CUAT.LO.ZS": "nivel_alcanzado_secundaria_baja_pct",
    "SE.SEC.CUAT.UP.ZS": "nivel_alcanzado_secundaria_alta_pct",
    "SE.SEC.CUAT.PO.ZS": "nivel_alcanzado_postsecundaria_pct",
    "SE.TER.CUAT.ST.ZS": "nivel_alcanzado_terciaria_ciclo_corto_pct",
    "SE.TER.CUAT.BA.ZS": "nivel_alcanzado_licenciatura_pct",
    "SE.TER.CUAT.MS.ZS": "nivel_alcanzado_maestria_pct",
    "SE.TER.CUAT.DO.ZS": "nivel_alcanzado_doctorado_pct",
}
CAPITAL_HUMANO = {
    "HD.HCI.EYRS": "escolaridad_esperada_anios",                 # años que un chico de 4 años espera cursar
    "HD.HCI.LAYS": "escolaridad_ajustada_aprendizaje_anios",     # los mismos años, descontando lo no aprendido
}
# Base de estadísticas educativas del Banco Mundial (source=12): años promedio de escolaridad, 25+
ESCOLARIDAD_UIS = {"UIS.EA.MEAN.1T6.AG25T99": "escolaridad_promedio_25mas_anios"}


def educacion():
    largo = pd.concat([banco_mundial(ALFABETIZACION), banco_mundial(NIVEL_ALCANZADO),
                       banco_mundial(ESCOLARIDAD_UIS, fuente=12), banco_mundial(CAPITAL_HUMANO)])
    columnas = (list(ALFABETIZACION.values()) + list(NIVEL_ALCANZADO.values())
                + list(ESCOLARIDAD_UIS.values()) + list(CAPITAL_HUMANO.values()))
    return guardar(ancho(largo, columnas), "pais_educacion_anual.csv")


# ---------------------------------------------------------------------------
# 2. Redes sociales y compra de videojuegos (OCDE, encuesta TIC a personas de 16 a 74 años)
# ---------------------------------------------------------------------------
# medida, edad -> columna. Son % de personas que lo hicieron en los últimos 3 meses (redes) o 12 (compras).
DIGITAL = {
    ("D1B_I", "Y16T74"): "usa_redes_sociales_16_74_pct",
    ("D1B_I", "Y16T24"): "usa_redes_sociales_16_24_pct",
    ("G2DBIS_I", "Y16T74"): "compro_online_videojuegos_software_16_74_pct",
    ("G2DBIS_I", "Y16T24"): "compro_online_videojuegos_software_16_24_pct",
    ("G1_I", "Y16T74"): "compro_online_algo_16_74_pct",
}


def digital_ocio():
    medidas = "+".join(sorted({m for m, _ in DIGITAL}))
    d = ocde("OECD.STI.DEP,DSD_ICT_HH_IND@DF_IND,", f".A.{medidas}.PT_POP.......", "ocde_tic_personas.csv")
    for dim in ("SEX", "EDUCATION_LEVEL", "INCOME_GROUP", "EMP_STATUS"):
        d = d[d[dim] == "_T"]
    d["variable"] = [DIGITAL.get((m, e)) for m, e in zip(d.MEASURE, d.AGE)]
    d = d.dropna(subset=["variable"])
    largo = solo_paises(pd.DataFrame({"iso3": d.REF_AREA, "anio": d.TIME_PERIOD.astype(int),
                                      "variable": d.variable, "valor": d.OBS_VALUE}))
    return guardar(ancho(largo, list(DIGITAL.values())), "pais_digital_ocio_anual.csv")


# ---------------------------------------------------------------------------
# 3. Empleo en construcción, cultura y juegos de azar (OIT)
# ---------------------------------------------------------------------------
# Estimaciones modeladas de la OIT: todos los países, todos los años, comparables entre sí.
EMPLEO_MODELADO = {
    "ECO_AGGREGATE_TOTAL": "empleo_total_modelado_miles_personas",
    "ECO_AGGREGATE_CON": "empleo_construccion_modelado_miles_personas",
}
# Encuestas de hogares a 2 dígitos de la CIIU rev. 4: solo los países que publican ese detalle.
EMPLEO_ENCUESTA = {
    "EC2_ISIC4_TOTAL": "empleo_total_encuesta_miles_personas",
    "EC2_ISIC4_R90": "empleo_artes_espectaculos_miles_personas",           # actividades creativas y artísticas
    "EC2_ISIC4_R91": "empleo_bibliotecas_museos_patrimonio_miles_personas",
    "EC2_ISIC4_R92": "empleo_juegos_azar_apuestas_miles_personas",         # casinos, loterías, apuestas
}


def empleo_sectorial():
    partes = []
    for indicador, codigos, archivo in (("EMP_2EMP_SEX_ECO_NB_A", EMPLEO_MODELADO, "oit_empleo_modelado.csv"),
                                        ("EMP_TEMP_SEX_EC2_NB_A", EMPLEO_ENCUESTA, "oit_empleo_ciiu2.csv")):
        d = oit(indicador, archivo)
        d = d[d.classif1.isin(codigos)]
        # una sola fuente por país y año en estos indicadores; si apareciera otra, se avisa
        assert not d.duplicated(["iso3", "anio", "classif1"]).any(), indicador
        partes.append(d.assign(variable=d.classif1.map(codigos))[["iso3", "anio", "variable", "valor"]])
    columnas = list(EMPLEO_MODELADO.values()) + list(EMPLEO_ENCUESTA.values())
    return guardar(ancho(pd.concat(partes), columnas), "pais_empleo_sectorial_anual.csv")


# ---------------------------------------------------------------------------
# 4. Inversión pública en cultura (FMI y OCDE, clasificación COFOG)
# ---------------------------------------------------------------------------
# FMI, Government Finance Statistics por función: ~90 países, ya en % del PIB y % del gasto total.
# COFOG 08 = recreación, cultura y religión; 08.2 = servicios culturales (museos, bibliotecas, teatros...).
GASTO_FMI = {  # (sector, función, transformación) -> columna
    ("S13", "GF08_T", "POGDP_PT"): "gasto_recreacion_cultura_religion_pct_pib",
    ("S13", "GF08_T", "POTO_PT"): "gasto_recreacion_cultura_religion_pct_gasto_publico",
    ("S13", "GF0820_T", "POGDP_PT"): "gasto_servicios_culturales_pct_pib",
    ("S13", "GF0820_T", "POTO_PT"): "gasto_servicios_culturales_pct_gasto_publico",
    # gobierno central solo: lo publican países sin dato de gobierno general (Argentina, México, Chile...)
    ("S1311", "GF08_T", "POGDP_PT"): "gasto_recreacion_cultura_religion_gob_central_pct_pib",
    ("S1311", "GF0820_T", "POGDP_PT"): "gasto_servicios_culturales_gob_central_pct_pib",
}
# OCDE, Government at a Glance: completa Chile y Colombia (que el FMI no tiene para gobierno general)
# y aporta el monto en US$ PPA.
GASTO_OCDE = {
    "PT_B1GQ": "gasto_recreacion_cultura_religion_pct_pib",
    "PT_OTE_S13": "gasto_recreacion_cultura_religion_pct_gasto_publico",
    "USD_PPP": "gasto_recreacion_cultura_religion_usd_ppa_millones",
}
ISO3_FMI = {"KOS": "XKX", "WBG": "PSE"}


def gasto_fmi():
    sectores = "+".join(sorted({s for s, _, _ in GASTO_FMI}))
    funciones = "+".join(sorted({f for _, f, _ in GASTO_FMI}))
    ruta = descargar(f"https://api.imf.org/external/sdmx/2.1/data/IMF.STA,GFS_COFOG,11.0.0/"
                     f".{sectores}.G2MF.{funciones}.POGDP_PT+POTO_PT.A", "fmi_cofog.csv",
                     params={"startPeriod": ANIO_INICIO},
                     cabeceras={"Accept": "application/vnd.sdmx.data+csv;version=1.0.0"})
    d = pd.read_csv(ruta, low_memory=False, usecols=["COUNTRY", "SECTOR", "INDICATOR", "TYPE_OF_TRANSFORMATION",
                                                     "TIME_PERIOD", "OBS_VALUE", "SCALE"]).dropna(subset=["OBS_VALUE"])
    assert set(d.SCALE) == {0}
    d["variable"] = [GASTO_FMI.get(k) for k in zip(d.SECTOR, d.INDICATOR, d.TYPE_OF_TRANSFORMATION)]
    d = d.dropna(subset=["variable"])
    return solo_paises(pd.DataFrame({"iso3": d.COUNTRY.replace(ISO3_FMI), "anio": d.TIME_PERIOD.astype(int),
                                     "variable": d.variable, "valor": d.OBS_VALUE}))


def gasto_ocde():
    g = ocde("OECD.GOV.GIP,DSD_GOV_COFOG@DF_GOV_COFOG_YU,", "A..GE..S13.GF08..", "ocde_cofog_gag.csv")
    g = g[g.UNIT_MEASURE.isin(GASTO_OCDE)]
    assert set(g.UNIT_MULT[g.UNIT_MEASURE == "USD_PPP"]) == {6}  # millones
    return solo_paises(pd.DataFrame({"iso3": g.REF_AREA, "anio": g.TIME_PERIOD.astype(int),
                                     "variable": g.UNIT_MEASURE.map(GASTO_OCDE), "valor": g.OBS_VALUE}))


def gasto_cultura():
    """FMI primero; la OCDE solo llena los país-año que el FMI no tiene (columna fuente_gobierno_general)."""
    columnas = list(dict.fromkeys(list(GASTO_FMI.values()) + list(GASTO_OCDE.values())))
    fmi, ocd = ancho(gasto_fmi(), columnas), ancho(gasto_ocde(), columnas)
    t = fmi.merge(ocd, on=["iso3", "anio"], how="outer", suffixes=("", "_ocde"))
    principal = "gasto_recreacion_cultura_religion_pct_pib"
    t["fuente_gobierno_general"] = pd.NA
    t.loc[t[principal].notna(), "fuente_gobierno_general"] = "FMI"
    usa_ocde = t[principal].isna() & t[f"{principal}_ocde"].notna()
    t.loc[usa_ocde, "fuente_gobierno_general"] = "OCDE"
    for c in GASTO_OCDE.values():
        if c == "gasto_recreacion_cultura_religion_usd_ppa_millones":
            t[c] = t[f"{c}_ocde"]
        else:
            t.loc[usa_ocde, c] = t.loc[usa_ocde, f"{c}_ocde"]
    # control: donde hay las dos fuentes, el % del PIB tiene que parecerse
    ambos = t[principal].notna() & t[f"{principal}_ocde"].notna() & ~usa_ocde
    dif = (t.loc[ambos, principal] - t.loc[ambos, f"{principal}_ocde"]).abs()
    print(f"   FMI vs OCDE, % del PIB en cultura: {ambos.sum()} país-año, diferencia mediana {dif.median():.3f} pp")
    t = t[["iso3", "anio"] + columnas + ["fuente_gobierno_general"]]
    return guardar(t, "pais_gasto_cultura_anual.csv")


# ---------------------------------------------------------------------------
# 5. Rendimiento deportivo: medallero olímpico (Olympedia)
# ---------------------------------------------------------------------------
# Olympedia (OlyMADMen) publica por edición el medallero por comité olímpico (con las medallas
# reasignadas por dopaje) y la cantidad de atletas de cada país. El código del comité (NOC) se pasa a
# ISO3 con noc_iso3.csv (de Wikidata, corregido a mano). Quedan afuera los equipos sin país:
# atletas neutrales (AIN, 2024), refugiados (EOR) y participantes independientes (IOA).
OLYMPEDIA = "https://www.olympedia.org/editions"


def ediciones_olimpicas():
    """{id de Olympedia: (año, 'verano'/'invierno')} de los Juegos desde ANIO_INICIO hasta hoy."""
    html = descargar(OLYMPEDIA, "olympedia_ediciones.html").read_text(encoding="utf-8")
    html = html[:html.index("<h2>Intercalated Games</h2>")]  # solo los Juegos Olímpicos
    _, verano, invierno = re.split(r"<h3>(?:Summer|Winter)</h3>", html)[:3]
    invierno = invierno.split("<h3>")[0]  # después viene Equestrian (1956)
    ediciones = {}
    for juegos, bloque in (("verano", verano), ("invierno", invierno)):
        for fila in re.findall(r"<tr>(.*?)</tr>", bloque, re.S):
            ids, anios = re.findall(r'href="/editions/(\d+)"', fila), re.findall(r">(\d{4})<", fila)
            if ids and anios and ANIO_INICIO <= int(anios[0]) <= date.today().year:
                ediciones[int(ids[0])] = (int(anios[0]), juegos)
    return ediciones


def medallero():
    noc = dict(pd.read_csv(CARPETA / "noc_iso3.csv", keep_default_na=False)[["noc", "iso3"]].values)
    partes = []
    for id_ed, (anio, juegos) in ediciones_olimpicas().items():
        paginas = {}
        for pagina in ("", "/countries"):
            ruta = descargar(f"{OLYMPEDIA}/{id_ed}{pagina}", f"olympedia/{id_ed}{pagina.replace('/', '_')}.html")
            # keep_default_na=False: que un texto como "NA" no se convierta en vacío
            paginas[pagina] = pd.read_html(io.StringIO(ruta.read_text(encoding="utf-8")), keep_default_na=False)
            time.sleep(1)
        tabla = [t for t in paginas[""] if {"NOC.1", "Gold", "Silver", "Bronze"} <= set(t.columns)]
        paises = [t for t in paginas["/countries"] if {"Country", "Men", "Women"} <= set(t.columns)]
        if not paises:
            continue  # edición anunciada sin participantes cargados todavía
        m = tabla[0].rename(columns={"NOC.1": "noc", "Gold": "medallas_oro", "Silver": "medallas_plata",
                                     "Bronze": "medallas_bronce"})
        m = m[m.noc.str.fullmatch(r"[A-Z]{3}")]
        p = paises[0].rename(columns={paises[0].columns[0]: "noc"})
        p = p[p.noc.str.fullmatch(r"[A-Z]{3}")]
        p = pd.DataFrame({"noc": p.noc, "atletas_participantes": pd.to_numeric(p.Total),
                          "atletas_mujeres": pd.to_numeric(p.Women)})
        e = p.merge(m[["noc", "medallas_oro", "medallas_plata", "medallas_bronce"]], on="noc", how="outer")
        e[["medallas_oro", "medallas_plata", "medallas_bronce"]] = (
            e[["medallas_oro", "medallas_plata", "medallas_bronce"]].apply(pd.to_numeric).fillna(0))
        e["iso3"] = e.noc.map(noc)
        sin = e[e.iso3.isna()]
        if len(sin):
            print(f"   {anio} {juegos}: sin país {dict(zip(sin.noc, sin.medallas_oro + sin.medallas_plata + sin.medallas_bronce))}"
                  " (medallas)")
        e = e.dropna(subset=["iso3"])
        e = e.groupby("iso3", as_index=False)[["atletas_participantes", "atletas_mujeres", "medallas_oro",
                                                "medallas_plata", "medallas_bronce"]].sum(min_count=1)
        partes.append(e.assign(anio=anio, juegos_olimpicos=juegos))
    t = solo_paises(pd.concat(partes, ignore_index=True))
    medallas = ["medallas_oro", "medallas_plata", "medallas_bronce"]
    t[medallas] = t[medallas].astype(int)
    columnas = ["juegos_olimpicos", "atletas_participantes", "atletas_mujeres", "medallas_oro", "medallas_plata",
                "medallas_bronce"]
    return guardar(t[["iso3", "anio"] + columnas], "pais_deporte_olimpico.csv")


# ---------------------------------------------------------------------------
# 6. Compra de videojuegos, aproximación mundial: comercio de consolas (UN Comtrade)
# ---------------------------------------------------------------------------
# HS 950450 = consolas y máquinas de videojuegos (nomenclatura HS 2012 en adelante). Hasta 2011 el
# mismo producto era la HS 950410, "videojuegos de los tipos utilizables con receptor de televisión".
# Mide hardware importado en US$, no juegos digitales. La API pública (sin clave) devuelve hasta 500
# filas por pedido: un pedido por año y flujo alcanza (~160 países informantes).
COMTRADE = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
FLUJOS = {"M": "importaciones_consolas", "X": "exportaciones_consolas"}


def consolas():
    reporteros = pd.read_json(descargar("https://comtradeapi.un.org/files/v1/app/reference/Reporters.json",
                                        "comtrade_reporteros.json"), typ="series")["results"]
    iso = {r["reporterCode"]: r["reporterCodeIsoAlpha3"] for r in reporteros if not r["isGroup"]}
    filas = []
    for anio in range(ANIO_INICIO, date.today().year):
        codigo = "950450" if anio >= 2012 else "950410"
        for flujo, nombre in FLUJOS.items():
            ruta = descargar(COMTRADE, f"comtrade/consolas_{anio}_{flujo}.json",
                             params={"period": anio, "cmdCode": codigo, "flowCode": flujo, "partnerCode": 0,
                                     "partner2Code": 0, "customsCode": "C00", "motCode": 0})
            cuerpo = pd.read_json(ruta, typ="series")
            assert not cuerpo.get("error"), cuerpo.get("error")
            datos = cuerpo["data"]
            assert len(datos) < 500, (anio, flujo)  # si llega al tope, faltan países
            for f in datos:
                filas.append({"iso3": iso.get(f["reporterCode"]), "anio": anio, "variable": f"{nombre}_usd",
                              "valor": f["primaryValue"]})
            time.sleep(2)  # la API pública limita la frecuencia de pedidos
    largo = solo_paises(pd.DataFrame(filas).dropna(subset=["iso3"]))
    columnas = [f"{n}_usd" for n in FLUJOS.values()]
    return guardar(ancho(largo, columnas), "pais_consolas_comercio_anual.csv")


PASOS = {"educacion": educacion, "digital": digital_ocio, "empleo": empleo_sectorial, "cultura": gasto_cultura,
         "deporte": medallero, "consolas": consolas}


def main():
    """Sin argumentos corre todo; con nombres de pasos (p. ej. `educacion cultura`) corre solo esos."""
    CRUDOS.mkdir(exist_ok=True)
    for nombre in sys.argv[1:] or list(PASOS):
        print(f"== {nombre}")
        PASOS[nombre]()


if __name__ == "__main__":
    main()
