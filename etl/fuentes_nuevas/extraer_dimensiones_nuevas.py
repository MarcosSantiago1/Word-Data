"""
Seis dimensiones nuevas para el modelo unificado: migración y remesas, transición energética y
clima, capital social y diversidad cultural, estado de derecho y gobernanza, riesgo de crédito,
y federalismo fiscal provincial. Más dos complementos: salud crónica y tecnología.

El plan (qué fuente, por qué y qué quedó afuera) está en FUENTES_DIMENSIONES_NUEVAS.md.
Este script baja los datos, los limpia y deja una tabla CSV por tema en esta carpeta:

    País (clave iso3 + anio)
      pais_migracion_anual.csv            Banco Mundial (ONU WPP, balanza de pagos)
      pais_emisiones_energia_anual.csv    Banco Mundial (EDGAR, SE4All), Our World in Data (Ember, EM-DAT)
      pais_capital_social_anual.csv       CEPALSTAT (Latinobarómetro), OWID (World Values Survey), V-Dem
      pais_diversidad_cultural_anual.csv  Comparative Constitutions Project
      pais_poblacion_indigena.csv         CEPALSTAT / CELADE (clave iso3 + decada_censal)
      pais_gobernanza_anual.csv           Banco Mundial WGI, V-Dem v16, BID DPI 2020
      pais_financiero_deuda_anual.csv     Banco Mundial (IDS, QEDS), BCRP (EMBIG)
      pais_salud_cronica_anual.csv        Banco Mundial, OMS GHO, OMS GHE vía OWID
      pais_tecnologia_anual.csv           Banco Mundial, OCDE (hogares con internet)

    Subdivisión (clave subdivision_iso + anio)
      subdivision_deuda_anual.csv             Coordinación Fiscal Provincial (stock al 31-12 y servicios)
      subdivision_finanzas_publicas_anual.csv Coordinación Fiscal Provincial (esquema Ahorro-Inversión-Financiamiento)
      subdivision_emisiones_anual.csv         OCDE, emisiones regionales (6 países de América Latina)
      subdivision_internet_anual.csv          ENACOM (accesos a internet fijo cada 100 hogares)

Las tasas y cocientes que se pueden calcular con otras columnas (remesas enviadas / PIB, deuda
externa / PIB, autonomía fiscal...) NO se guardan: los arma construir_master.py como vistas.

    cd etl/fuentes_nuevas
    python extraer_dimensiones_nuevas.py

Dominios que tiene que permitir el entorno: api.worldbank.org ghoapi.azureedge.net sdmx.oecd.org
raw.githubusercontent.com estadisticas.bcrp.gob.pe www.argentina.gob.ar ourworldindata.org
api-cepalstat.cepal.org data.iadb.org indicadores.enacom.gob.ar utexas.box.com public.boxcloud.com

Requiere: requests, pandas, openpyxl, xlrd, pyreadr
"""
import io
import os
import re
import sys
import time
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd
import pyreadr
import requests

CARPETA = Path(__file__).resolve().parent
CRUDOS = CARPETA / "crudos"
ETL = CARPETA.parent
sys.path.insert(0, str(ETL / "argentina_provincias"))
sys.path.insert(0, str(ETL / "latam_subnacional"))
sys.path.insert(0, str(ETL / "alianzas"))
from extraer_argentina_provincias import PROVINCIAS, nombre_limpio  # noqa: E402

ANIO_INICIO = 2000
NAVEGADOR = {"User-Agent": "Mozilla/5.0 (proyecto educativo analista de datos)"}
# ENACOM manda una cadena de certificados incompleta (le falta el intermedio Sectigo DV R36, el
# mismo problema que datos.salud.gob.ar): se arma un bundle con el del proxy + ese intermedio.
SECTIGO = ETL / "argentina_provincias" / "crudos" / "sectigo_dv_r36.pem"

PAISES = set(pd.read_csv(ETL / "maestros" / "paises_maestro.csv", keep_default_na=False).iso3)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def descargar(url, archivo, fija=False, verify=True, intentos=4):
    """Baja url a crudos/archivo. fija=True: si ya existe no se vuelve a bajar (datos históricos)."""
    destino = CRUDOS / archivo
    if fija and destino.exists():
        return destino
    for intento in range(intentos):
        try:
            r = requests.get(url, headers=NAVEGADOR, timeout=300, verify=verify)
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
    """Deja afuera agregados regionales (WLD, LCN...) y códigos que no son países del maestro."""
    return d[d.iso3.isin(PAISES)]


def ancho(largo, columnas, clave=("iso3", "anio")):
    """De largo (clave, variable, valor) a una columna por variable, en el orden de `columnas`."""
    t = largo.pivot_table(index=list(clave), columns="variable", values="valor", aggfunc="first").reset_index()
    t.columns.name = None
    for c in columnas:
        if c not in t:
            t[c] = pd.NA
    return t[list(clave) + list(columnas)]


def juntar(*tablas, clave=("iso3", "anio")):
    t = tablas[0]
    for otra in tablas[1:]:
        t = t.merge(otra, on=list(clave), how="outer")
    return t.sort_values(list(clave)).reset_index(drop=True)


def guardar(t, archivo, clave=("iso3", "anio")):
    t = t.dropna(how="all", subset=[c for c in t.columns if c not in clave])
    assert not t.duplicated(list(clave)).any(), archivo
    t.to_csv(CARPETA / archivo, index=False)
    anio = "anio" if "anio" in t else clave[-1]
    print(f"   {archivo}: {len(t)} filas, {t[clave[0]].nunique()} unidades, {t[anio].min()}-{t[anio].max()}")
    return t


# ---------------------------------------------------------------------------
# Fuentes que se usan en varias dimensiones
# ---------------------------------------------------------------------------
def banco_mundial(codigos, fuente=None, fechas=f"{ANIO_INICIO}:2030"):
    """Indicadores del Banco Mundial en formato largo (iso3, anio, periodo, variable, valor)."""
    partes = []
    for codigo, variable in codigos.items():
        params = {"format": "json", "per_page": 20000, "date": fechas}
        if fuente:
            params["source"] = fuente
        r = requests.get(f"https://api.worldbank.org/v2/country/all/indicator/{codigo}", params=params,
                         headers=NAVEGADOR, timeout=300)
        r.raise_for_status()
        cabecera, filas = r.json()[0], (r.json() + [None])[1]
        assert filas, (codigo, cabecera)
        assert cabecera["pages"] == 1, codigo
        # en las bases trimestrales (QEDS) countryiso3code viene vacío y el ISO3 está en country.id
        partes.append(pd.DataFrame({"iso3": f["countryiso3code"] or f["country"]["id"], "anio": int(f["date"][:4]),
                                    "periodo": f["date"], "variable": variable, "valor": f["value"]}
                                   for f in filas if f["value"] is not None))
    largo = pd.concat(partes, ignore_index=True)
    largo.to_csv(CRUDOS / f"banco_mundial_{list(codigos.values())[0]}.csv.gz", index=False)
    return solo_paises(largo)


def owid(grafico, archivo):
    """Un gráfico de Our World in Data como CSV (entity, code, year, columnas...)."""
    ruta = descargar(f"https://ourworldindata.org/grapher/{grafico}.csv?useColumnShortNames=true", archivo)
    d = pd.read_csv(ruta).rename(columns={"code": "iso3", "year": "anio"})
    return solo_paises(d[d.anio >= ANIO_INICIO])


def cepalstat(indicador, variable, filtros):
    """Un indicador de CEPALSTAT; `filtros` = {id de dimensión: nombre del miembro a conservar}."""
    ruta = descargar(f"https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/{indicador}/data"
                     "?lang=es&format=json", f"cepalstat_{indicador}.json")
    cuerpo = pd.read_json(ruta, typ="series")["body"]
    nombres = {f"dim_{d['id']}": {m["id"]: m["name"] for m in d["members"]} for d in cuerpo["dimensions"]}
    d = pd.DataFrame(cuerpo["data"])
    for dim, miembros in nombres.items():
        if dim in d:
            d[dim] = d[dim].map(miembros)
    for dim, conservar in filtros.items():
        d = d[d[f"dim_{dim}"] == conservar]
    d = d.assign(variable=variable, valor=pd.to_numeric(d.value, errors="coerce"))
    return solo_paises(d)


VDEM = None


def vdem(columnas):
    """V-Dem v16 (país-año). El .RData pesa 34 MB y se lee una sola vez."""
    global VDEM
    if VDEM is None:
        ruta = descargar("https://raw.githubusercontent.com/vdeminstitute/vdemdata/master/data/vdem.RData",
                         "vdem_v16.RData", fija=True)
        VDEM = pyreadr.read_r(ruta)["vdem"]
        VDEM = VDEM.rename(columns={"country_text_id": "iso3", "year": "anio"})
        VDEM["anio"] = VDEM.anio.astype(int)
    d = VDEM[VDEM.anio >= ANIO_INICIO][["iso3", "anio"] + list(columnas)].rename(columns=columnas)
    return solo_paises(d)


# ---------------------------------------------------------------------------
# 1. Migración y remesas
# ---------------------------------------------------------------------------
MIGRACION = {
    "SM.POP.NETM": "saldo_migratorio_neto",
    "SM.POP.TOTL.ZS": "stock_migrantes_pct_poblacion",
    "BX.TRF.PWKR.CD.DT": "remesas_recibidas_usd",
    "BX.TRF.PWKR.DT.GD.ZS": "remesas_recibidas_pct_pib",
    "BM.TRF.PWKR.CD.DT": "remesas_enviadas_usd",
}


def migracion():
    t = ancho(banco_mundial(MIGRACION), MIGRACION.values())
    t["saldo_migratorio_neto"] = t.saldo_migratorio_neto.round().astype("Int64")
    return guardar(t, "pais_migracion_anual.csv")


# ---------------------------------------------------------------------------
# 2. Transición energética y cambio climático
# ---------------------------------------------------------------------------
EMISIONES = {
    "EN.GHG.ALL.PC.CE.AR5": "emisiones_gei_per_capita_tco2e",
    "EN.GHG.ALL.MT.CE.AR5": "emisiones_gei_total_mtco2e",
    "EN.GHG.CO2.PC.CE.AR5": "emisiones_co2_per_capita_tco2e",
    "EG.FEC.RNEW.ZS": "energia_renovable_pct_consumo_final",
}
# EM-DAT clasifica los desastres; estos son los climáticos e hidrológicos (sin sismos ni volcanes)
DESASTRES_CLIMATICOS = ["drought", "flood", "landslide", "extreme_weather", "wildfire", "extreme_temperature"]


def emisiones_energia():
    bm = ancho(banco_mundial(EMISIONES), EMISIONES.values())
    # La serie eléctrica del BM termina en 2021; OWID (Ember + Energy Institute) llega al año pasado
    energia = pd.read_csv(descargar("https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv",
                                    "owid_energy_data.csv"), usecols=["iso_code", "year", "renewables_share_elec",
                                                                       "other_renewables_share_elec_exc_biofuel",
                                                                       "hydro_share_elec", "solar_share_elec",
                                                                       "wind_share_elec"])
    energia = solo_paises(energia.rename(columns={"iso_code": "iso3", "year": "anio"}))
    energia = energia[energia.anio >= ANIO_INICIO]
    energia = energia.assign(
        electricidad_renovable_pct=energia.renewables_share_elec,
        electricidad_hidro_pct=energia.hydro_share_elec,
        electricidad_solar_eolica_pct=energia.solar_share_elec.fillna(0) + energia.wind_share_elec.fillna(0),
    )[["iso3", "anio", "electricidad_renovable_pct", "electricidad_hidro_pct", "electricidad_solar_eolica_pct"]]
    energia.loc[energia.electricidad_renovable_pct.isna(), "electricidad_solar_eolica_pct"] = pd.NA

    afectados = owid("total-affected-by-natural-disasters", "owid_desastres_afectados.csv")
    muertos = owid("natural-disasters-deaths", "owid_desastres_muertes.csv")
    desastres = pd.DataFrame({
        "iso3": afectados.iso3, "anio": afectados.anio,
        "personas_afectadas_desastres_climaticos": afectados[
            [f"total_affected_{t}_yearly" for t in DESASTRES_CLIMATICOS]].sum(axis=1, min_count=1),
    }).merge(pd.DataFrame({
        "iso3": muertos.iso3, "anio": muertos.anio,
        "muertes_desastres_climaticos": muertos[
            [f"total_dead_{t}_yearly" for t in DESASTRES_CLIMATICOS]].sum(axis=1, min_count=1),
    }), on=["iso3", "anio"], how="outer")
    for c in ("personas_afectadas_desastres_climaticos", "muertes_desastres_climaticos"):
        desastres[c] = desastres[c].round().astype("Int64")
    return guardar(juntar(bm, energia, desastres), "pais_emisiones_energia_anual.csv")


# ---------------------------------------------------------------------------
# 3. Capital social, confianza y diversidad cultural
# ---------------------------------------------------------------------------
def capital_social():
    # Latinobarómetro procesado por CEPAL: porcentaje sobre el total de entrevistados, ambos sexos
    latino = pd.concat([
        cepalstat(1831, "confianza_interpersonal_pct", {4821: "Ambos sexos"}),
        cepalstat(5528, "desconfianza_poder_judicial_pct", {144: "Ambos sexos"}),
        cepalstat(995, "desconfianza_partidos_congreso_pct", {4821: "Ambos sexos"}),
        cepalstat(3257, "confianza_policia_pct", {4821: "Ambos sexos"}),
    ])
    latino["anio"] = latino.dim_29117.astype(int)
    latino = latino[latino.anio >= ANIO_INICIO]
    latino = ancho(latino, ["confianza_interpersonal_pct", "desconfianza_poder_judicial_pct",
                            "desconfianza_partidos_congreso_pct", "confianza_policia_pct"])
    # World Values Survey / European Values Study (por ola, no todos los años)
    wvs = owid("self-reported-trust-attitudes", "owid_confianza_wvs.csv")
    wvs = wvs[["iso3", "anio", "trust"]].rename(columns={"trust": "confianza_interpersonal_wvs_pct"})
    sociedad_civil = vdem({"v2xcs_ccsi": "indice_sociedad_civil_0_1",
                           "v2csprtcpt": "sociedad_civil_participacion_vdem"})
    return guardar(juntar(latino, wvs, sociedad_civil), "pais_capital_social_anual.csv")


def poblacion_indigena():
    d = cepalstat(4992, "poblacion_indigena_pct", {48525: "Total"})
    d["decada_censal"] = d.dim_47491.str.extract(r"(\d{4})")[0].astype(int)
    t = d[["iso3", "decada_censal", "valor"]].rename(columns={"valor": "poblacion_indigena_pct"})
    return guardar(t.sort_values(["iso3", "decada_censal"]), "pais_poblacion_indigena.csv",
                   clave=("iso3", "decada_censal"))


# Comparative Constitutions Project, "Characteristics of National Constitutions" v5 (1789-2023)
URL_CCP = "https://utexas.box.com/shared/static/cpgysqaogi1590ucv5x0wn59urqm00x3.zip"


def si_no(serie, si=(1,), no=(2, 3)):
    """Códigos del CCP a 0/1: 1 = sí; 2 = no, 3 = neutralidad; 96-99 (otro, no aplica...) = vacío."""
    return serie.map(lambda v: 1 if v in si else (0 if v in no else pd.NA)).astype("Int64")


def diversidad_cultural():
    # mismo cruce COW -> ISO3 que el de alianzas: códigos ambiguos a mano, el resto por nombre
    from extraer_alianzas_internacionales import COW_CCODE_ISO3, iso3_por_nombre  # noqa: E402
    ruta = descargar(URL_CCP, "ccpcnc_v5.zip", fija=True)
    columnas = ["cowcode", "country", "year", "langprot", "cultrght"] + [f"indpolgr_{i}" for i in range(1, 8)]
    with zipfile.ZipFile(ruta) as z:
        d = pd.read_csv(io.BytesIO(z.read("ccpcnc_v5/ccpcnc/ccpcnc_v5.csv")), usecols=columnas,
                        encoding="latin-1", low_memory=False)
    d = d[d.year >= ANIO_INICIO]
    mapa = {(cc, nombre): None if nombre in ("Abkhazia", "South Ossetia") else
            COW_CCODE_ISO3[cc] if cc in COW_CCODE_ISO3 else iso3_por_nombre(nombre)
            for cc, nombre in set(zip(d.cowcode, d.country))}
    d["iso3"] = [mapa[k] for k in zip(d.cowcode, d.country)]
    sin_iso = sorted(set(d[d.iso3.isna()].country))
    if sin_iso:
        print("   CCP sin código ISO (se descartan):", sin_iso)
    # Derechos de pueblos indígenas: voto, representación, partidos, impuestos, actividades propias,
    # autogobierno o derechos culturales (indpolgr_1..7). 99 = la constitución no los menciona.
    indigenas = d[[f"indpolgr_{i}" for i in range(1, 8)]]
    derechos_indigenas = (indigenas == 1).any(axis=1).astype("Int64")
    derechos_indigenas[indigenas.isna().all(axis=1)] = pd.NA
    t = pd.DataFrame({
        "iso3": d.iso3, "anio": d.year.astype(int),
        "es_proteccion_lenguas_constitucion": si_no(d.langprot),
        "es_derechos_indigenas_constitucion": derechos_indigenas,
        "es_derechos_culturales_constitucion": si_no(d.cultrght, no=(2,)),
    })
    # el año en que cambia la constitución puede tener dos filas: queda la vigente al cierre
    t = t.dropna(subset=["iso3"]).drop_duplicates(["iso3", "anio"], keep="last")
    return guardar(solo_paises(t), "pais_diversidad_cultural_anual.csv")


# ---------------------------------------------------------------------------
# 4. Estado de derecho y gobernanza
# ---------------------------------------------------------------------------
WGI = {
    "GOV_WGI_CC.EST": "indice_control_corrupcion",
    "GOV_WGI_CC.SC": "indice_control_corrupcion_0_100",
    "GOV_WGI_RL.EST": "indice_estado_derecho",
    "GOV_WGI_RL.SC": "indice_estado_derecho_0_100",
    "GOV_WGI_PV.EST": "estabilidad_politica_ausencia_violencia",
    "GOV_WGI_GE.EST": "efectividad_gobierno",
    "GOV_WGI_RQ.EST": "calidad_regulatoria",
    "GOV_WGI_VA.EST": "voz_rendicion_cuentas",
}
# DPI 2020 del BID: el CSV de la base (el otro enlace del sitio es el PDF de definiciones)
URL_DPI = "https://data.iadb.org/files/download/5e9bae0b-2d7d-4537-8f9a-b52fa845fd62"


def gobernanza():
    wgi = ancho(banco_mundial(WGI, fuente=3), WGI.values())
    dpi = pd.read_csv(descargar(URL_DPI, "dpi2020.csv", fija=True), low_memory=False)
    dpi = dpi.rename(columns={"ifs": "iso3", "year": "anio"})
    dpi = dpi[dpi.anio >= ANIO_INICIO]
    # checks = cantidad de actores con poder de veto; -999 es "sin dato" en la DPI
    dpi["veto_players_count"] = dpi.checks.where(dpi.checks >= 0).astype("Int64")
    dpi = solo_paises(dpi[["iso3", "anio", "veto_players_count"]])
    v = vdem({"v2x_polyarchy": "indice_democracia_electoral_0_1", "v2x_libdem": "indice_democracia_liberal_0_1",
              "v2x_rule": "indice_estado_derecho_vdem_0_1", "v2x_corr": "indice_corrupcion_politica_vdem_0_1",
              "v2x_jucon": "restricciones_judiciales_ejecutivo_0_1",
              "v2xlg_legcon": "restricciones_legislativas_ejecutivo_0_1"})
    return guardar(juntar(wgi, dpi, v), "pais_gobernanza_anual.csv")


# ---------------------------------------------------------------------------
# 5. Riesgo de crédito y deuda
# ---------------------------------------------------------------------------
DEUDA = {
    "NY.GDP.MKTP.CD": "pib_usd",
    "DT.DOD.DECT.CD": "deuda_externa_ids_usd",
    "DT.DOD.DECT.GN.ZS": "deuda_externa_pct_ingreso_nacional",
    "DT.DOD.DSTC.ZS": "deuda_externa_corto_plazo_pct",
    "DT.TDS.DECT.EX.ZS": "servicio_deuda_pct_exportaciones",
    "DT.TDS.DECT.GN.ZS": "servicio_deuda_pct_ingreso_nacional",
    "GC.DOD.TOTL.GD.ZS": "deuda_gobierno_central_pct_pib",
    "GC.XPN.INTP.RV.ZS": "intereses_pct_ingresos_fiscales",
    "FI.RES.TOTL.CD": "reservas_internacionales_usd",
    "FI.RES.TOTL.MO": "reservas_internacionales_meses_importacion",
}
# Spread EMBIG (J.P. Morgan) que publica el Banco Central de Reserva del Perú, mensual, en pb
EMBIG_BCRP = {"PN01129XM": "PER", "PN01130XM": "ARG", "PN01131XM": "BRA", "PN01132XM": "CHL",
              "PN01133XM": "COL", "PN01134XM": "ECU", "PN01135XM": "MEX", "PN01136XM": "VEN"}
MESES = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9,
         "Oct": 10, "Nov": 11, "Dic": 12}


def embig():
    filas = []
    for serie, iso3 in EMBIG_BCRP.items():
        ruta = descargar(f"https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{serie}/json/"
                         f"{ANIO_INICIO}-1/2030-12", f"bcrp_embig_{serie}.json")
        texto = ruta.read_text(encoding="utf-8", errors="ignore")
        assert texto.lstrip().startswith("{"), f"BCRP devolvió HTML para {serie} (Incapsula): volver a correr"
        for p in pd.read_json(io.StringIO(texto), typ="series")["periods"]:
            mes, anio = p["name"].split(".")
            valor = pd.to_numeric(p["values"][0], errors="coerce")
            if pd.notna(valor):
                filas.append(dict(iso3=iso3, anio=int(anio), mes=MESES[mes], valor=valor))
        time.sleep(3)  # el sitio tiene Incapsula: muchas consultas seguidas devuelven una página HTML
    m = pd.DataFrame(filas)
    m.to_csv(CRUDOS / "bcrp_embig_mensual.csv", index=False)
    return m.groupby(["iso3", "anio"]).agg(spread_embi_pb=("valor", "mean"),
                                           spread_embi_meses=("valor", "size")).reset_index()


def financiero_deuda():
    bm = ancho(banco_mundial(DEUDA), DEUDA.values())
    # Deuda externa bruta trimestral (QEDS, BM/FMI): cubre también a los países de ingreso alto.
    # Se toma el cuarto trimestre como dato de fin de año.
    q = banco_mundial({"DT.DOD.DECT.CD.AR.US": "deuda_externa_usd"}, fuente=22,
                      fechas=f"{ANIO_INICIO}Q1:2030Q4")
    q = q[q.periodo.str.endswith("Q4")]
    q = ancho(q, ["deuda_externa_usd"])
    return guardar(juntar(bm, q, embig()), "pais_financiero_deuda_anual.csv")


# ---------------------------------------------------------------------------
# Complementos: salud crónica y tecnología
# ---------------------------------------------------------------------------
SALUD_BM = {
    "SH.STA.DIAB.ZS": "diabetes_prevalencia_pct",
    "SH.DYN.NCOM.ZS": "mortalidad_ent_30_70_pct",
    "SH.DTH.NCOM.ZS": "muertes_ent_pct",
}
SALUD_OMS = {"NCD_HYP_PREVALENCE_A": "hipertension_prevalencia_pct", "NCD_BMI_30A": "obesidad_adultos_pct"}


def oms(codigo, variable):
    ruta = descargar(f"https://ghoapi.azureedge.net/api/{codigo}?$filter=Dim1 eq 'SEX_BTSX' and "
                     "SpatialDimType eq 'COUNTRY'", f"oms_{codigo}.json")
    d = pd.DataFrame(pd.read_json(ruta, typ="series")["value"])
    assert d.Dim2.nunique() <= 1, (codigo, d.Dim2.unique())  # un solo grupo de edad
    return solo_paises(pd.DataFrame({"iso3": d.SpatialDim, "anio": d.TimeDim, "variable": variable,
                                     "valor": d.NumericValue}))


def salud_cronica():
    bm = banco_mundial(SALUD_BM)
    o = pd.concat([oms(c, v) for c, v in SALUD_OMS.items()])
    t = ancho(pd.concat([bm, o[o.anio >= ANIO_INICIO]]), list(SALUD_BM.values()) + list(SALUD_OMS.values()))
    # AVAD (DALY) totales de la OMS, Global Health Estimates 2021, republicados por OWID
    avad = owid("total-disease-burden-who", "owid_avad_oms.csv")
    avad = avad[["iso3", "anio", "daly_count__age_group_allages__sex_both_sexes__cause_all_causes"]].rename(
        columns={"daly_count__age_group_allages__sex_both_sexes__cause_all_causes": "avad_total"})
    avad["avad_total"] = avad.avad_total.round().astype("Int64")
    return guardar(juntar(t, avad), "pais_salud_cronica_anual.csv")


TECNOLOGIA = {
    "IT.NET.BBND.P2": "banda_ancha_fija_x100",
    "IT.NET.USER.ZS": "usuarios_internet_pct",
    "GB.XPD.RSDV.GD.ZS": "gasto_en_i_d_pct_pib",
}


def hogares_internet_ocde():
    ruta = descargar("https://sdmx.oecd.org/public/rest/data/OECD.STI.DEP,DSD_ICT_HH_IND@DF_HH,1.1/"
                     f"?startPeriod={ANIO_INICIO}&format=csvfilewithlabels", "ocde_hogares_tic.csv")
    d = pd.read_csv(ruta, low_memory=False)
    d = d[(d.MEASURE == "B1_HH") & (d.UNIT_MEASURE == "PT_HH")]
    for dim in ("GEO_AREA", "AGE", "SEX", "EDUCATION_LEVEL", "INCOME_GROUP", "EMP_STATUS"):
        d = d[d[dim].isin(["_T", "_Z"])]
    return solo_paises(pd.DataFrame({"iso3": d.REF_AREA, "anio": d.TIME_PERIOD.astype(int),
                                     "variable": "hogares_con_conectividad_pct", "valor": d.OBS_VALUE}))


def tecnologia():
    t = ancho(pd.concat([banco_mundial(TECNOLOGIA), hogares_internet_ocde()]),
              list(TECNOLOGIA.values()) + ["hogares_con_conectividad_pct"])
    return guardar(t, "pais_tecnologia_anual.csv")


# ---------------------------------------------------------------------------
# 6. Provincias argentinas: deuda y federalismo fiscal (Coordinación Fiscal Provincial)
# ---------------------------------------------------------------------------
PAGINA_CFP = "https://www.argentina.gob.ar/economia/sechacienda/coordinacion-fiscal-provincial/"
ARCHIVOS = "https://www.argentina.gob.ar/sites/default/files/"


def iso_provincia(texto):
    """Código ISO de una provincia escrita a la manera de cada planilla (None si no es provincia)."""
    t = re.sub(r"\(\d+\)|\*", "", str(texto))
    t = re.sub(r"\s+", " ", t).strip()
    sin = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    if sin in ("ciudad", "ciudad de buenos aires", "c.a.b.a.", "ciudad autonoma de bs. as.", "ciudad de bs. as.",
               "c.a.b.a", "gcba", "mcba") or sin.startswith("ciudad autonoma"):
        return PROVINCIAS["Ciudad de Buenos Aires"]
    return PROVINCIAS.get(nombre_limpio(t))


def enlaces(pagina, patron):
    """Archivos de una página de argentina.gob.ar cuyo nombre cumple `patron` -> {año: nombre}."""
    html = requests.get(PAGINA_CFP + pagina, headers=NAVEGADOR, timeout=120).text
    encontrados = {}
    for nombre in sorted(set(re.findall(r"sites/default/files/([^\"')\s]+\.xlsx?)", html))):
        m = re.search(patron, nombre)
        if m:
            encontrados[int(next(g for g in m.groups() if g))] = nombre  # el último en orden alfabético gana (p. ej. "_2" sobre "_1")
    return encontrados


def unidad_en_millones(tabla):
    """Las planillas viejas vienen en miles de pesos y las nuevas en millones."""
    texto = " ".join(str(v) for v in tabla.head(15).to_numpy().ravel() if isinstance(v, str)).lower()
    if "millones" in texto:
        return 1.0
    if "miles" not in texto:  # servicios 2022 no dice la unidad: por su magnitud son miles
        print("   sin unidad, se asume miles de pesos:", tabla.attrs.get("archivo"))
    return 1 / 1000


ACREEDOR = [  # (palabra en el encabezado, nombre de columna); se usa la primera que coincide
    ("TOTAL", "total"), ("GOBIERNO NACIONAL", "gobierno_nacional"), ("FFFIR", "fffir"),
    ("INFRAESTRUCTURA", "fffir"), ("FFDP", "ffdp"), ("DESARROLLO PROVINCIAL", "ffdp"), ("BANC", "bancos"),
    ("CONSOLIDADA", "deuda_consolidada"), ("BONOS", "bonos"), ("TÍTULOS", "bonos"), ("TITULOS", "bonos"),
    ("ORGANISMOS", "organismos_internacionales"), ("INDIRECTA", "deuda_indirecta"),
]


def acreedor(encabezado):
    e = str(encabezado).upper()
    return next((c for palabra, c in ACREEDOR if palabra in e), None)


def filas_provincias(tabla, columna_nombre):
    """Las 24 filas de provincias que siguen al encabezado (las planillas viejas repiten todo en inglés)."""
    vistas, filas = set(), []
    for i, v in tabla[columna_nombre].items():
        iso = iso_provincia(v)
        if iso and iso not in vistas:
            vistas.add(iso)
            filas.append((i, iso))
    # alguna planilla omite una provincia sin deuda (servicios 2007 no trae San Luis)
    assert len(filas) >= 23, (len(filas), sorted(vistas))
    if len(filas) < 24:
        print("   falta", set(PROVINCIAS.values()) - vistas - {None}, "en", tabla.attrs.get("archivo"))
    return filas


def leer_stock(ruta):
    tabla = pd.read_excel(ruta, header=None)
    tabla.attrs["archivo"] = ruta.name
    escala = unidad_en_millones(tabla)
    fila_enc, col_nombre = next((i, c) for i, fila in tabla.iterrows() for c, v in fila.items()
                                if isinstance(v, str) and v.strip().upper().startswith("JURISDICC"))
    columnas = {c: acreedor(v) for c, v in tabla.loc[fila_enc].items() if c != col_nombre and acreedor(v)}
    filas = []
    for i, iso in filas_provincias(tabla.loc[fila_enc + 1:], col_nombre):
        fila = {"subdivision_iso": iso}
        for c, nombre in columnas.items():
            if nombre not in fila:  # la primera columna "TOTAL..." es el total sin deuda flotante
                fila[nombre] = pd.to_numeric(tabla.at[i, c], errors="coerce") * escala
        filas.append(fila)
    return pd.DataFrame(filas)


def leer_servicios(ruta):
    tabla = pd.read_excel(ruta, header=None)
    tabla.attrs["archivo"] = ruta.name
    escala = unidad_en_millones(tabla)
    # encabezado de dos filas: acreedor arriba, "Amortización" / "Interés" abajo
    fila_tipo = next(i for i, fila in tabla.iterrows()
                     if sum(isinstance(v, str) and v.strip().startswith("Amortizaci") for v in fila) >= 3)
    fila_enc = fila_tipo - 1
    col_nombre = next(c for c, v in tabla.loc[fila_enc].items()
                      if isinstance(v, str) and v.strip().upper() in ("JURISDICCION", "JURISDICCIÓN", "AÑO"))
    columnas, actual = {}, None
    for c in tabla.columns:
        actual = acreedor(tabla.at[fila_enc, c]) or actual if c != col_nombre else None
        tipo = str(tabla.at[fila_tipo, c])
        if actual and tipo.startswith(("Amortizaci", "Inter")):
            columnas[c] = f"{'amortizacion' if tipo.startswith('Amortizaci') else 'intereses'}_{actual}"
    filas = []
    for i, iso in filas_provincias(tabla.loc[fila_tipo + 1:], col_nombre):
        fila = {"subdivision_iso": iso}
        for c, nombre in columnas.items():
            if nombre not in fila:
                fila[nombre] = pd.to_numeric(tabla.at[i, c], errors="coerce") * escala
        filas.append(fila)
    return pd.DataFrame(filas)


def deuda_provincial():
    stock = enlaces("deuda-publica-provincial/evolucion-de-stock",
                    r"^stock_(?:consolidado_(\d{4})_-_3112|iv_trim_(\d{4}))")
    servicios = enlaces("deuda-publica-provincial/evolucion-de-servicios",
                        r"^(?:ev\._de_servicios_-_consolidado_(\d{4})_-_trim\._iv|servicios_iv_trim_(\d{4}))")
    partes_s, partes_v = [], []
    for anio, nombre in sorted(a for a in stock.items() if a[0] >= ANIO_INICIO):
        d = leer_stock(descargar(ARCHIVOS + nombre, f"deuda_provincial/{nombre}", fija=True))
        partes_s.append(d.assign(anio=anio))
    for anio, nombre in sorted(servicios.items()):
        d = leer_servicios(descargar(ARCHIVOS + nombre, f"deuda_provincial/{nombre}", fija=True))
        partes_v.append(d.assign(anio=anio))
    s = pd.concat(partes_s)
    s = s.rename(columns={c: f"deuda_{c}_mill_pesos" for c in s.columns if c not in ("subdivision_iso", "anio")})
    s = s.rename(columns={"deuda_total_mill_pesos": "deuda_stock_mill_pesos"})
    v = pd.concat(partes_v)
    v = v[["subdivision_iso", "anio", "amortizacion_total", "intereses_total"]].rename(columns={
        "amortizacion_total": "servicio_deuda_amortizacion_mill_pesos",
        "intereses_total": "servicio_deuda_intereses_mill_pesos"})
    orden = ["deuda_stock_mill_pesos", "deuda_gobierno_nacional_mill_pesos", "deuda_fffir_mill_pesos",
             "deuda_ffdp_mill_pesos", "deuda_bancos_mill_pesos", "deuda_deuda_consolidada_mill_pesos",
             "deuda_bonos_mill_pesos", "deuda_organismos_internacionales_mill_pesos"]
    t = s.merge(v, on=["subdivision_iso", "anio"], how="outer")
    t = t.rename(columns={"deuda_deuda_consolidada_mill_pesos": "deuda_consolidada_mill_pesos"})
    orden = [c.replace("deuda_deuda_", "deuda_") for c in orden]
    t = t[["subdivision_iso", "anio"] + [c for c in orden if c in t] +
          ["servicio_deuda_amortizacion_mill_pesos", "servicio_deuda_intereses_mill_pesos"]]
    return guardar(t.sort_values(["subdivision_iso", "anio"]), "subdivision_deuda_anual.csv",
                   clave=("subdivision_iso", "anio"))


# Renglones del esquema Ahorro-Inversión-Financiamiento: (sección, comienzo del renglón) -> columna.
# La sección hace falta porque "Transferencias corrientes" y "Rentas de la propiedad" aparecen
# como ingreso y como gasto.
RENGLONES_AIF = {
    ("ingresos_corrientes", "I. INGRESOS CORRIENTES"): "ingresos_corrientes_mill_pesos",
    ("ingresos_corrientes", ". Tributarios"): "tributarios_mill_pesos",
    ("ingresos_corrientes", "- De Orígen Provincial"): "tributarios_origen_provincial_mill_pesos",
    ("ingresos_corrientes", "- De Orígen Nacional"): "tributarios_origen_nacional_mill_pesos",
    ("ingresos_corrientes", "- Distribución Secundaria"): "coparticipacion_neta_mill_pesos",
    ("ingresos_corrientes", ". Contribuciones a la Seguridad Social"): "contribuciones_seguridad_social_mill_pesos",
    ("ingresos_corrientes", "- Regalías"): "regalias_mill_pesos",
    ("ingresos_corrientes", ". Transferencias Corrientes"): "transferencias_corrientes_recibidas_mill_pesos",
    ("gastos_corrientes", "II. GASTOS CORRIENTES"): "gasto_corriente_mill_pesos",
    ("gastos_corrientes", "- Personal"): "gasto_personal_mill_pesos",
    ("gastos_corrientes", ". Rentas de la Propiedad"): "intereses_deuda_mill_pesos",
    ("ingresos_capital", ". Transferencias de Capital"): "transferencias_capital_recibidas_mill_pesos",
    ("gastos_capital", ". Inversión Real Directa"): "inversion_real_directa_mill_pesos",
    ("resultados", "VI. INGRESOS TOTALES"): "ingresos_totales_mill_pesos",
    ("resultados", "VII. GASTOS TOTALES"): "gasto_total_mill_pesos",
    ("resultados", "VIII. RESULTADO FINANCIERO"): "resultado_financiero_mill_pesos",
}
SECCIONES_AIF = {"I. INGRESOS CORRIENTES": "ingresos_corrientes", "II. GASTOS CORRIENTES": "gastos_corrientes",
                 "III. RESULTADO ECONOMICO": "otros", "IV. INGRESOS DE CAPITAL": "ingresos_capital",
                 "V. GASTOS DE CAPITAL": "gastos_capital", "VI. INGRESOS TOTALES": "resultados"}


def leer_hoja_aif(tabla):
    fila_anios = next(i for i, v in tabla[0].items() if str(v).strip().upper() == "CONCEPTO")
    anios = {c: int(v) for c, v in tabla.loc[fila_anios].items() if c != 0 and pd.notna(v)}
    seccion, valores = None, {}
    for i in range(fila_anios + 1, len(tabla)):
        renglon = re.sub(r"\s+", " ", str(tabla.at[i, 0])).strip()
        seccion = next((s for inicio, s in SECCIONES_AIF.items() if renglon.startswith(inicio)), seccion)
        columna = next((c for (sec, inicio), c in RENGLONES_AIF.items()
                        if sec == seccion and renglon.startswith(inicio)), None)
        if columna and columna not in valores:
            valores[columna] = {anio: pd.to_numeric(tabla.at[i, c], errors="coerce") for c, anio in anios.items()}
    faltan = set(RENGLONES_AIF.values()) - set(valores)
    assert not faltan, faltan
    return pd.DataFrame(valores).rename_axis("anio").reset_index()


def finanzas_publicas_provinciales():
    html = requests.get(PAGINA_CFP + "ejecucion-presupuestaria-provincial/ejecuciones", headers=NAVEGADOR,
                        timeout=120).text
    serie = max(re.findall(r"sites/default/files/(serie_aif-apnf-(\d{4})[^\"')\s]*\.xlsx?)", html),
                key=lambda x: int(x[1]))[0]
    hojas = pd.read_excel(descargar(ARCHIVOS + serie, f"aif_{serie}"), header=None, sheet_name=None)
    partes = []
    for hoja, tabla in hojas.items():
        d = leer_hoja_aif(tabla)
        if hoja.strip().lower() == "consolidado":
            consolidado = d
            continue
        iso = iso_provincia(hoja)
        assert iso, hoja
        partes.append(d.assign(subdivision_iso=iso))
    t = pd.concat(partes)
    assert t.subdivision_iso.nunique() == 24
    # Control: la suma de las 24 jurisdicciones tiene que dar el consolidado
    suma = t.groupby("anio").ingresos_totales_mill_pesos.sum()
    dif = (suma / consolidado.set_index("anio").ingresos_totales_mill_pesos - 1).abs().max()
    assert dif < 0.001, f"la suma de provincias difiere del consolidado en {dif:.2%}"
    print(f"   AIF {serie}: suma de provincias = consolidado (diferencia máxima {dif:.4%})")
    t = t[["subdivision_iso", "anio"] + list(RENGLONES_AIF.values())]
    return guardar(t.sort_values(["subdivision_iso", "anio"]), "subdivision_finanzas_publicas_anual.csv",
                   clave=("subdivision_iso", "anio"))


# ---------------------------------------------------------------------------
# 7. Subdivisiones: emisiones (OCDE) e internet (ENACOM)
# ---------------------------------------------------------------------------
MEDIDAS_GHG = {  # medida de la OCDE -> columna; en toneladas de CO2 equivalente
    "GHG_REG_TOTAL": "emisiones_gei_total_tco2e", "GHG_POWER": "emisiones_gei_electricidad_tco2e",
    "GHG_INDUSTRY": "emisiones_gei_industria_tco2e", "GHG_TRANSPORT": "emisiones_gei_transporte_tco2e",
    "GHG_BUILDINGS": "emisiones_gei_edificios_tco2e", "GHG_AGRICULTURE": "emisiones_gei_agro_tco2e",
    "GHG_WASTE": "emisiones_gei_residuos_tco2e",
}


def emisiones_subdivisiones():
    from extraer_latam_subnacional import regiones_ocde  # noqa: E402 (TL2 de la OCDE -> ISO 3166-2)
    regiones = regiones_ocde()
    clave = "A.TL2." + "+".join(sorted(regiones.REF_AREA)) + "." * 7
    ruta = descargar(f"https://sdmx.oecd.org/public/rest/data/OECD.CFE.EDS,DSD_REG_CLIM@DF_GHG,2.4/{clave}"
                     f"?startPeriod={ANIO_INICIO}&format=csvfilewithlabels", "ocde_emisiones_regionales.csv")
    d = pd.read_csv(ruta, low_memory=False)
    d = d[d.MEASURE.isin(MEDIDAS_GHG)]
    d["subdivision_iso"] = d.REF_AREA.map(dict(zip(regiones.REF_AREA, regiones.subdivision_iso)))
    total = d[d.UNIT_MEASURE == "T_CO2E"].assign(variable=lambda x: x.MEASURE.map(MEDIDAS_GHG))
    pc = d[(d.UNIT_MEASURE == "T_CO2E_PS") & (d.MEASURE == "GHG_REG_TOTAL")].assign(
        variable="emisiones_gei_per_capita_tco2e")
    largo = pd.concat([total, pc]).rename(columns={"TIME_PERIOD": "anio", "OBS_VALUE": "valor"})
    t = ancho(largo, ["emisiones_gei_per_capita_tco2e"] + list(MEDIDAS_GHG.values()),
              clave=("subdivision_iso", "anio"))
    return guardar(t, "subdivision_emisiones_anual.csv", clave=("subdivision_iso", "anio"))


def internet_provincias():
    bundle = CRUDOS / "ca_enacom.pem"
    base = os.environ.get("REQUESTS_CA_BUNDLE") or requests.certs.where()  # en la nube, el del proxy
    bundle.write_text(Path(base).read_text() + SECTIGO.read_text())
    ruta = descargar("https://indicadores.enacom.gob.ar/Files/DatosAbiertos/internet_accesos_penetracion_provincias.csv",
                     "enacom_internet_penetracion_provincias.csv", verify=str(bundle))
    d = pd.read_csv(ruta)
    d["subdivision_iso"] = d.provincia.map(iso_provincia)
    assert d.subdivision_iso.notna().all(), set(d[d.subdivision_iso.isna()].provincia)
    # dato anual = último trimestre publicado del año (el 4.º en los años cerrados)
    ultimo = d.sort_values("trimestre").groupby(["subdivision_iso", "anio"]).tail(1)
    t = ultimo.rename(columns={"accesos_cada_100_hogares": "internet_fijo_accesos_x100_hogares",
                               "accesos_cada_100_habitantes": "internet_fijo_accesos_x100_hab",
                               "trimestre": "internet_fijo_trimestre"})
    t = t[["subdivision_iso", "anio", "internet_fijo_accesos_x100_hogares", "internet_fijo_accesos_x100_hab",
           "internet_fijo_trimestre"]]
    return guardar(t.sort_values(["subdivision_iso", "anio"]), "subdivision_internet_anual.csv",
                   clave=("subdivision_iso", "anio"))


PASOS = {
    "migracion": migracion, "emisiones": emisiones_energia, "capital_social": capital_social,
    "indigena": poblacion_indigena, "constituciones": diversidad_cultural, "gobernanza": gobernanza,
    "deuda": financiero_deuda, "salud": salud_cronica, "tecnologia": tecnologia,
    "deuda_provincial": deuda_provincial, "aif": finanzas_publicas_provinciales,
    "emisiones_subdivisiones": emisiones_subdivisiones, "internet_provincias": internet_provincias,
}


def main():
    """Sin argumentos corre todo; con nombres de pasos (p. ej. `aif deuda`) corre solo esos."""
    CRUDOS.mkdir(exist_ok=True)
    pedidos = sys.argv[1:] or list(PASOS)
    for nombre in pedidos:
        print(f"== {nombre}")
        PASOS[nombre]()


if __name__ == "__main__":
    main()
