"""
ARGENTINA POR PROVINCIA: actividad económica por provincia y año, con fuentes oficiales.

Cuatro fuentes, cuatro preguntas distintas:

  1. ¿Cuánto vale cada actividad en cada provincia?  (dinero)
     CEPAL + Ministerio de Economía, "Desagregación provincial del valor agregado
     bruto de la Argentina, base 2004". Excel con 52 ramas de actividad para las
     24 jurisdicciones, 2004-2024, en millones de pesos a precios de 2004.
     (2023 es dato provisorio y 2024 preliminar.)

  2. ¿Cuánto petróleo y gas sale de cada provincia?  (cantidades físicas)
     Secretaría de Energía, "Producción de Petróleo y Gas (SESCO + Capítulo IV)".
     Mensual desde 2009, en m³ de petróleo y miles de m³ de gas.

  3. ¿Cuánto se siembra y cosecha en cada provincia?  (cantidades físicas)
     Ministerio de Agricultura (MAGyP), "Estimaciones agrícolas". Por departamento
     y campaña desde 1969/70: hectáreas sembradas y cosechadas, toneladas.

  4. ¿Cuánto ganado hay en cada provincia?  (cantidades físicas)
     Ministerio de Agricultura con datos de SENASA, "Serie stock bovino por provincia
     al 31-12 (2007-2025)": cabezas de ganado bovino por categoría (vacas, novillos...).

Qué genera (en esta carpeta):
  vab_provincia_sector_largo.csv     una fila por provincia + año + rama (52 ramas)
  vab_provincia_grupos_largo.csv     lo mismo agrupado en 8 grupos (Agro, Petróleo y gas,
                                     Minería, Industria, Servicios...)
  petroleo_gas_provincia_anual.csv   una fila por provincia + año
  agricultura_provincia_anual.csv    una fila por provincia + campaña + cultivo
  ganaderia_bovinos_provincia_anual.csv  una fila por provincia + año (stock al 31 de diciembre)
  indicadores_provincia_anual.csv    una fila por provincia + año: PBG per cápita, población,
                                     % del VAB que genera el Estado y % que generan hoteles y restaurantes
  censo_vivienda_servicios_educacion.csv  una fila por provincia + censo (2010 y 2022)
  turismo_hoteles_provincia_anual.csv     una fila por provincia + año: viajeros y noches en hoteles
  temperatura_provincia_anual.csv         una fila por provincia + año: temperatura media (°C)
  poblacion_provincia_anual.csv           una fila por provincia + año: habitantes (proyección INDEC)
  gobernadores_elecciones.csv             una fila por elección a gobernador (1983-2025)
  gobierno_provincial_anual.csv           una fila por provincia + año: familia política del gobierno
  legisladores_nacionales_provincia_anual.csv  una fila por provincia + año + cámara: bancas por familia
  salud_provincia_anual.csv               una fila por provincia + año: vacuna triple viral y médicos
  pymes_provincia.csv                     una fila por provincia: pymes con certificado vigente (dic. 2024)
  empresas_con_empleados_provincia_anual.csv  una fila por provincia + año: empresas con empleados (1996-2024)
  carga_impositiva_provincia_anual.csv    una fila por provincia + año: recaudación propia, % del PBG, por habitante
  alicuotas_ingresos_brutos_provincia.csv una fila por provincia + año + actividad: alícuota de Ingresos Brutos
  salarios_provincia_anual.csv            una fila por provincia + año: salario promedio de asalariados registrados
  canastas_provincia_anual.csv            una fila por provincia + año: CBA y CBT estimadas (valor de su región)
  pobreza_gini_provincia_anual.csv        una fila por provincia + año: pobreza, indigencia y Gini estimados (EPH, grandes ciudades)
  festivales_provincia.csv                una fila por provincia: fiestas y festivales por tipo (foto 2019-2023)
  festivales_lista.csv                    una fila por fiesta o festival, con provincia y ubicación

Los archivos originales quedan en crudos/. Si un archivo ya está ahí, no se vuelve a
descargar (borralo para forzar la descarga de la versión más nueva).

Cómo ejecutarlo (desde la carpeta etl/):
    pip install -r requirements.txt
    python argentina_provincias/extraer_argentina_provincias.py
"""

import os
from pathlib import Path

import pandas as pd
import requests

CARPETA = Path(__file__).resolve().parent
CRUDOS = CARPETA / "crudos"
# Con ETL_REFRESCAR=1 (lo pone actualizar_mensual.py) se vuelven a bajar las fuentes que se
# actualizan; si una descarga falla, se sigue con la copia anterior y se avisa con AVISO_FUENTE.
REFRESCAR = os.environ.get("ETL_REFRESCAR") == "1"

URL_CEPAL = ("https://repositorio.cepal.org/server/api/core/bitstreams/"
             "539fcce5-8977-4061-a222-fbfd7358a35f/content")
URL_ENERGIA = "http://datos.energia.gob.ar/dataset/590d1284-fd6d-4686-afd8-b3da5d90a6e9/resource/"
URL_PETROLEO = URL_ENERGIA + ("86270da2-6292-4719-b7c1-20671ff9ae40/download/"
                              "produccin-petrleo-sesco-tight-y-shale-captulo-iv-por-provincia.csv")
URL_GAS = URL_ENERGIA + ("ad1b9472-a370-47e7-8de3-b742495ec7f1/download/"
                         "produccin-gas-sesco-tight-y-shale-captulo-iv-por-provincia.csv")
URL_MAGYP = "https://datosestimaciones.magyp.gob.ar/reportes.php?reporte=Estimaciones"
URL_BOVINOS = ("https://www.magyp.gob.ar/sitio/areas/bovinos/informacion_interes/informes/_archivos/"
               "000001=Series%20de%20stock%20bovino%20y%20mapas/000000_Stock/"
               "251231_Serie%20stock%20Bovino%20por%20provincia%20al%2031-12%20(2007-2025).xlsx")

# Nombre "limpio" de cada provincia -> código ISO 3166-2 (la clave para unir tablas)
PROVINCIAS = {
    "Ciudad de Buenos Aires": "AR-C", "Buenos Aires": "AR-B", "Catamarca": "AR-K",
    "Córdoba": "AR-X", "Corrientes": "AR-W", "Chaco": "AR-H", "Chubut": "AR-U",
    "Entre Ríos": "AR-E", "Formosa": "AR-P", "Jujuy": "AR-Y", "La Pampa": "AR-L",
    "La Rioja": "AR-F", "Mendoza": "AR-M", "Misiones": "AR-N", "Neuquén": "AR-Q",
    "Río Negro": "AR-R", "Salta": "AR-A", "San Juan": "AR-J", "San Luis": "AR-D",
    "Santa Cruz": "AR-Z", "Santa Fe": "AR-S", "Santiago del Estero": "AR-G",
    "Tucumán": "AR-T", "Tierra del Fuego": "AR-V",
}
# Cada fuente escribe los nombres a su manera (mayúsculas, sin tildes...).
# Comparamos sin tildes y en minúscula para encontrar el nombre limpio.
SIN_TILDES = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")


def nombre_limpio(nombre):
    clave = str(nombre).strip().translate(SIN_TILDES).lower().replace("_", " ")
    if clave in ("caba", "ciudad autonoma de buenos aires", "ciudad autonoma buenos aires",
                 "capital federal"):
        return "Ciudad de Buenos Aires"
    if clave.startswith("tierra del fuego"):  # "Tierra del Fuego, Antártida e Islas del Atlántico Sur"
        return "Tierra del Fuego"
    for limpio in PROVINCIAS:
        if limpio.translate(SIN_TILDES).lower() == clave:
            return limpio
    return nombre  # p. ej. "Estado Nacional" (producción en el mar)


# Las 52 ramas de CEPAL, en orden, agrupadas para el análisis
def grupo_de_rama(n):
    if n in (1, 2):
        return "Agro (agricultura, ganadería y silvicultura)"
    if n == 3:
        return "Pesca"
    if n == 4:
        return "Petróleo y gas"
    if n == 5:
        return "Minería"
    if 6 <= n <= 29:
        return "Industria"
    if 30 <= n <= 32:
        return "Electricidad, gas y agua"
    if n == 33:
        return "Construcción"
    return "Servicios"  # ramas 34 a 52: comercio, transporte, finanzas, salud...


def descargar(url, archivo, metodo="get", datos=None, fija=False):
    """fija=True: datos históricos que no cambian, no se vuelven a bajar ni con ETL_REFRESCAR."""
    destino = CRUDOS / archivo
    if destino.exists() and (fija or not REFRESCAR):
        print(f"  ya existe {archivo}, no se descarga")
        return destino
    print(f"  descargando {archivo} ...")
    try:
        r = requests.request(metodo, url, data=datos, timeout=300)
        r.raise_for_status()
    except requests.RequestException as error:
        if not destino.exists():
            raise
        print(f"  AVISO_FUENTE {archivo}: falló la descarga ({error}); se usa la copia anterior")
        return destino
    destino.write_bytes(r.content)
    return destino


# ---------------------------------------------------------------------------
# 1. VAB por provincia y rama (CEPAL)
# ---------------------------------------------------------------------------
def procesar_vab():
    xlsx = descargar(URL_CEPAL, "cepal_Jurisdiccion_52sectores.xlsx")
    hojas = pd.read_excel(xlsx, sheet_name=None, header=None)
    filas = []
    for hoja, tabla in hojas.items():
        if hoja in ("VABpb", "No_distribuido"):
            continue  # VABpb es el resumen; "No distribuido" no es una provincia
        provincia = nombre_limpio(tabla.iloc[1, 1].title())
        encabezado = tabla.iloc[5]  # fila con "Sector de actividad económica", 2004, 2005...
        ramas = tabla.iloc[6:58]    # las 52 ramas
        for i, (_, fila) in enumerate(ramas.iterrows(), start=1):
            for col, anio in encabezado.items():
                if col < 2 or pd.isna(anio):
                    continue
                anio_txt = str(anio)
                filas.append({
                    "provincia_iso": PROVINCIAS[provincia],
                    "provincia": provincia,
                    "anio": int(anio_txt[:4]),
                    "estado_dato": ("provisorio" if "(1)" in anio_txt
                                    else "preliminar" if "(2)" in anio_txt else "definitivo"),
                    "rama_nro": i,
                    "rama": " ".join(str(fila[1]).split()),
                    "grupo": grupo_de_rama(i),
                    "vab_mill_pesos_2004": fila[col],
                })
    sector = pd.DataFrame(filas)
    total = sector.groupby(["provincia_iso", "anio"]).vab_mill_pesos_2004.transform("sum")
    sector["participacion_en_provincia"] = sector.vab_mill_pesos_2004 / total

    claves = ["provincia_iso", "provincia", "anio", "estado_dato", "grupo"]
    grupos = sector.groupby(claves, as_index=False)[["vab_mill_pesos_2004", "participacion_en_provincia"]].sum()

    sector.sort_values(["provincia", "anio", "rama_nro"]).round(4).to_csv(
        CARPETA / "vab_provincia_sector_largo.csv", index=False)
    grupos.sort_values(["provincia", "anio", "grupo"]).round(4).to_csv(
        CARPETA / "vab_provincia_grupos_largo.csv", index=False)
    print(f"  VAB: {sector.provincia.nunique()} provincias, {sector.anio.min()}-{sector.anio.max()}, "
          f"{sector.rama_nro.nunique()} ramas, {len(sector)} filas")


# ---------------------------------------------------------------------------
# 2. Petróleo y gas por provincia (Secretaría de Energía)
# ---------------------------------------------------------------------------
def procesar_hidrocarburos():
    pet = pd.read_csv(descargar(URL_PETROLEO, "energia_petroleo_por_provincia.csv"), encoding="utf-8-sig")
    gas = pd.read_csv(descargar(URL_GAS, "energia_gas_por_provincia.csv"), encoding="utf-8-sig")

    # De formato mensual a anual: sumamos los meses, separando convencional y no convencional
    def anual(df, col, nombre):
        df = df.copy()
        df["tipo"] = df.concepto.map(lambda c: "convencional" if "convencional" in c.lower() else "no_convencional")
        t = df.pivot_table(index=["provincia", "anio"], columns="tipo", values=col, aggfunc="sum").fillna(0)
        t.columns = [f"{nombre}_{c}" for c in t.columns]
        t[f"{nombre}_total"] = t.sum(axis=1)
        return t

    meses = pet.groupby("anio").mes.nunique().rename("meses_con_dato")
    tabla = anual(pet, "cantidad_m3", "petroleo_m3").join(anual(gas, "cantidad_mm3", "gas_miles_m3"), how="outer")
    tabla = tabla.reset_index().merge(meses, on="anio")
    tabla["provincia"] = tabla.provincia.map(nombre_limpio)
    tabla.insert(0, "provincia_iso", tabla.provincia.map(PROVINCIAS).fillna("AR-offshore"))
    tabla.sort_values(["provincia", "anio"]).round(1).to_csv(CARPETA / "petroleo_gas_provincia_anual.csv", index=False)
    print(f"  Petróleo y gas: {tabla.provincia.nunique()} jurisdicciones, {tabla.anio.min()}-{tabla.anio.max()}")


# ---------------------------------------------------------------------------
# 3. Agricultura por provincia (MAGyP)
# ---------------------------------------------------------------------------
def procesar_agricultura():
    csv = descargar(URL_MAGYP, "magyp_estimaciones_agricolas.csv", metodo="post", datos={"Dataset": "Dataset"})
    df = pd.read_csv(csv, sep=";", encoding="latin-1")
    df.columns = ["id_provincia", "provincia", "id_depto", "departamento", "id_cultivo", "cultivo",
                  "id_campania", "campania", "sup_sembrada_ha", "sup_cosechada_ha", "produccion_tn", "rendimiento"]
    # Sumamos los departamentos para obtener el total de la provincia
    prov = df.groupby(["provincia", "campania", "cultivo"], as_index=False)[
        ["sup_sembrada_ha", "sup_cosechada_ha", "produccion_tn"]].sum()
    prov["provincia"] = prov.provincia.map(lambda p: nombre_limpio(p.title()))
    prov.insert(0, "provincia_iso", prov.provincia.map(PROVINCIAS))
    # La campaña 2021/22 se cosecha mayormente en 2022: usamos ese año para unir con el VAB
    prov.insert(3, "anio_cosecha", prov.campania.str[:4].astype(int) + 1)
    prov["rendimiento_kg_ha"] = (prov.produccion_tn * 1000 / prov.sup_cosechada_ha.where(prov.sup_cosechada_ha > 0)).round(0)
    prov.sort_values(["provincia", "anio_cosecha", "cultivo"]).to_csv(
        CARPETA / "agricultura_provincia_anual.csv", index=False)
    print(f"  Agricultura: {prov.provincia.nunique()} provincias, campañas {prov.campania.min()} a "
          f"{prov.campania.max()}, {prov.cultivo.nunique()} cultivos")


# ---------------------------------------------------------------------------
# 4. Ganadería: stock bovino por provincia (MAGyP con datos de SENASA)
# ---------------------------------------------------------------------------
def procesar_ganaderia():
    xlsx = descargar(URL_BOVINOS, "magyp_stock_bovino_provincia.xlsx")
    hojas = pd.read_excel(xlsx, sheet_name=None, header=None)
    filas = []
    for hoja, tabla in hojas.items():
        if not hoja.isdigit():
            continue  # una hoja por año; "Serie 2007-2024" es un resumen
        # Buscamos la fila de encabezados ("Provincia", "Vacas", ...) y leemos hasta "Total"
        inicio = tabla.index[tabla[0].astype(str).str.strip() == "Provincia"][0]
        columnas = [str(c).strip() for c in tabla.loc[inicio]]
        for _, fila in tabla.loc[inicio + 1:].iterrows():
            nombre = str(fila[0]).strip()
            if nombre.lower().startswith("total") or nombre == "nan":
                break
            registro = dict(zip(columnas, fila))
            provincia = nombre_limpio(nombre.title())
            filas.append({"provincia_iso": PROVINCIAS[provincia], "provincia": provincia, "anio": int(hoja),
                          **{c.lower().replace(" ", "_"): registro[c] for c in columnas[1:] if c != "nan"}})
    stock = pd.DataFrame(filas).rename(columns={"total_bovinos": "total_cabezas"})
    stock.sort_values(["provincia", "anio"]).round(0).to_csv(CARPETA / "ganaderia_bovinos_provincia_anual.csv", index=False)
    print(f"  Ganadería: {stock.provincia.nunique()} provincias, {stock.anio.min()}-{stock.anio.max()}")


# ---------------------------------------------------------------------------
# 5. Indicadores por provincia y año (calculados con el VAB de CEPAL)
# ---------------------------------------------------------------------------
# PBG per cápita: Fundar (Argendata) lo calcula con el VAB de CEPAL y la población del INDEC.
URL_PBG_PC = "https://raw.githubusercontent.com/argendatafundar/data/main/CRECIM/provincia_pib_pc.csv"
RAMAS_SECTOR_PUBLICO = {44: "adm_publica", 45: "ensenanza_publica", 47: "salud_publica"}
RAMAS_TURISMO = {35: "hoteles", 36: "restaurantes"}


def procesar_indicadores():
    sector = pd.read_csv(CARPETA / "vab_provincia_sector_largo.csv")
    pc = pd.read_csv(descargar(URL_PBG_PC, "argendata_pbg_per_capita.csv"))
    pc = pc.rename(columns={"geocodigoFundar": "provincia_iso", "pib_pc": "pbg_per_capita_pesos_2004"})

    # Una fila por provincia-año, con el VAB total
    base = sector.groupby(["provincia_iso", "provincia", "anio", "estado_dato"], as_index=False).vab_mill_pesos_2004.sum()
    base = base.rename(columns={"vab_mill_pesos_2004": "vab_total_mill_pesos_2004"})

    # Participación (%) de las ramas del Estado y de las ramas turísticas en el VAB de la provincia
    for ramas in (RAMAS_SECTOR_PUBLICO, RAMAS_TURISMO):
        pivote = (sector[sector.rama_nro.isin(ramas)]
                  .pivot_table(index=["provincia_iso", "anio"], columns="rama_nro", values="participacion_en_provincia")
                  .rename(columns=ramas) * 100)
        pivote.columns = [f"pct_vab_{c}" for c in pivote.columns]
        base = base.merge(pivote.reset_index(), on=["provincia_iso", "anio"], how="left")
    base["pct_vab_sector_publico"] = base[[f"pct_vab_{c}" for c in RAMAS_SECTOR_PUBLICO.values()]].sum(axis=1)
    base["pct_vab_turismo"] = base[[f"pct_vab_{c}" for c in RAMAS_TURISMO.values()]].sum(axis=1)

    # PBG per cápita y, despejando, la población que usó Fundar (VAB / VAB per cápita)
    base = base.merge(pc[["provincia_iso", "anio", "pbg_per_capita_pesos_2004"]], on=["provincia_iso", "anio"], how="left")
    base["poblacion"] = (base.vab_total_mill_pesos_2004 * 1e6 / base.pbg_per_capita_pesos_2004).round(-2)

    base.sort_values(["provincia", "anio"]).round(3).to_csv(CARPETA / "indicadores_provincia_anual.csv", index=False)
    print(f"  Indicadores: {base.provincia.nunique()} provincias, {base.anio.min()}-{base.anio.max()} "
          f"(per cápita hasta {base.dropna(subset=['pbg_per_capita_pesos_2004']).anio.max()})")


# ---------------------------------------------------------------------------
# 6. Censos 2010 y 2022 (INDEC): vivienda, servicios y nivel educativo
# ---------------------------------------------------------------------------
# El INDEC publica, para cada provincia, un .zip con tres tablas (hogar, persona, vivienda)
# que cuentan cuántos hogares o personas hay en cada categoría, por radio censal.
# Nosotros sumamos todos los radios para obtener el total de la provincia.
CKAN_CENSO = {2010: "censo-nacional-de-poblacion-hogares-y-viviendas-2010",
              2022: "censo-nacional-de-poblacion-hogares-y-viviendas-2022"}

# Para cada censo: variable del INDEC -> {código de categoría: nombre del indicador}
# (los nombres y códigos cambian entre censos; los traducimos a indicadores comunes)
INDICADORES_CENSO = {
    2010: {
        "HOGAR_TOTPERS": "TOTAL",  # todas sus categorías suman el total de hogares
        "HOGAR_PROP": {1: "propietario", 2: "propietario", 3: "inquilino", 4: "prestada_o_cedida",
                       5: "prestada_o_cedida", 6: "otra_tenencia"},
        "HOGAR_H1409": {1: "agua_de_red"},
        "HOGAR_H1712": {1: "cloaca"},
        "HOGAR_H2014": {1: "gas_de_red"},
        "HOGAR_ALGUNBI": {1: "con_nbi"},
        # Personas (la base 2010 publicada no trae nivel educativo máximo ni cobertura de salud)
        "PERSONA_P02": "TOTAL_PERSONAS",
        "PERSONA_P1808": {1: "escuela_asiste", 2: "escuela_asistio", 3: "escuela_nunca_asistio"},
    },
    2022: {
        "HOGAR_TIPHOGAR": "TOTAL",
        "HOGAR_H22": {1: "propietario", 2: "inquilino", 3: "prestada_o_cedida", 4: "prestada_o_cedida",
                      5: "otra_tenencia"},
        "HOGAR_H14": {1: "agua_de_red"},
        "HOGAR_H18": {1: "cloaca"},
        "HOGAR_H19": {2: "gas_de_red"},  # combustible para cocinar; el censo 2022 no pregunta por electricidad
        "HOGAR_NBI_TOT": {1: "con_nbi"},
        "PERSONA_P02": "TOTAL_PERSONAS",
        "PERSONA_CONASI": {1: "escuela_asiste", 2: "escuela_asistio", 3: "escuela_nunca_asistio"},
        "PERSONA_MNI": {1: "max_nivel_sin_primario", 2: "max_nivel_sin_primario", 3: "max_nivel_primario",
                        4: "max_nivel_primario", 5: "max_nivel_secundario", 6: "max_nivel_secundario",
                        8: "max_nivel_secundario", 7: "max_nivel_superior", 9: "max_nivel_superior",
                        10: "max_nivel_superior", 11: "max_nivel_superior"},
        "PERSONA_P19": {1: "salud_obra_social_o_prepaga", 2: "salud_solo_plan_estatal", 3: "salud_sin_cobertura"},
    },
}


def urls_censo(anio):
    r = requests.get("https://datos.gob.ar/api/3/action/package_show", params={"id": CKAN_CENSO[anio]}, timeout=60)
    urls = [x["url"] for x in r.json()["result"]["resources"] if x["url"].endswith(".zip")]
    if anio == 2010:
        # El catálogo tiene mal los enlaces de 2010 ("...-2022.zip"); estos son los nombres reales
        reales = {"02-caba-2022.zip": "02-ciudad-autonoma-de-buenos-aires-2010.zip",
                  "94-tierra-del-fuego-2022.zip": "94-tierra-del-fuego-antartida-e-islas-del-atlantico-sur-2010.zip",
                  "86-santiago-del-estero-2022.zip": "86-santiago-del-estero.zip"}
        urls = [u.rsplit("/", 1)[0] + "/" + reales.get(u.rsplit("/", 1)[1], u.rsplit("/", 1)[1].replace("-2022.zip", "-2010.zip"))
                for u in urls]
    return urls


def contar_censo(anio):
    """Descarga provincia por provincia, suma los radios y guarda solo los totales (crudos/censo_<año>_totales.csv)."""
    import io
    import zipfile

    destino = CRUDOS / f"censo_{anio}_totales.csv"
    if destino.exists():
        print(f"  ya existe {destino.name}, no se descarga")
        return pd.read_csv(destino)
    variables = list(INDICADORES_CENSO[anio])
    partes = []
    for url in urls_censo(anio):
        print(f"  descargando {url.rsplit('/', 1)[-1]} ...")
        r = requests.get(url, timeout=900)
        r.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            for nombre in z.namelist():
                if not nombre.endswith(("hogar.csv", "persona.csv")):
                    continue
                for trozo in pd.read_csv(z.open(nombre), usecols=["provincia", "cod_variable", "cod_categoria", "cantidad"],
                                         chunksize=2_000_000):
                    trozo = trozo[trozo.cod_variable.isin(variables)]
                    partes.append(trozo.groupby(["provincia", "cod_variable", "cod_categoria"], as_index=False).cantidad.sum())
    totales = pd.concat(partes).groupby(["provincia", "cod_variable", "cod_categoria"], as_index=False).cantidad.sum()
    totales.to_csv(destino, index=False)
    return totales


def procesar_censos():
    filas = []
    for anio, reglas in INDICADORES_CENSO.items():
        t = contar_censo(anio)
        t["cod_categoria"] = pd.to_numeric(t.cod_categoria, errors="coerce")
        for provincia, tp in t.groupby("provincia"):
            fila = {"provincia": nombre_limpio(provincia), "anio_censo": anio}
            var_total = next(v for v, r in reglas.items() if r == "TOTAL")
            hogares = tp[(tp.cod_variable == var_total) & (tp.cod_categoria > 0)].cantidad.sum()
            fila["hogares"] = hogares
            fila["habitantes"] = tp[tp.cod_variable == "PERSONA_P02"].cantidad.sum()
            for var, mapa in reglas.items():
                if not isinstance(mapa, dict):
                    continue
                datos = tp[tp.cod_variable == var].assign(indicador=lambda d: d.cod_categoria.map(mapa))
                if var.startswith("PERSONA_"):
                    # % de personas que respondieron esa pregunta (sin contar "ignorado")
                    validos = datos.dropna(subset=["indicador"])
                    for ind, n in validos.groupby("indicador").cantidad.sum().items():
                        fila[f"pct_personas_{ind}"] = 100 * n / validos.cantidad.sum()
                else:
                    for ind, n in datos.dropna(subset=["indicador"]).groupby("indicador").cantidad.sum().items():
                        fila[f"pct_hogares_{ind}"] = 100 * n / hogares
            filas.append(fila)
    censo = pd.DataFrame(filas)
    # Si una categoría no aparece es porque ningún hogar la tiene (p. ej. gas de red en Formosa 2010)
    cols_hogar = [c for c in censo.columns if c.startswith("pct_hogares_")]
    censo[cols_hogar] = censo[cols_hogar].fillna(0)
    censo.insert(0, "provincia_iso", censo.provincia.map(PROVINCIAS))
    censo.sort_values(["provincia", "anio_censo"]).round(2).to_csv(CARPETA / "censo_vivienda_servicios_educacion.csv", index=False)
    print(f"  Censos: {censo.provincia.nunique()} provincias, años {sorted(censo.anio_censo.unique())}")


# ---------------------------------------------------------------------------
# 7. Turismo: Encuesta de Ocupación Hotelera (Ministerio de Turismo, datos.yvera.gob.ar)
# ---------------------------------------------------------------------------
# La EOH no mide provincias sino 52 localidades turísticas. Sumamos las localidades
# de cada provincia: el total es un piso (no incluye hoteles fuera de esas localidades).
URL_EOH = "https://datos.yvera.gob.ar/dataset/93db331e-6970-4d74-8589-c1223ac9c282/resource/"
URL_PERNOCTES = URL_EOH + "7b6ba47f-4aa9-4743-96be-d0e6157cfc5e/download/pernoctes_por_localidad_segun_residencia.csv"
URL_VIAJEROS = URL_EOH + "57b5deae-026e-4413-9f90-89a428496bfb/download/viajeros_por_localidad_segun_residencia.csv"
LOCALIDAD_PROVINCIA = {
    "CABA": "Ciudad de Buenos Aires",
    "Bahía Blanca": "Buenos Aires", "Mar Chiquita": "Buenos Aires", "Mar del Plata": "Buenos Aires",
    "Pinamar": "Buenos Aires", "Tandil": "Buenos Aires", "Villa Gesell": "Buenos Aires",
    "Catamarca": "Catamarca", "Resistencia": "Chaco", "Puerto Madryn": "Chubut",
    "Córdoba": "Córdoba", "Carlos Paz": "Córdoba", "La Falda": "Córdoba", "Mina Clavero": "Córdoba",
    "Río Cuarto": "Córdoba", "Villa General Belgrano": "Córdoba",
    "Corrientes": "Corrientes", "Paraná": "Entre Ríos", "Gualeguaychú": "Entre Ríos", "Formosa": "Formosa",
    "Jujuy": "Jujuy", "Quebrada": "Jujuy", "Valles": "Jujuy", "Yungas": "Jujuy",
    "Santa Rosa": "La Pampa", "La Rioja": "La Rioja",
    "Mendoza": "Mendoza", "Malargue-Las Leñas": "Mendoza", "San Rafael": "Mendoza", "Valle de Uco": "Mendoza",
    "Posadas": "Misiones", "Puerto Iguazú": "Misiones",
    "Neuquén": "Neuquén", "La Angostura": "Neuquén", "San Martín de los Andes": "Neuquén",
    "Bariloche": "Río Negro", "Las Grutas": "Río Negro", "Viedma": "Río Negro",
    "Salta": "Salta", "Cafayate": "Salta", "San Juan": "San Juan", "San Luis": "San Luis", "Merlo": "San Luis",
    "Calafate": "Santa Cruz", "Rio Gallegos": "Santa Cruz",
    "Santa Fe": "Santa Fe", "Rosario": "Santa Fe", "Rafaela": "Santa Fe",
    "Santiago del Estero": "Santiago del Estero", "Termas": "Santiago del Estero",
    "Tucumán": "Tucumán", "Ushuaia": "Tierra del Fuego",
}


def procesar_turismo():
    tablas = []
    for url, archivo, col in [(URL_PERNOCTES, "turismo_pernoctes_por_localidad_segun_residencia.csv", "pernoctes"),
                              (URL_VIAJEROS, "turismo_viajeros_por_localidad_segun_residencia.csv", "viajeros")]:
        df = pd.read_csv(descargar(url, archivo), encoding="utf-8-sig")
        origen = [c for c in df.columns if c.startswith("origen")][0]
        df["provincia"] = df.localidad.map(LOCALIDAD_PROVINCIA)
        df["anio"] = df.indice_tiempo.str[:4].astype(int)
        df[col] = pd.to_numeric(df[col], errors="coerce")
        t = df.pivot_table(index=["provincia", "anio"], columns=origen, values=col, aggfunc="sum")
        t.columns = [f"{col}_{c.lower().replace(' ', '_')}" for c in t.columns]
        if col == "pernoctes":
            t["meses_con_dato"] = df.groupby(["provincia", "anio"]).indice_tiempo.nunique()
            t["localidades_relevadas"] = df.groupby(["provincia", "anio"]).localidad.nunique()
        tablas.append(t)
    tur = pd.concat(tablas, axis=1).reset_index()
    tur.insert(0, "provincia_iso", tur.provincia.map(PROVINCIAS))
    tur.sort_values(["provincia", "anio"]).to_csv(CARPETA / "turismo_hoteles_provincia_anual.csv", index=False)
    print(f"  Turismo: {tur.provincia.nunique()} provincias, {tur.anio.min()}-{tur.anio.max()}")


# ---------------------------------------------------------------------------
# 8. Temperatura media anual por provincia (Banco Mundial, Climate Change Knowledge Portal)
# ---------------------------------------------------------------------------
# Es el promedio de toda la superficie de la provincia (reanálisis ERA5, grilla de 0,25°),
# no la temperatura de una estación en la capital. Por eso Catamarca o San Juan, que tienen
# Cordillera, dan más frío que sus ciudades.
URL_CCKP = ("https://cckpapi.worldbank.org/cckp/v1/era5-x0.25_timeseries_tas_timeseries_annual_"
            "1950-2024_mean_historical_era5_x0.25_mean/{codigos}?_format=json")
# El código de cada provincia es "ARG." + código GAUL del país (12) + código GAUL de la provincia
CODIGO_CCKP = {
    "Buenos Aires": 12429, "Ciudad de Buenos Aires": 12430, "Catamarca": 12431, "Chaco": 12432,
    "Chubut": 12433, "Córdoba": 12434, "Corrientes": 12435, "Entre Ríos": 12436, "Formosa": 12437,
    "Jujuy": 12438, "La Pampa": 12439, "La Rioja": 12440, "Mendoza": 12441, "Misiones": 12442,
    "Neuquén": 12443, "Río Negro": 12444, "Salta": 12445, "San Juan": 12446, "San Luis": 12447,
    "Santa Cruz": 12448, "Santa Fe": 12449, "Santiago del Estero": 12450, "Tierra del Fuego": 12451,
    "Tucumán": 12452,
}


def procesar_temperatura():
    import json

    destino = CRUDOS / "cckp_temperatura_provincias.json"
    if destino.exists() and not REFRESCAR:
        print(f"  ya existe {destino.name}, no se descarga")
        datos = json.loads(destino.read_text())
    else:
        datos = {}
        for provincia, cod in CODIGO_CCKP.items():
            r = requests.get(URL_CCKP.format(codigos=f"ARG.{cod}"), timeout=120)
            r.raise_for_status()
            datos.update(r.json()["data"])
        destino.write_text(json.dumps(datos))
    nombre_por_codigo = {f"ARG.{c}": p for p, c in CODIGO_CCKP.items()}
    filas = [{"provincia": nombre_por_codigo[cod], "anio": int(fecha[:4]), "temperatura_media_c": t}
             for cod, serie in datos.items() for fecha, t in serie.items()]
    temp = pd.DataFrame(filas)
    temp.insert(0, "provincia_iso", temp.provincia.map(PROVINCIAS))
    temp.sort_values(["provincia", "anio"]).to_csv(CARPETA / "temperatura_provincia_anual.csv", index=False)
    print(f"  Temperatura: {temp.provincia.nunique()} provincias, {temp.anio.min()}-{temp.anio.max()}")


# ---------------------------------------------------------------------------
# 9. Habitantes por año: proyecciones del INDEC (base Censo 2010)
# ---------------------------------------------------------------------------
# Son estimaciones al 1 de julio de cada año. El Censo 2022 contó algo menos de lo proyectado
# (46,0 millones contra 46,2): para 2022 conviene comparar con la columna "habitantes" del censo.
URL_PROYECCIONES = "https://www.indec.gob.ar/ftp/cuadros/poblacion/c1_proyecciones_prov_2010_2040.xls"


def procesar_poblacion():
    xls = descargar(URL_PROYECCIONES, "indec_proyecciones_prov_2010_2040.xls")
    filas = []
    for hoja, tabla in pd.read_excel(xls, sheet_name=None, header=None).items():
        if not hoja[:2].isdigit() or hoja.startswith("01"):
            continue  # "01" es el total del país
        nombre = hoja[3:].title().replace("Sante Fe", "Santa Fe")
        provincia = nombre_limpio(nombre)
        for _, f in tabla.iterrows():
            if isinstance(f[0], (int, float)) and not pd.isna(f[0]) and 1900 < f[0] < 2100:
                filas.append({"provincia_iso": PROVINCIAS[provincia], "provincia": provincia, "anio": int(f[0]),
                              "habitantes": int(f[1]), "varones": int(f[2]), "mujeres": int(f[3])})
    pob = pd.DataFrame(filas)
    pob.sort_values(["provincia", "anio"]).to_csv(CARPETA / "poblacion_provincia_anual.csv", index=False)
    print(f"  Población: {pob.provincia.nunique()} provincias, {pob.anio.min()}-{pob.anio.max()}")


# ---------------------------------------------------------------------------
# 10. Gobierno provincial: quién ganó cada elección a gobernador
# ---------------------------------------------------------------------------
# Resultados oficiales por elección (Atlas Electoral de Andy Tow), publicados por el
# proyecto "electorAr" de Politica Argentina en GitHub. Cubren de 1983 a 2019
# (Santiago del Estero hasta 2017 y Corrientes con huecos). Las elecciones que faltan
# (1995 en 7 provincias y todo lo posterior a 2019) se cargan a mano más abajo.
URL_ELECTORAR = ("https://raw.githubusercontent.com/PoliticaArgentina/data_warehouse/master/"
                 "electorAr/data/escrutinios_definitivos/{archivo}")

# Nombre que usa electorAr para cada provincia -> nombre limpio
SLUG_PROVINCIA = {
    "caba": "Ciudad de Buenos Aires", "pba": "Buenos Aires", "catamarca": "Catamarca",
    "chaco": "Chaco", "chubut": "Chubut", "cordoba": "Córdoba", "corrientes": "Corrientes",
    "erios": "Entre Ríos", "formosa": "Formosa", "jujuy": "Jujuy", "mendoza": "Mendoza",
    "misiones": "Misiones", "neuquen": "Neuquén", "pampa": "La Pampa", "rioja": "La Rioja",
    "rnegro": "Río Negro", "salta": "Salta", "sanluis": "San Luis", "santiago": "Santiago del Estero",
    "scruz": "Santa Cruz", "sfe": "Santa Fe", "sjuan": "San Juan", "tdf": "Tierra del Fuego",
    "tucuman": "Tucumán",
}
# Años de elección que existen en electorAr: (primera vuelta, segunda vuelta)
ANIOS_TIPICOS = [1983, 1987, 1991, 1995, 1999, 2003, 2007, 2011, 2015, 2019]
SIN_1995 = [a for a in ANIOS_TIPICOS if a != 1995]
ELECCIONES_ELECTORAR = {
    "caba": ([1996, 2000, 2003, 2007, 2011, 2015, 2019], [2003, 2007, 2011, 2015]),
    "catamarca": ([1983, 1987, 1988, 1991, 1995, 1999, 2003, 2007, 2011, 2015, 2019], []),
    "chaco": (ANIOS_TIPICOS, [1995]),
    "corrientes": ([1983, 1987, 1991, 1993, 1997, 2001, 2005, 2009, 2017], [1997, 2001, 2009]),
    "santiago": ([1983, 1987, 1991, 1995, 1999, 2002, 2005, 2008, 2013, 2017], []),
    "tdf": ([1991, 1995, 1999, 2003, 2007, 2011, 2015, 2019], [1991, 1999, 2003, 2007, 2011, 2015]),
    **{s: (SIN_1995, []) for s in ["cordoba", "jujuy", "mendoza", "neuquen", "pampa", "rioja", "rnegro"]},
}
for slug in SLUG_PROVINCIA:
    ELECCIONES_ELECTORAR.setdefault(slug, (ANIOS_TIPICOS, []))

# Elecciones que no están en electorAr, cargadas a mano: (provincia, año, ganador, familia)
GOBERNADORES_A_MANO = [
    ("cordoba", 1995, "Mestre (Unión Cívica Radical)", "radicalismo"),
    ("jujuy", 1995, "Snopek (Partido Justicialista)", "peronismo"),
    ("mendoza", 1995, "Lafalla (Partido Justicialista)", "peronismo"),
    ("neuquen", 1995, "Sapag (Movimiento Popular Neuquino)", "partido provincial"),
    ("pampa", 1995, "Marín (Partido Justicialista)", "peronismo"),
    ("rioja", 1995, "Maza (Partido Justicialista)", "peronismo"),
    ("rnegro", 1995, "Verani (Unión Cívica Radical)", "radicalismo"),
    ("corrientes", 2013, "Colombi (Encuentro por Corrientes)", "radicalismo"),
    ("corrientes", 2021, "G. Valdés (Encuentro por Corrientes)", "radicalismo"),
    ("corrientes", 2025, "J. P. Valdés (Vamos Corrientes)", "radicalismo"),
    ("santiago", 2021, "G. Zamora (Frente Cívico por Santiago)", "partido provincial"),
    ("santiago", 2025, "Suárez (Frente Cívico por Santiago)", "partido provincial"),
    ("pba", 2023, "Kicillof (Unión por la Patria)", "peronismo"),
    ("caba", 2023, "J. Macri (Juntos por el Cambio)", "PRO / Juntos por el Cambio"),
    ("catamarca", 2023, "Jalil (frente justicialista)", "peronismo"),
    ("chaco", 2023, "Zdero (Juntos por el Cambio)", "radicalismo"),
    ("chubut", 2023, "Torres (Despierta Chubut)", "PRO / Juntos por el Cambio"),
    ("cordoba", 2023, "Llaryora (Hacemos Unidos por Córdoba)", "peronismo"),
    ("erios", 2023, "Frigerio (Juntos por Entre Ríos)", "PRO / Juntos por el Cambio"),
    ("formosa", 2023, "Insfrán (Partido Justicialista)", "peronismo"),
    ("jujuy", 2023, "Sadir (Cambia Jujuy)", "radicalismo"),
    ("mendoza", 2023, "Cornejo (Cambia Mendoza)", "radicalismo"),
    ("misiones", 2023, "Passalacqua (Frente Renovador de la Concordia)", "partido provincial"),
    ("neuquen", 2023, "Figueroa (Comunidad)", "partido provincial"),
    ("pampa", 2023, "Ziliotto (Frente Justicialista Pampeano)", "peronismo"),
    ("rioja", 2023, "Quintela (frente justicialista)", "peronismo"),
    ("rnegro", 2023, "Weretilneck (Juntos Somos Río Negro)", "partido provincial"),
    ("salta", 2023, "Sáenz (frente propio)", "partido provincial"),
    ("sanluis", 2023, "Poggi (Cambia San Luis)", "PRO / Juntos por el Cambio"),
    ("sjuan", 2023, "Orrego (Cambia San Juan)", "PRO / Juntos por el Cambio"),
    ("scruz", 2023, "Vidal (SER Santa Cruz)", "partido provincial"),
    ("sfe", 2023, "Pullaro (Unidos para Cambiar Santa Fe)", "radicalismo"),
    ("tdf", 2023, "Melella (FORJA y peronismo)", "peronismo"),
    ("tucuman", 2023, "Jaldo (frente justicialista)", "peronismo"),
]

# Familia política según palabras del nombre de la lista (se revisan en este orden)
PALABRAS_FAMILIA = [
    ("radicalismo", ["union civica radical", "alianza para el trabajo", "cambia mendoza", "cambia jujuy",
                     "encuentro por corrientes", "frente civico y social", "concertacion para el desarrollo"]),
    ("PRO / Juntos por el Cambio", ["propuesta republicana", "compromiso para el cambio", "union pro",
                                    "juntos por el cambio", "cambiemos"]),
    ("peronismo", ["justicialist", "frente para la victoria", "frente de todos", "frente todos",
                   "union por cordoba", "hacemos por cordoba", "frente juntos", "chaco merece",
                   "frente chaqueno", "pueblo riojano", "compromiso federal", "frente movimiento popular",
                   "frente de la victoria", "frente de la esperanza", "frente fundacional"]),
    ("partido provincial", ["movimiento popular neuquino", "pacto autonomista", "partido nuevo", "bloquista",
                            "movimiento popular fueguino", "renovador de salta", "fuerza republicana",
                            "frente renovador", "civico por santiago", "juntos somos", "accion chaquena",
                            "unidad provincial", "chubut", "saenz", "alianza por san juan"]),
    ("otro", ["progresista", "afirmacion para una republica", "social patagonico"]),
]
# Listas que solo traen nombres (sin partido) o cuyo nombre confunde
FAMILIA_A_MANO = {
    ("caba", 1996): "radicalismo", ("caba", 2000): "otro", ("caba", 2003): "otro",
    ("chaco", 1995): "radicalismo", ("chaco", 1999): "radicalismo", ("chaco", 2003): "radicalismo",
    ("chaco", 2007): "peronismo", ("chubut", 2007): "peronismo", ("cordoba", 2007): "peronismo",
    ("corrientes", 2001): "radicalismo", ("corrientes", 2005): "radicalismo",
    ("mendoza", 2003): "radicalismo", ("mendoza", 2007): "peronismo", ("misiones", 1999): "peronismo",
    ("pba", 1999): "peronismo", ("rnegro", 2007): "radicalismo", ("sjuan", 2003): "peronismo",
    ("sjuan", 2007): "peronismo", ("tdf", 2007): "otro", ("tdf", 2019): "peronismo",
    ("tucuman", 1987): "peronismo",
    **{("neuquen", a): "partido provincial" for a in (2003, 2007, 2011, 2015, 2019)},
}
ACLARACIONES = {
    ("tucuman", 1987): "La UCR sacó más votos, pero el colegio electoral eligió a Domato (PJ)",
    ("corrientes", 1991): "El colegio electoral no eligió gobernador: intervención federal 1992-1993",
    ("chubut", 2015): "Chubut Somos Todos: partido provincial nacido del peronismo (Das Neves)",
    ("chubut", 2019): "Chubut Somos Todos: partido provincial nacido del peronismo (Arcioni)",
    ("tdf", 2019): "Melella viene de FORJA, aliado del peronismo",
    ("tdf", 2023): "Melella viene de FORJA, aliado del peronismo",
    ("scruz", 2015): "Ley de lemas: ganó el lema más votado aunque otro candidato sacó más votos",
}
# Años en que gobernó un interventor federal y no el gobernador electo
INTERVENCIONES = {("corrientes", 1992), ("corrientes", 1993), ("corrientes", 2000), ("corrientes", 2001),
                  ("catamarca", 1991), ("santiago", 1994), ("santiago", 2004)}
NO_SON_LISTAS = r"^(0|blanco|votos? (en )?blancos?.*|votos (nulos|recurridos|impugnados))$"


def familia_politica(slug, anio, lista):
    if (slug, anio) in FAMILIA_A_MANO:
        return FAMILIA_A_MANO[(slug, anio)]
    texto = lista.translate(SIN_TILDES).lower().replace("ñ", "n")
    for familia, palabras in PALABRAS_FAMILIA:
        if any(p in texto for p in palabras):
            return familia
    return "sin clasificar"


def procesar_gobernadores():
    import re

    (CRUDOS / "electorAr_gobernadores").mkdir(exist_ok=True)
    elecciones = []
    for slug, (generales, balotajes) in ELECCIONES_ELECTORAR.items():
        for anio in generales:
            # Si hubo segunda vuelta, el ganador sale de esa
            vuelta = "balota" if anio in balotajes else "gral"
            archivo = f"{slug}_gober_{vuelta}{anio}.csv"
            tabla = pd.read_csv(descargar(URL_ELECTORAR.format(archivo=archivo),
                                          f"electorAr_gobernadores/{archivo}", fija=True))
            tabla["lista"] = tabla.lista.astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
            tabla = tabla[~tabla.lista.str.lower().str.match(NO_SON_LISTAS)]
            ganador = tabla.sort_values("votos", ascending=False).iloc[0]
            elecciones.append({"slug": slug, "anio_eleccion": anio, "lista_ganadora": ganador.lista,
                               "pct_votos_ganador": round(100 * ganador.votos / tabla.votos.sum(), 1),
                               "segunda_vuelta": vuelta == "balota", "fuente": "electorAr (Atlas Electoral)"})
    for slug, anio, ganador, familia in GOBERNADORES_A_MANO:
        FAMILIA_A_MANO[(slug, anio)] = familia
        elecciones.append({"slug": slug, "anio_eleccion": anio, "lista_ganadora": ganador,
                           "segunda_vuelta": False, "fuente": "carga manual"})
    elec = pd.DataFrame(elecciones)
    elec["familia_politica"] = [familia_politica(s, a, l) for s, a, l in
                                zip(elec.slug, elec.anio_eleccion, elec.lista_ganadora)]
    elec["aclaracion"] = [ACLARACIONES.get((s, a), "") for s, a in zip(elec.slug, elec.anio_eleccion)]
    elec.insert(0, "provincia", elec.slug.map(SLUG_PROVINCIA))
    elec.insert(0, "provincia_iso", elec.provincia.map(PROVINCIAS))
    elec = elec.sort_values(["provincia", "anio_eleccion"])

    # De elección a año: el electo asume en diciembre, así que gobierna desde el año siguiente
    # (Santiago del Estero 2005 es la excepción: votó en febrero y asumió en marzo).
    elec["desde"] = elec.anio_eleccion + 1
    elec.loc[(elec.slug == "santiago") & (elec.anio_eleccion == 2005), "desde"] = 2005
    filas = []
    for slug, grupo in elec.groupby("slug"):
        grupo = grupo.sort_values("desde")
        for anio in range(1984, 2027):
            vigente = grupo[grupo.desde <= anio]
            if vigente.empty:
                continue
            e = vigente.iloc[-1]
            intervenida = (slug, anio) in INTERVENCIONES
            filas.append({"provincia_iso": e.provincia_iso, "provincia": e.provincia, "anio": anio,
                          "familia_politica_gobierno": "intervención federal" if intervenida else e.familia_politica,
                          "ganador_ultima_eleccion": e.lista_ganadora, "anio_ultima_eleccion": e.anio_eleccion})
    anual = pd.DataFrame(filas)
    elec.drop(columns=["slug", "desde"]).to_csv(CARPETA / "gobernadores_elecciones.csv", index=False)
    anual.to_csv(CARPETA / "gobierno_provincial_anual.csv", index=False)
    print(f"  Gobernadores: {len(elec)} elecciones, {anual.provincia.nunique()} provincias, "
          f"{anual.anio.min()}-{anual.anio.max()}; sin clasificar: {(elec.familia_politica == 'sin clasificar').sum()}")


# ---------------------------------------------------------------------------
# 11. Diputados y senadores nacionales de cada provincia
# ---------------------------------------------------------------------------
# Diputados: Cámara de Diputados, dataset "legisladores" (un registro por diputado y bloque,
#   con fechas). Completo desde 2010 (antes solo trae la mitad de la cámara).
# Senado: listado histórico de senadores (desde 1924) con el partido o alianza por el que
#   entraron. Para los diputados se usa el bloque (que puede cambiar en el mandato).
# Foto al 1 de julio de cada año: cuántas bancas tiene cada familia política por provincia.
URL_DIPUTADOS = ("https://datos.hcdn.gob.ar/dataset/a80e0fa7-d73a-4ed1-9dec-80465e368951/resource/"
                 "169de2eb-465f-4007-a4c2-39a5ba4c0df3/download/diputados2.1.csv")
URL_SENADORES = "https://www.senado.gob.ar/micrositios/DatosAbiertos/ExportarListadoSenadoresHistorico/json"

# Palabras que identifican la familia de un bloque o partido (se prueban en este orden).
# Las palabras de 3 letras o menos tienen que aparecer como palabra suelta ("pro", "ucr").
PALABRAS_LEGISLADORES = [
    ("La Libertad Avanza", ["libertad avanza"]),
    ("izquierda", ["izquierda", "trabajadores", "pts", "mst", "obrero"]),
    ("partido provincial", ["concordia"]),  # "Frente Renovador de la Concordia" es misionero, no de Massa
    ("radicalismo", ["ucr", "union civica radical", "radical", "cambia mendoza", "democracia para siempre",
                     "encuentro por corrientes", "encuentro corrientes", "vamos corrientes", "frente civico y social",
                     "concertacion para el desarrollo"]),
    ("PRO / Juntos por el Cambio", ["pro", "cambiemos", "juntos por el cambio", "coalicion civica", "despierta chubut",
                                    "hacemos coalicion", "juntos por argentina", "avanzar san luis",
                                    "buenos aires por el cambio"]),
    ("peronismo", ["justicialista", "peronis", "frente para la victoria", "frente de todos", "frente todos",
                   "union por la patria", "fuerza patria", "unidad ciudadana", "frente renovador", "union por cordoba",
                   "hacemos por cordoba", "cordoba federal", "frente de la victoria", "partido de la victoria",
                   "compromiso federal", "frejuli", "nuevo encuentro", "movimiento evita", "ahora patria",
                   "conviccion federal", "justicia social", "chaco merece"]),
    ("partido provincial", ["neuquin", "fueguino", "bloquista", "cruzada renovadora", "fuerza republicana",
                            "civico por santiago", "misiones", "renovador de salta", "renovador federal",
                            "juntos somos rio negro", "santa cruz", "autonomista", "liberal de corrientes", "salten",
                            "fuerza entre rios", "por san juan", "elijo catamarca", "produccion y trabajo",
                            "innovacion federal", "chubut somos todos", "partido nuevo"]),
]


def familia_legislador(nombre):
    texto = " " + str(nombre).translate(SIN_TILDES).lower().replace("ñ", "n").replace("-", " ") + " "
    for familia, palabras in PALABRAS_LEGISLADORES:
        for palabra in palabras:
            if (len(palabra) <= 3 and f" {palabra} " in texto) or (len(palabra) > 3 and palabra in texto):
                return familia
    return "otros"


def bancas_por_anio(tabla, anios, camara):
    """tabla: una fila por legislador y período, con provincia, desde, hasta y nombre (bloque o partido)."""
    filas = []
    for anio in anios:
        dia = pd.Timestamp(f"{anio}-07-01")
        en_funciones = tabla[(tabla.desde <= dia) & (tabla.hasta.isna() | (tabla.hasta >= dia))]
        for provincia, grupo in en_funciones.groupby("provincia"):
            fila = {"provincia_iso": PROVINCIAS.get(provincia), "provincia": provincia, "anio": anio,
                    "camara": camara, "bancas": len(grupo)}
            por_familia = grupo.familia.value_counts()
            for familia in por_familia.index:
                fila[f"bancas_{familia}"] = por_familia[familia]
            # Familia con más bancas ("empate" si dos tienen las mismas)
            empate = len(por_familia) > 1 and por_familia.iloc[0] == por_familia.iloc[1]
            fila["familia_mayoritaria"] = "empate" if empate else por_familia.index[0]
            por_nombre = grupo.nombre.value_counts()
            fila["bloque_o_partido_mayoritario"] = por_nombre.index[0]
            filas.append(fila)
    return filas


def procesar_legisladores():
    import json

    dip = pd.read_csv(descargar(URL_DIPUTADOS, "hcdn_diputados.csv"))
    dip = pd.DataFrame({
        "provincia": dip.DISTRITO.map(nombre_limpio), "nombre": dip.BLOQUE.str.strip(),
        "desde": pd.to_datetime(dip.BLOQUE_INICIO, errors="coerce"),
        # termina cuando cambia de bloque o cuando deja la banca, lo que pase antes
        "hasta": pd.concat([pd.to_datetime(dip.BLOQUE_FIN, errors="coerce"),
                            pd.to_datetime(dip.CESE, errors="coerce")], axis=1).min(axis=1)})

    sen = json.loads(descargar(URL_SENADORES, "senado_ExportarListadoSenadoresHistorico.json")
                     .read_text(encoding="utf-8-sig"))["table"]["rows"]
    sen = pd.DataFrame(sen)
    sen = pd.DataFrame({
        "provincia": sen.PROVINCIA.map(nombre_limpio),
        "nombre": sen["PARTIDO POLITICO O ALIANZA"].str.strip().replace("", "SIN DATO"),
        "desde": pd.to_datetime(sen["INICIO PERIODO REAL"], errors="coerce"),
        "hasta": pd.to_datetime(sen["CESE PERIODO REAL"], errors="coerce")})  # vacío = sigue en funciones

    for tabla in (dip, sen):
        tabla["familia"] = tabla.nombre.map(familia_legislador)
    filas = bancas_por_anio(dip, range(2010, 2027), "diputados") + bancas_por_anio(sen, range(1984, 2027), "senado")
    leg = pd.DataFrame(filas)
    columnas_bancas = sorted(c for c in leg.columns if c.startswith("bancas_"))
    leg[columnas_bancas] = leg[columnas_bancas].fillna(0).astype(int)
    leg = leg[["provincia_iso", "provincia", "anio", "camara", "bancas"] + columnas_bancas
              + ["familia_mayoritaria", "bloque_o_partido_mayoritario"]]
    leg.sort_values(["camara", "provincia", "anio"]).to_csv(CARPETA / "legisladores_nacionales_provincia_anual.csv",
                                                           index=False)
    for camara, g in leg.groupby("camara"):
        print(f"  {camara}: {g.provincia.nunique()} provincias, {g.anio.min()}-{g.anio.max()}, "
              f"bancas en {g.anio.max()}: {g[g.anio == g.anio.max()].bancas.sum()}")


# ---------------------------------------------------------------------------
# 12. Salud: vacunación (triple viral) y médicos por provincia
# ---------------------------------------------------------------------------
# Ministerio de Salud (datos.salud.gob.ar):
#   - Cobertura de la vacuna triple viral (SRP): % de chicos vacunados con la 1.ª dosis a los
#     12 meses y con la 2.ª al ingreso escolar, 2009-2024. Puede pasar de 100 % (el denominador
#     es una estimación de población).
#   - Médicos con matrícula activa por provincia de residencia, 2012-2023.
# El servidor de Salud manda su certificado sin el certificado "intermedio" de Sectigo, y
# Python no lo puede verificar. Lo agregamos a mano: el intermedio igual tiene que estar
# firmado por una raíz de confianza, así que la verificación sigue siendo segura.
URL_SALUD_API = "https://datos.salud.gob.ar/api/3/action/package_show?id={id}"
URL_SRP = ("https://datos.salud.gob.ar/dataset/f70b1357-b57e-4077-9746-af8193243207/resource/"
           "2e316239-2718-4ee8-b896-9d23f79f104c/download/dicei-vacunas-srp-2009-2024.xls")
URL_INTERMEDIO_SECTIGO = "http://crt.sectigo.com/SectigoPublicServerAuthenticationCADVR36.crt"


def certificados_salud():
    """Arma un archivo con las raíces de siempre + el intermedio que le falta al servidor."""
    import os
    import ssl

    import certifi

    intermedio = CRUDOS / "sectigo_dv_r36.pem"
    if not intermedio.exists():
        der = requests.get(URL_INTERMEDIO_SECTIGO, timeout=60).content
        intermedio.write_text(ssl.DER_cert_to_PEM_cert(der))
    raices = Path(os.environ.get("REQUESTS_CA_BUNDLE") or certifi.where())
    combinado = CRUDOS / "certificados_salud.pem"
    combinado.write_text(raices.read_text() + "\n" + intermedio.read_text())
    return str(combinado)


def procesar_salud():
    ca = certificados_salud()

    # Vacuna triple viral: una columna por año y dosis -> una fila por provincia y año
    archivo = CRUDOS / "salud_srp_2009_2024.xls"
    if not archivo.exists() or REFRESCAR:
        r = requests.get(URL_SRP, timeout=120, verify=ca)
        r.raise_for_status()
        archivo.write_bytes(r.content)
    srp = pd.read_excel(archivo)
    srp = srp.melt(id_vars=["jurisdiccion_id", "jurisdiccion_nombre"], var_name="columna", value_name="cobertura")
    srp["anio"] = srp.columna.str[:4].astype(int)
    srp["dosis"] = srp.columna.str.contains("ingreso_escolar").map(
        {False: "pct_vacuna_srp_1ra_dosis_12_meses", True: "pct_vacuna_srp_2da_dosis_ingreso_escolar"})
    srp["provincia"] = srp.jurisdiccion_nombre.map(nombre_limpio)
    srp = srp.pivot_table(index=["provincia", "anio"], columns="dosis", values="cobertura").reset_index()

    # Médicos: un CSV grande por año; guardamos solo el total por provincia
    totales = CRUDOS / "salud_medicos_totales.csv"
    if totales.exists() and not REFRESCAR:
        print(f"  ya existe {totales.name}, no se descarga")
        med = pd.read_csv(totales)
    else:
        import io

        recursos = requests.get(URL_SALUD_API.format(id="serie-de-profesionales-de-medicina"),
                                timeout=60, verify=ca).json()["result"]["resources"]
        partes = []
        for recurso in recursos:
            if recurso["format"].upper() != "CSV":
                continue
            print(f"  descargando {recurso['url'].rsplit('/', 1)[-1]} ...")
            r = requests.get(recurso["url"], timeout=300, verify=ca)
            r.raise_for_status()
            tabla = pd.read_csv(io.BytesIO(r.content))
            partes.append(tabla.groupby(["anio_corte", "provincia_residencia"], as_index=False).total.sum())
        med = pd.concat(partes).rename(columns={"anio_corte": "anio", "total": "medicos"})
        med.to_csv(totales, index=False)
    med["provincia"] = med.provincia_residencia.map(nombre_limpio)
    med = med[med.provincia.isin(PROVINCIAS)].groupby(["provincia", "anio"], as_index=False).medicos.sum()

    salud = srp.merge(med, on=["provincia", "anio"], how="outer")
    pob = pd.read_csv(CARPETA / "poblacion_provincia_anual.csv")[["provincia", "anio", "habitantes"]]
    salud = salud.merge(pob, on=["provincia", "anio"], how="left")
    salud["medicos_cada_10000_hab"] = (salud.medicos / salud.habitantes * 10000).round(1)
    salud = salud.drop(columns="habitantes")
    salud.insert(0, "provincia_iso", salud.provincia.map(PROVINCIAS))
    salud.sort_values(["provincia", "anio"]).to_csv(CARPETA / "salud_provincia_anual.csv", index=False)
    print(f"  Salud: {salud.provincia.nunique()} provincias, vacunas {srp.anio.min()}-{srp.anio.max()}, "
          f"médicos {med.anio.min()}-{med.anio.max()} ({med[med.anio == med.anio.max()].medicos.sum()} en el último año)")


# ---------------------------------------------------------------------------
# 13. Pymes: Registro MiPyME (Secretaría de Pymes)
# ---------------------------------------------------------------------------
# Una fila por certificado MiPyME emitido desde 2016, con categoría (micro, pequeña,
# mediana tramo 1 y 2), provincia y si sigue vigente. Solo cuenta las empresas que
# pidieron el certificado, no todas las pymes que existen.
# No sirve como serie por año: la cantidad de certificados salta de unos 100.000 a más de
# 1,6 millones en 2024, así que solo usamos la foto de los certificados vigentes a la fecha
# del archivo. El archivo pesa unos 250 MB: lo bajamos a una carpeta temporal y guardamos
# solo el resumen.
URL_MIPYME = "https://cdn.produccion.gob.ar/cdn-sepyme/registro_mipyme_23-12-2024.csv"
FECHA_MIPYME = "2024-12-23"


def procesar_pymes():
    import tempfile

    resumen = CRUDOS / "registro_mipyme_vigentes_resumen.csv"
    if resumen.exists():
        print(f"  ya existe {resumen.name}, no se descarga")
        tabla = pd.read_csv(resumen)
    else:
        print("  descargando registro MiPyME (unos 250 MB) ...")
        with tempfile.TemporaryDirectory() as carpeta:
            archivo = Path(carpeta) / "mipyme.csv"
            with requests.get(URL_MIPYME, stream=True, timeout=600) as r:
                r.raise_for_status()
                with open(archivo, "wb") as f:
                    for trozo in r.iter_content(1 << 20):
                        f.write(trozo)
            mipyme = pd.read_csv(archivo, usecols=["Provincia", "Categoria", "Vigente"])
        tabla = (mipyme[mipyme.Vigente == 1].groupby(["Provincia", "Categoria"]).size()
                 .rename("certificados").reset_index())
        tabla.to_csv(resumen, index=False)
    tabla["provincia"] = tabla.Provincia.map(nombre_limpio)
    nombres = {"micro": "micro", "peq": "pequenas", "tramo1": "medianas_tramo1", "tramo2": "medianas_tramo2"}
    pymes = tabla.pivot_table(index="provincia", columns="Categoria", values="certificados",
                              aggfunc="sum", fill_value=0).rename(columns=nombres)
    pymes.columns = [f"pymes_{c}" for c in pymes.columns]
    pymes.insert(0, "pymes_total", pymes.sum(axis=1))
    pymes = pymes.reset_index()
    pob = pd.read_csv(CARPETA / "poblacion_provincia_anual.csv")
    pob = pob[pob.anio == int(FECHA_MIPYME[:4])][["provincia", "habitantes"]]
    pymes = pymes.merge(pob, on="provincia", how="left")
    pymes["pymes_cada_1000_hab"] = (pymes.pymes_total / pymes.habitantes * 1000).round(1)
    pymes = pymes.drop(columns="habitantes")
    pymes.insert(0, "provincia_iso", pymes.provincia.map(PROVINCIAS))
    pymes.insert(2, "anio", int(FECHA_MIPYME[:4]))
    pymes.insert(3, "fecha_corte", FECHA_MIPYME)
    pymes.sort_values("provincia").to_csv(CARPETA / "pymes_provincia.csv", index=False)
    print(f"  Pymes: {pymes.provincia.nunique()} provincias, {pymes.pymes_total.sum()} certificados vigentes "
          f"al {FECHA_MIPYME}")


# ---------------------------------------------------------------------------
# 14. Empresas con empleados registrados por provincia
# ---------------------------------------------------------------------------
# Serie principal: Observatorio de Empleo y Dinámica Empresarial (OEDE, Secretaría de Trabajo),
#   "Estadísticas regionales": empresas privadas con empleados registrados (SIPA) activas en
#   cada provincia, 1996-2024. Para 2024 trae además el tamaño (micro, pequeña, mediana, grande),
#   pero solo para industria, comercio y servicios.
#   Ojo: una empresa con empleados en varias provincias cuenta en cada una, así que la suma
#   de provincias da más que el total del país. Buenos Aires = partidos del GBA + resto.
# Complemento: CEP XXI (Ministerio de Economía), "Distribución geográfica de los
#   establecimientos productivos", 2021-2022: locales según cuántos empleados tienen.
URL_OEDE_RAMAS = "https://www.argentina.gob.ar/sites/default/files/provinciales_serie_empresas1_2.xlsx"
URL_OEDE_CUADROS = "https://www.argentina.gob.ar/sites/default/files/provinciales_serie_empresas2_2.xlsx"
URL_ESTABLECIMIENTOS = ("https://cdn.produccion.gob.ar/cdn-cep/establecimientos-productivos/"
                        "distribucion_establecimientos_productivos_sexo.csv")
# Código INDEC de cada provincia (el que usan casi todas las bases oficiales)
CODIGO_INDEC = {
    2: "Ciudad de Buenos Aires", 6: "Buenos Aires", 10: "Catamarca", 14: "Córdoba", 18: "Corrientes",
    22: "Chaco", 26: "Chubut", 30: "Entre Ríos", 34: "Formosa", 38: "Jujuy", 42: "La Pampa",
    46: "La Rioja", 50: "Mendoza", 54: "Misiones", 58: "Neuquén", 62: "Río Negro", 66: "Salta",
    70: "San Juan", 74: "San Luis", 78: "Santa Cruz", 82: "Santa Fe", 86: "Santiago del Estero",
    90: "Tucumán", 94: "Tierra del Fuego",
}
TAMANIOS = {"a. 1-9": "1_a_9", "b. 10-49": "10_a_49", "c. 50-199": "50_a_199",
            "d. 200-499": "200_a_499", "e. 500+": "500_o_mas"}


def provincia_oede(nombre):
    """El OEDE separa Buenos Aires en 'Partidos de GBA' y 'Resto de Buenos Aires'."""
    if "buenos aires" in nombre.lower() and "capital" not in nombre.lower() or "gba" in nombre.lower():
        return "Buenos Aires"
    return nombre_limpio(nombre)


def empresas_oede():
    # Serie 1996-2024: la fila TOTAL de la hoja de cada provincia
    hojas = pd.read_excel(descargar(URL_OEDE_RAMAS, "oede_empresas_provincia_ramas.xlsx"),
                          sheet_name=None, header=None)
    filas = []
    for hoja, tabla in hojas.items():
        if hoja in ("Carátula", "Indice", "Metodología", "Hoja1"):
            continue
        anios = tabla.iloc[3]
        total = tabla[tabla[1].astype(str).str.strip().str.upper() == "TOTAL"].iloc[0]
        for col in range(2, tabla.shape[1]):
            if pd.notna(anios[col]) and pd.notna(total[col]):
                filas.append({"provincia": provincia_oede(hoja), "anio": int(anios[col]),
                              "empresas_con_empleados": int(total[col])})
    serie = pd.DataFrame(filas).groupby(["provincia", "anio"], as_index=False).sum()

    # Tamaño en 2024 (Cuadro 3: industria, comercio y servicios)
    cuadro = pd.read_excel(descargar(URL_OEDE_CUADROS, "oede_empresas_provincia_cuadros.xlsx"),
                           sheet_name="T3", header=None)
    provincias = cuadro.iloc[1]
    inicio = cuadro[cuadro[0].astype(str).str.strip() == "Total"].index[0]  # bloque "Total" de los 3 sectores
    tamanios = {}
    for fila in range(inicio + 1, inicio + 5):
        nombre = str(cuadro.iloc[fila, 0]).strip().lower().replace("microempresas", "micro")
        nombre = nombre.replace("ñ", "n")
        for col in range(1, cuadro.shape[1]):
            if pd.notna(provincias[col]) and provincias[col] != "Total":
                clave = (provincia_oede(str(provincias[col])), 2024)
                tamanios.setdefault(clave, {})
                columna = f"empresas_{nombre}_ind_com_serv"
                tamanios[clave][columna] = tamanios[clave].get(columna, 0) + int(round(cuadro.iloc[fila, col]))
    tamanios = pd.DataFrame([{"provincia": p, "anio": a, **v} for (p, a), v in tamanios.items()])
    return serie.merge(tamanios, on=["provincia", "anio"], how="left")


def locales_cep():
    import tempfile

    resumen = CRUDOS / "cep_establecimientos_resumen.csv"
    if resumen.exists():
        print(f"  ya existe {resumen.name}, no se descarga")
        tabla = pd.read_csv(resumen)
    else:
        print("  descargando establecimientos productivos (unos 100 MB) ...")
        with tempfile.TemporaryDirectory() as carpeta:
            archivo = Path(carpeta) / "establecimientos.csv"
            with requests.get(URL_ESTABLECIMIENTOS, stream=True, timeout=600) as r:
                r.raise_for_status()
                with open(archivo, "wb") as f:
                    for trozo in r.iter_content(1 << 20):
                        f.write(trozo)
            locales = pd.read_csv(archivo, usecols=["cuit", "anio", "provincia_id", "empleo"])
        por_tamanio = locales.pivot_table(index=["provincia_id", "anio"], columns="empleo", values="cuit",
                                          aggfunc="size", fill_value=0).rename(columns=TAMANIOS)
        por_tamanio.columns = [f"locales_{c}_empleados" for c in por_tamanio.columns]
        empresas = locales.groupby(["provincia_id", "anio"]).cuit.nunique().rename("empresas_con_empleados")
        tabla = pd.concat([empresas, por_tamanio], axis=1).reset_index()
        tabla.to_csv(resumen, index=False)
    tabla["provincia"] = tabla.provincia_id.map(CODIGO_INDEC)
    tabla = tabla.rename(columns={"empresas_con_empleados": "cep_empresas_con_empleados"})
    columnas = [c for c in tabla.columns if c.startswith("locales_")]
    tabla = tabla.rename(columns={c: "cep_" + c for c in columnas})
    return tabla.drop(columns="provincia_id")


def procesar_empresas():
    tabla = empresas_oede().merge(locales_cep(), on=["provincia", "anio"], how="outer")
    pob = pd.read_csv(CARPETA / "poblacion_provincia_anual.csv")[["provincia", "anio", "habitantes"]]
    tabla = tabla.merge(pob, on=["provincia", "anio"], how="left")
    tabla.insert(3, "empresas_cada_1000_hab", (tabla.empresas_con_empleados / tabla.habitantes * 1000).round(1))
    tabla = tabla.drop(columns="habitantes")
    tabla.insert(0, "provincia_iso", tabla.provincia.map(PROVINCIAS))
    tabla.sort_values(["provincia", "anio"]).to_csv(CARPETA / "empresas_con_empleados_provincia_anual.csv",
                                                   index=False)
    print(f"  Empresas: {tabla.provincia.nunique()} provincias, {tabla.anio.min()}-{tabla.anio.max()}; "
          f"total 2024 (suma de provincias): {tabla[tabla.anio == 2024].empresas_con_empleados.sum()}")


# ---------------------------------------------------------------------------
# 15. Carga impositiva provincial
# ---------------------------------------------------------------------------
# Dirección Nacional de Asuntos Provinciales (Ministerio de Economía):
#   - "Serie de Tributarios de Origen Provincial 1984-2025": lo que recauda cada provincia con
#     sus propios impuestos (Ingresos Brutos, Inmobiliario, Sellos, Automotores y otros), en
#     millones de pesos de cada año. Usamos desde 1991: antes hubo cambios de moneda y no está
#     claro en qué unidad vienen los números.
#   - "Alícuotas teóricas de Ingresos Brutos" 2024 y 2025: la tasa general de cada actividad.
# Para comparar entre provincias y años calculamos:
#   - % del PBG (estimado): el PBG en pesos de cada año no se publica, así que lo estimamos
#     repartiendo el PIB nominal del país (Banco Mundial) según el peso de cada provincia en
#     el VAB de CEPAL. Supone que los precios suben igual en todas las provincias.
#   - Recaudación por habitante en pesos de 2024 (con el deflactor del PIB del Banco Mundial).
URL_TOP = "https://www.argentina.gob.ar/sites/default/files/serie_top_1984_2025.csv"
URL_ALICUOTAS_IIBB = "https://www.argentina.gob.ar/sites/default/files/{anio}_ib.xlsx"
URL_BM_ARG = "https://api.worldbank.org/v2/country/ARG/indicator/{indicador}?format=json&date=1990:2030&per_page=100"
IMPUESTOS = {"ingresos brutos": "ingresos_brutos", "inmobiliario": "inmobiliario", "sellos": "sellos",
             "automotores": "automotores", "otros": "otros"}


def serie_banco_mundial(indicador):
    import json

    archivo = descargar(URL_BM_ARG.format(indicador=indicador), f"bm_arg_{indicador}.json")
    datos = json.loads(archivo.read_text())[1]
    return pd.Series({int(x["date"]): x["value"] for x in datos if x["value"] is not None})


def alicuotas_iibb():
    filas = []
    for anio in (2024, 2025):
        tabla = pd.read_excel(descargar(URL_ALICUOTAS_IIBB.format(anio=anio), f"dnap_alicuotas_iibb_{anio}.xlsx"),
                              header=None)
        enc = tabla[tabla[2].astype(str).str.contains("Consenso", na=False)].index[0]
        columnas = {col: nombre_limpio(str(tabla.iloc[enc, col]).replace("Sgo del", "Santiago del"))
                    for col in range(3, tabla.shape[1]) if pd.notna(tabla.iloc[enc, col])}
        for fila in range(enc + 1, len(tabla)):
            actividad = tabla.iloc[fila, 0]
            # Las filas con nombre en la primera columna son las actividades principales;
            # las de abajo (sin nombre) son excepciones dentro de esa actividad.
            if pd.isna(actividad) or str(actividad).startswith("Fuente"):
                continue
            for col, provincia in columnas.items():
                valor = tabla.iloc[fila, col]
                if pd.isna(valor):
                    continue
                # Casi siempre es un número (0,035 = 3,5 %); a veces es texto ("exenta",
                # "0,25% + 0,50% FFSS"): lo guardamos tal cual en alicuota_texto.
                texto = " ".join(str(valor).split())
                try:
                    pct, texto = round(float(valor) * 100, 3), ""
                except ValueError:
                    pct = 0.0 if texto.lower() == "exenta" else None
                filas.append({"provincia": provincia, "anio": anio, "actividad": " ".join(str(actividad).split()),
                              "alicuota_pct": pct, "alicuota_texto": texto})
    ali = pd.DataFrame(filas)
    ali.insert(0, "provincia_iso", ali.provincia.map(PROVINCIAS))
    ali.to_csv(CARPETA / "alicuotas_ingresos_brutos_provincia.csv", index=False)
    return ali


def procesar_impuestos():
    top = pd.read_csv(descargar(URL_TOP, "dnap_serie_top_1984_2025.csv"), sep=";", decimal=",")
    top["provincia"] = top.provincia.replace({"c.a.b.a.": "caba", "sgo. del estero": "santiago del estero"}).map(nombre_limpio)
    top["impuesto"] = top.impuesto.map(IMPUESTOS)
    top = top[top.ano >= 1991]
    imp = top.pivot_table(index=["provincia", "ano"], columns="impuesto", values="monto", aggfunc="sum")
    imp.columns = [f"recaudacion_{c}_mill_pesos" for c in imp.columns]
    imp.insert(0, "recaudacion_propia_mill_pesos", imp.sum(axis=1))
    imp = imp[imp.recaudacion_propia_mill_pesos > 0]  # La Pampa 2025 viene en cero (sin dato)
    imp = imp.reset_index().rename(columns={"ano": "anio"})
    imp["pct_ingresos_brutos_en_total"] = (100 * imp.recaudacion_ingresos_brutos_mill_pesos
                                           / imp.recaudacion_propia_mill_pesos).round(1)

    # PBG nominal aproximado = PIB nominal del país × peso de la provincia en el VAB (CEPAL)
    vab = pd.read_csv(CARPETA / "vab_provincia_grupos_largo.csv")
    columna_vab = [c for c in vab.columns if c.startswith("vab")][0]
    vab = vab.groupby(["provincia", "anio"])[columna_vab].sum().reset_index()
    vab["peso"] = vab[columna_vab] / vab.groupby("anio")[columna_vab].transform("sum")
    pib = serie_banco_mundial("NY.GDP.MKTP.CN") / 1e6  # millones de pesos
    vab["pbg_nominal_estimado_mill_pesos"] = vab.peso * vab.anio.map(pib)
    imp = imp.merge(vab[["provincia", "anio", "pbg_nominal_estimado_mill_pesos"]], on=["provincia", "anio"], how="left")
    imp["presion_tributaria_pct_pbg_estimado"] = (100 * imp.recaudacion_propia_mill_pesos
                                               / imp.pbg_nominal_estimado_mill_pesos).round(2)

    # Por habitante, en pesos de 2024
    deflactor = serie_banco_mundial("NY.GDP.DEFL.ZS")
    pob = pd.read_csv(CARPETA / "poblacion_provincia_anual.csv")[["provincia", "anio", "habitantes"]]
    imp = imp.merge(pob, on=["provincia", "anio"], how="left")
    imp["recaudacion_por_habitante_pesos_2024"] = (imp.recaudacion_propia_mill_pesos * 1e6 / imp.habitantes
                                                   * deflactor[2024] / imp.anio.map(deflactor)).round(0)
    imp = imp.drop(columns=["habitantes", "pbg_nominal_estimado_mill_pesos"])

    # Alícuotas generales de Ingresos Brutos en dos actividades clave
    ali = alicuotas_iibb()
    for actividad, nombre in [("Comercio", "comercio"), ("Industria Manufacturera", "industria")]:
        sub = ali[ali.actividad.str.startswith(actividad)][["provincia", "anio", "alicuota_pct"]]
        imp = imp.merge(sub.rename(columns={"alicuota_pct": f"alicuota_iibb_{nombre}_pct"}),
                        on=["provincia", "anio"], how="left")
    imp.insert(0, "provincia_iso", imp.provincia.map(PROVINCIAS))
    imp.sort_values(["provincia", "anio"]).to_csv(CARPETA / "carga_impositiva_provincia_anual.csv", index=False)
    ult = imp[imp.anio == 2024]
    print(f"  Impuestos: {imp.provincia.nunique()} provincias, {imp.anio.min()}-{imp.anio.max()}; "
          f"presión 2024 (mediana) {ult.presion_tributaria_pct_pbg_estimado.median()} % del PBG; "
          f"alícuotas: {len(ali)} filas")


# ---------------------------------------------------------------------------
# 16. Salario promedio (OEDE, Secretaría de Trabajo)
# ---------------------------------------------------------------------------
# Remuneración promedio por todo concepto de los asalariados registrados del sector privado
# (SIPA), por provincia, 1995-2025, en pesos de cada año. Lo pasamos también a pesos de 2024
# con el deflactor del PIB. El OEDE separa Buenos Aires en partidos del GBA y resto: los
# juntamos con un promedio ponderado por la cantidad de puestos de trabajo de cada parte.
URL_OEDE_SALARIOS = "https://www.argentina.gob.ar/sites/default/files/provinciales_serie_remuneraciones_anual_3.xlsx"
URL_OEDE_EMPLEO = "https://www.argentina.gob.ar/sites/default/files/provinciales_serie_empleo_anual_3.xlsx"


def tabla_anual_oede(hoja, primera_fila_anios, filas_por_nombre):
    """Lee una tabla OEDE con una fila de años y una fila por provincia."""
    anios = hoja.iloc[primera_fila_anios]
    filas = []
    for i in range(primera_fila_anios + 1, len(hoja)):
        nombre = hoja.iloc[i, 0]
        if not isinstance(nombre, str) or nombre.strip() not in filas_por_nombre:
            continue
        for col in range(1, hoja.shape[1]):
            if pd.notna(anios[col]) and pd.notna(hoja.iloc[i, col]) and not isinstance(hoja.iloc[i, col], str):
                filas.append({"unidad": nombre.strip(), "anio": int(anios[col]), "valor": float(hoja.iloc[i, col])})
    return pd.DataFrame(filas)


def procesar_salarios():
    sal = pd.read_excel(descargar(URL_OEDE_SALARIOS, "oede_remuneraciones_provincia_anual.xlsx"),
                        sheet_name="Total", header=None)
    fila_anios = sal[sal[0].astype(str).str.strip() == "Provincia"].index[0]
    nombres = [str(x).strip() for x in sal[0].dropna() if str(x).strip().isupper()]
    sal = tabla_anual_oede(sal, fila_anios, set(nombres)).rename(columns={"valor": "salario"})

    emp = pd.read_excel(descargar(URL_OEDE_EMPLEO, "oede_empleo_provincia_anual.xlsx"), sheet_name="T5", header=None)
    unidades_empleo = {"Partidos de GBA": "GRAN BUENOS AIRES", "Capital Federal": "CAPITAL FEDERAL",
                       "Resto de Buenos Aires": "BUENOS AIRES"}
    nombres_empleo = {n: n.upper() for n in emp[0].dropna().astype(str).str.strip()
                      if n in PROVINCIAS or nombre_limpio(n) in PROVINCIAS}
    nombres_empleo.update(unidades_empleo)
    emp = tabla_anual_oede(emp, 1, set(nombres_empleo)).rename(columns={"valor": "puestos_miles"})
    emp["unidad"] = emp.unidad.map(nombres_empleo).str.translate(SIN_TILDES).str.upper()

    datos = sal.merge(emp, on=["unidad", "anio"], how="left")
    # En el OEDE, "GRAN BUENOS AIRES" son los partidos del conurbano y "BUENOS AIRES" el resto
    datos["provincia"] = datos.unidad.replace({"GRAN BUENOS AIRES": "BUENOS AIRES"}).map(nombre_limpio)
    datos = datos[datos.provincia.isin(PROVINCIAS)]
    datos["salario_x_puestos"] = datos.salario * datos.puestos_miles
    prov = datos.groupby(["provincia", "anio"]).agg(salario_x_puestos=("salario_x_puestos", "sum"),
                                                   puestos_miles=("puestos_miles", "sum"),
                                                   salario_simple=("salario", "mean")).reset_index()
    prov["puestos_miles"] = prov.puestos_miles.where(prov.puestos_miles > 0)  # 1995: sin dato de empleo
    prov["salario_promedio_mensual_pesos"] = (prov.salario_x_puestos / prov.puestos_miles).fillna(prov.salario_simple).round(0)
    deflactor = serie_banco_mundial("NY.GDP.DEFL.ZS")
    prov["salario_promedio_mensual_pesos_2024"] = (prov.salario_promedio_mensual_pesos * deflactor[2024]
                                                   / prov.anio.map(deflactor)).round(0)
    prov["puestos_asalariados_privados_registrados"] = (prov.puestos_miles * 1000).round(0)
    prov = prov[["provincia", "anio", "salario_promedio_mensual_pesos", "salario_promedio_mensual_pesos_2024",
                 "puestos_asalariados_privados_registrados"]]
    prov.insert(0, "provincia_iso", prov.provincia.map(PROVINCIAS))
    prov.sort_values(["provincia", "anio"]).to_csv(CARPETA / "salarios_provincia_anual.csv", index=False)
    print(f"  Salarios: {prov.provincia.nunique()} provincias, {prov.anio.min()}-{prov.anio.max()}")


# ---------------------------------------------------------------------------
# 17. Canasta básica alimentaria (CBA) y canasta básica total (CBT)
# ---------------------------------------------------------------------------
# El INDEC publica todos los meses la CBA y la CBT del Gran Buenos Aires por "adulto
# equivalente" (un varón de 30 a 45 años). Para las otras 5 regiones publica las canastas
# en los informes de pobreza (PDF); el paquete de R "eph" (rOpenSci) las tiene juntas en
# una tabla trimestral. De ahí sacamos cuánto más cara o barata es cada región que el GBA
# y lo aplicamos a la serie mensual del INDEC. Es un dato por REGIÓN, no por provincia:
# todas las provincias de una región tienen el mismo valor. Buenos Aires usa el del GBA
# (la mayoría de su gente vive en el conurbano; el interior de la provincia es Pampeana,
# un 1,5 % más barata).
URL_CBA_CBT = "https://www.indec.gob.ar/ftp/cuadros/sociedad/serie_cba_cbt.xls"
URL_CANASTAS_REGIONALES = "https://raw.githubusercontent.com/holatam/data/master/eph/canasta/canastas.rds"
REGION_EPH = {1: "GBA", 40: "Noroeste", 41: "Noreste", 42: "Cuyo", 43: "Pampeana", 44: "Patagonia"}
REGION_DE_PROVINCIA = {
    "Ciudad de Buenos Aires": "GBA", "Buenos Aires": "GBA",
    "Córdoba": "Pampeana", "Santa Fe": "Pampeana", "Entre Ríos": "Pampeana", "La Pampa": "Pampeana",
    "Mendoza": "Cuyo", "San Juan": "Cuyo", "San Luis": "Cuyo",
    "Corrientes": "Noreste", "Chaco": "Noreste", "Formosa": "Noreste", "Misiones": "Noreste",
    "Jujuy": "Noroeste", "Salta": "Noroeste", "Tucumán": "Noroeste", "Catamarca": "Noroeste",
    "Santiago del Estero": "Noroeste", "La Rioja": "Noroeste",
    "Neuquén": "Patagonia", "Río Negro": "Patagonia", "Chubut": "Patagonia", "Santa Cruz": "Patagonia",
    "Tierra del Fuego": "Patagonia",
}


def canastas_mensuales_por_region():
    """CBA y CBT mensual por adulto equivalente para cada región (pesos de cada mes)."""
    gba = pd.read_excel(descargar(URL_CBA_CBT, "indec_serie_cba_cbt.xls"), sheet_name="CBA-CBT", header=None)
    gba = gba[pd.to_datetime(gba[0], errors="coerce").notna()][[0, 1, 3]]
    gba.columns = ["mes", "cba", "cbt"]
    gba["mes"] = pd.to_datetime(gba.mes)
    gba[["cba", "cbt"]] = gba[["cba", "cbt"]].astype(float)

    # Relación de cada región con el GBA, por trimestre
    regionales = CRUDOS / "canastas_regionales_trimestrales.csv"
    if not regionales.exists() or REFRESCAR:
        import pyreadr  # solo hace falta la primera vez

        rds = descargar(URL_CANASTAS_REGIONALES, "canastas_regionales.rds")
        list(pyreadr.read_r(str(rds)).values())[0].to_csv(regionales, index=False)
    reg = pd.read_csv(regionales)
    reg["anio"] = reg.periodo.astype(str).str[:4].astype(int)
    reg["trimestre"] = reg.periodo.astype(str).str[5].astype(int)
    base = reg[reg.region == "GBA"].set_index(["anio", "trimestre"])[["CBA", "CBT"]]
    reg = reg.join(base, on=["anio", "trimestre"], rsuffix="_gba")
    reg["rel_cba"], reg["rel_cbt"] = reg.CBA / reg.CBA_gba, reg.CBT / reg.CBT_gba

    filas = []
    for region in REGION_EPH.values():
        r = reg[reg.region == region].sort_values(["anio", "trimestre"])
        for _, m in gba.iterrows():
            trimestre = (m.mes.month - 1) // 3 + 1
            anteriores = r[(r.anio < m.mes.year) | ((r.anio == m.mes.year) & (r.trimestre <= trimestre))]
            rel = (anteriores if len(anteriores) else r).iloc[-1]  # después del último dato, se repite
            filas.append({"region": region, "mes": m.mes, "cba": m.cba * rel.rel_cba, "cbt": m.cbt * rel.rel_cbt})
    return pd.DataFrame(filas)


def procesar_canastas():
    can = canastas_mensuales_por_region()
    can["anio"] = can.mes.dt.year
    anual = can.groupby(["region", "anio"]).agg(cba_adulto_equivalente_pesos=("cba", "mean"),
                                                cbt_adulto_equivalente_pesos=("cbt", "mean"),
                                                meses_con_dato=("mes", "size")).reset_index()
    filas = [{"provincia": p, "region": r} for p, r in REGION_DE_PROVINCIA.items()]
    tabla = pd.DataFrame(filas).merge(anual, on="region")
    # Ejemplo del INDEC: hogar de 4 (pareja de 35 y 31 años, hijos de 6 y 8) = 3,09 adultos equivalentes
    tabla["cbt_hogar_tipo_4_personas_pesos"] = tabla.cbt_adulto_equivalente_pesos * 3.09
    for c in ["cba_adulto_equivalente_pesos", "cbt_adulto_equivalente_pesos", "cbt_hogar_tipo_4_personas_pesos"]:
        tabla[c] = tabla[c].round(0)
    tabla.insert(0, "provincia_iso", tabla.provincia.map(PROVINCIAS))
    # Valores de la región (no de la provincia), reconstruidos con los cocientes región/GBA
    tabla = tabla.rename(columns={c: c.replace("_pesos", "_pesos_estimado_por_region")
                                  for c in ["cba_adulto_equivalente_pesos", "cbt_adulto_equivalente_pesos",
                                            "cbt_hogar_tipo_4_personas_pesos"]})
    tabla.sort_values(["provincia", "anio"]).to_csv(CARPETA / "canastas_provincia_anual.csv", index=False)
    print(f"  Canastas: {tabla.region.nunique()} regiones, {tabla.anio.min()}-{tabla.anio.max()}")


# ---------------------------------------------------------------------------
# 18. Pobreza, indigencia y Gini con la Encuesta Permanente de Hogares (EPH, INDEC)
# ---------------------------------------------------------------------------
# El INDEC publica la pobreza por aglomerado solo en PDF y el Gini solo para el país. Así
# que los calculamos nosotros con los microdatos de la EPH, siguiendo el método del INDEC:
#   - Pobre: persona en un hogar cuyo ingreso total no alcanza la CBT de su región
#     multiplicada por los adultos equivalentes del hogar. Indigente: lo mismo con la CBA.
#   - Gini del ingreso per cápita familiar de las personas.
# Ojo: la EPH solo cubre 31 ciudades grandes (aglomerados urbanos). El dato de cada
# provincia sale de sus aglomerados (por ejemplo Río Negro = Viedma) y es un promedio de los
# 4 trimestres del año. Es una estimación propia: comparamos el total país con el oficial.
URL_EPH = "https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_usu_{t}_Trim_{anio}_txt.zip"
# Algunos trimestres tienen otro nombre de archivo (por ejemplo "EPH_usu_2doTrim_2016_txt.zip")
URL_EPH_VARIANTES = ["EPH_usu_{t}_Trim_{anio}_txt.zip", "EPH_usu_{o}_Trim_{anio}_txt.zip", "EPH_usu_{o}Trim_{anio}_txt.zip"]
ORDINAL = {1: "1er", 2: "2do", 3: "3er", 4: "4to"}
AGLOMERADO_PROVINCIA = {
    2: "Buenos Aires", 3: "Buenos Aires", 33: "Buenos Aires", 34: "Buenos Aires", 38: "Buenos Aires",
    32: "Ciudad de Buenos Aires", 4: "Santa Fe", 5: "Santa Fe", 6: "Entre Ríos", 14: "Entre Ríos",
    7: "Misiones", 8: "Chaco", 9: "Chubut", 91: "Chubut", 10: "Mendoza", 12: "Corrientes",
    13: "Córdoba", 36: "Córdoba", 15: "Formosa", 17: "Neuquén", 18: "Santiago del Estero",
    19: "Jujuy", 20: "Santa Cruz", 22: "Catamarca", 23: "Salta", 25: "La Rioja", 26: "San Luis",
    27: "San Juan", 29: "Tucumán", 30: "La Pampa", 31: "Tierra del Fuego", 93: "Río Negro",
}


def adulto_equivalente(edad, sexo):
    """Tabla de necesidades energéticas del INDEC (sexo: 1 varón, 2 mujer; edad -1 = menor de 1 año)."""
    import numpy as np

    mujer = [0.35, 0.37, 0.46, 0.51, 0.55, 0.60, 0.64, 0.66, 0.68, 0.69,
             0.70, 0.72, 0.74, 0.76, 0.76, 0.77, 0.77, 0.77]
    varon = [0.35, 0.37, 0.46, 0.51, 0.55, 0.60, 0.64, 0.66, 0.68, 0.69,
             0.79, 0.82, 0.85, 0.90, 0.96, 1.00, 1.03, 1.04]
    edad = np.clip(edad, 0, None)
    tramos = [(18, 29, 0.76, 1.02), (30, 45, 0.77, 1.00), (46, 60, 0.76, 1.00), (61, 75, 0.67, 0.83),
              (76, 200, 0.63, 0.74)]
    resultado = np.where(sexo == 1, np.take(varon, np.minimum(edad, 17)), np.take(mujer, np.minimum(edad, 17)))
    for desde, hasta, m, v in tramos:
        resultado = np.where((edad >= desde) & (edad <= hasta), np.where(sexo == 1, v, m), resultado)
    return resultado


def gini_ponderado(ingreso, peso):
    import numpy as np

    orden = np.argsort(ingreso)
    y, w = np.asarray(ingreso, float)[orden], np.asarray(peso, float)[orden]
    acumulado = np.cumsum(y * w)
    anterior = np.concatenate([[0], acumulado[:-1]])
    return 1 - np.sum(w * (acumulado + anterior)) / (w.sum() * acumulado[-1])


def personas_eph(anio, trimestre, canastas):
    import io
    import zipfile

    contenido = None
    for variante in URL_EPH_VARIANTES:
        archivo = variante.format(t=trimestre, o=ORDINAL[trimestre], anio=anio)
        r = requests.get(URL_EPH.rsplit("/", 1)[0] + "/" + archivo, timeout=300)
        if r.status_code == 200 and r.content.startswith(b"PK"):
            contenido = r.content
            break
    if contenido is None:
        return None  # ese trimestre no está publicado
    with zipfile.ZipFile(io.BytesIO(contenido)) as z:
        # La base de personas se llama "individual" o "personas" según el trimestre
        nombre = [n for n in z.namelist() if ("individual" in n.lower() or "personas" in n.lower())
                  and n.lower().endswith(".txt")][0]
        p = pd.read_csv(z.open(nombre), sep=";", decimal=",", low_memory=False,
                        usecols=["CODUSU", "NRO_HOGAR", "REGION", "AGLOMERADO", "CH04", "CH06", "ITF", "IPCF", "PONDIH"])
    # Algunos trimestres traen los ingresos como texto con punto decimal (ej. 1.º y 3.º de 2021)
    for columna in ["REGION", "AGLOMERADO", "CH04", "CH06", "ITF", "IPCF", "PONDIH"]:
        p[columna] = pd.to_numeric(p[columna].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    p["ae"] = adulto_equivalente(p.CH06.to_numpy(), p.CH04.to_numpy())
    p["ae_hogar"] = p.groupby(["CODUSU", "NRO_HOGAR"]).ae.transform("sum")
    meses = canastas[(canastas.mes.dt.year == anio) & ((canastas.mes.dt.month - 1) // 3 + 1 == trimestre)]
    lineas = meses.groupby("region")[["cba", "cbt"]].mean()
    p["region"] = p.REGION.map(REGION_EPH)
    p["pobre"] = p.ITF < p.region.map(lineas.cbt) * p.ae_hogar
    p["indigente"] = p.ITF < p.region.map(lineas.cba) * p.ae_hogar
    p["provincia"] = p.AGLOMERADO.map(AGLOMERADO_PROVINCIA)
    p["anio"], p["trimestre"] = anio, trimestre
    return p[p.PONDIH > 0][["anio", "trimestre", "provincia", "IPCF", "PONDIH", "pobre", "indigente"]]


def procesar_eph():
    resumen = CRUDOS / "eph_resumen_provincia_anual.csv"
    control = CRUDOS / "eph_control_total_pais_semestral.csv"
    if resumen.exists() and not REFRESCAR:
        print(f"  ya existe {resumen.name}, no se recalcula (borralo para actualizar)")
        tabla = pd.read_csv(resumen)
    else:
        from datetime import date

        canastas = canastas_mensuales_por_region()
        filas, pais = [], []
        for anio in range(2016, date.today().year + 1):
            trimestres = []
            for t in range(1, 5):
                personas = personas_eph(anio, t, canastas)
                if personas is not None:
                    print(f"  EPH {t}.º trimestre {anio}: {len(personas)} personas")
                    trimestres.append(personas)
            if not trimestres:
                continue
            datos = pd.concat(trimestres)
            for semestre, g in datos.groupby((datos.trimestre > 2) + 1):  # control contra el dato oficial
                pais.append({"anio": anio, "semestre": semestre,
                             "pct_personas_pobres": round(100 * (g.pobre * g.PONDIH).sum() / g.PONDIH.sum(), 1)})
            for provincia, g in datos.groupby("provincia"):
                filas.append({"provincia": provincia, "anio": anio, "trimestres_con_dato": g.trimestre.nunique(),
                              "pct_personas_pobres": 100 * (g.pobre * g.PONDIH).sum() / g.PONDIH.sum(),
                              "pct_personas_indigentes": 100 * (g.indigente * g.PONDIH).sum() / g.PONDIH.sum(),
                              "gini_ingreso_per_capita_familiar": gini_ponderado(g.IPCF, g.PONDIH),
                              "casos_encuestados": len(g)})
        tabla = pd.DataFrame(filas)
        tabla.to_csv(resumen, index=False)
        pd.DataFrame(pais).to_csv(control, index=False)
    for c, dec in [("pct_personas_pobres", 1), ("pct_personas_indigentes", 1), ("gini_ingreso_per_capita_familiar", 3)]:
        tabla[c] = tabla[c].round(dec)
    tabla.insert(0, "provincia_iso", tabla.provincia.map(PROVINCIAS))
    # Cálculo propio con la EPH (solo 31 aglomerados urbanos), no es un dato oficial por provincia
    tabla = tabla.rename(columns={
        "pct_personas_pobres": "pct_personas_pobres_estimado",
        "pct_personas_indigentes": "pct_personas_indigentes_estimado",
        "gini_ingreso_per_capita_familiar": "gini_ingreso_per_capita_familiar_estimado_grandes_ciudades"})
    tabla.sort_values(["provincia", "anio"]).to_csv(CARPETA / "pobreza_gini_provincia_anual.csv", index=False)
    print(f"  Pobreza y Gini: {tabla.provincia.nunique()} provincias, {tabla.anio.min()}-{tabla.anio.max()}")


# ---------------------------------------------------------------------------
# 19. Fiestas populares y festivales (Ministerio de Cultura, Mapa Cultural)
# ---------------------------------------------------------------------------
# datos.cultura.gob.ar está detrás de un desafío de Cloudflare y no deja bajar el archivo
# con un script: hay que bajar a mano "10_fiestaspopulares_festivales-datos_abiertos-2.csv"
# y guardarlo como crudos/cultura_fiestas_festivales.csv.
# Es una foto (relevamiento con último año de realización 2019-2023), no una serie anual.
# Cada provincia cargó sus fiestas con distinto detalle: comparar cantidades con cuidado.

def procesar_festivales():
    archivo = CRUDOS / "cultura_fiestas_festivales.csv"
    if not archivo.exists():
        print(f"  falta {archivo.name}: bajarlo a mano de datos.cultura.gob.ar (ver comentario del paso 19)")
        return
    d = pd.read_csv(archivo, dtype=str)
    d.columns = [c.strip() for c in d.columns]
    d = d.apply(lambda col: col.str.strip())
    d = d.replace("s/d", pd.NA)

    lista = pd.DataFrame({
        "provincia": d.cod_prov.astype(int).map(CODIGO_INDEC),
        "departamento": d.Departamento,
        "localidad": d["Localidad/Paraje"],
        "nombre": d.Nombre,
        "categoria": d.Categoria,
        "tematica": d["Temática_principal"],
        "gestion": d["Tipo de gestion"],
        "entrada": d.Tipo_Entrada,
        "mes": d["Mes de realización"].str.capitalize(),
        "asistentes_aprox": pd.to_numeric(d["Cantidad aprox de asistentes"].str.replace(",", "", regex=False),
                                          errors="coerce"),
        "anio_primera_edicion": pd.to_numeric(d["Año_primera_edicion"], errors="coerce").astype("Int64"),
        "ultimo_anio_realizacion": pd.to_numeric(d["último año de realizacion"], errors="coerce").astype("Int64"),
        "latitud": pd.to_numeric(d.Latitud, errors="coerce"),
        "longitud": pd.to_numeric(d.Longitud, errors="coerce"),
        "fuente": d.Fuente,
    })
    lista.insert(0, "provincia_iso", lista.provincia.map(PROVINCIAS))
    lista.sort_values(["provincia", "nombre"]).to_csv(CARPETA / "festivales_lista.csv", index=False)

    def contar(columna, valores, prefijo):
        return pd.DataFrame({f"{prefijo}_{nombre}": (lista[columna] == valor).groupby(lista.provincia).sum()
                             for valor, nombre in valores.items()})

    tabla = pd.concat([
        lista.groupby("provincia").size().rename("festivales_total"),
        contar("categoria", {"Fiesta y/o festival": "fiestas_festivales", "Aniversario": "aniversarios",
                             "Carnaval": "carnavales"}, "cantidad"),
        contar("tematica", {"Religiosa / de Culto": "religiosa", "Cívico / Histórica": "civico_historica",
                            "Artística": "artistica", "Tradicionales": "tradicional", "Folclórico": "folclorica",
                            "Productiva": "productiva", "Gastronómica": "gastronomica",
                            "Expresiones del carnaval": "carnaval",
                            "Pueblos Indígenas/Originarios": "pueblos_originarios", "Otra": "otra"}, "tematica"),
        contar("gestion", {"Público": "publica", "Privado": "privada", "Mixto": "mixta"}, "gestion"),
        contar("entrada", {"Gratuita": "gratuita", "Paga": "paga", "Mixta": "mixta"}, "entrada"),
        lista.groupby("provincia").asistentes_aprox.count().rename("festivales_con_asistentes_informados"),
        lista.groupby("provincia").asistentes_aprox.sum().rename("asistentes_aprox_suma"),
    ], axis=1).reset_index()
    poblacion = pd.read_csv(CARPETA / "poblacion_provincia_anual.csv").query("anio == 2022")
    tabla = tabla.merge(poblacion[["provincia", "habitantes"]], on="provincia", how="left")
    tabla["festivales_cada_100_mil_habitantes"] = (100_000 * tabla.festivales_total / tabla.habitantes).round(1)
    tabla = tabla.drop(columns="habitantes")
    tabla.insert(0, "provincia_iso", tabla.provincia.map(PROVINCIAS))
    tabla.sort_values("provincia").to_csv(CARPETA / "festivales_provincia.csv", index=False)
    print(f"  Festivales: {len(lista)} en {tabla.provincia.nunique()} provincias")


if __name__ == "__main__":
    CRUDOS.mkdir(exist_ok=True)
    print("1. VAB por provincia y rama (CEPAL)")
    procesar_vab()
    print("2. Petróleo y gas (Secretaría de Energía)")
    procesar_hidrocarburos()
    print("3. Agricultura (MAGyP)")
    procesar_agricultura()
    print("4. Ganadería (MAGyP / SENASA)")
    procesar_ganaderia()
    print("5. Indicadores provincia-año (PBG per cápita, sector público, turismo)")
    procesar_indicadores()
    print("6. Censos 2010 y 2022 (INDEC): vivienda, servicios y educación")
    procesar_censos()
    print("7. Turismo: Encuesta de Ocupación Hotelera")
    procesar_turismo()
    print("8. Temperatura media anual (Banco Mundial, ERA5)")
    procesar_temperatura()
    print("9. Habitantes por año (proyecciones INDEC)")
    procesar_poblacion()
    print("10. Gobierno provincial: ganador de cada elección a gobernador")
    procesar_gobernadores()
    print("11. Diputados y senadores nacionales por provincia")
    procesar_legisladores()
    print("12. Salud: vacuna triple viral y médicos (Ministerio de Salud)")
    procesar_salud()
    print("13. Pymes con certificado MiPyME vigente")
    procesar_pymes()
    print("14. Empresas con empleados registrados (OEDE y CEP XXI)")
    procesar_empresas()
    print("15. Carga impositiva provincial (Ministerio de Economía)")
    procesar_impuestos()
    print("16. Salario promedio de los asalariados registrados privados (OEDE)")
    procesar_salarios()
    print("17. Canasta básica alimentaria y total (INDEC, por región)")
    procesar_canastas()
    print("18. Pobreza, indigencia y Gini (microdatos EPH, INDEC)")
    procesar_eph()
    print("19. Fiestas populares y festivales (Ministerio de Cultura, archivo bajado a mano)")
    procesar_festivales()
