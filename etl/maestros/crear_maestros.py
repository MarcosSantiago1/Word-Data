"""
Tablas maestras de países y de sus subdivisiones de primer nivel.

Arma dos tablas en etl/maestros/:

1. paises_maestro.csv        -> una fila por país o territorio: códigos ISO
   (alfa-3, alfa-2, numérico), nombres en español e inglés, región y nivel de
   ingreso del Banco Mundial, capital, coordenadas y cuántas subdivisiones
   tiene. Incluye los 217 países del panel (en_panel = 1) y los demás
   territorios que tienen código ISO (Taiwán, Guayana Francesa, Antártida...).
2. subdivisiones_maestro.csv -> una fila por subdivisión de primer nivel
   (provincia, estado, región, departamento...) según ISO 3166-2, con el iso3
   del país para unir con el panel.

"Primer nivel" = las subdivisiones que en ISO 3166-2 no dependen de otra.
Ejemplos: las 24 jurisdicciones de Argentina, los 50 estados + DC + 6 áreas
de ultramar de EE. UU., las 17 comunidades autónomas + Ceuta y Melilla de
España (las provincias españolas dependen de ellas y quedan afuera).

Fuentes (todas abiertas):
- ISO 3166-1 y 3166-2 vía el paquete pycountry (copia los datos del proyecto
  iso-codes de Debian, que sigue los boletines de cambios de ISO).
- API del Banco Mundial (api.worldbank.org/v2/{es,en}/country): región,
  nivel de ingreso, capital y coordenadas.
- Wikidata (query.wikidata.org): nombres en español e inglés de países
  (propiedad P298, código alfa-3) y subdivisiones (P300, código ISO 3166-2),
  y coordenadas de las subdivisiones (P625).

Para Argentina la columna `nombre` usa los mismos nombres que
etl/argentina_provincias/ (por ejemplo "Ciudad de Buenos Aires"), así que se
puede unir por nombre o por provincia_iso = subdivision_iso.

Uso:  python crear_maestros.py              (usa los crudos ya bajados)
      python crear_maestros.py --descargar  (vuelve a bajar todo)
Requiere: requests, pandas, pycountry
"""

import difflib
import gettext
import json
import pathlib
import re
import sys
import unicodedata

import pandas as pd
import pycountry
import requests

AQUI = pathlib.Path(__file__).resolve().parent
CRUDOS = AQUI / "crudos"
ETL = AQUI.parent
PANEL_PAISES = ETL / "datos_crudos" / "paises.csv"  # lista de los 217 del panel
ARG_PROVINCIAS = ETL / "argentina_provincias" / "poblacion_provincia_anual.csv"

WIKIDATA = "https://query.wikidata.org/sparql"
CABECERA = {"User-Agent": "analista-datos-etl/1.0 (proyecto educativo)"}

CONSULTA_SUBDIVISIONES = """
SELECT ?item ?code ?es ?en ?coord ?fin WHERE {
  ?item wdt:P300 ?code .
  OPTIONAL { ?item rdfs:label ?es FILTER(LANG(?es)="es") }
  OPTIONAL { ?item rdfs:label ?en FILTER(LANG(?en)="en") }
  OPTIONAL { ?item wdt:P625 ?coord }
  OPTIONAL { ?item wdt:P576 ?fin }
}
"""

CONSULTA_PAISES = """
SELECT ?item ?code ?es ?en ?fin WHERE {
  ?item wdt:P298 ?code .
  OPTIONAL { ?item rdfs:label ?es FILTER(LANG(?es)="es") }
  OPTIONAL { ?item rdfs:label ?en FILTER(LANG(?en)="en") }
  OPTIONAL { ?item wdt:P576 ?fin }
}
"""

# Tipos de subdivisión de ISO 3166-2 (vienen en inglés) traducidos a mano.
TIPOS_ES = {
    "Province": "provincia", "Region": "región", "Municipality": "municipio",
    "District": "distrito", "State": "estado", "Department": "departamento",
    "County": "condado", "Governorate": "gobernación",
    "Local council": "consejo local", "Administrative region": "región administrativa",
    "Prefecture": "prefectura", "Parish": "parroquia", "Rayon": "raión",
    "Canton": "cantón", "City": "ciudad",
    "City with county rights": "ciudad con derechos de condado",
    "Republic": "república", "Division": "división", "Popularate": "popularato",
    "Administrative atoll": "atolón administrativo",
    "Autonomous region": "región autónoma",
    "Autonomous community": "comunidad autónoma", "Quarter": "barrio",
    "Land": "estado federado (Land)", "Voivodship": "voivodato",
    "Special municipality": "municipio especial", "Commune": "comuna",
    "Metropolitan region": "región metropolitana",
    "Urban municipality": "municipio urbano", "Regional state": "estado regional",
    "Union territory": "territorio de la unión",
    "Administrative territory": "territorio administrativo (krai)",
    "Islands, groups of islands": "islas o grupos de islas",
    "Dependency": "dependencia", "Metropolitan city": "ciudad metropolitana",
    "Emirate": "emirato", "Geographical unit": "unidad geográfica",
    "State city": "ciudad estatal", "Island council": "consejo insular",
    "Oblast": "óblast", "Autonomous district": "distrito autónomo",
    "Geographical region": "región geográfica", "Country": "país constituyente",
    "Outlying area": "área periférica (ultramar)", "Territory": "territorio",
    "Overseas collectivity": "colectividad de ultramar", "Island": "isla",
    "Town": "pueblo", "Capital city": "ciudad capital",
    "Indigenous region": "comarca indígena",
    "Autonomous republic": "república autónoma",
    "Special administrative region": "región administrativa especial",
    "Overseas departmental collectivity": "colectividad departamental de ultramar",
    "Group of islands (20 inhabited islands)": "grupo de islas",
    "Federal territory": "territorio federal", "Capital territory": "territorio capital",
    "Geographical entity": "entidad geográfica", "Borough": "municipio (borough)",
    "Administrative precinct": "recinto administrativo", "Entity": "entidad",
    "Economic prefecture": "prefectura económica", "Capital district": "distrito capital",
    "Autonomous city in north africa": "ciudad autónoma",
    "Administration": "administración (ciudad)",
    "Overseas unique territorial collectivity": "colectividad territorial única de ultramar",
    "Special city": "ciudad especial",
    "Special self-governing province": "provincia autónoma especial",
    "Chain (of islands)": "cadena de islas", "Arctic region": "región ártica",
    "Pakistan administered area": "territorio administrado por Pakistán",
    "Autonomous province": "provincia autónoma", "Autonomous city": "ciudad autónoma",
    "District with special status": "distrito con estatus especial",
    "Federal district": "distrito federal",
    "Metropolitan collectivity with special status": "colectividad metropolitana con estatus especial",
    "Overseas collectivity with special status": "colectividad de ultramar con estatus especial",
    "Overseas territory": "territorio de ultramar",
    "Self-governed part": "parte autónoma", "Autonomous sector": "sector autónomo",
    "Autonomous municipality": "municipio autónomo",
    "Special self-governing city": "ciudad autónoma especial",
    "Autonomous territorial unit": "unidad territorial autónoma",
    "Territorial unit": "unidad territorial", "Federal entity": "entidad federativa",
    "Urban community": "comunidad urbana",
    "Special island authority": "autoridad insular especial",
    "Federal capital territory": "territorio de la capital federal",
    "Capital": "capital", "Area": "área",
    "Metropolitan administration": "administración metropolitana",
    "Special administrative city": "ciudad administrativa especial",
    "Districts under republic administration": "distritos bajo administración de la república",
    "Ward": "distrito (ward)", "Town council": "consejo municipal",
    "Federal dependency": "dependencia federal",
}

# Subdivisiones que ISO también lista como país aparte (tienen su propio
# código ISO 3166-1). Ojo al sumar: Puerto Rico está en EE. UU. y además es
# un país del panel; sumar los dos lo cuenta dos veces.
SUBDIVISION_TAMBIEN_PAIS = {
    "US-AS": "ASM", "US-GU": "GUM", "US-MP": "MNP", "US-PR": "PRI",
    "US-UM": "UMI", "US-VI": "VIR",
    "CN-HK": "HKG", "CN-MO": "MAC", "CN-TW": "TWN",
    "NL-AW": "ABW", "NL-CW": "CUW", "NL-SX": "SXM",
    "NL-BQ1": "BES", "NL-BQ2": "BES", "NL-BQ3": "BES",
    "FR-BL": "BLM", "FR-MF": "MAF", "FR-NC": "NCL", "FR-PF": "PYF",
    "FR-PM": "SPM", "FR-TF": "ATF", "FR-WF": "WLF",
    "FR-971": "GLP", "FR-972": "MTQ", "FR-973": "GUF", "FR-974": "REU",
    "FR-976": "MYT",
    "NO-21": "SJM", "NO-22": "SJM",
    "FI-01": "ALA",
}


# Nombres en español de Wikidata que conviene corregir (desactualizados,
# demasiado formales o que se repiten).
NOMBRE_ES_A_MANO = {
    "CHN": "China", "NLD": "Países Bajos", "TWN": "Taiwán", "SWZ": "Esuatini",
    "MMR": "Myanmar", "CCK": "Islas Cocos",
    "MAF": "San Martín (parte francesa)", "SXM": "San Martín (parte neerlandesa)",
}
NOMBRE_EN_A_MANO = {"TWN": "Taiwan"}

# El Banco Mundial en español escribe el nivel de ingreso de dos maneras
# ("Ingreso alto" y "Países de ingreso bajo"); lo traducimos desde el inglés.
INGRESO_ES = {
    "High income": "Ingreso alto", "Upper middle income": "Ingreso mediano alto",
    "Lower middle income": "Ingreso mediano bajo", "Low income": "Ingreso bajo",
}


def sin_tildes(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in texto if not unicodedata.combining(c)).lower().strip()


def nombre_limpio(nombre_iso):
    """ISO escribe algunos nombres con agregados: "Galicia [Galicia]",
    "Stockholms län [SE-01]", "Madrid, Comunidad de", "Adygeya, Respublika".
    Sacamos lo que va entre corchetes y damos vuelta el orden invertido."""
    nombre = re.sub(r"\s*\[[^\]]*\]$", "", nombre_iso).strip()
    m = re.match(r"^(.+), ((?:Région|Hlavní město|Principado|Región|Comunidad|Respublika"
                 r"|Unitatea|unitatea).*)$", nombre)
    if m:
        nombre = f"{m.group(2)} {m.group(1)}"
    return nombre


def bajar(url, destino, params=None, cabecera_extra=None):
    """Descarga una sola vez; con --descargar se fuerza de nuevo."""
    if destino.exists() and "--descargar" not in sys.argv:
        return
    print(f"  bajando {destino.name}")
    r = requests.get(url, params=params, timeout=180,
                     headers={**CABECERA, **(cabecera_extra or {})})
    r.raise_for_status()
    destino.write_bytes(r.content)


def bajar_crudos():
    CRUDOS.mkdir(exist_ok=True)
    for idioma in ("es", "en"):
        bajar(f"https://api.worldbank.org/v2/{idioma}/country?format=json&per_page=400",
              CRUDOS / f"banco_mundial_paises_{idioma}.json")
    for consulta, nombre in ((CONSULTA_SUBDIVISIONES, "wikidata_subdivisiones_p300.csv"),
                             (CONSULTA_PAISES, "wikidata_paises_p298.csv")):
        # Wikidata devuelve CSV si se lo pedimos en la cabecera Accept
        bajar(WIKIDATA, CRUDOS / nombre, params={"query": consulta},
              cabecera_extra={"Accept": "text/csv"})


def elegir_item_wikidata(w, nombre_referencia):
    """Wikidata a veces tiene más de un ítem con el mismo código (ej.: la
    provincia de Santa Cruz y el Parque Nacional Los Glaciares figuran ambos
    con AR-Z). Nos quedamos con el ítem vigente cuyo nombre se parece más al
    nombre oficial de ISO."""
    vigentes = w[w["fin"].isna()]
    if len(vigentes):
        w = vigentes
    ref = sin_tildes(nombre_referencia)

    def puntaje(fila):
        etiquetas = [sin_tildes(fila[c]) for c in ("en", "es") if pd.notna(fila[c])]
        if not etiquetas:
            return -1
        contiene = any(ref in e for e in etiquetas)
        parecido = max(difflib.SequenceMatcher(None, ref, e).ratio() for e in etiquetas)
        return contiene + parecido

    return w.loc[w.apply(puntaje, axis=1).idxmax()]


def coordenadas(punto):
    """'Point(lon lat)' -> (lat, lon)"""
    m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", str(punto))
    if not m:
        return None, None
    return round(float(m.group(2)), 4), round(float(m.group(1)), 4)


def armar_subdivisiones():
    w = pd.read_csv(CRUDOS / "wikidata_subdivisiones_p300.csv")
    w = w.drop_duplicates(subset=["item", "code"])
    por_codigo = dict(tuple(w.groupby("code")))

    arg = pd.read_csv(ARG_PROVINCIAS)[["provincia_iso", "provincia"]].drop_duplicates()
    nombres_arg = dict(zip(arg["provincia_iso"], arg["provincia"]))

    filas = []
    for s in pycountry.subdivisions:
        if s.parent_code is not None:
            continue  # segundo nivel o más abajo
        pais = pycountry.countries.get(alpha_2=s.country_code)
        fila = {
            "subdivision_iso": s.code,
            "iso2": s.country_code,
            "iso3": pais.alpha_3,
            "nombre": nombres_arg.get(s.code, nombre_limpio(s.name)),
            "nombre_iso": s.name,
            "nombre_es": None,
            "nombre_en": None,
            "tipo_iso": s.type,
            "tipo_es": TIPOS_ES.get(s.type, s.type.lower()),
            "tambien_pais_iso3": SUBDIVISION_TAMBIEN_PAIS.get(s.code),
            "latitud": None,
            "longitud": None,
            "wikidata_id": None,
        }
        if s.code in por_codigo:
            item = elegir_item_wikidata(por_codigo[s.code], s.name)
            fila["nombre_es"] = item["es"] if pd.notna(item["es"]) else None
            fila["nombre_en"] = item["en"] if pd.notna(item["en"]) else None
            fila["latitud"], fila["longitud"] = coordenadas(item["coord"])
            fila["wikidata_id"] = item["item"].rsplit("/", 1)[-1]
        filas.append(fila)

    sub = pd.DataFrame(filas)
    # Si Wikidata no tiene nombre en español, usamos el inglés y después el de ISO.
    sub["nombre_es"] = sub["nombre_es"].fillna(sub["nombre_en"]).fillna(sub["nombre_iso"])
    sub["nombre_en"] = sub["nombre_en"].fillna(sub["nombre_iso"])
    return sub.sort_values(["iso3", "subdivision_iso"]).reset_index(drop=True)


def armar_paises(sub):
    panel = pd.read_csv(PANEL_PAISES)  # iso3, pais, region, nivel_ingreso

    bm_es = {p["id"]: p for p in json.load(open(CRUDOS / "banco_mundial_paises_es.json"))[1]}
    bm_en = {p["id"]: p for p in json.load(open(CRUDOS / "banco_mundial_paises_en.json"))[1]}

    w = pd.read_csv(CRUDOS / "wikidata_paises_p298.csv")
    wd = {c: elegir_item_wikidata(g, g["en"].iloc[0]) for c, g in w.groupby("code")}

    es_iso = gettext.translation("iso3166-1", pycountry.LOCALES_DIR, languages=["es"])

    # Universo: los 217 del panel + todos los códigos ISO 3166-1.
    codigos = list(dict.fromkeys(list(panel["iso3"]) + [c.alpha_3 for c in pycountry.countries]))
    panel = panel.set_index("iso3")

    filas = []
    for iso3 in codigos:
        iso = pycountry.countries.get(alpha_3=iso3)
        es, en = bm_es.get(iso3), bm_en.get(iso3)
        en_panel = iso3 in panel.index
        nombre_wd = wd[iso3]["es"] if iso3 in wd and pd.notna(wd[iso3]["es"]) else None
        fila = {
            "iso3": iso3,
            "iso2": iso.alpha_2 if iso else (en or {}).get("iso2Code"),
            "iso_numerico": iso.numeric if iso else None,
            "nombre_es": NOMBRE_ES_A_MANO.get(iso3) or nombre_wd
                         or (es["name"] if es else es_iso.gettext(iso.name)),
            "nombre_es_banco_mundial": es["name"] if es else None,
            # mismo texto que la columna `pais` del panel
            "nombre_en": panel.at[iso3, "pais"] if en_panel
                         else NOMBRE_EN_A_MANO.get(iso3) or (en["name"] if en else iso.name),
            "nombre_oficial_en": getattr(iso, "official_name", None) if iso else None,
            "region_bm": panel.at[iso3, "region"] if en_panel else (en["region"]["value"].strip() if en else None),
            "region_bm_es": es["region"]["value"].strip() if es else None,
            "nivel_ingreso_bm": panel.at[iso3, "nivel_ingreso"] if en_panel else (en["incomeLevel"]["value"] if en else None),
            "capital": (en or {}).get("capitalCity") or None,
            # coordenadas de la capital según el Banco Mundial
            "latitud_capital": float(en["latitude"]) if en and en["latitude"] else None,
            "longitud_capital": float(en["longitude"]) if en and en["longitude"] else None,
            "en_panel": int(en_panel),
            "tiene_codigo_iso": int(iso is not None),
        }
        filas.append(fila)

    paises = pd.DataFrame(filas)
    # Los "no clasificados" del Banco Mundial (ej.: Venezuela en ingreso) quedan vacíos.
    for col in ("region_bm", "region_bm_es", "nivel_ingreso_bm"):
        paises[col] = paises[col].replace({"": None, "Not classified": None, "No clasificado": None})
    paises.insert(paises.columns.get_loc("nivel_ingreso_bm") + 1, "nivel_ingreso_bm_es",
                  paises["nivel_ingreso_bm"].map(INGRESO_ES))

    conteo = sub.groupby("iso3").agg(
        n_subdivisiones=("subdivision_iso", "size"),
        tipo_subdivision_principal=("tipo_es", lambda t: t.value_counts().index[0]),
    )
    paises = paises.merge(conteo, on="iso3", how="left")
    paises["n_subdivisiones"] = paises["n_subdivisiones"].fillna(0).astype(int)
    return paises.sort_values(["en_panel", "iso3"], ascending=[False, True]).reset_index(drop=True)


def controles(paises, sub):
    panel = pd.read_csv(PANEL_PAISES)
    assert paises["iso3"].is_unique and sub["subdivision_iso"].is_unique
    assert set(panel["iso3"]) == set(paises.loc[paises["en_panel"] == 1, "iso3"])
    arg = sub[sub["iso3"] == "ARG"]
    nombres_arg = set(pd.read_csv(ARG_PROVINCIAS)["provincia"])
    assert len(arg) == 24 and set(arg["nombre"]) == nombres_arg, "Argentina no empata"
    esperado = {"USA": 57, "BRA": 27, "MEX": 32, "ESP": 19, "DEU": 16, "CHL": 16, "URY": 19}
    for iso3, n in esperado.items():
        real = int(paises.loc[paises["iso3"] == iso3, "n_subdivisiones"].iloc[0])
        assert real == n, f"{iso3}: {real} subdivisiones, se esperaban {n}"
    sin_tipo = set(sub["tipo_iso"]) - set(TIPOS_ES)
    assert not sin_tipo, f"tipos sin traducir: {sin_tipo}"


def main():
    print("Descargando crudos (solo si faltan)...")
    bajar_crudos()
    print("Armando subdivisiones...")
    sub = armar_subdivisiones()
    print("Armando países...")
    paises = armar_paises(sub)
    controles(paises, sub)

    paises.to_csv(AQUI / "paises_maestro.csv", index=False, encoding="utf-8")
    sub.to_csv(AQUI / "subdivisiones_maestro.csv", index=False, encoding="utf-8")

    p = paises[paises["en_panel"] == 1]
    print(f"paises_maestro.csv: {len(paises)} filas ({len(p)} del panel)")
    print(f"subdivisiones_maestro.csv: {len(sub)} filas de {sub['iso3'].nunique()} países")
    print(f"Países del panel sin subdivisiones ISO: {sorted(p.loc[p['n_subdivisiones'] == 0, 'iso3'])}")


if __name__ == "__main__":
    main()
