"""
Gráfico de progreso en el tiempo: prepara los datos y arma la página.

Lee las tablas ya procesadas del ETL (no descarga nada) y genera:
  - datos_progreso.json: series anuales por nivel (países, provincias argentinas,
    subdivisiones de Latinoamérica), indicador y entidad.
  - progreso_en_el_tiempo.html: la página interactiva, que es plantilla_progreso.html
    con el JSON incrustado (se abre sin servidor y se publica tal cual).

Uso (desde la carpeta etl/):
    python graficos_progreso/preparar_datos_progreso.py

Correrlo después de actualizar cualquiera de las tablas de origen.
Ver GUIA_GRAFICO_PROGRESO.md.
"""

import json
import math
from datetime import date
from pathlib import Path

import pandas as pd

CARPETA = Path(__file__).resolve().parent
ETL = CARPETA.parent
ANIO_ACTUAL = date.today().year

# Para los flujos (producción, pernoctes) el año en curso todavía no terminó:
# se descarta para no comparar 8 meses contra 12.
ULTIMO_ANIO_COMPLETO = ANIO_ACTUAL - 1


def leer(ruta, **kw):
    # keep_default_na=False evita que Namibia ("NA") se lea como vacío.
    return pd.read_csv(ETL / ruta, keep_default_na=False, na_values=[""], **kw)


# ---------------------------------------------------------------------------
# Catálogo de indicadores
# mejor: "alto" (más es mejor), "bajo" (menos es mejor) o None (sin juicio:
#        población, temperatura, producción, gasto...).
# cambio: "pct" = cambio relativo en %, "pts" = diferencia en la unidad
#         (se usa para porcentajes, años, °C, índices acotados).
# ---------------------------------------------------------------------------
def ind(id_, nombre, unidad, fuente, mejor, cambio, dec=1, nota=""):
    return dict(id=id_, nombre=nombre, unidad=unidad, fuente=fuente,
                mejor=mejor, cambio=cambio, dec=dec, nota=nota)


IND_PAISES = [
    ind("pib_pc_ppp", "PIB per cápita", "US$ PPA internacionales", "Banco Mundial", "alto", "pct", 0),
    ind("esperanza_vida", "Esperanza de vida al nacer", "años", "Banco Mundial", "alto", "pts", 1),
    ind("mortalidad_infantil", "Mortalidad infantil", "por 1.000 nacidos vivos", "Banco Mundial", "bajo", "pct", 1),
    ind("medicos_x1000", "Médicos", "por 1.000 habitantes", "Banco Mundial / OMS", "alto", "pct", 2),
    ind("camas_hospital_x1000", "Camas de hospital", "por 1.000 habitantes", "Banco Mundial / OMS", "alto", "pct", 2),
    ind("suicidio_total_x100k", "Tasa de suicidio", "por 100.000 habitantes", "Banco Mundial / OMS", "bajo", "pct", 1,
        "Llega hasta 2021."),
    ind("gasto_salud_pct_pib", "Gasto en salud", "% del PIB", "Banco Mundial / OMS", None, "pts", 1),
    ind("gasto_educacion_pct_pib", "Gasto público en educación", "% del PIB", "Banco Mundial / UNESCO", None, "pts", 1),
    ind("gini", "Desigualdad (Gini)", "0 a 100", "Banco Mundial", "bajo", "pts", 1,
        "Sale de encuestas de hogares: muchos países no tienen dato todos los años."),
    ind("ratio_palma", "Ratio de Palma", "veces", "Cálculo propio con datos del Banco Mundial", "bajo", "pts", 2,
        "Ingreso del 10 % más rico dividido por el del 40 % más pobre."),
    ind("pct_no_puede_pagar_dieta_saludable", "Población que no puede pagar una dieta saludable", "% de la población",
        "Banco Mundial, Food Prices for Nutrition", "bajo", "pts", 1),
    ind("salario_promedio_mensual_ppa", "Salario promedio mensual", "US$ PPA de 2021", "OIT (ILOSTAT)", "alto", "pct", 0),
    ind("felicidad", "Felicidad (evaluación de vida)", "0 a 10", "World Happiness Report 2025", "alto", "pts", 2,
        "Promedio de 3 años; el año es el último del trienio."),
    ind("poblacion", "Población", "habitantes", "Banco Mundial", None, "pct", 0),
]

IND_PROVINCIAS = [
    ind("pbg_per_capita_pesos_2004", "PBG per cápita", "pesos de 2004", "Argendata / CEPAL", "alto", "pct", 0),
    ind("salario_real", "Salario privado registrado", "pesos de 2024 por mes", "OEDE, Ministerio de Trabajo", "alto", "pct", 0,
        "Asalariados privados registrados (SIPA). No incluye empleo público ni informal."),
    ind("pobreza", "Pobreza", "% de personas", "Cálculo propio con microdatos EPH (INDEC)", "bajo", "pts", 1,
        "Solo aglomerados urbanos de la EPH, no la provincia entera."),
    ind("indigencia", "Indigencia", "% de personas", "Cálculo propio con microdatos EPH (INDEC)", "bajo", "pts", 1,
        "Solo aglomerados urbanos de la EPH, no la provincia entera."),
    ind("gini_eph", "Desigualdad (Gini, grandes ciudades)", "0 a 1", "Cálculo propio con microdatos EPH (INDEC)", "bajo", "pts", 3),
    ind("medicos_cada_10000_hab", "Médicos", "por 10.000 habitantes", "Ministerio de Salud", "alto", "pct", 1),
    ind("vacuna_srp", "Vacuna triple viral (1.ª dosis)", "% de cobertura", "Ministerio de Salud", "alto", "pts", 1,
        "Puede superar 100 % por diferencias entre padrón y población estimada."),
    ind("empresas_cada_1000_hab", "Empresas con empleados", "cada 1.000 habitantes", "OEDE, Ministerio de Trabajo", "alto", "pct", 1),
    ind("presion_tributaria_pct_pbg_estimado", "Presión tributaria provincial", "% del PBG (estimado)", "DNAP, Ministerio de Economía", None, "pts", 1),
    ind("pct_vab_sector_publico", "Peso del sector público", "% del valor agregado", "CEPAL", None, "pts", 1),
    ind("pct_vab_turismo", "Peso del turismo (hoteles y restaurantes)", "% del valor agregado", "CEPAL", None, "pts", 1),
    ind("agua_de_red", "Hogares con agua de red", "% de hogares", "Censos 2010 y 2022 (INDEC)", "alto", "pts", 1,
        "Solo dos puntos: censos 2010 y 2022."),
    ind("cloaca", "Hogares con cloaca", "% de hogares", "Censos 2010 y 2022 (INDEC)", "alto", "pts", 1,
        "Solo dos puntos: censos 2010 y 2022."),
    ind("nbi", "Hogares con necesidades básicas insatisfechas", "% de hogares", "Censos 2010 y 2022 (INDEC)", "bajo", "pts", 1,
        "Solo dos puntos: censos 2010 y 2022."),
    ind("petroleo_m3", "Producción de petróleo", "m³ por año", "Secretaría de Energía", None, "pct", 0),
    ind("gas_miles_m3", "Producción de gas", "miles de m³ por año", "Secretaría de Energía", None, "pct", 0),
    ind("soja_tn", "Producción de soja", "toneladas (año de cosecha)", "MAGyP", None, "pct", 0),
    ind("maiz_tn", "Producción de maíz", "toneladas (año de cosecha)", "MAGyP", None, "pct", 0),
    ind("trigo_tn", "Producción de trigo", "toneladas (año de cosecha)", "MAGyP", None, "pct", 0),
    ind("bovinos", "Stock bovino", "cabezas al 31 de diciembre", "MAGyP / SENASA", None, "pct", 0),
    ind("pernoctes", "Pernoctes en hoteles", "noches por año", "EOH (INDEC)", None, "pct", 0,
        "Suma de las localidades relevadas: es un piso, no el total provincial."),
    ind("temperatura", "Temperatura media anual", "°C", "Banco Mundial (CCKP, ERA5)", None, "pts", 2),
    ind("habitantes", "Población", "habitantes", "INDEC (proyecciones base Censo 2010)", None, "pct", 0),
]

IND_LATAM = [
    ind("pib_pc_usd_ppa_constante", "PIB per cápita", "US$ PPA constantes", "OCDE (regiones)", "alto", "pct", 0,
        "Brasil, Chile, Colombia, México y Perú."),
    ind("esperanza_vida_anios", "Esperanza de vida al nacer", "años", "OCDE (regiones)", "alto", "pts", 1),
    ind("mortalidad_infantil_x1000", "Mortalidad infantil", "por 1.000 nacidos vivos", "OCDE (regiones)", "bajo", "pct", 1),
    ind("tasa_desempleo_pct", "Desempleo", "% de la población activa", "OCDE (regiones)", "bajo", "pts", 1),
    ind("homicidios_x100mil", "Homicidios", "por 100.000 habitantes", "OCDE (regiones)", "bajo", "pct", 1),
    ind("medicos_x1000", "Médicos", "por 1.000 habitantes", "OCDE (regiones)", "alto", "pct", 2),
    ind("pct_25_64_con_terciaria", "Adultos con educación terciaria", "% de 25 a 64 años", "OCDE (regiones)", "alto", "pts", 1),
    ind("temperatura", "Temperatura media anual", "°C", "Banco Mundial (CCKP) y OCDE", None, "pts", 2),
    ind("bovinos", "Stock bovino", "cabezas", "MAGyP (ARG), IBGE (BRA), ICA (COL)", None, "pct", 0),
    ind("soja_tn", "Producción de soja", "toneladas", "MAGyP (ARG), IBGE (BRA), EVA (COL)", None, "pct", 0),
    ind("maiz_tn", "Producción de maíz", "toneladas", "MAGyP (ARG), IBGE (BRA), EVA (COL)", None, "pct", 0),
    ind("petroleo_m3", "Producción de petróleo", "m³ por año", "Energía (ARG), ANP (BRA), ANH (COL)", None, "pct", 0),
    ind("poblacion", "Población", "habitantes", "OCDE (regiones)", None, "pct", 0),
]


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def a_series(df, col_ent, col_anio, col_valor):
    """Tabla larga -> {entidad: {"a0": primer año, "v": [valores con None]}}."""
    d = df[[col_ent, col_anio, col_valor]].dropna()
    d = d[d[col_valor].map(lambda x: isinstance(x, (int, float)) and math.isfinite(x))]
    if d.duplicated([col_ent, col_anio]).any():
        dup = d[d.duplicated([col_ent, col_anio], keep=False)].head()
        raise ValueError(f"Valores repetidos para {col_valor}:\n{dup}")
    out = {}
    for ent, g in d.groupby(col_ent):
        g = g.sort_values(col_anio)
        a0, a1 = int(g[col_anio].min()), int(g[col_anio].max())
        vals = [None] * (a1 - a0 + 1)
        for a, v in zip(g[col_anio], g[col_valor]):
            vals[int(a) - a0] = round(float(v), 4) if abs(v) < 1e6 else round(float(v))
        out[str(ent)] = {"a0": a0, "v": vals}
    return out


def armar_nivel(nombre, descripcion, entidades, indicadores, tablas, defecto):
    datos = {}
    for i in indicadores:
        df, col_ent, col_anio, col_val = tablas[i["id"]]
        datos[i["id"]] = a_series(df, col_ent, col_anio, col_val)
    usadas = {e for serie in datos.values() for e in serie}
    entidades = {k: v for k, v in entidades.items() if k in usadas}
    for i in indicadores:
        anios = [s["a0"] + len(s["v"]) - 1 for s in datos[i["id"]].values()] + \
                [s["a0"] for s in datos[i["id"]].values()]
        i["anios"] = [min(anios), max(anios)]
        i["n_entidades"] = len(datos[i["id"]])
    for e in defecto["entidades"]:
        assert e in entidades, f"Entidad por defecto sin datos: {e}"
    return dict(nombre=nombre, descripcion=descripcion, entidades=entidades,
                indicadores=indicadores, datos=datos, defecto=defecto)


# ---------------------------------------------------------------------------
# Nivel 1: países
# ---------------------------------------------------------------------------
def nivel_paises():
    panel = leer("datos_procesados/paises_anual.csv")
    maestro = leer("maestros/paises_maestro.csv").set_index("iso3")
    entidades = {}
    for iso3 in panel.iso3.unique():
        fila = maestro.loc[iso3]
        entidades[iso3] = {"n": fila.nombre_es, "g": fila.region_bm_es}
    tablas = {i["id"]: (panel, "iso3", "anio", i["id"]) for i in IND_PAISES}
    return armar_nivel(
        "Países", "217 países del panel del Banco Mundial",
        entidades, IND_PAISES, tablas,
        dict(indicador="pib_pc_ppp", entidades=["ARG", "BRA", "CHL", "URY", "MEX", "ESP"],
             modo="indice", desde=2000, hasta=2024))


# ---------------------------------------------------------------------------
# Nivel 2: provincias argentinas (+ total país donde se puede sumar)
# ---------------------------------------------------------------------------
TOTAL_ARG = "AR-TOTAL"


def con_total(df, col_valor, como="suma", peso=None, numerador=None, denominador=None, factor=1.0):
    """Agrega una fila 'AR-TOTAL' por año.

    suma: suma de provincias (solo años con las 24 o las que reportan; en flujos
    las provincias sin producción simplemente no aparecen).
    cociente: sum(numerador) / sum(denominador) * factor.
    ponderado: promedio de col_valor ponderado por la columna peso.
    """
    d = df.copy()
    if como == "suma":
        tot = d.groupby("anio")[col_valor].sum(min_count=1).reset_index()
    elif como == "cociente":
        g = d.dropna(subset=[numerador, denominador]).groupby("anio")
        n = g.size()
        tot = (g[numerador].sum() / g[denominador].sum() * factor).rename(col_valor)
        tot = tot[n >= 24].reset_index()  # solo años con todas las provincias
    elif como == "ponderado":
        g = d.dropna(subset=[col_valor, peso])
        g = g.assign(_p=g[col_valor] * g[peso]).groupby("anio")
        n = g.size()
        tot = (g["_p"].sum() / g[peso].sum()).rename(col_valor)
        tot = tot[n >= 24].reset_index()
    tot["provincia_iso"] = TOTAL_ARG
    return pd.concat([d[["provincia_iso", "anio", col_valor]], tot[["provincia_iso", "anio", col_valor]]])


def nivel_provincias():
    P = "argentina_provincias/"
    indic = leer(P + "indicadores_provincia_anual.csv")
    pobl = leer(P + "poblacion_provincia_anual.csv")
    pobl = pobl[pobl.anio <= ULTIMO_ANIO_COMPLETO + 1]  # proyecciones: no ir al futuro
    sal = leer(P + "salarios_provincia_anual.csv")
    pob = leer(P + "pobreza_gini_provincia_anual.csv")
    pob = pob[pob.trimestres_con_dato >= 3]  # un solo trimestre es muy ruidoso
    salud = leer(P + "salud_provincia_anual.csv")
    emp = leer(P + "empresas_con_empleados_provincia_anual.csv")
    imp = leer(P + "carga_impositiva_provincia_anual.csv")
    censo = leer(P + "censo_vivienda_servicios_educacion.csv").rename(columns={"anio_censo": "anio"})
    petro = leer(P + "petroleo_gas_provincia_anual.csv")
    petro = petro[(petro.meses_con_dato >= 12) & (petro.anio <= ULTIMO_ANIO_COMPLETO)]
    petro = petro[petro.provincia_iso.str.startswith("AR-") & (petro.provincia_iso != "AR-offshore")]
    agro = leer(P + "agricultura_provincia_anual.csv")
    agro = agro[agro.anio_cosecha <= ANIO_ACTUAL].rename(columns={"anio_cosecha": "anio"})
    bov = leer(P + "ganaderia_bovinos_provincia_anual.csv")
    tur = leer(P + "turismo_hoteles_provincia_anual.csv")
    tur = tur[(tur.meses_con_dato >= 12) & (tur.anio <= ULTIMO_ANIO_COMPLETO)]
    temp = leer(P + "temperatura_provincia_anual.csv")

    def cultivo(nombre, col):
        d = agro[agro.cultivo == nombre][["provincia_iso", "anio", "produccion_tn"]].rename(columns={"produccion_tn": col})
        return con_total(d, col)

    # Médicos y empresas por habitante para el total país: con población INDEC.
    med = salud.merge(pobl[["provincia_iso", "anio", "habitantes"]], on=["provincia_iso", "anio"], how="left")
    emp2 = emp.merge(pobl[["provincia_iso", "anio", "habitantes"]], on=["provincia_iso", "anio"], how="left")
    cen = censo.assign(
        n_agua=censo.pct_hogares_agua_de_red * censo.hogares,
        n_cloaca=censo.pct_hogares_cloaca * censo.hogares,
        n_nbi=censo.pct_hogares_con_nbi * censo.hogares)

    T = {}
    T["pbg_per_capita_pesos_2004"] = con_total(
        indic.assign(_vab=indic.vab_total_mill_pesos_2004 * 1e6), "pbg_per_capita_pesos_2004",
        "cociente", numerador="_vab", denominador="poblacion")
    T["salario_real"] = con_total(
        sal.rename(columns={"salario_promedio_mensual_pesos_2024": "salario_real"}), "salario_real",
        "ponderado", peso="puestos_asalariados_privados_registrados")
    T["pobreza"] = pob.rename(columns={"pct_personas_pobres_estimado": "pobreza"})
    T["indigencia"] = pob.rename(columns={"pct_personas_indigentes_estimado": "indigencia"})
    T["gini_eph"] = pob.rename(columns={"gini_ingreso_per_capita_familiar_estimado_grandes_ciudades": "gini_eph"})
    T["medicos_cada_10000_hab"] = con_total(med, "medicos_cada_10000_hab", "cociente",
                                            numerador="medicos", denominador="habitantes", factor=1e4)
    T["vacuna_srp"] = salud.rename(columns={"pct_vacuna_srp_1ra_dosis_12_meses": "vacuna_srp"})
    T["empresas_cada_1000_hab"] = con_total(emp2, "empresas_cada_1000_hab", "cociente",
                                            numerador="empresas_con_empleados", denominador="habitantes", factor=1e3)
    T["presion_tributaria_pct_pbg_estimado"] = imp
    T["pct_vab_sector_publico"] = indic
    T["pct_vab_turismo"] = indic
    T["agua_de_red"] = con_total(cen.rename(columns={"pct_hogares_agua_de_red": "agua_de_red"}), "agua_de_red",
                                 "cociente", numerador="n_agua", denominador="hogares")
    T["cloaca"] = con_total(cen.rename(columns={"pct_hogares_cloaca": "cloaca"}), "cloaca",
                            "cociente", numerador="n_cloaca", denominador="hogares")
    T["nbi"] = con_total(cen.rename(columns={"pct_hogares_con_nbi": "nbi"}), "nbi",
                         "cociente", numerador="n_nbi", denominador="hogares")
    T["petroleo_m3"] = con_total(petro.rename(columns={"petroleo_m3_total": "petroleo_m3"}), "petroleo_m3")
    T["gas_miles_m3"] = con_total(petro.rename(columns={"gas_miles_m3_total": "gas_miles_m3"}), "gas_miles_m3")
    T["soja_tn"] = cultivo("Soja total", "soja_tn")
    T["maiz_tn"] = cultivo("Maíz", "maiz_tn")
    T["trigo_tn"] = cultivo("Trigo total", "trigo_tn")
    T["bovinos"] = con_total(bov.rename(columns={"total_cabezas": "bovinos"}), "bovinos")
    T["pernoctes"] = con_total(tur.rename(columns={"pernoctes_total": "pernoctes"}), "pernoctes")
    T["temperatura"] = temp.rename(columns={"temperatura_media_c": "temperatura"})
    T["habitantes"] = con_total(pobl, "habitantes")
    tablas = {k: (v, "provincia_iso", "anio", k) for k, v in T.items()}

    entidades = {r.provincia_iso: {"n": r.provincia, "g": "Provincia"}
                 for r in indic.drop_duplicates("provincia_iso").itertuples()}
    entidades[TOTAL_ARG] = {"n": "Argentina (total país)", "g": "Total"}
    return armar_nivel(
        "Provincias argentinas", "24 jurisdicciones; el total país se calcula donde se puede sumar o ponderar",
        entidades, IND_PROVINCIAS, tablas,
        dict(indicador="pbg_per_capita_pesos_2004",
             entidades=[TOTAL_ARG, "AR-C", "AR-B", "AR-X", "AR-S", "AR-M", "AR-Q", "AR-A"],
             modo="valor", desde=2004, hasta=2023))


# ---------------------------------------------------------------------------
# Nivel 3: subdivisiones de Latinoamérica
# Las tablas comunes (temperatura, agro, ganadería, petróleo) ya traen a
# Argentina: aquí se usan tal cual, sin sumar además argentina_provincias/,
# para no duplicar provincias.
# ---------------------------------------------------------------------------
def nivel_latam():
    L = "latam_subnacional/"
    ocde = leer(L + "indicadores_ocde_subdivision_anual.csv")
    temp = leer(L + "temperatura_subdivision_anual.csv")
    agro = leer(L + "agricultura_subdivision_anual.csv")
    agro = agro[agro.anio <= ANIO_ACTUAL]
    gan = leer(L + "ganaderia_subdivision_anual.csv")
    pet = leer(L + "petroleo_gas_subdivision_anual.csv")
    pet = pet[(pet.anio <= ULTIMO_ANIO_COMPLETO) & ((pet.meses_con_dato.isna()) | (pet.meses_con_dato >= 12))]
    maestro_sub = leer("maestros/subdivisiones_maestro.csv").set_index("subdivision_iso")
    maestro_pais = leer("maestros/paises_maestro.csv").set_index("iso3")

    T = {}
    for c in ["pib_pc_usd_ppa_constante", "esperanza_vida_anios", "mortalidad_infantil_x1000", "tasa_desempleo_pct",
              "homicidios_x100mil", "medicos_x1000", "pct_25_64_con_terciaria", "poblacion"]:
        T[c] = ocde
    T["temperatura"] = temp.rename(columns={"temperatura_media_c": "temperatura"})
    T["bovinos"] = gan[gan.especie == "Bovinos"].rename(columns={"cabezas": "bovinos"})
    T["soja_tn"] = agro[agro.cultivo == "Soja"].rename(columns={"produccion": "soja_tn"})
    T["maiz_tn"] = agro[agro.cultivo == "Maíz"].rename(columns={"produccion": "maiz_tn"})
    T["petroleo_m3"] = pet
    tablas = {k: (v, "subdivision_iso", "anio", k) for k, v in T.items()}

    codigos = set()
    for df in T.values():
        codigos |= set(df.subdivision_iso.dropna())
    entidades = {}
    for cod in sorted(codigos):
        sub = maestro_sub.loc[cod]
        entidades[cod] = {"n": sub.nombre, "g": maestro_pais.loc[sub.iso3].nombre_es}
    return armar_nivel(
        "Subdivisiones de Latinoamérica", "Estados, provincias, departamentos y regiones de 20 países (ISO 3166-2)",
        entidades, IND_LATAM, tablas,
        dict(indicador="pib_pc_usd_ppa_constante",
             entidades=["CL-RM", "BR-SP", "MX-CMX", "CO-DC", "PE-LIM", "MX-NLE", "BR-MA"],
             modo="indice", desde=2008, hasta=2023))


def main():
    salida = {
        "generado": date.today().isoformat(),
        "niveles": {
            "paises": nivel_paises(),
            "provincias": nivel_provincias(),
            "latam": nivel_latam(),
        },
    }
    texto = json.dumps(salida, ensure_ascii=False, separators=(",", ":"))
    (CARPETA / "datos_progreso.json").write_text(texto, encoding="utf-8")

    plantilla = (CARPETA / "plantilla_progreso.html").read_text(encoding="utf-8")
    marca = "/*__DATOS__*/null"
    assert marca in plantilla, "La plantilla no tiene la marca de datos"
    # "</" se escapa para que el JSON no pueda cerrar la etiqueta <script>.
    html = plantilla.replace(marca, texto.replace("</", "<\\/"))
    (CARPETA / "progreso_en_el_tiempo.html").write_text(html, encoding="utf-8")

    for clave, n in salida["niveles"].items():
        print(f"{clave}: {len(n['entidades'])} entidades, {len(n['indicadores'])} indicadores")
        for i in n["indicadores"]:
            print(f"   {i['id']:<40} {i['anios'][0]}-{i['anios'][1]}  {i['n_entidades']} entidades")
    print(f"JSON: {len(texto) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
