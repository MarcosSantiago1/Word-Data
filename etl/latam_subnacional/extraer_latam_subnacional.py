"""
LATINOAMÉRICA POR SUBDIVISIÓN: estados, departamentos, provincias y regiones de 20 países.

Es la versión latinoamericana de argentina_provincias/: la misma idea (una fila por
subdivisión + año), pero para Bolivia, Brasil, Chile, Colombia, Costa Rica, Cuba, Ecuador,
El Salvador, Guatemala, Haití, Honduras, México, Nicaragua, Panamá, Paraguay, Perú,
República Dominicana, Uruguay y Venezuela. Argentina se incluye en las fuentes compiladas
para poder compararla con el resto (su detalle fino sigue en argentina_provincias/).

La clave de unión es subdivision_iso (código ISO 3166-2, ej. BR-SP, MX-JAL, CO-ANT), el mismo
de etl/maestros/subdivisiones_maestro.csv. Con iso3 + anio se une también al panel de países.

Hay dos tipos de fuentes:
  - Compiladas: una sola base que cubre todos (o casi todos) los países con el mismo método.
    Sirven para comparar Jalisco con Antioquia o con Córdoba.
  - Oficiales de cada país (IBGE, INEGI, DANE...): más detalle y más actuales, pero cada
    país mide distinto. Sirven para mirar adentro de un país.

Qué genera (en esta carpeta):
  indicadores_ocde_subdivision_anual.csv  una fila por subdivisión + año: PIB, % del valor agregado
                                          por sector, población, salud, empleo, homicidios (OCDE)
  ocde_regional_largo.csv.gz              todas las series de la OCDE, una fila por dato
  temperatura_subdivision_anual.csv       una fila por subdivisión + año: temperatura media (°C)
  gobernantes_subdivision.csv             una fila por mandato de gobernador (Wikidata, incompleto)
  gobierno_subdivision_anual.csv          una fila por subdivisión + año: quién gobernaba
  brasil_pib_poblacion_estado_anual.csv   una fila por estado + año: PIB por sector y población (IBGE)
  agricultura_subdivision_anual.csv       una fila por subdivisión + año + cultivo (ARG, BRA, COL)
  ganaderia_subdivision_anual.csv         una fila por subdivisión + año + especie (ARG, BRA, COL)
  petroleo_gas_subdivision_anual.csv      una fila por subdivisión + año: m³ de petróleo y gas (ARG, BRA, COL)
La explicación paso a paso está en GUIA_LATAM_SUBNACIONAL.md.

Los archivos originales quedan en crudos/. Si un archivo ya está ahí, no se vuelve a
descargar (borralo para forzar la descarga de la versión más nueva).

Cómo ejecutarlo (desde la carpeta etl/):
    pip install -r requirements.txt
    python latam_subnacional/extraer_latam_subnacional.py
"""

import gzip
import json
import os
import re
import unicodedata
from pathlib import Path

import pandas as pd
import requests

CARPETA = Path(__file__).resolve().parent
CRUDOS = CARPETA / "crudos"
MAESTRO_SUBDIVISIONES = CARPETA.parent / "maestros" / "subdivisiones_maestro.csv"
# Con ETL_REFRESCAR=1 (lo pone actualizar_mensual.py) se vuelven a bajar las fuentes que se
# actualizan; si una descarga falla, se sigue con la copia anterior y se avisa con AVISO_FUENTE.
REFRESCAR = os.environ.get("ETL_REFRESCAR") == "1"

# Los 20 países de América Latina (iso3 -> iso2). El Caribe angloparlante queda afuera.
PAISES = {
    "ARG": "AR", "BOL": "BO", "BRA": "BR", "CHL": "CL", "COL": "CO", "CRI": "CR", "CUB": "CU",
    "DOM": "DO", "ECU": "EC", "GTM": "GT", "HND": "HN", "HTI": "HT", "MEX": "MX", "NIC": "NI",
    "PAN": "PA", "PER": "PE", "PRY": "PY", "SLV": "SV", "URY": "UY", "VEN": "VE",
}
NAVEGADOR = {"User-Agent": "Mozilla/5.0 (proyecto educativo analista de datos)"}


def leer_subdivisiones():
    """Las subdivisiones de primer nivel de los 20 países, del maestro ISO 3166-2."""
    sub = pd.read_csv(MAESTRO_SUBDIVISIONES, keep_default_na=False, na_values=[""])
    return sub[sub.iso3.isin(PAISES)].reset_index(drop=True)


SUBDIVISIONES = leer_subdivisiones()
NOMBRE_SUBDIVISION = dict(zip(SUBDIVISIONES.subdivision_iso, SUBDIVISIONES.nombre))


def normalizar(texto):
    """'Región de Ñuble' -> 'nuble': sin tildes, sin mayúsculas, sin palabras genéricas."""
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower()
    texto = re.sub(r"\b(departamento|department|provincia|province|region|estado|state|de|del|la|el|"
                   r"y|and|of|distrito|district|regional)\b", " ", texto)
    return re.sub(r"[^a-z0-9]", "", texto)


# Para buscar una subdivisión por nombre: (iso3, nombre normalizado) -> código ISO.
# Se prueban el nombre limpio, el nombre ISO y los nombres de Wikidata en español e inglés.
BUSCAR_POR_NOMBRE = {}
for _, s in SUBDIVISIONES.iterrows():
    for columna in ("nombre", "nombre_iso", "nombre_es", "nombre_en"):
        if pd.notna(s[columna]):
            BUSCAR_POR_NOMBRE.setdefault((s.iso3, normalizar(s[columna])), s.subdivision_iso)


def codigo_por_nombre(iso3, nombre, a_mano=None):
    """Código ISO 3166-2 de una subdivisión a partir de su nombre (None si no se encuentra)."""
    if a_mano and nombre in a_mano:
        return a_mano[nombre]
    return BUSCAR_POR_NOMBRE.get((iso3, normalizar(nombre)))


def descargar(url, archivo, metodo="get", datos=None, fija=False, encabezados=None, timeout=300):
    """fija=True: datos históricos que no cambian, no se vuelven a bajar ni con ETL_REFRESCAR."""
    destino = CRUDOS / archivo
    if destino.exists() and (fija or not REFRESCAR):
        print(f"  ya existe {archivo}, no se descarga")
        return destino
    print(f"  descargando {archivo} ...")
    try:
        r = requests.request(metodo, url, data=datos, headers=encabezados or NAVEGADOR, timeout=timeout)
        r.raise_for_status()
    except requests.RequestException as error:
        if not destino.exists():
            raise
        print(f"  AVISO_FUENTE {archivo}: falló la descarga ({error}); se usa la copia anterior")
        return destino
    # Si el nombre termina en .gz se guarda comprimido (pandas lo lee igual)
    destino.write_bytes(gzip.compress(r.content) if archivo.endswith(".gz") else r.content)
    return destino


def consultar_wikidata(consultas, archivo, por_pais=False):
    """Corre una o varias consultas SPARQL en Wikidata y guarda el resultado como CSV en crudos/.
    por_pais=True: la consulta tiene {valores} y se corre una vez por país (si no, tarda demasiado);
    {valores} se reemplaza por los pares (ítem de Wikidata, código ISO) de las subdivisiones del país."""
    destino = CRUDOS / archivo
    if destino.exists() and not REFRESCAR:
        print(f"  ya existe {archivo}, no se descarga")
        return pd.read_csv(destino)
    print(f"  consultando Wikidata -> {archivo} ...")
    try:
        partes = []
        for consulta, iso3 in [(c, p) for c in ([consultas] if isinstance(consultas, str) else consultas)
                               for p in (PAISES if por_pais else [None])]:
            texto = consulta
            if iso3:
                subs = SUBDIVISIONES[(SUBDIVISIONES.iso3 == iso3) & SUBDIVISIONES.wikidata_id.notna()]
                texto = consulta.replace("{valores}", " ".join(
                    f'(wd:{q} "{c}")' for q, c in zip(subs.wikidata_id, subs.subdivision_iso)))
            r = requests.get("https://query.wikidata.org/sparql", params={"query": texto},
                             headers={"Accept": "text/csv", "User-Agent": "analista-datos/1.0 (proyecto educativo)"},
                             timeout=300)
            r.raise_for_status()
            # Con timeout, Wikidata responde 200 pero corta el CSV y pega el error de Java al final
            if "java.lang." in r.text[-20000:]:
                raise requests.RequestException("respuesta cortada por timeout del servidor")
            partes.append(r.text if not partes else r.text.split("\n", 1)[1])
        destino.write_text("".join(partes))
    except requests.RequestException as error:
        if not destino.exists():
            raise
        print(f"  AVISO_FUENTE {archivo}: falló la consulta ({error}); se usa la copia anterior")
    return pd.read_csv(destino)


def guardar(tabla, archivo, orden):
    """Agrega nombre e iso3 de la subdivisión, ordena y guarda en esta carpeta."""
    desconocidos = set(tabla.subdivision_iso) - set(NOMBRE_SUBDIVISION)
    if desconocidos:
        raise ValueError(f"{archivo}: códigos que no están en el maestro: {sorted(desconocidos)}")
    tabla = tabla.copy()
    if "subdivision" not in tabla:
        tabla.insert(1, "subdivision", tabla.subdivision_iso.map(NOMBRE_SUBDIVISION))
    if "iso3" not in tabla:
        tabla.insert(0, "iso3", tabla.subdivision_iso.map(
            dict(zip(SUBDIVISIONES.subdivision_iso, SUBDIVISIONES.iso3))))
    tabla.sort_values(orden).to_csv(CARPETA / archivo, index=False)
    return tabla


# ---------------------------------------------------------------------------
# 2. Temperatura media anual por subdivisión (Banco Mundial, Climate Change Knowledge Portal)
# ---------------------------------------------------------------------------
# Es el promedio de toda la superficie (reanálisis ERA5, grilla de 0,25°), igual que para las
# provincias argentinas. El portal identifica cada subdivisión con "ISO3." + código GAUL del país
# + código GAUL de la subdivisión (GAUL = Global Administrative Unit Layers, de la FAO).
# Los códigos GAUL de cada subdivisión salen de la base "Subnational Population" del Banco
# Mundial, cuyos identificadores los traen (ej. "BRA_Acre_BR.AC_665_BRA001" -> 665).
URL_CCKP = ("https://cckpapi.worldbank.org/cckp/v1/era5-x0.25_timeseries_tas_timeseries_annual_"
            "1950-2024_mean_historical_era5_x0.25_mean/{codigos}?_format=json")
URL_BM_SUBNACIONAL = "https://api.worldbank.org/v2/sources/50/country?format=json&per_page=5000"
GAUL_PAIS = {
    "ARG": 12, "BOL": 33, "BRA": 37, "CHL": 51, "COL": 57, "CRI": 61, "CUB": 63, "DOM": 72,
    "ECU": 73, "GTM": 103, "HND": 111, "PER": 195, "PRY": 194,
    "SLV": 75, "URY": 260, "VEN": 263,
}
# Nombres del Banco Mundial que no coinciden con el maestro: (iso3, nombre) -> código ISO
GAUL_NOMBRE_A_MANO = {
    ("ARG", "Buenos Aires D.f."): "AR-C", ("CHL", "Arica y Painacota"): "CL-AP",
    ("CHL", "Libertador Gral. Bernardo O'Higgins"): "CL-LI", ("CHL", "Metropolitana"): "CL-RM",
    ("COL", "San Andres Y Providencia"): "CO-SAP", ("COL", "Bogota"): "CO-DC",
    ("CUB", "Ciudad De La Habana"): "CU-03", ("PER", "Callao, Provincia Constitucion"): "PE-CAL",
    ("PER", "Lima"): "PE-LIM", ("VEN", "Distrito Capital"): "VE-A", ("VEN", "Vargas"): "VE-X",
    # La antigua provincia La Habana (hasta 2010) no es la actual: se usa solo para Artemisa y Mayabeque
    ("CUB", "La Habana"): "antigua La Habana",
}
# Identificadores del Banco Mundial con el código GAUL equivocado (comprobado consultando los
# vecinos: San José de Costa Rica y San José de Uruguay vienen cruzados; Santiago de R. Dominicana
# trae un código que no existe y el suyo es el hueco de la serie alfabética).
CODIGO_CCKP_A_MANO = {("CRI", "San Jose"): "CRI.61987", ("URY", "San Jose"): "URY.2603280",
                      ("DOM", "Santiago"): "DOM.721132"}
# Paraguay no está en esa base: sus 17 departamentos tienen los códigos 2311-2327 en orden
# alfabético (comprobado con la temperatura: los del Chaco dan más calor e Itapúa menos).
GAUL_PARAGUAY = ["PY-16", "PY-10", "PY-13", "PY-19", "PY-5", "PY-6", "PY-14", "PY-11", "PY-1",
                 "PY-3", "PY-4", "PY-7", "PY-8", "PY-12", "PY-9", "PY-15", "PY-2"]
# Subdivisiones creadas después de los límites GAUL 2015: se les asigna la temperatura de la
# unidad de la que se separaron (con 0,25° de grilla la diferencia es chica) y se marca.
# Lima Metropolitana NO se aproxima: el departamento de Lima incluye la sierra y da 6 °C menos
# que la ciudad. Bogotá tampoco (Cundinamarca es más cálida que la sabana).
TEMPERATURA_PRESTADA = {
    "CL-NB": "CL-BI",   # Ñuble se separó de Biobío en 2018
    "CU-15": "antigua La Habana",  # Artemisa y Mayabeque salieron de la antigua provincia
    "CU-16": "antigua La Habana",  # La Habana en 2011 (Artemisa también de Pinar del Río)
    "PY-ASU": "PY-11",  # Asunción (117 km²) no tiene código propio: se usa Central, que la rodea
}
# República Dominicana: ISO usa 10 regiones de desarrollo y GAUL las 32 provincias.
# La región se arma promediando sus provincias, ponderadas por superficie (km², de Wikidata).
REGION_DOMINICANA = {
    "DO-33": ["Duarte", "Hermanas Mirabal", "Maria Trinidad Sanches", "Samana"],
    "DO-34": ["Dajabon", "Monte Cristi", "Santiago Rodriguez", "Valverde"],
    "DO-35": ["Espaillat", "Puerto Plata", "Santiago"],
    "DO-36": ["La Vega", "Monsenor Nouel", "Sanchez Ramirez"],
    "DO-37": ["Elias Pina", "San Juan"],
    "DO-38": ["Baoruco", "Barahona", "Independencia", "Pedernales"],
    "DO-39": ["Hato Mayor", "Monte Plata", "San Pedro de Macoris"],
    "DO-40": ["Distrito Nacional", "Santo Domingo"],
    "DO-41": ["Azua", "Peravia", "San Cristobal", "San Jose de Ocoa"],
    "DO-42": ["El Seibo", "La Altagracia", "La Romana"],
}
# Superficie de cada provincia dominicana en km² (Wikidata P2046, consultado el 14-10-2026)
SUPERFICIE_PROVINCIA_DOM = {
    "Azua": 2531.77, "Baoruco": 1284.9, "Barahona": 1666.19, "Dajabon": 1021.25, "Distrito Nacional": 91.95,
    "Duarte": 1649.48, "El Seibo": 1788.41, "Elias Pina": 1395.47, "Espaillat": 842.96, "Hato Mayor": 1319.3,
    "Hermanas Mirabal": 427.38, "Independencia": 2007.4, "La Altagracia": 2998.43, "La Romana": 652.12,
    "La Vega": 2292.45, "Maria Trinidad Sanches": 1206.5, "Monsenor Nouel": 992.03, "Monte Cristi": 1885.8,
    "Monte Plata": 2601.61, "Pedernales": 2080.5, "Peravia": 785.21, "Puerto Plata": 1805.63,
    "Samana": 862.82, "San Cristobal": 1240.63, "San Jose de Ocoa": 853.43, "San Juan": 3363.83,
    "San Pedro de Macoris": 1254.33, "Sanchez Ramirez": 1185.8, "Santiago": 2806.29,
    "Santiago Rodriguez": 1147.54, "Santo Domingo": 1301.61, "Valverde": 822.95,
}


# México, Nicaragua, Panamá y Haití: el portal usa otra numeración (1, 2, 3...) y no publica qué
# número es cada estado. No se adivina: quedan sin temperatura de esta fuente.


def codigos_gaul():
    """Tabla subdivisión ISO -> código CCKP, armada con la base subnacional del Banco Mundial."""
    archivo = descargar(URL_BM_SUBNACIONAL, "bm_subnational_population_unidades.json", fija=True)
    unidades = json.loads(archivo.read_text(encoding="utf-8-sig"))["source"][0]["concept"][0]["variable"]
    filas = []
    for u in unidades:
        iso3 = u["id"][:3]
        if iso3 not in GAUL_PAIS or "_" not in u["id"]:
            continue
        gaul = int(re.match(r"^[A-Z]{3}_.*?_(\d+)(?:_[A-Z]{3}\d+)?$", u["id"])[1])
        nombre = u["value"].split(", ", 1)[1].removeprefix("RB, ")
        filas.append({"iso3": iso3, "nombre_gaul": nombre, "gaul": gaul,
                      "codigo_cckp": CODIGO_CCKP_A_MANO.get((iso3, nombre), f"{iso3}.{GAUL_PAIS[iso3]}{gaul}"),
                      "subdivision_iso": GAUL_NOMBRE_A_MANO.get((iso3, nombre)) or codigo_por_nombre(iso3, nombre)})
    for i, codigo in enumerate(GAUL_PARAGUAY):
        filas.append({"iso3": "PRY", "nombre_gaul": NOMBRE_SUBDIVISION[codigo], "gaul": 2311 + i,
                      "codigo_cckp": f"PRY.194{2311 + i}", "subdivision_iso": codigo})
    tabla = pd.DataFrame(filas)
    provincias_dom = {p for lista in REGION_DOMINICANA.values() for p in lista}
    sin_codigo = tabla[tabla.subdivision_iso.isna() & ~tabla.nombre_gaul.isin(provincias_dom)]
    # Lo que queda sin código es una unidad vieja (La Habana provincia, que se partió en
    # Artemisa y Mayabeque) o una zona en litigio (Ecuador "Zona No Delimitada")
    print(f"  unidades GAUL sin subdivisión ISO actual: {', '.join(sin_codigo.nombre_gaul)}")
    return tabla


def procesar_temperatura():
    codigos = codigos_gaul()
    destino = CRUDOS / "cckp_temperatura_subdivisiones.json"
    if destino.exists() and not REFRESCAR:
        print(f"  ya existe {destino.name}, no se descarga")
        datos = json.loads(destino.read_text())
    else:
        datos = {}
        lista = list(codigos.codigo_cckp)
        for i in range(0, len(lista), 40):  # de a 40 códigos por consulta
            r = requests.get(URL_CCKP.format(codigos=",".join(lista[i:i + 40])), timeout=300)
            r.raise_for_status()
            datos.update(r.json()["data"] or {})
        destino.write_text(json.dumps(datos))
    serie = pd.DataFrame([{"codigo_cckp": c, "anio": int(f[:4]), "temperatura_media_c": t}
                          for c, s in datos.items() for f, t in s.items()]).merge(codigos, on="codigo_cckp")
    # Subdivisiones con código propio
    directas = serie.dropna(subset=["subdivision_iso"])[["subdivision_iso", "anio", "temperatura_media_c"]]
    madres = directas[directas.subdivision_iso.str.startswith("antigua")]
    directas = directas.drop(madres.index)
    directas = directas.assign(fuente_unidad="propia")
    # República Dominicana: promedio de las provincias ponderado por superficie
    dom = serie[serie.iso3 == "DOM"].copy()
    region_de = {p: r for r, lista in REGION_DOMINICANA.items() for p in lista}
    dom["subdivision_iso"] = dom.nombre_gaul.map(region_de)
    dom["km2"] = dom.nombre_gaul.map(SUPERFICIE_PROVINCIA_DOM)
    dom = (dom.assign(t_por_km2=dom.temperatura_media_c * dom.km2)
           .groupby(["subdivision_iso", "anio"], as_index=False)[["t_por_km2", "km2"]].sum())
    dom = dom.assign(temperatura_media_c=(dom.t_por_km2 / dom.km2).round(2),
                     fuente_unidad="promedio de sus provincias")[directas.columns]
    # Subdivisiones nuevas: temperatura de la unidad de la que salieron
    prestadas = []
    for nueva, madre in TEMPERATURA_PRESTADA.items():
        t = pd.concat([directas, madres])
        t = t[t.subdivision_iso == madre].copy()
        prestadas.append(t.assign(subdivision_iso=nueva,
                                  fuente_unidad=f"aproximada: {NOMBRE_SUBDIVISION.get(madre, madre)}"))
    temp = pd.concat([directas, dom] + prestadas, ignore_index=True).assign(fuente="CCKP Banco Mundial")
    # México (y lo que falte de los países OCDE) sale de la OCDE, que también usa ERA5 pero con
    # otro método: comparada con el CCKP en los mismos estados da en promedio 0,1 a 0,7 °C menos
    # y hasta 2 °C de diferencia. Sirve para comparar estados de México entre sí y en el tiempo.
    ocde = CARPETA / "indicadores_ocde_subdivision_anual.csv"
    if ocde.exists():
        o = pd.read_csv(ocde)[["subdivision_iso", "anio", "temperatura_media_c_ocde"]].dropna()
        o = o[~o.subdivision_iso.isin(temp.subdivision_iso)]
        temp = pd.concat([temp, o.rename(columns={"temperatura_media_c_ocde": "temperatura_media_c"})
                         .assign(temperatura_media_c=lambda t: t.temperatura_media_c.round(2),
                                 fuente_unidad="propia", fuente="OCDE")], ignore_index=True)
    temp = guardar(temp, "temperatura_subdivision_anual.csv", ["iso3", "subdivision_iso", "anio"])
    faltan = sorted(set(SUBDIVISIONES.subdivision_iso) - set(temp.subdivision_iso))
    print(f"  Temperatura: {temp.subdivision_iso.nunique()} subdivisiones, {temp.anio.min()}-{temp.anio.max()}"
          f"; sin dato: {', '.join(faltan)}")


# ---------------------------------------------------------------------------
# 3. Gobernadores (y prefectos, intendentes regionales...) según Wikidata
# ---------------------------------------------------------------------------
# No hay una base oficial común: cada país publica sus elecciones a su manera. Wikidata
# (la base de datos detrás de Wikipedia) sí tiene, para muchos estados, el cargo
# "gobernador de X" y quién lo ocupó, con fecha de inicio y fin. Está INCOMPLETA: sirve para
# México, Brasil, Colombia y Perú desde los 90, y poco para el resto. La columna
# cobertura de gobierno_subdivision_anual.csv dice si el año tiene a alguien cargado.
# Tres formas en que Wikidata liga un cargo con una subdivisión (cada una se consulta aparte,
# porque juntas en una sola consulta superan el tiempo máximo del servidor):
VIAS_CARGO = {
    "cargo de la subdivision": "?sub wdt:P1313 ?cargo .",  # la subdivisión dice cuál es su cargo
    "jurisdiccion del cargo": "?cargo wdt:P1001 ?sub . ?cargo wdt:P279*/wdt:P31* wd:Q132050 .",  # gobernador de
    "calificador de": "?st pq:P642 ?sub .",  # "gobernador", con el calificador "de: Jalisco"
}
CONSULTA_GOBERNANTES = """
SELECT DISTINCT ?iso ?via ?cargo ?persona ?personaLabel ?cargoLabel ?inicio ?fin WHERE {
  VALUES (?sub ?iso) { {valores} }
  {via}
  ?persona p:P39 ?st . ?st ps:P39 ?cargo ; pq:P580 ?inicio .
  OPTIONAL { ?st pq:P582 ?fin }
  BIND("{nombre_via}" AS ?via)
  SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en". }
}
"""
# Cargos que no son el gobierno de la subdivisión aunque cuelguen de ella
CARGOS_DESCARTADOS = r"vice|alcalde|intendente municipal|senador|diputado|vicegobernador|teniente"


def procesar_gobernantes():
    consultas = [CONSULTA_GOBERNANTES.replace("{via}", v).replace("{nombre_via}", n) for n, v in VIAS_CARGO.items()]
    crudo = consultar_wikidata(consultas, "wikidata_gobernantes_subdivisiones.csv", por_pais=True)
    g = crudo[~crudo.cargoLabel.str.contains(CARGOS_DESCARTADOS, case=False, na=False)].copy()
    # Un cargo genérico ("gobernador", "prefecto") que varias subdivisiones declaran como suyo
    # cruzaría a todos sus titulares con todas ellas: por esa vía solo valen los cargos propios.
    compartidos = g[g.via == "cargo de la subdivision"].groupby("cargo").iso.nunique()
    g = g[~((g.via == "cargo de la subdivision") & g.cargo.isin(compartidos[compartidos > 1].index))]
    g = g[g.iso.isin(NOMBRE_SUBDIVISION)]
    g["inicio"] = pd.to_datetime(g.inicio, errors="coerce", utc=True).dt.date
    g["fin"] = pd.to_datetime(g.fin, errors="coerce", utc=True).dt.date
    g = g.dropna(subset=["inicio"])
    g["persona_wikidata"] = g.persona.str.rsplit("/", n=1).str[-1]
    # El partido NO se usa: Wikidata da los partidos de toda la vida de la persona (no el del
    # mandato) y tiene errores graves (un gobernador de Antioquia figura en las FARC).
    g = (g.groupby(["iso", "persona_wikidata", "personaLabel", "cargoLabel", "inicio"], as_index=False)
         .agg(fin=("fin", "max")))
    g = g.rename(columns={"iso": "subdivision_iso", "personaLabel": "persona", "cargoLabel": "cargo"})
    g = g[g.inicio >= pd.Timestamp("1900-01-01").date()]
    g = guardar(g, "gobernantes_subdivision.csv", ["iso3", "subdivision_iso", "inicio"])

    # Por año: quién estaba en el cargo el 1 de julio (si hubo más de uno, el último en asumir)
    filas = []
    for anio in range(1980, pd.Timestamp.today().year + 1):
        corte = pd.Timestamp(anio, 7, 1).date()
        vigentes = g[(g.inicio <= corte) & (g.fin.isna() | (g.fin >= corte))]
        # Sin fecha de fin solo cuenta si asumió hace menos de 8 años (si no, es un dato faltante)
        vigentes = vigentes[vigentes.fin.notna() | (vigentes.inicio >= pd.Timestamp(anio - 8, 7, 1).date())]
        for codigo, v in vigentes.sort_values("inicio").groupby("subdivision_iso"):
            u = v.iloc[-1]
            filas.append({"subdivision_iso": codigo, "anio": anio, "gobernante": u.persona,
                          "persona_wikidata": u.persona_wikidata, "cargo": u.cargo})
    anual = pd.DataFrame(filas)
    anual = guardar(anual, "gobierno_subdivision_anual.csv", ["iso3", "subdivision_iso", "anio"])
    cobertura = (anual[anual.anio >= 2000].groupby("iso3").subdivision_iso.size()
                 / SUBDIVISIONES.groupby("iso3").size() / (pd.Timestamp.today().year - 1999) * 100)
    print(f"  Gobernantes: {len(g)} mandatos; % de subdivisión-año 2000-hoy con dato: "
          + ", ".join(f"{k} {v:.0f}" for k, v in cobertura.dropna().round().sort_values(ascending=False).items()))


# ---------------------------------------------------------------------------
# 1. Estadísticas regionales de la OCDE (Brasil, Chile, Colombia, México, Perú y algo de Argentina)
# ---------------------------------------------------------------------------
# La OCDE junta, con el mismo método para todos, los datos de las oficinas de estadística de
# cada país a nivel "TL2" (que en estos países coincide con estados, departamentos o regiones):
# PIB y valor agregado por sector, empleo, población, esperanza de vida, desempleo,
# homicidios, médicos, educación... Es la fuente compilada más rica para comparar Jalisco
# con Antioquia. Se baja por la API SDMX (sdmx.oecd.org), un "flujo" por tema.
# Costa Rica queda afuera: la OCDE usa sus 6 regiones de planificación, no las 7 provincias.
URL_OCDE = ("https://sdmx.oecd.org/public/rest/data/OECD.CFE.EDS,{flujo},/{clave}"
            "?startPeriod={desde}&format=csvfilewithlabels")
FLUJOS_OCDE = {  # tema -> (flujo, cantidad de dimensiones)
    "economia": ("DSD_REG_ECO@DF_ECO", 8),        # PIB, valor agregado por sector, empleo, ingreso
    "demografia": ("DSD_REG_DEMO@DF_DEMO", 8),    # población, nacimientos, esperanza de vida
    "trabajo": ("DSD_REG_LABOUR@DF_LAB", 8),      # desempleo, participación, empleo
    "sociedad": ("DSD_REG_SOC@DF_SOC", 8),        # homicidios, vivienda, autos, participación electoral
    "salud": ("DSD_REG_HEALTH@DF_HEALTH", 8),     # médicos, camas, mortalidad
    "educacion": ("DSD_REG_EDU@DF_EDU", 10),      # nivel educativo de la población
    "clima": ("DSD_REG_CLIM@DF_AIR_TEMP", 10),    # temperatura, días de calor
}
PAISES_OCDE = ["ARG", "BRA", "CHL", "COL", "MEX", "PER"]
REGION_OCDE_A_MANO = {
    ("COL", "San Andres"): "CO-SAP", ("COL", "Cauca Valley"): "CO-VAC",
    ("COL", "Bogota Capital District"): "CO-DC", ("MEX", "México D.C."): "MX-CMX",
}


def regiones_ocde():
    """Códigos TL2 de la OCDE de los países latinoamericanos, con su código ISO."""
    # Población total (todas las edades, ambos sexos) desde 2010: liviano y trae todas las regiones
    archivo = descargar(URL_OCDE.format(flujo="DSD_REG_DEMO@DF_POP_BROAD", clave="A.TL2.._Z.POP._T._T.PS",
                                        desde=2010), "ocde_regiones_tl2.csv.gz")
    r = pd.read_csv(archivo, low_memory=False)
    r = r[r.COUNTRY.isin(PAISES_OCDE)][["COUNTRY", "REF_AREA", "Reference area"]].drop_duplicates()
    r["subdivision_iso"] = [REGION_OCDE_A_MANO.get((p, n)) or codigo_por_nombre(p, n)
                            for p, n in zip(r.COUNTRY, r["Reference area"])]
    # "Chile, not regionalised" (CLZZ) es lo que no se puede asignar a ninguna región
    return r.dropna(subset=["subdivision_iso"])


def procesar_ocde():
    regiones = regiones_ocde()
    codigos = "+".join(sorted(regiones.REF_AREA))
    partes = []
    for tema, (flujo, dimensiones) in FLUJOS_OCDE.items():
        clave = "A.TL2." + codigos + "." * (dimensiones - 3)
        archivo = descargar(URL_OCDE.format(flujo=flujo, clave=clave, desde=1990), f"ocde_{tema}.csv.gz")
        d = pd.read_csv(archivo, low_memory=False)
        # Las columnas vienen de a pares: código (MEASURE) y etiqueta en inglés (Measure).
        # Todo lo que no es región, año, valor o medida es una "desagregación" (sexo, edad,
        # actividad...): se junta en un texto, y si es el total queda vacío.
        etiquetas = {c: d.columns[i + 1] for i, c in enumerate(d.columns[:-1])
                     if c.isupper() and not d.columns[i + 1].isupper()}
        desagregar = [c for c in ("ACTIVITY", "AGE", "SEX", "EDUCATION_LEV", "PRICES") if c in d]
        d["desagregacion"] = d.apply(lambda f: "; ".join(
            str(f[etiquetas[c]]) for c in desagregar
            if f[c] not in ("_T", "_Z", "T", "Y_GE0", "_X")), axis=1)
        # Se descartan los grupos quinquenales de edad (0-4, 5-9...) y las series a "precios
        # regionales" (ROPI): son variantes muy detalladas que multiplican el tamaño del archivo.
        quinquenal = d.get("AGE", pd.Series("", index=d.index)).astype(str).str.fullmatch(
            r"Y\d+T\d+|Y_LT5|Y_GE80|Y_GE85") & ~d.get("AGE", pd.Series("", index=d.index)).isin(
            ["Y15T64", "Y25T64", "Y25T34", "Y15T24", "Y55T64", "Y20T64", "Y15T29", "Y18T24"])
        ropi = d.get("PRICES", pd.Series("", index=d.index)).astype(str).str.contains("ROPI")
        d = d[~quinquenal & ~ropi]
        partes.append(pd.DataFrame({
            "codigo_ocde": d.REF_AREA, "anio": d.TIME_PERIOD, "tema": tema,
            "medida": d.Measure, "codigo_medida": d.MEASURE, "desagregacion": d.desagregacion,
            "unidad": d["Unit of measure"],
            "multiplicador": 10 ** d.UNIT_MULT.fillna(0).astype(int) if "UNIT_MULT" in d else 1,
            "valor": d.OBS_VALUE}))
        print(f"  OCDE {tema}: {len(d):,} datos")
    largo = pd.concat(partes, ignore_index=True).dropna(subset=["valor"])
    # Fuera: lo que se repite entre temas (esperanza de vida y mortalidad están en "demografia"
    # y en "salud"), lo derivable (productividad = VAB / empleo; deflactores e índices) y el
    # empleo según nivel educativo.
    repetidas = set(largo[largo.tema == "demografia"].medida)
    largo = largo[~((largo.tema == "salud") & largo.medida.isin(repetidas))]
    largo = largo[~largo.medida.isin(["Labour productivity"]) & ~largo.unidad.isin(["Index"])
                  & ~largo.desagregacion.str.contains("Deflator", na=False)
                  & ~((largo.tema == "educacion") & (largo.medida == "Employment to population ratio"))]
    largo = largo.merge(regiones.rename(columns={"REF_AREA": "codigo_ocde", "Reference area": "nombre_ocde"})
                        [["codigo_ocde", "nombre_ocde", "subdivision_iso"]], on="codigo_ocde")
    largo.insert(0, "subdivision_iso", largo.pop("subdivision_iso"))
    # Son ~700.000 filas con etiquetas largas (100 MB): se guarda comprimido (.csv.gz).
    # pandas lo lee igual: pd.read_csv("ocde_regional_largo.csv.gz")
    largo = guardar(largo, "ocde_regional_largo.csv.gz", ["iso3", "subdivision_iso", "tema", "medida", "anio"])
    print(f"  OCDE: {len(largo):,} filas, {largo.subdivision_iso.nunique()} subdivisiones de "
          f"{largo.iso3.nunique()} países")
    indicadores_ocde(largo)
    return largo


# Las series más usadas, una columna cada una: (columna, tema, medida, unidad, desagregación)
INDICADORES_OCDE = [
    ("poblacion", "demografia", "Population", "Persons", ""),
    ("superficie_km2", "demografia", "Land area", "Square kilometres", ""),
    ("pib_millones_moneda_nacional_corriente", "economia", "Gross domestic product", "National currency", "Current prices"),
    ("pib_pc_usd_ppa_corriente", "economia", "Gross domestic product", "US dollars per person, PPP converted", "Current prices"),
    ("pib_pc_usd_ppa_constante", "economia", "Gross domestic product", "US dollars per person, PPP converted", "Constant prices"),
    ("esperanza_vida_anios", "demografia", "Life expectancy", "Years", "0 years"),
    ("mortalidad_infantil_x1000", "demografia", "Infant mortality rate", "Deaths per 1 000 live births",
     "Less than 1 years"),
    ("tasa_fecundidad", "demografia", "Fertility rate", "Live births per woman", "Female"),
    ("tasa_desempleo_pct", "trabajo", "Unemployment rate", "Percentage of labour force in the same subgroup", "Over 15 years"),
    ("tasa_participacion_laboral_pct", "trabajo", "Labour force participation rate",
     "Percentage of population in the same subgroup", "Over 15 years"),
    ("homicidios_x100mil", "sociedad", "Intentional homicides", "Cases per 100 000 persons", ""),
    ("vehiculos_x1000", "sociedad", "Vehicles fleet, total", "Per 1 000 inhabitants", ""),
    ("participacion_electoral_pct", "sociedad", "Voters turnout to general elections",
     "Percentage of population in the same subgroup", ""),
    ("medicos_x1000", "salud", "Active physicians", "Per 1 000 inhabitants", ""),
    ("camas_hospital_x1000", "salud", "Hospital beds", "Per 1 000 inhabitants", ""),
    ("pct_25_64_con_terciaria", "educacion", "Population educational attainment",
     "Percentage of population in the same sex and age", "From 25 to 64 years; Tertiary education"),
    ("temperatura_media_c_ocde", "clima", "Air temperature", "Degrees celsius", ""),
]
# Valor agregado por sector, en % del total (a precios corrientes)
SECTORES_OCDE = {
    "Agriculture, forestry and fishing": "agro_pesca",
    "Industry (except construction)": "industria_mineria_energia",
    "Manufacturing": "manufactura",
    "Construction": "construccion",
    "Wholesale and retail trade; repair of motor vehicles and motorcycles; transportation and storage; "
    "accommodation and food service activities": "comercio_transporte_turismo",
    "Information and communication": "informacion_comunicaciones",
    "Financial and insurance activities": "finanzas",
    "Real estate activities": "inmobiliarias",
    "Professional, scientific and technical activities; administrative and support service activities": "servicios_profesionales",
    "Public administration, defence, education, human health and social work activities": "estado_educacion_salud",
    "Arts, entertainment and recreation; other service activities; activities of household and "
    "extra-territorial organizations and bodies": "otros_servicios",
}


def indicadores_ocde(largo):
    """Tabla ancha subdivisión + año con las series principales de la OCDE."""
    largo = largo.assign(desagregacion=largo.desagregacion.fillna(""))
    columnas = []
    for columna, tema, medida, unidad, desagregacion in INDICADORES_OCDE:
        sel = largo[(largo.tema == tema) & (largo.medida == medida) & (largo.unidad == unidad)
                    & (largo.desagregacion == desagregacion)]
        valor = sel.valor * (sel.multiplicador / 1e6 if "millones" in columna else 1)
        columnas.append(sel.assign(valor=valor).set_index(["subdivision_iso", "anio"]).valor.rename(columna))
    # % del valor agregado = VAB del sector / VAB total, ambos en moneda nacional a precios corrientes
    vab = largo[(largo.medida == "Value added, gross") & (largo.unidad == "National currency")
                & largo.desagregacion.str.endswith("Current prices")]
    vab = vab.assign(sector=vab.desagregacion.str.removesuffix("Current prices").str.rstrip("; "))
    total = vab[vab.sector == ""].set_index(["subdivision_iso", "anio"]).valor
    for sector, corto in SECTORES_OCDE.items():
        parte = vab[vab.sector == sector].set_index(["subdivision_iso", "anio"]).valor
        columnas.append((100 * parte / total).round(2).rename(f"pct_vab_{corto}"))
    tabla = pd.concat(columnas, axis=1).reset_index().dropna(how="all", subset=[c.name for c in columnas])
    tabla = guardar(tabla, "indicadores_ocde_subdivision_anual.csv", ["iso3", "subdivision_iso", "anio"])
    print(f"  Indicadores OCDE: {len(tabla):,} filas subdivisión-año, {tabla.anio.min()}-{tabla.anio.max()}")


# ---------------------------------------------------------------------------
# 4. Brasil por estado: PIB por sector, población, agricultura y ganadería (IBGE)
# ---------------------------------------------------------------------------
# El IBGE publica todo en SIDRA, una API pública: cada "tabela" es un cuadro y se piden
# variables (v), períodos (p), niveles territoriales (n3 = unidad de la federación = estado)
# y clasificaciones (c782 = producto agrícola). Devuelve JSON. Límite: 100.000 valores por
# consulta (en la práctica 50.000), por eso la agricultura se pide de a 5 años.
URL_SIDRA = "https://apisidra.ibge.gov.br/values/t/{tabla}/n3/all/v/{variables}/p/{periodos}{clasif}"
URL_ANP = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/ppgn-el/"


def sidra(tabla, variables, periodos="all", clasif="", archivo=None):
    """Baja un cuadro de SIDRA por estado y lo devuelve como tabla (una fila por valor)."""
    destino = descargar(URL_SIDRA.format(tabla=tabla, variables=variables, periodos=periodos, clasif=clasif),
                        archivo, timeout=600)
    filas = json.loads(gzip.decompress(destino.read_bytes()) if archivo.endswith(".gz") else destino.read_text())
    encabezado, datos = filas[0], filas[1:]
    t = pd.DataFrame(datos).rename(columns={"V": "valor", "MN": "unidad"})
    nombres = {k: v for k, v in encabezado.items() if k.startswith("D")}
    t = t.rename(columns={k: v for k, v in nombres.items()})
    # "-" = cero absoluto, ".." / "..." / "X" = no corresponde, no disponible o reservado
    t["valor"] = pd.to_numeric(t.valor.replace("-", "0"), errors="coerce")
    t["subdivision_iso"] = [codigo_por_nombre("BRA", n) for n in t["Unidade da Federação"]]
    return t


def procesar_brasil():
    # PIB y valor agregado por gran sector (miles de reales corrientes), 2002 en adelante
    pib = sidra(5938, "37,498,513,517,6575,525,543", archivo="ibge_pib_uf_5938.json")
    pib["anio"] = pib.Ano.astype(int)
    ancho = pib.pivot_table(index=["subdivision_iso", "anio"], columns="Variável (Código)", values="valor")
    ancho = ancho.rename(columns={"37": "pib_miles_reales", "498": "vab_total_miles_reales",
                                  "513": "vab_agropecuaria_miles_reales", "517": "vab_industria_miles_reales",
                                  "6575": "vab_servicios_privados_miles_reales",
                                  "525": "vab_administracion_publica_miles_reales",
                                  "543": "impuestos_netos_miles_reales"})
    # Población estimada al 1 de julio (en los años de censo 2010 y 2022 el IBGE no estima)
    pob = sidra(6579, "9324", archivo="ibge_poblacion_6579.json")
    pob = pob.assign(anio=pob.Ano.astype(int), poblacion_fuente="estimación IBGE")
    # Los años sin estimación se completan con los conteos: Contagem 2007, Censo 2010 y Censo 2022
    conteos = [sidra(793, "93", archivo="ibge_contagem_2007_793.json").assign(poblacion_fuente="Contagem 2007"),
               sidra(202, "93", "2010", archivo="ibge_censo_2010_202.json").assign(poblacion_fuente="Censo 2010"),
               sidra(4709, "93", archivo="ibge_censo_2022_4709.json").assign(poblacion_fuente="Censo 2022")]
    for c in conteos:
        if "Sexo" in c:  # el cuadro del censo 2010 viene abierto por sexo y zona: se usa el total
            c.drop(c[(c.Sexo != "Total") | (c["Situação do domicílio"] != "Total")].index, inplace=True)
    pob = pd.concat([pob] + [c.assign(anio=c.Ano.astype(int)) for c in conteos])
    pob = pob.drop_duplicates(["subdivision_iso", "anio"]).set_index(["subdivision_iso", "anio"])
    pob = pob[["valor", "poblacion_fuente"]].rename(columns={"valor": "poblacion"})
    tabla = ancho.join(pob, how="outer").reset_index()
    # 2023 no tiene ni estimación ni censo: punto medio entre el Censo 2022 y la estimación 2024
    for codigo, g in tabla.groupby("subdivision_iso"):
        anios = g.set_index("anio").poblacion
        if pd.isna(anios.get(2023)) and pd.notna(anios.get(2022)) and pd.notna(anios.get(2024)):
            fila = (tabla.subdivision_iso == codigo) & (tabla.anio == 2023)
            tabla.loc[fila, "poblacion"] = round((anios[2022] + anios[2024]) / 2)
            tabla.loc[fila, "poblacion_fuente"] = "interpolada (Censo 2022 y estimación 2024)"
    tabla["pib_per_capita_reales"] = (1000 * tabla.pib_miles_reales / tabla.poblacion).round(0)
    for sector in ("agropecuaria", "industria", "servicios_privados", "administracion_publica"):
        tabla[f"pct_vab_{sector}"] = (100 * tabla[f"vab_{sector}_miles_reales"] / tabla.vab_total_miles_reales).round(2)
    tabla = guardar(tabla, "brasil_pib_poblacion_estado_anual.csv", ["subdivision_iso", "anio"])
    print(f"  Brasil PIB y población: {tabla.subdivision_iso.nunique()} estados, {tabla.anio.min()}-{tabla.anio.max()}")

    # Agricultura: Producción Agrícola Municipal (PAM), cultivos temporales y permanentes
    partes = []
    for desde in range(1974, pd.Timestamp.today().year + 1, 5):
        periodos = f"{desde}-{desde + 4}"
        partes.append(sidra(5457, "8331,216,214,215", periodos, "/c782/allxt",
                            archivo=f"ibge_pam_5457_{desde}.json.gz"))
    pam = pd.concat(partes)
    pam = pam.dropna(subset=["valor"])
    pam["anio"] = pam.Ano.astype(int)
    pam["variable"] = pam["Variável (Código)"].map({"8331": "area_sembrada_ha", "216": "area_cosechada_ha",
                                                   "214": "produccion", "215": "valor_produccion"})
    pam["cultivo_original"] = pam["Produto das lavouras temporárias e permanentes"]
    unidades = pam[pam.variable.isin(["produccion", "valor_produccion"])].pivot_table(
        index=["subdivision_iso", "anio", "cultivo_original"], columns="variable", values="unidad", aggfunc="first")
    agro = pam.pivot_table(index=["subdivision_iso", "anio", "cultivo_original"], columns="variable", values="valor")
    agro = agro.join(unidades.add_prefix("unidad_")).reset_index()
    agro_brasil = agro.assign(fuente="IBGE - Producción Agrícola Municipal (tabla 5457)")

    # Ganadería: Pesquisa da Pecuária Municipal (PPM), cabezas al 31 de diciembre
    ppm = sidra(3939, "105", "all", "/c79/all", archivo="ibge_ppm_rebanos_3939.json.gz")
    ppm = ppm.dropna(subset=["valor"])
    ganado = pd.DataFrame({"subdivision_iso": ppm.subdivision_iso, "anio": ppm.Ano.astype(int),
                           "especie_original": ppm["Tipo de rebanho"], "cabezas": ppm.valor,
                           "fuente": "IBGE - Pesquisa da Pecuária Municipal (tabla 3939)"})

    # Petróleo y gas: ANP (Agência Nacional do Petróleo), mensual por estado desde 1997.
    # La producción en el mar se asigna al estado que tiene enfrente (criterio de la ANP).
    hidro = []
    for archivo, columna, producto in (("producao-petroleo-m3.csv", "petroleo_m3", "petróleo"),
                                       ("producao-gas-natural-1000m3.csv", "gas_miles_m3", "gas")):
        crudo = descargar(URL_ANP + archivo, "anp_" + archivo)
        t = pd.read_csv(crudo, sep=";", encoding="utf-8-sig", decimal=",")
        t.columns = ["anio", "mes", "region", "estado", "producto", "localizacion", "produccion"]
        t["subdivision_iso"] = [codigo_por_nombre("BRA", n) for n in t.estado]
        t["en_mar"] = t.produccion.where(t.localizacion.str.upper() == "MAR", 0)
        g = t.groupby(["subdivision_iso", "anio"]).agg(**{columna: ("produccion", "sum"),
                                                          f"meses_{producto}": ("mes", "nunique"),
                                                          f"_mar_{columna}": ("en_mar", "sum")})
        hidro.append(g)
    hidro = pd.concat(hidro, axis=1).reset_index()
    hidro["pct_petroleo_en_el_mar"] = (100 * hidro.pop("_mar_petroleo_m3") / hidro.petroleo_m3).round(1)
    hidro.pop("_mar_gas_miles_m3")
    hidro["meses_con_dato"] = hidro[["meses_petróleo", "meses_gas"]].max(axis=1).astype(int)
    hidro = hidro.drop(columns=["meses_petróleo", "meses_gas"]).assign(fuente="ANP - Produção de petróleo e gás natural por estado")
    return agro_brasil, ganado, hidro


# ---------------------------------------------------------------------------
# 5. Colombia por departamento: agricultura, ganado bovino, petróleo y gas (datos.gov.co)
# ---------------------------------------------------------------------------
# datos.gov.co es el portal de datos abiertos del Estado colombiano. Usa Socrata: cada base
# tiene un identificador (ej. uejq-wxrr) y se baja como CSV desde /resource/<id>.csv,
# de a 50.000 filas por vez ($limit y $offset).
URL_DATOS_GOV_CO = "https://www.datos.gov.co/resource/{id}.csv"
# Código DANE del departamento -> ISO 3166-2
DEPARTAMENTO_DANE = {
    5: "CO-ANT", 8: "CO-ATL", 11: "CO-DC", 13: "CO-BOL", 15: "CO-BOY", 17: "CO-CAL", 18: "CO-CAQ",
    19: "CO-CAU", 20: "CO-CES", 23: "CO-COR", 25: "CO-CUN", 27: "CO-CHO", 41: "CO-HUI", 44: "CO-LAG",
    47: "CO-MAG", 50: "CO-MET", 52: "CO-NAR", 54: "CO-NSA", 63: "CO-QUI", 66: "CO-RIS", 68: "CO-SAN",
    70: "CO-SUC", 73: "CO-TOL", 76: "CO-VAC", 81: "CO-ARA", 85: "CO-CAS", 86: "CO-PUT", 88: "CO-SAP",
    91: "CO-AMA", 94: "CO-GUA", 95: "CO-GUV", 97: "CO-VAU", 99: "CO-VID",
}
M3_POR_BARRIL = 0.158987
M3_POR_MIL_PIES3 = 28.3168  # "kpc" = miles de pies cúbicos


def socrata(identificador, archivo):
    """Baja una base completa de datos.gov.co (en páginas de 50.000 filas) y la guarda comprimida."""
    destino = CRUDOS / archivo
    if not (destino.exists() and not REFRESCAR):
        print(f"  descargando {archivo} ...")
        try:
            partes, desde = [], 0
            while True:
                r = requests.get(URL_DATOS_GOV_CO.format(id=identificador), headers=NAVEGADOR, timeout=600,
                                 params={"$limit": 50000, "$offset": desde, "$order": ":id"})
                r.raise_for_status()
                lineas = r.text.split("\n", 1)
                if len(lineas) < 2 or not lineas[1].strip():
                    break
                partes.append(r.text if not partes else lineas[1])
                desde += 50000
            destino.write_bytes(gzip.compress("".join(partes).encode()))
        except requests.RequestException as error:
            if not destino.exists():
                raise
            print(f"  AVISO_FUENTE {archivo}: falló la descarga ({error}); se usa la copia anterior")
    else:
        print(f"  ya existe {archivo}, no se descarga")
    return pd.read_csv(destino, dtype=str)


def numero(serie):
    """'8,731.00' -> 8731.0 (las bases de la ANH usan coma de miles)."""
    return pd.to_numeric(serie.astype(str).str.replace(",", ""), errors="coerce")


def procesar_colombia():
    # Agricultura: Evaluaciones Agropecuarias Municipales (EVA). Dos bases con metodología
    # distinta: 2006-2018 y 2019 en adelante. Los cultivos transitorios se informan por semestre
    # (2021A, 2021B): se suman para el total del año.
    vieja = socrata("2pnw-mmge", "datosgovco_eva_2006_2018.csv.gz").rename(columns={
        "c_d_dep": "dep", "a_o": "anio", "rea_sembrada_ha": "area_sembrada_ha",
        "rea_cosechada_ha": "area_cosechada_ha", "producci_n_t": "produccion"})
    nueva = socrata("uejq-wxrr", "datosgovco_eva_2019_en_adelante.csv.gz").rename(columns={
        "c_digo_dane_departamento": "dep", "a_o": "anio", "rea_sembrada": "area_sembrada_ha",
        "rea_cosechada": "area_cosechada_ha", "producci_n": "produccion"})
    # La base nueva junta la caña en "Caña" (azúcar, panela y miel van en la desagregación);
    # la vieja las separaba. Se usa la desagregación para que coincidan.
    nueva["cultivo"] = nueva.cultivo.where(nueva.cultivo.str.strip() != "Caña", nueva.desagregaci_n_cultivo)
    eva = pd.concat([vieja.assign(base="EVA 2006-2018"), nueva.assign(base="EVA 2019 en adelante")])
    eva["subdivision_iso"] = pd.to_numeric(eva.dep, errors="coerce").map(DEPARTAMENTO_DANE)
    # Sin tildes: la base nueva escribe "Plátano" y la vieja "Platano"
    eva["cultivo_original"] = eva.cultivo.str.strip().map(sin_tildes).str.capitalize()
    for c in ("area_sembrada_ha", "area_cosechada_ha", "produccion"):
        eva[c] = numero(eva[c])
    eva["anio"] = pd.to_numeric(eva.anio, errors="coerce").astype(int)
    agro = (eva.groupby(["subdivision_iso", "anio", "cultivo_original", "base"], as_index=False)
            [["area_sembrada_ha", "area_cosechada_ha", "produccion"]].sum(min_count=1))
    agro = agro.assign(unidad_produccion="Toneladas",
                       fuente="MADR/UPRA - Evaluaciones Agropecuarias Municipales (" + agro.pop("base") + ")")

    # Ganado bovino: censo del ICA para la vacunación contra la aftosa (1.er ciclo de cada año)
    ica = socrata("cea5-4ctf", "datosgovco_ica_inventario_bovino.csv.gz")
    ica = ica[ica.ciclo.str.strip() == "Ciclo I"]
    ica["subdivision_iso"] = [codigo_por_nombre("COL", n, {"BOGOTA D.C.": "CO-DC", "BOGOTÁ D.C.": "CO-DC",
                                                          "SAN ANDRES": "CO-SAP", "SAN ANDRÉS": "CO-SAP",
                                                          "GUAJIRA": "CO-LAG"}) for n in ica.departamento.str.strip()]
    ica["anio"] = pd.to_numeric(ica.vigencia, errors="coerce").astype(int)
    ganado = []
    for columna, especie in (("total_bovinos_pm", "Bovinos"), ("total_bufalinos_pm", "Bufalinos")):
        g = ica.assign(cabezas=numero(ica[columna])).groupby(["subdivision_iso", "anio"], as_index=False).cabezas.sum()
        ganado.append(g.assign(especie_original=especie, fuente="ICA - Inventario bovino y bufalino (ciclo I de vacunación)"))
    ganado = pd.concat(ganado)

    # Petróleo y gas: producción fiscalizada mensual por campo (Agencia Nacional de Hidrocarburos)
    crudo = socrata("fdvb-hsrf", "datosgovco_anh_produccion_crudo.csv.gz")
    gas = socrata("5dux-bfvx", "datosgovco_anh_produccion_gas.csv.gz")
    crudo = crudo.assign(subdivision_iso=pd.to_numeric(crudo.cod_dane_departamento, errors="coerce").map(DEPARTAMENTO_DANE),
                         anio=pd.to_numeric(crudo.vigencia).astype(int), mes=pd.to_numeric(crudo.mes),
                         petroleo_m3=numero(crudo.produccion_bls) * M3_POR_BARRIL)
    gas = gas.assign(subdivision_iso=pd.to_numeric(gas.coddanedepartamento, errors="coerce").map(DEPARTAMENTO_DANE),
                     anio=pd.to_numeric(gas.vigencia).astype(int), mes=pd.to_numeric(gas.mes),
                     gas_miles_m3=numero(gas.produccionkpc) * M3_POR_MIL_PIES3 / 1000)
    hidro = (crudo.groupby(["subdivision_iso", "anio"]).agg(petroleo_m3=("petroleo_m3", "sum"),
                                                            meses_petroleo=("mes", "nunique"))
             .join(gas.groupby(["subdivision_iso", "anio"]).agg(gas_miles_m3=("gas_miles_m3", "sum"),
                                                                meses_gas=("mes", "nunique")), how="outer")
             .reset_index())
    hidro["meses_con_dato"] = hidro[["meses_petroleo", "meses_gas"]].max(axis=1).astype(int)
    hidro = hidro.drop(columns=["meses_petroleo", "meses_gas"]).assign(
        fuente="ANH - Producción fiscalizada de crudo y gas")
    return agro, ganado, hidro


# ---------------------------------------------------------------------------
# 6. Tablas comunes: agricultura, ganadería y petróleo/gas de todos los países juntos
# ---------------------------------------------------------------------------
# Cada país nombra los cultivos en su idioma y con su criterio ("Milho (em grão)", "Maiz",
# "Maíz"). La columna cultivo guarda un nombre común para los principales, así se puede
# comparar la soja de Mato Grosso con la de Córdoba; cultivo_original queda como vino.
# Ojo con no sumar dos veces: "Soja total" = 1ra + 2da (Argentina), "Café (em grão) Total" =
# Arábica + Canephora (Brasil). Solo el total recibe nombre común.
CULTIVO_COMUN = {
    "soja (em grao)": "Soja", "soya": "Soja", "soja total": "Soja",
    "milho (em grao)": "Maíz", "maiz": "Maíz",
    "trigo (em grao)": "Trigo", "trigo total": "Trigo", "trigo": "Trigo",
    "arroz (em casca)": "Arroz", "arroz": "Arroz",
    "feijao (em grao)": "Frijol / poroto", "frijol": "Frijol / poroto", "poroto total": "Frijol / poroto",
    "cana-de-acucar": "Caña de azúcar", "cana azucarera": "Caña de azúcar", "cana de azucar": "Caña de azúcar",
    "cafe (em grao) total": "Café", "cafe": "Café",
    "mandioca": "Mandioca / yuca", "yuca": "Mandioca / yuca",
    "algodao herbaceo (em caroco)": "Algodón", "algodon": "Algodón",
    "laranja": "Naranja", "naranja": "Naranja", "limao": "Limón", "limon": "Limón",
    "banana (cacho)": "Banana", "banano": "Banana", "banana": "Banana", "platano": "Plátano",
    "batata-inglesa": "Papa", "papa": "Papa", "papa total": "Papa",
    "cacau (em amendoa)": "Cacao", "cacao": "Cacao",
    "dende (cacho de coco)": "Palma aceitera", "palma de aceite": "Palma aceitera",
    "sorgo (em grao)": "Sorgo", "sorgo": "Sorgo",
    "girassol (em grao)": "Girasol", "girasol": "Girasol",
    "amendoim (em casca)": "Maní", "mani": "Maní",
    "cevada (em grao)": "Cebada", "cebada total": "Cebada", "aveia (em grao)": "Avena", "avena": "Avena",
    "uva": "Uva", "tomate": "Tomate", "cebola": "Cebolla", "cebolla de bulbo": "Cebolla",
    "cebolla total": "Cebolla", "fumo (em folha)": "Tabaco", "manga": "Mango", "mango": "Mango",
    "abacaxi*": "Ananá / piña", "pina": "Ananá / piña", "erva-mate (folha verde)": "Yerba mate",
    "yerba mate": "Yerba mate",
}
ESPECIE_COMUN = {"Bovino": "Bovinos", "Bovinos": "Bovinos", "Bubalino": "Búfalos", "Bufalinos": "Búfalos",
                 "Suíno - total": "Porcinos", "Ovino": "Ovinos", "Caprino": "Caprinos", "Equino": "Equinos",
                 "Galináceos - total": "Aves (gallinas y pollos)"}


def sin_tildes(texto):
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()


def argentina_para_comparar():
    """Las tablas de argentina_provincias/ con las mismas columnas que el resto."""
    carpeta = CARPETA.parent / "argentina_provincias"
    agro = pd.read_csv(carpeta / "agricultura_provincia_anual.csv").rename(columns={
        "provincia_iso": "subdivision_iso", "anio_cosecha": "anio", "cultivo": "cultivo_original",
        "sup_sembrada_ha": "area_sembrada_ha", "sup_cosechada_ha": "area_cosechada_ha",
        "produccion_tn": "produccion"})
    agro = agro.assign(unidad_produccion="Toneladas",
                       fuente="MAGyP - Estimaciones agrícolas (año = año de cosecha de la campaña)")
    bov = pd.read_csv(carpeta / "ganaderia_bovinos_provincia_anual.csv")
    ganado = pd.DataFrame({"subdivision_iso": bov.provincia_iso, "anio": bov.anio, "especie_original": "Bovinos",
                           "cabezas": bov.total_cabezas, "fuente": "MAGyP / SENASA - Stock bovino al 31-12"})
    hc = pd.read_csv(carpeta / "petroleo_gas_provincia_anual.csv")
    hc = hc[hc.provincia_iso.isin(NOMBRE_SUBDIVISION)]  # sin "Estado Nacional" (costa afuera)
    hidro = pd.DataFrame({"subdivision_iso": hc.provincia_iso, "anio": hc.anio, "petroleo_m3": hc.petroleo_m3_total,
                          "gas_miles_m3": hc.gas_miles_m3_total, "meses_con_dato": hc.meses_con_dato,
                          "fuente": "Secretaría de Energía - SESCO + Cap. IV (sin costa afuera)"})
    return agro, ganado, hidro


def procesar_tablas_comunes(brasil, colombia):
    argentina = argentina_para_comparar()
    agro = pd.concat([argentina[0], brasil[0], colombia[0]], ignore_index=True)
    # Valor de la producción solo en reales (Brasil desde 1994; antes, monedas viejas)
    agro["valor_produccion_miles_moneda_local"] = agro.valor_produccion.where(
        agro.get("unidad_valor_produccion").eq("Mil Reais"))
    agro["cultivo_original"] = agro.cultivo_original.astype(str).str.strip()
    agro["cultivo"] = agro.cultivo_original.map(lambda c: CULTIVO_COMUN.get(sin_tildes(c).lower()))
    agro = agro[["subdivision_iso", "anio", "cultivo", "cultivo_original", "area_sembrada_ha", "area_cosechada_ha",
                 "produccion", "unidad_produccion", "valor_produccion_miles_moneda_local", "fuente"]]
    agro = guardar(agro, "agricultura_subdivision_anual.csv", ["iso3", "subdivision_iso", "cultivo_original", "anio"])
    print(f"  Agricultura: {len(agro):,} filas, {agro.iso3.nunique()} países, "
          f"{agro.subdivision_iso.nunique()} subdivisiones, {agro.anio.min()}-{agro.anio.max()}")

    ganado = pd.concat([argentina[1], brasil[1], colombia[1]], ignore_index=True)
    ganado["especie"] = ganado.especie_original.map(ESPECIE_COMUN)
    ganado = guardar(ganado[["subdivision_iso", "anio", "especie", "especie_original", "cabezas", "fuente"]],
                     "ganaderia_subdivision_anual.csv", ["iso3", "subdivision_iso", "especie_original", "anio"])
    print(f"  Ganadería: {len(ganado):,} filas, {ganado.iso3.nunique()} países, {ganado.anio.min()}-{ganado.anio.max()}")

    hidro = pd.concat([argentina[2], brasil[2], colombia[2]], ignore_index=True)
    hidro[["petroleo_m3", "gas_miles_m3"]] = hidro[["petroleo_m3", "gas_miles_m3"]].round(1)
    hidro = guardar(hidro, "petroleo_gas_subdivision_anual.csv", ["iso3", "subdivision_iso", "anio"])
    print(f"  Petróleo y gas: {len(hidro):,} filas, {hidro.iso3.nunique()} países, {hidro.anio.min()}-{hidro.anio.max()}")


if __name__ == "__main__":
    CRUDOS.mkdir(exist_ok=True)
    print("1. Estadísticas regionales de la OCDE")
    procesar_ocde()
    print("2. Temperatura media anual (Banco Mundial, ERA5; México de la OCDE)")
    procesar_temperatura()
    print("3. Gobernadores según Wikidata")
    procesar_gobernantes()
    print("4. Brasil por estado (IBGE y ANP)")
    brasil = procesar_brasil()
    print("5. Colombia por departamento (datos.gov.co)")
    colombia = procesar_colombia()
    print("6. Tablas comunes de agricultura, ganadería y petróleo/gas (con Argentina)")
    procesar_tablas_comunes(brasil, colombia)
