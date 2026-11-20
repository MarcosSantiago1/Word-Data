"""
Kilómetros de subterráneo / metro por ciudad y por país.

Qué hace
--------
1. Baja de Wikipedia la tabla "List of metro systems" (todos los metros del mundo: ciudad, país,
   apertura, última ampliación, estaciones, largo del sistema y pasajeros por año). Es la referencia
   más pareja a nivel mundial: solo cuenta "metro" (tránsito rápido de alta capacidad), no tranvías,
   trenes suburbanos ni la mayoría de los trenes ligeros.
2. Busca en Wikipedia y Wikidata el código Wikidata y las coordenadas de la ciudad de cada sistema.
3. Asigna cada sistema a una de las 375 ciudades de +2 millones del scorecard
   (riesgo_ciudades_mundo/datos/ciudades_mundo.csv): primero por código Wikidata, después por la
   ciudad más cercana del mismo país a menos de DIST_MAX_KM, y con correcciones a mano (ASIGNACION).
4. Suma por ciudad (algunas tienen más de un sistema, p. ej. Tokio o Bombay) y por país (todos los
   sistemas del país, estén o no en una ciudad de la lista).
5. Guarda una "foto" por año en historial_metro_sistemas.csv: como la tabla de Wikipedia da solo el
   largo actual, la serie por año se arma sola con cada corrida mensual (el último dato de cada año).

Salidas (datos/)
----------------
- sistemas_metro_mundo.csv     un sistema por fila (234 al 20-11-2026), con la ciudad del scorecard asignada
- metro_ciudades.csv           las 375 ciudades: metro_km, metro_m, sistemas, estaciones, pasajeros, km por millón
- metro_paises.csv             por país (iso3): km, metros, sistemas, ciudades con metro, km por millón de hab.
- pais_metro_anual.csv         lo mismo en formato iso3 + anio (entra al master y a la base absoluta)
- metro_subdivision_anual.csv  Latinoamérica: km por provincia/estado (ISO 3166-2) donde está cada red
- historial_metro_sistemas.csv foto anual por sistema (fecha de consulta, revisión de Wikipedia)
- diccionario_metro.csv        qué es cada columna

Variables de entorno: ETL_REFRESCAR=1 vuelve a bajar Wikipedia/Wikidata (si falla, usa la copia en crudos/).
"""
import io
import json
import math
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from urllib.parse import unquote

AQUI = Path(__file__).resolve().parent
ETL = AQUI.parent
CRUDOS = AQUI / "crudos"
DATOS = AQUI / "datos"
CIUDADES = ETL / "riesgo_ciudades_mundo" / "datos" / "ciudades_mundo.csv"
MAESTRO = ETL / "maestros" / "paises_maestro.csv"
PANEL = ETL / "datos_procesados" / "paises_anual.csv"

REFRESCAR = os.environ.get("ETL_REFRESCAR") == "1"
UA = {"User-Agent": "word-data-etl/1.0 (proyecto de datos abiertos; python-requests)"}
WIKI_API = "https://en.wikipedia.org/w/api.php"
SPARQL = "https://query.wikidata.org/sparql"
PAGINA = "List_of_metro_systems"
URL_TABLA = f"{WIKI_API}?action=parse&page={PAGINA}&prop=revid&format=json"  # para chequear_fuentes.py
FUENTE = "Wikipedia, List of metro systems (largo del sistema); Wikidata (ciudad y coordenadas)"
DIST_MAX_KM = 25
LATAM = {"ARG", "BOL", "BRA", "CHL", "COL", "CRI", "CUB", "DOM", "ECU", "GTM", "HND", "MEX", "NIC", "PAN", "PER",
         "PRY", "SLV", "URY", "VEN"}

# Países de la tabla de Wikipedia cuyo nombre en inglés no coincide con el maestro
PAIS_A_ISO3 = {"Czech Republic": "CZE", "Egypt": "EGY", "Iran": "IRN", "North Korea": "PRK", "Russia": "RUS",
               "South Korea": "KOR", "Turkey": "TUR", "Venezuela": "VEN", "Vietnam": "VNM", "Taiwan": "TWN"}
# Ciudades que Wikipedia pone bajo "China" pero en el proyecto son territorio aparte
CIUDAD_A_ISO3 = {"Hong Kong": "HKG", "Macau": "MAC", "Macao": "MAC"}

# Correcciones a mano: nombre del sistema en Wikipedia -> ids de ciudades del scorecard ([] = ninguna).
# Regla: un sistema cuenta para una ciudad si tiene estaciones dentro de su gobierno local; si cruza varias
# ciudades de la lista cuenta completo en cada una (el total por país no se duplica: suma sistemas).
# Revisado el 20-11-2026 contra los mapas de cada red.
ASIGNACION = {
    "Gurugram Metro": [],             # todo en Gurugram (Haryana), fuera de la Corporación Municipal de Delhi
    "Noida Metro": [],                # todo en Noida (Uttar Pradesh)
    "Navi Mumbai Metro": [],          # Corporación Municipal de Navi Mumbai, distinta de Gran Mumbai
    "New Shuttle": [],                # prefectura de Saitama
    "Saitama Rapid Railway Line": [], # estaciones propias en Saitama (la terminal Akabane-iwabuchi es de Tokyo Metro)
    "Gimpo Goldline": ["seul"],       # Gimpo; su terminal Aeropuerto de Gimpo está en Seúl (Gangseo-gu)
    "Dhaka Metro Rail": ["dhaka_norte", "dhaka_sur"],  # línea 6: Uttara-Agargaon (norte), Shahbagh-Motijheel (sur)
    "Cairo Metro": ["el_cairo", "giza"],               # líneas 2 y 3 entran a Guiza (Dokki, Universidad, El Mounib)
    "Jabodebek LRT": ["yakarta", "bekasi", "depok"],   # ramales a Bekasi (Cikunir, Bekasi Barat) y Depok (Harjamukti)
    "Manila Light Rail Transit System": ["quezon"],    # LRT-1 (Roosevelt) y LRT-2 (Cubao, Anonas, Katipunan)
    "Manila Metro Rail Transit System": ["quezon"],    # MRT-3 por EDSA: North Avenue, Quezon Avenue, Cubao
}

# Latinoamérica: sistema -> subdivisión de primer nivel (ISO 3166-2) donde está la red, para sumar el metro
# a la base por provincia/estado (base absoluta). Si cruza el límite, va a la subdivisión con más estaciones.
SUBDIVISION_LATAM = {
    "Buenos Aires Underground": "AR-C", "Belo Horizonte Metro": "BR-MG", "Federal District Metro": "BR-DF",
    "Fortaleza Metro": "BR-CE", "Porto Alegre Metro": "BR-RS", "Recife Metro": "BR-PE",
    "Rio de Janeiro Metro": "BR-RJ", "Salvador Metro": "BR-BA", "São Paulo Metro": "BR-SP",
    "Santiago Metro": "CL-RM", "Medellín Metro": "CO-ANT", "Santo Domingo Metro": "DO-40",  # región Ozama
    "Quito Metro": "EC-P", "SITEUR": "MX-JAL", "Mexico City Metro": "MX-CMX", "Metrorrey": "MX-NLE",
    "Panama Metro": "PA-8", "Lima and Callao Metro": "PE-LMA", "Caracas Metro": "VE-A",
    "Maracaibo Metro": "VE-V", "Metro Valencia": "VE-G",
}


def get(url, **kw):
    """GET con reintentos; ante 429 (Wikipedia limita pedidos seguidos) espera lo que pide Retry-After."""
    for intento in range(5):
        try:
            r = requests.get(url, headers=UA, timeout=90, **kw)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            if intento == 4:
                raise
            espera = 10 * (intento + 1)
            if getattr(e.response, "status_code", None) == 429:
                espera = max(espera, int(e.response.headers.get("Retry-After", 0) or 0), 30)
            print(f"  reintento {intento + 1} en {espera} s ({type(e).__name__})")
            time.sleep(espera)


def con_cache(nombre, bajar):
    """Usa crudos/<nombre> salvo ETL_REFRESCAR=1; si la descarga falla, vuelve a la copia anterior."""
    ruta = CRUDOS / nombre
    if ruta.exists() and not REFRESCAR:
        return json.loads(ruta.read_text(encoding="utf-8"))
    try:
        datos = bajar()
    except Exception as e:  # noqa: BLE001
        if not ruta.exists():
            raise
        print(f"AVISO_FUENTE: no se pudo bajar {nombre} ({e}); se usa la copia anterior")
        return json.loads(ruta.read_text(encoding="utf-8"))
    CRUDOS.mkdir(exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    return datos


def bajar_tabla():
    r = get(WIKI_API, params={"action": "parse", "page": PAGINA, "prop": "text|revid", "format": "json",
                              "formatversion": 2})
    p = r.json()["parse"]
    return {"revid": p["revid"], "fecha_consulta": date.today().isoformat(), "html": p["text"]}


def numero(texto, patron=r"([\d][\d,]*\.?\d*)"):
    m = re.search(patron, str(texto))
    return float(m.group(1).replace(",", "")) if m else None


def anio(texto):
    m = re.search(r"(1[89]\d\d|20\d\d)", str(texto))
    return int(m.group(1)) if m else None


def leer_sistemas(crudo):
    tablas = pd.read_html(io.StringIO(crudo["html"]), extract_links="body")
    t = next(x for x in tablas if {"Name", "City", "Country", "System length"} <= set(x.columns))
    assert len(t) > 150, f"la tabla de Wikipedia vino corta ({len(t)} filas)"
    texto = t.map(lambda v: v[0] if isinstance(v, tuple) else v)
    enlace = t.map(lambda v: v[1] if isinstance(v, tuple) else None)
    s = pd.DataFrame({
        "sistema": texto["Name"].str.replace(r"\[.*?\]", "", regex=True).str.strip(),
        "ciudad_wikipedia": texto["City"].str.replace(r"\[.*?\]", "", regex=True).str.strip(),
        "pais_wikipedia": texto["Country"].str.strip(),
        "anio_apertura": texto["Service opened"].map(anio),
        "anio_ultima_ampliacion": texto["Last expanded"].map(anio),
        "estaciones": texto["Stations"].map(numero),
        "largo_km": texto["System length"].map(lambda v: numero(v, r"([\d][\d,]*\.?\d*)\s*km")),
        "pasajeros_anuales_millones": texto["Annual ridership (millions)"].map(numero),
        "anio_pasajeros": texto["Annual ridership (millions)"].map(
            lambda v: anio(re.search(r"\((\d{4})\)", str(v)).group(1)) if re.search(r"\((\d{4})\)", str(v)) else None),
        "sistema_wiki": enlace["Name"].map(lambda h: unquote(h.split("/wiki/")[-1]) if h and "/wiki/" in h else None),
        "ciudad_wiki": enlace["City"].map(lambda h: unquote(h.split("/wiki/")[-1]) if h and "/wiki/" in h else None),
    })
    assert s.largo_km.notna().mean() > 0.95, "no se pudo leer el largo de muchos sistemas"
    s["largo_m"] = (s.largo_km * 1000).round().astype("Int64")
    s["estaciones"] = s.estaciones.astype("Int64")
    return s


def bajar_qids(titulos):
    """Título de Wikipedia -> código Wikidata (sigue redirecciones)."""
    salida = {}
    for i in range(0, len(titulos), 50):
        lote = titulos[i:i + 50]
        time.sleep(1)
        r = get(WIKI_API, params={"action": "query", "prop": "pageprops", "ppprop": "wikibase_item",
                                  "redirects": 1, "titles": "|".join(lote), "format": "json", "formatversion": 2})
        q = r.json()["query"]
        nuevo = {n["from"]: n["to"] for n in q.get("normalized", [])}
        redir = {n["from"]: n["to"] for n in q.get("redirects", [])}
        por_titulo = {p["title"]: p.get("pageprops", {}).get("wikibase_item") for p in q["pages"]}
        for t in lote:
            u = nuevo.get(t.replace("_", " "), t.replace("_", " "))
            u = redir.get(u, u)
            salida[t] = por_titulo.get(u)
    return salida


def bajar_coordenadas(qids):
    salida = {}
    for i in range(0, len(qids), 200):
        valores = " ".join(f"wd:{q}" for q in qids[i:i + 200])
        consulta = f"""SELECT ?q (SAMPLE(?c) AS ?coord) WHERE {{ VALUES ?q {{ {valores} }}
                       ?q wdt:P625 ?c . }} GROUP BY ?q"""
        r = get(SPARQL, params={"query": consulta, "format": "json"})
        for b in r.json()["results"]["bindings"]:
            lon, lat = map(float, re.findall(r"-?[\d.]+", b["coord"]["value"])[:2])
            salida[b["q"]["value"].rsplit("/", 1)[-1]] = [lat, lon]
    return salida


def distancia_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def poblacion_pais():
    """Población del Banco Mundial (paso 1), último año con dato por país."""
    if not PANEL.exists():
        return None
    pob = pd.read_csv(PANEL, usecols=["iso3", "anio", "poblacion"]).dropna()
    return pob.sort_values("anio").groupby("iso3").poblacion.last()


def asignar(s, ciudades):
    por_qid = {q: i for q, i in zip(ciudades.wikidata, ciudades.id) if isinstance(q, str)}
    asignada, metodo, dist = [], [], []
    for _, f in s.iterrows():
        if f.sistema in ASIGNACION:
            asignada.append(";".join(ASIGNACION[f.sistema]) or None); metodo.append("a mano"); dist.append(None)
            continue
        if f.ciudad_qid in por_qid:
            asignada.append(por_qid[f.ciudad_qid]); metodo.append("código Wikidata"); dist.append(0.0)
            continue
        cand = ciudades[ciudades.iso3 == f.iso3]
        if pd.isna(f.lat) or cand.empty:
            asignada.append(None); metodo.append("sin ciudad de la lista"); dist.append(None)
            continue
        d = cand.apply(lambda c: distancia_km(f.lat, f.lon, c.lat, c.lon), axis=1)
        if d.min() <= DIST_MAX_KM:
            asignada.append(cand.loc[d.idxmin(), "id"]); metodo.append("ciudad más cercana"); dist.append(round(d.min(), 1))
        else:
            asignada.append(None); metodo.append("sin ciudad de la lista"); dist.append(round(d.min(), 1))
    s["ciudad_id"], s["asignacion"], s["distancia_km"] = asignada, metodo, dist
    return s


def main():
    print("1/5 Tabla de Wikipedia")
    crudo = con_cache("wikipedia_list_of_metro_systems.json", bajar_tabla)
    s = leer_sistemas(crudo)
    s["fecha_consulta"], s["revision_wikipedia"] = crudo["fecha_consulta"], crudo["revid"]
    print(f"   {len(s)} sistemas, {s.largo_km.sum():,.0f} km, revisión {crudo['revid']} del {crudo['fecha_consulta']}")

    maestro = pd.read_csv(MAESTRO, keep_default_na=False, na_values=[""])
    iso = dict(zip(maestro.nombre_en, maestro.iso3)) | PAIS_A_ISO3
    s["iso3"] = s.pais_wikipedia.map(iso)
    s.loc[s.ciudad_wikipedia.isin(CIUDAD_A_ISO3), "iso3"] = s.ciudad_wikipedia.map(CIUDAD_A_ISO3)
    assert s.iso3.notna().all(), s[s.iso3.isna()].pais_wikipedia.unique()

    print("2/5 Códigos Wikidata y coordenadas")
    titulos = sorted(set(s.ciudad_wiki.dropna()) | set(s.sistema_wiki.dropna()))
    qids = con_cache("wikipedia_qids.json", lambda: bajar_qids(titulos))
    if set(titulos) - set(qids):  # páginas nuevas en la tabla
        qids |= bajar_qids(sorted(set(titulos) - set(qids)))
        (CRUDOS / "wikipedia_qids.json").write_text(json.dumps(qids, ensure_ascii=False), encoding="utf-8")
    s["sistema_qid"], s["ciudad_qid"] = s.sistema_wiki.map(qids), s.ciudad_wiki.map(qids)
    todos = sorted({q for q in qids.values() if q})
    coords = con_cache("wikidata_coordenadas.json", lambda: bajar_coordenadas(todos))
    if set(todos) - set(coords) - set(coords.get("_sin", [])):
        faltan = sorted(set(todos) - set(coords) - set(coords.get("_sin", [])))
        nuevas = bajar_coordenadas(faltan)
        coords |= nuevas
        coords["_sin"] = sorted(set(coords.get("_sin", [])) | (set(faltan) - set(nuevas)))
        (CRUDOS / "wikidata_coordenadas.json").write_text(json.dumps(coords, ensure_ascii=False), encoding="utf-8")
    # coordenadas de la ciudad; si la ciudad no tiene, las del sistema
    for col in ("lat", "lon"):
        k = 0 if col == "lat" else 1
        s[col] = [coords.get(c, coords.get(q, [None, None]))[k] if (c or q) else None
                  for c, q in zip(s.ciudad_qid, s.sistema_qid)]

    print("3/5 Asignación a las 375 ciudades")
    ciudades = pd.read_csv(CIUDADES)
    s = asignar(s, ciudades)
    print("   " + ", ".join(f"{k}: {v}" for k, v in s.asignacion.value_counts().items()))

    print("4/5 Sumas por ciudad y por país")
    con = s[s.ciudad_id.notna()].assign(ciudad_id=lambda d: d.ciudad_id.str.split(";")).explode("ciudad_id")
    assert set(con.ciudad_id) <= set(ciudades.id), set(con.ciudad_id) - set(ciudades.id)
    por_ciudad = con.groupby("ciudad_id").agg(
        metro_km=("largo_km", "sum"), n_sistemas=("sistema", "size"),
        sistemas=("sistema", lambda x: "; ".join(x)), estaciones=("estaciones", "sum"),
        anio_apertura=("anio_apertura", "min"), anio_ultima_ampliacion=("anio_ultima_ampliacion", "max"),
        pasajeros_anuales_millones=("pasajeros_anuales_millones", lambda x: x.sum(min_count=1)),
        anio_pasajeros=("anio_pasajeros", "max"))
    mc = ciudades[["id", "nombre", "iso3", "pob", "anio_pob"]].merge(
        por_ciudad, left_on="id", right_index=True, how="left")
    mc["tiene_metro"] = mc.metro_km.notna().astype(int)
    mc["metro_km"] = mc.metro_km.fillna(0).round(1)
    mc["metro_m"] = (mc.metro_km * 1000).round().astype("Int64")
    mc["n_sistemas"] = mc.n_sistemas.fillna(0).astype(int)
    mc["estaciones"] = mc.estaciones.fillna(0).astype(int)
    mc["metro_km_por_millon_hab"] = (mc.metro_km / (mc.pob / 1e6)).round(2)
    mc["pasajeros_por_hab"] = (mc.pasajeros_anuales_millones * 1e6 / mc.pob).round(1)
    for c in ("anio_apertura", "anio_ultima_ampliacion", "anio_pasajeros"):
        mc[c] = mc[c].astype("Int64")
    mc["anio_dato"] = int(crudo["fecha_consulta"][:4])
    mc["fecha_consulta"], mc["fuente"] = crudo["fecha_consulta"], FUENTE
    mc = mc.rename(columns={"id": "ciudad_id", "pob": "poblacion", "anio_pob": "anio_poblacion"})
    mc = mc[["ciudad_id", "nombre", "iso3", "tiene_metro", "metro_km", "metro_m", "n_sistemas", "sistemas",
             "estaciones", "anio_apertura", "anio_ultima_ampliacion", "pasajeros_anuales_millones",
             "anio_pasajeros", "poblacion", "anio_poblacion", "metro_km_por_millon_hab", "pasajeros_por_hab",
             "anio_dato", "fecha_consulta", "fuente"]]

    pais = s.groupby("iso3").agg(
        metro_km=("largo_km", "sum"), metro_sistemas=("sistema", "size"),
        metro_ciudades=("ciudad_wikipedia", "nunique"), metro_estaciones=("estaciones", "sum"),
        metro_pasajeros_anuales_millones=("pasajeros_anuales_millones", lambda x: x.sum(min_count=1))
    ).reset_index()
    pais["metro_km"] = pais.metro_km.round(1)
    pais["metro_m"] = (pais.metro_km * 1000).round().astype("Int64")
    pais["anio"] = int(crudo["fecha_consulta"][:4])
    pob = poblacion_pais()
    if pob is not None:
        pais["metro_km_por_millon_hab"] = (pais.metro_km / pais.iso3.map(pob / 1e6)).round(2)
    pais.insert(1, "pais", pais.iso3.map(dict(zip(maestro.iso3, maestro.nombre_es))))

    print("5/5 Historial anual y archivos")
    DATOS.mkdir(exist_ok=True)
    hist_ruta = DATOS / "historial_metro_sistemas.csv"
    foto = s[["sistema", "ciudad_wikipedia", "iso3", "ciudad_id", "largo_km", "largo_m", "estaciones",
              "fecha_consulta", "revision_wikipedia"]].assign(anio=int(crudo["fecha_consulta"][:4]))
    hist = pd.concat([pd.read_csv(hist_ruta), foto]) if hist_ruta.exists() else foto
    hist = (hist.sort_values("fecha_consulta").drop_duplicates(["sistema", "iso3", "anio"], keep="last")
            .sort_values(["anio", "iso3", "sistema"]))
    # serie por país: el último dato de cada año del historial
    anual = (hist.groupby(["iso3", "anio"]).agg(metro_km=("largo_km", "sum"), metro_sistemas=("sistema", "size"))
             .reset_index())
    anual["metro_km"] = anual.metro_km.round(1)
    anual["metro_m"] = (anual.metro_km * 1000).round().astype("Int64")
    if pob is not None:
        anual["metro_km_por_millon_hab"] = (anual.metro_km / anual.iso3.map(pob / 1e6)).round(2)

    # Latinoamérica por subdivisión (serie anual desde el historial)
    sub = hist[hist.sistema.isin(SUBDIVISION_LATAM)].assign(subdivision_iso=lambda d: d.sistema.map(SUBDIVISION_LATAM))
    faltan = set(s.loc[s.iso3.isin(LATAM), "sistema"]) - set(SUBDIVISION_LATAM)
    if faltan:
        print(f"AVISO: sistemas latinoamericanos nuevos sin subdivisión asignada: {sorted(faltan)}")
    sub = (sub.groupby(["iso3", "subdivision_iso", "anio"])
           .agg(metro_km=("largo_km", "sum"), metro_sistemas=("sistema", "size"), metro_estaciones=("estaciones", "sum"))
           .reset_index())
    sub["metro_km"] = sub.metro_km.round(1)
    sub["metro_m"] = (sub.metro_km * 1000).round().astype("Int64")
    nombres_sub = pd.read_csv(ETL / "maestros" / "subdivisiones_maestro.csv", usecols=["subdivision_iso", "nombre_es"])
    sub.insert(2, "subdivision", sub.subdivision_iso.map(dict(zip(nombres_sub.subdivision_iso, nombres_sub.nombre_es))))
    assert sub.subdivision.notna().all(), sub[sub.subdivision.isna()]
    sub.to_csv(DATOS / "metro_subdivision_anual.csv", index=False)

    s_out = s[["sistema", "ciudad_wikipedia", "pais_wikipedia", "iso3", "ciudad_id", "asignacion", "distancia_km",
               "largo_km", "largo_m", "estaciones", "anio_apertura", "anio_ultima_ampliacion",
               "pasajeros_anuales_millones", "anio_pasajeros", "sistema_qid", "ciudad_qid", "lat", "lon",
               "fecha_consulta", "revision_wikipedia"]]
    for c in ("anio_apertura", "anio_ultima_ampliacion", "anio_pasajeros"):
        s_out[c] = s_out[c].astype("Int64")
    s_out.to_csv(DATOS / "sistemas_metro_mundo.csv", index=False)
    mc.to_csv(DATOS / "metro_ciudades.csv", index=False)
    pais.to_csv(DATOS / "metro_paises.csv", index=False)
    anual.to_csv(DATOS / "pais_metro_anual.csv", index=False)
    hist.to_csv(hist_ruta, index=False)
    pd.DataFrame(DICCIONARIO, columns=["archivo", "columna", "descripcion", "unidad"]).to_csv(
        DATOS / "diccionario_metro.csv", index=False)

    print(f"   ciudades con metro: {mc.tiene_metro.sum()} de {len(mc)}; "
          f"km en esas ciudades: {mc.metro_km.sum():,.0f}; países con metro: {len(pais)}")
    print(mc.sort_values("metro_km", ascending=False).head(10)[["nombre", "metro_km", "n_sistemas"]]
          .to_string(index=False))


DICCIONARIO = [
    ("metro_ciudades.csv", "ciudad_id", "id de la ciudad en riesgo_ciudades_mundo/datos/ciudades_mundo.csv", ""),
    ("metro_ciudades.csv", "tiene_metro", "1 si la ciudad tiene al menos un sistema de metro en la lista de Wikipedia", "0/1"),
    ("metro_ciudades.csv", "metro_km", "largo total de los sistemas de metro que sirven a la ciudad (0 = sin metro)", "km"),
    ("metro_ciudades.csv", "metro_m", "lo mismo en metros", "m"),
    ("metro_ciudades.csv", "n_sistemas", "cantidad de sistemas de metro sumados", "sistemas"),
    ("metro_ciudades.csv", "sistemas", "nombres de los sistemas (Wikipedia, en inglés)", ""),
    ("metro_ciudades.csv", "estaciones", "estaciones de todos los sistemas", "estaciones"),
    ("metro_ciudades.csv", "anio_apertura", "año en que abrió el primer sistema", "año"),
    ("metro_ciudades.csv", "anio_ultima_ampliacion", "año de la última ampliación de la red", "año"),
    ("metro_ciudades.csv", "pasajeros_anuales_millones", "viajes por año (suma de los sistemas con dato)", "millones"),
    ("metro_ciudades.csv", "metro_km_por_millon_hab", "km de metro por millón de habitantes del gobierno local", "km/millón hab."),
    ("metro_ciudades.csv", "pasajeros_por_hab", "viajes en metro por habitante y año", "viajes/hab."),
    ("metro_ciudades.csv", "anio_dato", "año de la consulta a Wikipedia (el largo es el vigente ese año)", "año"),
    ("metro_paises.csv", "metro_km", "largo de todos los metros del país, estén o no en una de las 375 ciudades", "km"),
    ("metro_paises.csv", "metro_ciudades", "ciudades del país con metro", "ciudades"),
    ("metro_paises.csv", "metro_km_por_millon_hab", "km por millón de habitantes (población Banco Mundial, último año)", "km/millón hab."),
    ("metro_subdivision_anual.csv", "metro_km", "km de metro de las redes latinoamericanas ubicadas en la subdivisión", "km"),
    ("pais_metro_anual.csv", "anio", "año de la foto; la serie crece con cada corrida mensual", "año"),
    ("sistemas_metro_mundo.csv", "asignacion", "cómo se unió a la ciudad: código Wikidata, ciudad más cercana del país "
     f"(≤{DIST_MAX_KM} km), a mano, o sin ciudad de la lista", ""),
    ("sistemas_metro_mundo.csv", "distancia_km", "distancia entre el centro de la ciudad del sistema y la ciudad asignada", "km"),
]

if __name__ == "__main__":
    sys.exit(main())
