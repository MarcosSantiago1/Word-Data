"""
CIA World Factbook: lo que aporta y no tenemos de otras fuentes.

La CIA dejó de publicar el World Factbook el 4 de febrero de 2026. Queda una copia de dominio
público en GitHub (github.com/factbook/factbook.json), un JSON por país que se actualizaba
cada semana. Usamos la última versión con datos (22 de enero de 2026), fijada por su commit,
así que el script siempre baja exactamente lo mismo.

Del Factbook tomamos SOLO lo que no cubren mejor el Banco Mundial, la OMS, ILOSTAT, COW o
Wikidata (que ya dan series de 2000 a 2024). Arma cinco tablas en etl/factbook/:

    factbook_entidades.csv            las 261 entidades del Factbook y su iso3 (o por qué no tienen)
    factbook_perfil_pais.csv          una fila por entidad: superficie, costa, elevación, clima,
                                      tipo de gobierno, sistema legal, independencia, sufragio...
    factbook_fronteras.csv            una fila por par de vecinos, con los km de frontera
    factbook_composicion.csv          religiones, etnias e idiomas con su % (formato largo)
    factbook_socios_comerciales.csv   5 principales destinos de exportación y orígenes de importación

Clave de unión: iso3. Ojo: Palestina tiene DOS entidades en el Factbook (Cisjordania "we" y
Franja de Gaza "gz"), por eso las tablas llevan también codigo_gec.

Uso:  python extraer_factbook.py
Requiere: requests, pandas
"""

import html
import json
import re
from pathlib import Path

import pandas as pd
import requests

AQUI = Path(__file__).resolve().parent
CRUDOS = AQUI / "crudos"
MAESTROS = AQUI.parent / "maestros"

COMMIT = "783ed27f7a1116663c10e7b39d162d0c4500505d"  # "auto-update week 4", 22-01-2026
FECHA_SNAPSHOT = "2026-01-22"
URL_JSON = f"https://raw.githubusercontent.com/factbook/factbook.json/{COMMIT}/{{region}}/{{gec}}.json"
WIKIDATA = "https://query.wikidata.org/sparql"
CABECERA = {"User-Agent": "analista-datos-etl/1.0 (proyecto educativo)"}

# La API de GitHub no está habilitada en el entorno: la lista de archivos va escrita acá
REGIONES = {
    "africa": "ag ao bc bn by cd cf cg cm cn ct cv dj eg ek er et ga gb gh gv iv ke li lt ly ma mi ml mo mp "
              "mr mz ng ni od pu rw se sf sg sh sl so su to tp ts tz ug uv wa wi wz za zi",
    "antarctica": "ay bv fs hm",
    "australia-oceania": "aq as at bp ck cq cr cw fj fm fp gq kr kt nc ne nf nh nr nz pc ps rm tl tn tv um "
                         "wf wq ws",
    "central-america-n-caribbean": "aa ac av bb bf bh bq cj cs cu do dr es gj gt ha ho jm mh nn nu pm rn rq "
                                   "sc st tb td tk uc vc vi vq",
    "central-asia": "kg kz rs ti tx uz",
    "east-n-southeast-asia": "bm bx cb ch hk id ja kn ks la mc mg my pf pg pp rp sn th tt tw vm",
    "europe": "al an au ax be bk bo bu cy da dx ee ei en ez fi fo fr gi gk gm gr hr hu ic im it je jn kv "
              "lg lh lo ls lu md mj mk mn mt nl no pl po ri ro si sm sp sv sw sz uk up vt",
    "middle-east": "ae aj am ba gg gz ir is iz jo ku le mu qa sa sy tu we ym",
    "north-america": "bd ca gl ip mx sb us",
    "oceans": "oo xo xq zh zn",
    "south-america": "ar bl br ci co ec fk gy ns pa pe sx uy ve",
    "south-asia": "af bg bt ce in io mv np pk",
    "world": "xx",
}

# ---------------------------------------------------------------------------
# Códigos de la CIA (GEC, antes FIPS 10-4) -> ISO 3166-1 alfa-3
# ---------------------------------------------------------------------------
# La base es Wikidata (propiedad P901, FIPS 10-4). Estos casos van a mano:
GEC_A_ISO3 = {
    "kv": "XKX",   # Kosovo: Wikidata dice XKS; el proyecto usa XKX (Banco Mundial)
    "nl": "NLD",   # Países Bajos: Wikidata no tiene su FIPS
    "sv": "SJM",   # Svalbard: ISO lo junta con Jan Mayen en SJM
    "um": "UMI",   # Islas menores alejadas de EE. UU.
    "we": "PSE",   # Cisjordania  } ISO las junta en Palestina;
    "gz": "PSE",   # Franja de Gaza } el Factbook las separa
}
SIN_ISO3 = {
    "at": "territorio australiano sin código ISO (Ashmore y Cartier)",
    "cr": "territorio australiano sin código ISO (Islas del Mar del Coral)",
    "ip": "territorio francés sin código ISO (Clipperton)",
    "ax": "base soberana británica en Chipre (Akrotiri)",
    "dx": "base soberana británica en Chipre (Dhekelia)",
    "jn": "parte de SJM; se usa Svalbard (sv)",
    "wq": "parte de UMI; se usa la entrada general (um)",
    "bq": "parte de UMI en ISO (isla Navaza); se usa la entrada general (um)",
    "pf": "islas en disputa (Paracel)", "pg": "islas en disputa (Spratly)",
    "ee": "Unión Europea (no es un país)", "xx": "el mundo",
    "oo": "océano Austral", "xo": "océano Índico", "xq": "océano Ártico",
    "zh": "océano Atlántico", "zn": "océano Pacífico",
}

# Cómo nombra el Factbook a otros países en fronteras y socios comerciales (lo que no sale solo)
ALIAS = {
    "US": "USA", "USA": "USA", "UK": "GBR", "UAE": "ARE", "S. Korea": "KOR", "N. Korea": "PRK",
    "South Korea": "KOR", "North Korea": "PRK", "DRC": "COD", "Democratic Republic of the Congo": "COD",
    "Republic of the Congo": "COG", "Congo, Republic of the": "COG", "Denmark (Greenland)": "GRL",
    "Gaza Strip": "PSE", "West Bank": "PSE", "Turkey": "TUR", "Russia": "RUS", "Vietnam": "VNM",
    "Burma": "MMR", "Laos": "LAO", "Macau": "MAC", "Hong Kong": "HKG", "Taiwan": "TWN", "Iran": "IRN",
    "Syria": "SYR", "Bolivia": "BOL", "Venezuela": "VEN", "Tanzania": "TZA", "Moldova": "MDA",
    "Czechia": "CZE", "The Gambia": "GMB", "The Bahamas": "BHS", "Brunei": "BRN", "Kosovo": "XKX",
    "Cote d'Ivoire": "CIV", "Curacao": "CUW", "Turkiye": "TUR", "Eswatini": "SWZ",
    "Bosnia and Herzegovina": "BIH", "North Macedonia": "MKD", "Saint Martin": "MAF",
    "Sint Maarten": "SXM", "Holy See (Vatican City)": "VAT", "Micronesia": "FSM",
    "Central African Republic": "CAF", "Cabo Verde": "CPV", "Timor-Leste": "TLS", "Macedonia": "MKD",
    "Saint Martin (France)": "MAF", "US Naval Base at Guantanamo Bay": "USA",
    "Antigua and Barbuda": "ATG", "St. Kitts and Nevis": "KNA", "St. Vincent and the Grenadines": "VCT",
    "Trinidad and Tobago": "TTO", "The Republic of the Congo": "COG",
}


def bajar(url, destino, **kw):
    if not destino.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, timeout=120, **kw)
        r.raise_for_status()
        destino.write_bytes(r.content)
    return destino


def limpiar(texto):
    """Saca HTML (<br>, <strong>, &nbsp;...) y espacios de más."""
    if texto is None:
        return None
    texto = html.unescape(re.sub(r"<[^>]+>", " ", str(texto))).replace("\xa0", " ")
    return re.sub(r"\s+", " ", texto).strip() or None


def campo(d, seccion, nombre, sub="text"):
    v = d.get(seccion, {}).get(nombre)
    if isinstance(v, dict):
        v = v.get(sub)
        if isinstance(v, dict):
            v = v.get("text")
    return limpiar(v)


def numero(texto):
    """'2,780,400 sq km' -> 2780400.0 ; '-105 m' -> -105.0"""
    if not texto:
        return None
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", texto)
    return float(m.group().replace(",", "")) if m else None


def nivel_cero(texto, separador):
    """Corta por `separador` solo fuera de paréntesis."""
    partes, actual, nivel = [], "", 0
    for ch in texto:
        nivel += (ch == "(") - (ch == ")")
        if ch == separador and nivel == 0:
            partes.append(actual)
            actual = ""
        else:
            actual += ch
    return partes + [actual]


# ---------------------------------------------------------------------------
# 1. Descarga y equivalencias
# ---------------------------------------------------------------------------
def descargar():
    paises = {}
    for region, codigos in REGIONES.items():
        for gec in codigos.split():
            archivo = bajar(URL_JSON.format(region=region, gec=gec), CRUDOS / "json" / region / f"{gec}.json")
            paises[gec] = (region, json.loads(archivo.read_text()))
    return paises


def entidades(paises, iso3_validos):
    consulta = "SELECT ?iso3 ?fips WHERE { ?p wdt:P298 ?iso3; wdt:P901 ?fips }"
    archivo = bajar(WIKIDATA, CRUDOS / "wikidata_fips_iso3.csv", params={"query": consulta},
                    headers=CABECERA | {"Accept": "text/csv"})
    wd = pd.read_csv(archivo, keep_default_na=False)
    wd = wd[wd.iso3.isin(iso3_validos)]
    desde_wikidata = dict(zip(wd.fips.str.lower(), wd.iso3))
    filas = []
    for gec, (region, d) in paises.items():
        nombre = campo(d, "Government", "Country name", "conventional short form")
        if nombre in (None, "none"):
            nombre = campo(d, "Government", "Country name", "conventional long form")
        if gec in SIN_ISO3:
            iso3, motivo = None, SIN_ISO3[gec]
        else:
            iso3, motivo = GEC_A_ISO3.get(gec, desde_wikidata.get(gec)), None
            assert iso3 in iso3_validos, (gec, nombre, iso3)
        filas.append(dict(codigo_gec=gec, region_factbook=region, nombre_factbook=nombre, iso3=iso3,
                          motivo_sin_iso3=motivo))
    ent = pd.DataFrame(filas)
    con_iso = ent[ent.iso3.notna()]
    repetidos = con_iso[con_iso.iso3.duplicated(keep=False)]
    assert set(repetidos.codigo_gec) == {"we", "gz"}, repetidos  # solo Palestina
    return ent


def diccionario_nombres(paises, ent, maestro):
    """Nombre en inglés -> iso3, con los nombres del propio Factbook, del maestro y los alias."""
    nombres = {}
    for r in maestro.itertuples():
        for n in (r.nombre_en, r.nombre_oficial_en, r.nombre_es):
            if isinstance(n, str):
                nombres[n] = r.iso3
    iso_de = dict(zip(ent.codigo_gec, ent.iso3))
    for gec, (_, d) in paises.items():
        for forma in ("conventional short form", "conventional long form", "abbreviation"):
            n = campo(d, "Government", "Country name", forma)
            if n and n != "none" and iso_de[gec]:
                nombres[n] = iso_de[gec]
    return nombres | ALIAS


# ---------------------------------------------------------------------------
# 2. Tablas
# ---------------------------------------------------------------------------
def perfil(paises, ent):
    filas = []
    for r in ent[ent.iso3.notna()].itertuples():
        d = paises[r.codigo_gec][1]
        area = d.get("Geography", {}).get("Area", {})
        total = area.get("total ", area.get("total", {})) if isinstance(area, dict) else {}
        alto = campo(d, "Geography", "Elevation", "highest point")
        bajo = campo(d, "Geography", "Elevation", "lowest point")
        sufragio = campo(d, "Government", "Suffrage")
        indep = campo(d, "Government", "Independence")
        # primer año del texto ("9 July 1816 (from Spain)"); no se toma "2,000 years" (Etiopía)
        anio_indep = (re.search(r"(?<![\d,])(\d{3,4})(?![\d,])", indep)
                      if indep and not indep.lower().startswith(("none", "no official")) else None)
        # la menor edad entre 15 y 25 que aparece ("voluntary between 16 and 18 years...; compulsory 18-70")
        edades = [int(n) for n in re.findall(r"\d+", sufragio or "") if 15 <= int(n) <= 25]
        filas.append(dict(
            iso3=r.iso3, codigo_gec=r.codigo_gec, fecha_snapshot=FECHA_SNAPSHOT,
            superficie_total_km2=numero(limpiar(total.get("text"))),
            superficie_tierra_km2=numero(campo(d, "Geography", "Area", "land")),
            superficie_agua_km2=numero(campo(d, "Geography", "Area", "water")),
            costa_km=numero(campo(d, "Geography", "Coastline")),
            fronteras_terrestres_km=numero(campo(d, "Geography", "Land boundaries", "total")),
            punto_mas_alto=re.sub(r"\s*-?[\d,\.]+ m\b.*$", "", alto) if alto else None,
            elevacion_maxima_m=numero(re.search(r"-?[\d,\.]+ m\b", alto).group()) if alto and re.search(r"-?[\d,\.]+ m\b", alto) else None,
            elevacion_minima_m=numero(re.search(r"-?[\d,\.]+ m\b", bajo).group()) if bajo and re.search(r"-?[\d,\.]+ m\b", bajo) else None,
            elevacion_media_m=numero(campo(d, "Geography", "Elevation", "mean elevation")),
            clima=campo(d, "Geography", "Climate"),
            terreno=campo(d, "Geography", "Terrain"),
            recursos_naturales=campo(d, "Geography", "Natural resources"),
            tipo_gobierno=campo(d, "Government", "Government type"),
            sistema_legal=campo(d, "Government", "Legal system"),
            independencia=indep,
            anio_independencia=int(anio_indep.group(1)) if anio_indep else None,
            sufragio=sufragio,
            edad_minima_voto=min(edades) if edades and "year" in sufragio else None,
            es_voto_obligatorio=(int("compulsory" in sufragio) if sufragio else None),
            servicio_militar=campo(d, "Military and Security", "Military service age and obligation"),
            exportaciones_productos=campo(d, "Economy", "Exports - commodities"),
            importaciones_productos=campo(d, "Economy", "Imports - commodities"),
        ))
    return pd.DataFrame(filas)


def fronteras(paises, ent, nombres):
    """'Bolivia 942 km; Brazil 1,263 km; ...' (a veces separado por comas o por "and")."""
    patron = re.compile(r"(?:^|[;,]\s*|\band\s+)([A-Z][^;,\d]*?)\s+(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*km"
                        r"(?:\s*\(([^)]*)\))?")
    filas, sin_mapear = [], set()
    gec_de_nombre = {"Gaza Strip": "gz", "West Bank": "we"}
    for r in ent[ent.iso3.notna()].itertuples():
        texto = campo(paises[r.codigo_gec][1], "Geography", "Land boundaries", "border countries")
        for m in patron.finditer(texto or ""):
            vecino, km, nota = m.groups()
            # "Russia (Kaliningrad Oblast)", "Spain (Ceuta)": si el nombre completo no está, el país sin paréntesis
            iso = nombres.get(vecino) or nombres.get(re.sub(r"\s*\(.*\)$", "", vecino))
            if iso is None:
                sin_mapear.add(vecino)
            filas.append(dict(iso3=r.iso3, codigo_gec=r.codigo_gec, vecino_iso3=iso,
                              vecino_codigo_gec=gec_de_nombre.get(vecino), vecino_nombre_factbook=vecino,
                              frontera_km=numero(km), nota=nota))
    f = pd.DataFrame(filas)
    # Un mismo vecino en dos tramos (China con Rusia noreste y noroeste; España con Ceuta y Melilla): se suman
    f = (f.groupby(["iso3", "codigo_gec", "vecino_iso3", "vecino_codigo_gec"], dropna=False, sort=False)
         .agg(vecino_nombre_factbook=("vecino_nombre_factbook", " + ".join), frontera_km=("frontera_km", "sum"),
              nota=("nota", lambda x: "; ".join(x.dropna()) or None)).reset_index())
    # el código GEC del vecino, cuando el vecino tiene una sola entidad
    unico = ent[ent.iso3.notna() & ~ent.codigo_gec.isin(["we", "gz"])].set_index("iso3").codigo_gec
    f["vecino_codigo_gec"] = f.vecino_codigo_gec.fillna(f.vecino_iso3.map(unico))
    return f, sin_mapear


def composicion(paises, ent):
    """Religiones, etnias e idiomas: 'Roman Catholic 62.9%, Evangelical 15.3% (...), ... (2019 est.)'"""
    filas = []
    for r in ent[ent.iso3.notna()].itertuples():
        d = paises[r.codigo_gec][1]
        for dimension, nombre, sub in [("religion", "Religions", "text"), ("etnia", "Ethnic groups", "text"),
                                       ("idioma", "Languages", "text")]:
            texto = campo(d, "People and Society", nombre, sub)
            if texto is None and dimension == "idioma":
                texto = campo(d, "People and Society", "Languages", "Languages")
            if not texto:
                continue
            texto = nivel_cero(texto, ";")[0].strip().rstrip(".")  # lo que sigue al ";" suele ser una nota
            anio = re.search(r"\((\d{4})(?: est\.)?\)\s*$", texto)
            if anio:
                texto = texto[:anio.start()].strip()
            for orden, item in enumerate(nivel_cero(texto, ","), start=1):
                item = re.sub(r"^\s*(and|&)\s+", "", item.strip())
                if not item:
                    continue
                parentesis = re.findall(r"\(([^()]*(?:\([^()]*\)[^()]*)*)\)", item)
                sin_par = re.sub(r"\((?:[^()]|\([^()]*\))*\)", "", item).strip()
                pct = re.search(r"(<|less than)?\s*(\d+(?:\.\d+)?)\s*%\s*$", sin_par)
                grupo = (sin_par[:pct.start()] if pct else sin_par).strip(" ,.")
                filas.append(dict(
                    iso3=r.iso3, codigo_gec=r.codigo_gec, dimension=dimension, orden=orden,
                    grupo=grupo or item, poblacion_pct=float(pct.group(2)) if pct else None,
                    es_cota_superior=int(bool(pct.group(1))) if pct else None,  # "<1%" o "less than 1%"
                    es_oficial=int(any("official" in p for p in parentesis)) if dimension == "idioma" else None,
                    detalle="; ".join(parentesis) or None,
                    anio_estimacion=int(anio.group(1)) if anio else None,
                ))
    return pd.DataFrame(filas)


def socios(paises, ent, nombres):
    filas, sin_mapear = [], set()
    for r in ent[ent.iso3.notna()].itertuples():
        for flujo, nombre in [("exportacion", "Exports - partners"), ("importacion", "Imports - partners")]:
            texto = campo(paises[r.codigo_gec][1], "Economy", nombre)
            if not texto:
                continue
            anio = re.search(r"\((\d{4})(?: est\.)?\)\s*$", texto)
            cuerpo = (texto[:anio.start()] if anio else texto).replace("&", "and")
            # "Congo, Republic of the 5%", "Gambia, The 10%": se da vuelta para no cortar en la coma
            cuerpo = re.sub(r"([A-Z][\w' ]*?), (The|Republic of the|Democratic Republic of the)(?= \d)", r"\2 \1", cuerpo)
            for rango, item in enumerate(nivel_cero(cuerpo, ","), start=1):
                m = re.match(r"\s*(.+?)\s+(\d+(?:\.\d+)?)%\s*$", item)
                if not m:  # p. ej. "NA" o texto sin porcentaje
                    continue
                socio, pct = m.groups()
                iso = nombres.get(socio)
                if iso is None:
                    sin_mapear.add(socio)
                filas.append(dict(iso3=r.iso3, codigo_gec=r.codigo_gec, flujo=flujo, rango=rango,
                                  socio_nombre_factbook=socio, socio_iso3=iso, participacion_pct=float(pct),
                                  anio=int(anio.group(1)) if anio else None))
    return pd.DataFrame(filas), sin_mapear


def main():
    maestro = pd.read_csv(MAESTROS / "paises_maestro.csv", keep_default_na=False, na_values=[""])
    print("1. Bajando los 261 JSON del Factbook (solo la primera vez) ...")
    paises = descargar()
    ent = entidades(paises, set(maestro.iso3))
    nombres = diccionario_nombres(paises, ent, maestro)
    print(f"   {ent.iso3.notna().sum()} entidades con iso3 ({ent.iso3.nunique()} países distintos), "
          f"{ent.iso3.isna().sum()} sin iso3")

    print("2. Armando tablas")
    tablas = {"factbook_entidades.csv": ent, "factbook_perfil_pais.csv": perfil(paises, ent)}
    fr, sin_fr = fronteras(paises, ent, nombres)
    so, sin_so = socios(paises, ent, nombres)
    n_vecinos = fr.groupby("codigo_gec").vecino_iso3.nunique()
    tablas["factbook_perfil_pais.csv"].insert(
        8, "n_paises_limitrofes", tablas["factbook_perfil_pais.csv"].codigo_gec.map(n_vecinos).fillna(0).astype(int))
    tablas |= {"factbook_fronteras.csv": fr, "factbook_composicion.csv": composicion(paises, ent),
               "factbook_socios_comerciales.csv": so}

    # Controles
    pares = set(zip(fr.iso3, fr.vecino_iso3))
    sin_reciproca = sorted((a, b) for a, b in pares if pd.notna(b) and (b, a) not in pares)
    print(f"   fronteras: {len(fr)} filas; vecinos sin nombre reconocido: {sorted(sin_fr) or 'ninguno'}")
    print(f"   fronteras sin su recíproca (A lista a B pero B no lista a A): {sin_reciproca or 'ninguna'}")
    print(f"   socios comerciales: {len(so)} filas; sin iso3: {sorted(sin_so) or 'ninguno'}")
    for nombre, t in tablas.items():
        t.to_csv(AQUI / nombre, index=False)
        print(f"   {nombre}: {len(t)} filas x {t.shape[1]} columnas")


if __name__ == "__main__":
    main()
