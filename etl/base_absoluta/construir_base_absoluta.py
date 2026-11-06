"""
BASE ABSOLUTA: toda la información del proyecto en una sola tabla.

Forma de la tabla (una fila = una variable de un país o de una provincia/departamento):

    nivel | pais_iso3 | pais | subdivision_codigo | provincia_departamento | tema | variable |
    apertura | unidad | fuente | sin_anio | 1945 | 1946 | ... | 2040

  - nivel = "pais" (provincia vacía) o "subdivision" (provincia, estado o departamento).
  - apertura = el detalle de las variables que vienen abiertas: cultivo, rama de actividad, cámara,
    organización, socio comercial, religión... Vacía en el resto.
  - sin_anio = datos fijos que no tienen año (perfil del Factbook, KPIs, festivales, coordenadas).
  - una columna por año con el valor de ese año (número o texto).

De dónde sale cada cosa (no descarga nada):
  1. El master (modelo_unificado/master_paises_provincias.sqlite): todas las tablas hecho_* por país
     y por subdivisión, las columnas calculadas de las vistas v_* (tasas, cocientes), membresías,
     fronteras, socios comerciales, religiones/etnias/idiomas y acuerdos comerciales.
  2. Lo que no está en el master: latam_subnacional/*.csv (OCDE, temperatura, gobernantes, Brasil,
     agro, ganado y petróleo de los otros países), festivales de Argentina y kpis/resultados/*.csv.
  Las alianzas militares quedan afuera porque son de a pares de países; su conteo por país y año
  (n_aliados_defensa, n_aliados_cualquier_pacto) sí está.

Orden de ejecución: al final del pipeline, después de modelo_unificado/construir_master.py y
kpis/calcular_kpis.py.

    cd etl/base_absoluta
    python construir_base_absoluta.py

Salidas (en esta carpeta): base_absoluta.csv, base_absoluta.sqlite (tabla base_absoluta +
diccionario_variables) y diccionario_variables.csv (una fila por variable, con cobertura).
"""

import sqlite3
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
ETL = AQUI.parent
MASTER = ETL / "modelo_unificado" / "master_paises_provincias.sqlite"
LATAM = ETL / "latam_subnacional"
LEER = dict(keep_default_na=False, na_values=[""], low_memory=False)  # "NA" es Namibia, no un nulo

SIN_ANIO = "sin_anio"
CLAVE = ["nivel", "pais_iso3", "subdivision_codigo", "tema", "variable", "apertura"]
LARGO = CLAVE + ["unidad", "fuente", "anio", "valor"]

# Columnas que identifican la fila y no son variables
NO_VARIABLE = {"pais_id", "subdivision_id", "anio", "iso3", "pais", "codigo", "nombre", "subdivision",
               "subdivision_iso", "region_subnacional", "codigo_gec", "fecha_snapshot", "campania",
               "anio_cosecha", "anio_censo", "anio_eleccion", "decada_censal", "fuente", "fuente_unidad",
               "persona_wikidata", "cargo"}
# Datos fijos de cada país que las vistas repiten año por año: van una sola vez, en tema identificacion
IDENTIFICACION_PAIS = {"continente", "region_bm", "nivel_ingreso"}

# Tablas del master que tienen otra dimensión además de (lugar, año):
# tabla -> (columna de año, columna de apertura, columnas que no van)
TABLAS_ABIERTAS = {
    "hecho_subdivision_agricultura": ("anio_cosecha", "cultivo", set()),
    "hecho_subdivision_vab_rama": ("anio", "rama", {"rama_nro", "estado_dato"}),
    "hecho_subdivision_alicuota_iibb": ("anio", "actividad", set()),
    "hecho_subdivision_legisladores": ("anio", "camara", set()),
    "hecho_subdivision_censo": ("anio_censo", None, set()),
    "hecho_subdivision_eleccion_gobernador": ("anio_eleccion", None, set()),
    "hecho_pais_poblacion_indigena": ("decada_censal", None, set()),
    "hecho_pais_perfil_factbook": (None, None, set()),
}

# Nombres que se repiten en dos tablas del mismo nivel: se les antepone el tema
# (igual que en la vista v_subdivision_anual: hidrocarburos_meses_con_dato, etc.)
RENOMBRAR = {("censo", "habitantes"): "censo_habitantes", ("poblacion", "habitantes"): "habitantes",
             ("economia", "estado_dato"): "estado_dato_vab"}

# Unidades que el diccionario del master tiene mal (se corrigen acá)
UNIDADES_CORREGIDAS = {
    "rendimiento_kg_ha": "kg por hectárea",
    "gas_miles_m3_convencional": "miles de m³", "gas_miles_m3_no_convencional": "miles de m³",
    "gas_miles_m3_total": "miles de m³",
    "tipo_cambio_lcu_por_usd": "moneda local por US$", "ppa_lcu_por_usd_intl": "moneda local por US$ internacional",
    "emisiones_gei_per_capita_tco2e": "t de CO2 equivalente por habitante",
    "emisiones_co2_per_capita_tco2e": "t de CO2 equivalente por habitante",
}

# Palestina tiene dos fichas en el Factbook: se distinguen en la apertura
TERRITORIOS_FACTBOOK = {"gz": "Franja de Gaza", "we": "Cisjordania"}

# Temas: nombre de la tabla sin el prefijo, salvo estos
TEMA = {"anual": "panel_base", "migracion_anual": "migracion", "relaciones_anual": "relaciones"}

# CSV que no están en el master: archivo, tema, fuente, renombres, filtro de países
COMPLEMENTOS_SUBDIVISION = [
    ("indicadores_ocde_subdivision_anual.csv", "ocde_regional", "OCDE, Regional Database (TL2)", {}, None),
    ("temperatura_subdivision_anual.csv", "clima", "Banco Mundial, Climate Change Knowledge Portal",
     {}, "sin_arg"),  # Argentina ya está en hecho_subdivision_clima
    ("gobierno_subdivision_anual.csv", "gobierno", "Wikidata (gobernante al cierre de cada año)", {}, None),
    ("brasil_pib_poblacion_estado_anual.csv", "brasil_pib", "IBGE (SIDRA)",
     {"poblacion": "poblacion_ibge", "poblacion_fuente": "poblacion_ibge_fuente"}, None),
    ("petroleo_gas_subdivision_anual.csv", "hidrocarburos", "Secretaría de Energía, ANP y otros",
     {"petroleo_m3": "petroleo_m3_total", "gas_miles_m3": "gas_miles_m3_total",
      "meses_con_dato": "hidrocarburos_meses_con_dato"}, "sin_arg"),
]


def leer_sql(con, sql):
    return pd.read_sql(sql, con)


def enteros(df, columnas):
    """Columnas numéricas sin decimales pasan a enteros (para que el CSV diga 90588 y no 90588.0)."""
    for c in columnas:
        s = df[c]
        if pd.api.types.is_float_dtype(s):
            v = s.dropna()
            if len(v) and (v == v.round()).all() and v.abs().max() < 2 ** 53:
                df[c] = s.astype("Int64")
    return df


def a_largo(df, nivel, tema, fuente, columnas, anio=None, apertura=None, nombres=None, unidades=None):
    """Pasa una tabla ancha (una columna por variable) al formato largo común."""
    nombres, unidades = nombres or {}, unidades or {}
    columnas = [c for c in columnas if df[c].notna().any()]
    if not columnas:
        return None
    df = enteros(df.copy(), columnas)
    base = pd.DataFrame({
        "nivel": nivel,
        "pais_iso3": df["pais_iso3"],
        "subdivision_codigo": df["subdivision_codigo"] if nivel == "subdivision" else "",
        "tema": tema,
        "apertura": df[apertura].astype(str).str.strip() if apertura else "",
        "anio": df[anio].astype("Int64").astype(str) if anio else SIN_ANIO,
    })
    partes = []
    for c in columnas:
        v = df[c]
        m = v.notna()
        p = base[m].copy()
        p["variable"] = nombres.get(c, c)
        p["unidad"] = UNIDADES_CORREGIDAS.get(c) or unidades.get(c) or ""
        p["fuente"] = fuente
        p["valor"] = v[m].astype(object).values
        partes.append(p)
    return pd.concat(partes, ignore_index=True)[LARGO]


def con_territorio(df, col="apertura"):
    """Antepone «Franja de Gaza: » / «Cisjordania: » a la apertura de las filas del Factbook."""
    t = df["codigo_gec"].map(TERRITORIOS_FACTBOOK)
    df[col] = (t + ": " + df[col]).where(t.notna(), df[col])
    return df


def apertura_unica(df, claves, col="apertura"):
    """Si un mismo lugar repite apertura (p. ej. dos grupos «other»), numera la repetición."""
    n = df.groupby(claves + [col]).cumcount()
    df[col] = df[col].where(n == 0, df[col] + " (" + (n + 1).astype(str) + ")")
    return df


def construir():
    assert MASTER.exists(), f"Falta {MASTER}: correr antes modelo_unificado/construir_master.py"
    con = sqlite3.connect(f"{MASTER.as_uri()}?mode=ro", uri=True)
    columnas = lambda t: [r[1] for r in con.execute(f'PRAGMA table_info("{t}")')]
    objetos = [n for (n,) in con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")]

    fuentes = dict(con.execute("SELECT tabla, fuente FROM ref_catalogo_tabla").fetchall())
    dicc = leer_sql(con, "SELECT tabla, columna, unidad FROM ref_diccionario_columna WHERE unidad IS NOT NULL")
    unidad_tabla = {(t, c): u for t, c, u in dicc.itertuples(index=False)}
    unidad_col = dicc.drop_duplicates("columna").set_index("columna")["unidad"].to_dict()
    unidades_de = lambda t, cols: {c: unidad_tabla.get((t, c), unidad_col.get(c)) for c in cols}

    paises = leer_sql(con, "SELECT pais_id, iso3 AS pais_iso3 FROM dim_pais")
    subdivs = leer_sql(con, """SELECT s.subdivision_id, s.codigo AS subdivision_codigo, p.iso3 AS pais_iso3
                               FROM dim_subdivision s JOIN dim_pais p USING (pais_id)""")
    partes = []

    # 1. Tablas hecho_* del master --------------------------------------------------------------
    for nivel, clave, lugares in [("pais", "pais_id", paises), ("subdivision", "subdivision_id", subdivs)]:
        tablas = sorted(t for t in objetos if t.startswith(f"hecho_{nivel}_"))
        cuenta = pd.Series([c for t in tablas for c in columnas(t)]).value_counts()
        vistas_hechas = set()
        for t in tablas:
            tema = t.removeprefix(f"hecho_{nivel}_")
            tema = TEMA.get(tema, tema)
            anio, apertura, sacar = TABLAS_ABIERTAS.get(t, ("anio", None, set()))
            df = leer_sql(con, f'SELECT * FROM "{t}"').merge(lugares, on=clave, how="left")
            assert df["pais_iso3"].notna().all(), f"{t}: hay códigos sin país en el master"
            if t == "hecho_pais_perfil_factbook":
                df["territorio"] = df["codigo_gec"].map(TERRITORIOS_FACTBOOK).fillna("")
                apertura = "territorio"
            if t == "hecho_subdivision_vab_rama":
                ramas = leer_sql(con, "SELECT rama_nro, rama FROM dim_rama_cepal")
                df = df.merge(ramas, on="rama_nro", how="left")
                df["rama"] = df["rama_nro"].map("{:02d}".format) + ". " + df["rama"]
            vars_ = [c for c in columnas(t) if c not in NO_VARIABLE | sacar and c != apertura]
            nombres = {c: RENOMBRAR.get((tema, c), f"{tema}_{c}" if cuenta[c] > 1 else c) for c in vars_}
            partes.append(a_largo(df, nivel, tema, fuentes.get(t, t), vars_, anio, apertura, nombres,
                                  unidades_de(t, vars_)))
            vistas_hechas.update(nombres.values())

        # 2. Columnas que solo existen en las vistas (cálculos: tasas, cocientes, sumas) ---------
        for v in sorted(o for o in objetos if o.startswith(f"v_{nivel}_")):
            cols = columnas(v)
            if "anio" not in cols or v in ("v_pais_membresia_anual", "v_vab_provincia_grupo"):
                continue
            nuevas = [c for c in cols if c not in NO_VARIABLE | IDENTIFICACION_PAIS and c not in cuenta.index
                      and c not in vistas_hechas]
            if not nuevas:
                continue
            df = leer_sql(con, f'SELECT * FROM "{v}"')
            if "pais_iso3" not in df:
                df = df.rename(columns={"iso3": "pais_iso3"}) if "iso3" in df else \
                    df.merge(subdivs[["subdivision_id", "pais_iso3"]], on="subdivision_id")
            if nivel == "subdivision":
                df["subdivision_codigo"] = df["codigo"]
            tema = {"v_pais_anual": "relaciones", "v_pais_indicadores_sociales": "indicadores_sociales"}.get(
                v, v.removeprefix(f"v_{nivel}_").removesuffix("_anual"))
            partes.append(a_largo(df, nivel, tema, f"cálculo propio (vista {v} del master)", nuevas, "anio",
                                  unidades=unidades_de(v, nuevas)))
            vistas_hechas.update(nuevas)

    # VAB por grupo de sectores (vista con apertura)
    df = leer_sql(con, "SELECT * FROM v_vab_provincia_grupo").merge(subdivs, on="subdivision_id")
    partes.append(a_largo(df, "subdivision", "vab_grupo", "cálculo propio (vista v_vab_provincia_grupo)",
                          ["vab_mill_pesos_2004", "participacion_en_provincia"], "anio", "grupo_sector",
                          {"vab_mill_pesos_2004": "vab_grupo_mill_pesos_2004",
                           "participacion_en_provincia": "participacion_grupo_en_provincia"}))

    # 3. Relaciones y composición por país --------------------------------------------------------
    df = leer_sql(con, """SELECT m.*, o.nombre AS organizacion FROM v_pais_membresia_anual m
                          JOIN dim_organizacion o USING (organizacion_codigo)""").merge(paises, on="pais_id")
    df["apertura"] = df["organizacion_codigo"] + " - " + df["organizacion"]
    partes.append(a_largo(df, "pais", "relaciones", fuentes["rel_pais_organizacion"], ["estado"], "anio",
                          "apertura", {"estado": "membresia_organizacion"}))

    df = leer_sql(con, "SELECT * FROM rel_pais_composicion").merge(paises, on="pais_id")
    df["apertura"] = df["grupo"]
    df = con_territorio(df)
    df = apertura_unica(df, ["pais_id", "dimension"])
    for dim, d in df.groupby("dimension"):
        d = d.copy()
        d["anio_txt"] = d["anio_estimacion"].astype("Int64").astype(str).where(d["anio_estimacion"].notna(),
                                                                                 SIN_ANIO)
        largo = a_largo(d, "pais", "composicion_poblacion", fuentes["rel_pais_composicion"],
                        ["poblacion_pct"], None, "apertura", {"poblacion_pct": f"{dim}_pct_poblacion"},
                        {"poblacion_pct": "% de la población"})
        largo["anio"] = d.loc[d["poblacion_pct"].notna(), "anio_txt"].values
        partes.append(largo)

    nombre_es = leer_sql(con, "SELECT pais_id, nombre_es FROM dim_pais").set_index("pais_id")["nombre_es"]
    df = leer_sql(con, "SELECT * FROM rel_pais_frontera").merge(paises, on="pais_id")
    df["apertura"] = df["vecino_pais_id"].map(nombre_es).fillna(df["vecino_nombre_factbook"])
    df = con_territorio(df)
    df = apertura_unica(df, ["pais_id"])
    partes.append(a_largo(df, "pais", "fronteras", fuentes["rel_pais_frontera"], ["frontera_km"], None,
                          "apertura", unidades={"frontera_km": "km"}))

    df = leer_sql(con, "SELECT * FROM rel_pais_socio_comercial").merge(paises, on="pais_id")
    df["apertura"] = df["socio_pais_id"].map(nombre_es).fillna(df["socio_nombre_factbook"])
    df = con_territorio(df)
    for flujo, d in df.groupby("flujo"):
        d = apertura_unica(d.copy(), ["pais_id", "anio"])
        partes.append(a_largo(d, "pais", "socios_comerciales", fuentes["rel_pais_socio_comercial"],
                              ["participacion_pct"], "anio", "apertura",
                              {"participacion_pct": f"socio_{flujo}_pct"}, {"participacion_pct": "%"}))

    df = leer_sql(con, """SELECT r.*, a.nombre FROM rel_pais_acuerdo_comercial r
                          JOIN dim_acuerdo_comercial a USING (acuerdo_id)""").merge(paises, on="pais_id")
    df["apertura"] = df["nombre"]
    df = apertura_unica(df, ["pais_id"])
    partes.append(a_largo(df, "pais", "acuerdos_comerciales", fuentes["rel_pais_acuerdo_comercial"],
                          ["anio_firma", "anio_entrada_vigor", "anio_salida"], None, "apertura",
                          {c: f"acuerdo_{c}" for c in ["anio_firma", "anio_entrada_vigor", "anio_salida"]}))

    # 4. Identificación (datos fijos de cada lugar) ------------------------------------------------
    df = leer_sql(con, "SELECT * FROM v_pais").rename(columns={"iso3": "pais_iso3"})
    ident = ["nombre_en", "nombre_oficial_en", "continente", "subregion", "region_intermedia", "region_bm",
             "nivel_ingreso", "capital", "latitud_capital", "longitud_capital", "tipo_entidad",
             "es_miembro_onu", "soberano_iso3", "n_subdivisiones_nivel1"]
    partes.append(a_largo(df, "pais", "identificacion", fuentes["dim_pais"], ident,
                          unidades=unidades_de("dim_pais", ident)))
    df = leer_sql(con, "SELECT * FROM v_pais_diversidad_cultural").rename(columns={"iso3": "pais_iso3"})
    fijas = ["indice_fragmentacion_etnica_0_1", "indice_fragmentacion_linguistica_0_1",
             "indice_fragmentacion_religiosa_0_1", "pct_composicion_etnica_cubierta",
             "pct_composicion_linguistica_cubierta", "anio_constitucion_ccp"]
    partes.append(a_largo(df.drop_duplicates("pais_iso3"), "pais", "diversidad_cultural",
                          "cálculo propio (vista v_pais_diversidad_cultural)", fijas))
    subdiv_ident = leer_sql(con, "SELECT * FROM v_subdivision").rename(columns={"iso3": "pais_iso3"})
    subdiv_ident["subdivision_codigo"] = subdiv_ident["codigo"]
    con.close()

    # 5. CSV que no están en el master -------------------------------------------------------------
    for archivo, tema, fuente, nombres, filtro in COMPLEMENTOS_SUBDIVISION:
        df = pd.read_csv(LATAM / archivo, **LEER).rename(columns={"iso3": "pais_iso3",
                                                                  "subdivision_iso": "subdivision_codigo"})
        if filtro == "sin_arg":
            df = df[df["pais_iso3"] != "ARG"]
        vars_ = [c for c in df.columns if c not in NO_VARIABLE | {"pais_iso3", "subdivision_codigo"}]
        partes.append(a_largo(df, "subdivision", tema, fuente, vars_, "anio", nombres=nombres))

    # Agro y ganado de los otros países, con los nombres de las tablas de Argentina
    df = pd.read_csv(LATAM / "agricultura_subdivision_anual.csv", **LEER).rename(
        columns={"iso3": "pais_iso3", "subdivision_iso": "subdivision_codigo"})
    df = df[df["pais_iso3"] != "ARG"]  # Argentina ya está en hecho_subdivision_agricultura
    assert set(df["unidad_produccion"].dropna()) <= {"Toneladas"}, "producción en otra unidad que toneladas"
    partes.append(a_largo(df, "subdivision", "agricultura", "MAGyP, IBGE, DANE y otros (formato común)",
                          ["area_sembrada_ha", "area_cosechada_ha", "produccion",
                           "valor_produccion_miles_moneda_local"], "anio", "cultivo_original",
                          {"area_sembrada_ha": "sup_sembrada_ha", "area_cosechada_ha": "sup_cosechada_ha",
                           "produccion": "produccion_tn"}))
    df = pd.read_csv(LATAM / "ganaderia_subdivision_anual.csv", **LEER).rename(
        columns={"iso3": "pais_iso3", "subdivision_iso": "subdivision_codigo"})
    df = df[df["pais_iso3"] != "ARG"]  # Argentina ya está en hecho_subdivision_ganaderia
    partes.append(a_largo(df, "subdivision", "ganaderia", "MAGyP/SENASA, IBGE y otros (formato común)",
                          ["cabezas"], "anio", "especie_original"))

    # Festivales de Argentina (relevamiento 2023, sin serie)
    df = pd.read_csv(ETL / "argentina_provincias" / "festivales_provincia.csv", **LEER)
    df = df.rename(columns={"provincia_iso": "subdivision_codigo"}).assign(pais_iso3="ARG")
    partes.append(a_largo(df, "subdivision", "cultura_festivales",
                          "Festivales Argentinos 2023 y relevamientos provinciales",
                          [c for c in df.columns if c not in ("subdivision_codigo", "provincia", "pais_iso3")]))

    # KPIs del proyecto (foto de un año de referencia, sin serie). Las columnas que copian una
    # variable que ya está en la base (pib_pc_ppp, gini...) no se repiten: van solo los resultados.
    ya_estan = set(pd.concat([p["variable"] for p in partes if p is not None]).unique())
    for archivo in sorted((ETL / "kpis" / "resultados").glob("KPI[0-9]_*.csv")):
        kpi = archivo.stem.split("_")[0].lower()
        df = pd.read_csv(archivo, **LEER)
        if "iso3" in df:
            nivel, df = "pais", df.rename(columns={"iso3": "pais_iso3"})
        else:
            nivel = "subdivision"
            df = df.rename(columns={"codigo": "subdivision_codigo"}).assign(pais_iso3="ARG")
        vars_ = [c for c in df.columns if c not in {"pais_iso3", "subdivision_codigo", "pais", "provincia",
                                                     "continente", "nivel_ingreso"} | ya_estan]
        partes.append(a_largo(df, nivel, "kpis", f"calcular_kpis.py ({archivo.name})", vars_,
                              nombres={c: f"{kpi}_{c}" for c in vars_}))

    largo = pd.concat([p for p in partes if p is not None], ignore_index=True)

    # Identificación de las subdivisiones que tienen algún dato
    con_datos = set(largo.loc[largo["nivel"] == "subdivision", "subdivision_codigo"])
    s = subdiv_ident[subdiv_ident["subdivision_codigo"].isin(con_datos)]
    ident = ["nombre_es", "tipo_es", "nivel", "codigo_padre", "region_subnacional", "latitud", "longitud"]
    largo = pd.concat([largo, a_largo(s, "subdivision", "identificacion",
                                      "maestros/subdivisiones_maestro.csv (ISO 3166-2, Wikidata)", ident,
                                      nombres={"nivel": "nivel_subdivision", "nombre_es": "nombre_oficial",
                                               "tipo_es": "tipo_subdivision"})], ignore_index=True)
    largo[["unidad", "apertura"]] = largo[["unidad", "apertura"]].fillna("")

    # Controles: un solo valor por lugar, variable, apertura y año; todos los códigos existen
    rep = largo.duplicated(CLAVE + ["anio"], keep=False)
    assert not rep.any(), "valores repetidos:\n" + largo[rep].head(20).to_string()
    falta = set(largo.loc[largo["nivel"] == "subdivision", "subdivision_codigo"]) - set(subdivs["subdivision_codigo"])
    assert not falta, f"subdivisiones que no están en el master: {sorted(falta)[:10]}"
    falta = set(largo["pais_iso3"]) - set(paises["pais_iso3"])
    assert not falta, f"países que no están en el master: {sorted(falta)}"
    return largo, subdiv_ident


def a_ancho(largo, subdiv_ident):
    """Una columna por año (y sin_anio primero)."""
    meta = largo.drop_duplicates(CLAVE)[CLAVE + ["unidad", "fuente"]]
    ancho = largo.set_index(CLAVE + ["anio"])["valor"].unstack("anio")
    anios = sorted(c for c in ancho.columns if c != SIN_ANIO)
    ancho = ancho[[c for c in [SIN_ANIO] if c in ancho.columns] + anios].reset_index()
    ancho = meta.merge(ancho, on=CLAVE, validate="one_to_one")

    con = sqlite3.connect(f"{MASTER.as_uri()}?mode=ro", uri=True)
    nombres_pais = pd.read_sql("SELECT iso3 AS pais_iso3, nombre_es AS pais FROM dim_pais", con)
    con.close()
    # nombre corto ("Buenos Aires", "Ciudad de Buenos Aires"); el nombre oficial queda como variable nombre_es
    nombres_sub = subdiv_ident.assign(provincia_departamento=subdiv_ident["nombre"].fillna(subdiv_ident["nombre_es"]))
    ancho = ancho.merge(nombres_pais, on="pais_iso3", how="left").merge(
        nombres_sub[["subdivision_codigo", "provincia_departamento"]], on="subdivision_codigo", how="left")
    ancho["provincia_departamento"] = ancho["provincia_departamento"].fillna("")

    # Orden: cada país, primero sus filas nacionales y después sus provincias; dentro, por tema y variable
    ancho["_n"] = (ancho["nivel"] == "subdivision").astype(int)
    ancho["_t"] = (ancho["tema"] != "identificacion").astype(int)
    ancho = ancho.sort_values(["pais", "_n", "provincia_departamento", "subdivision_codigo", "_t", "tema",
                               "variable", "apertura"]).drop(columns=["_n", "_t"])
    primeras = ["nivel", "pais_iso3", "pais", "subdivision_codigo", "provincia_departamento", "tema",
                "variable", "apertura", "unidad", "fuente"]
    return ancho[primeras + [c for c in ancho.columns if c not in primeras]].reset_index(drop=True)


def diccionario(largo):
    anios = pd.to_numeric(largo["anio"], errors="coerce")
    g = largo.assign(_a=anios).groupby(["nivel", "tema", "variable"], sort=True)
    return pd.DataFrame({
        "unidad": g["unidad"].first(),
        "fuente": g["fuente"].first(),
        "aperturas": g["apertura"].nunique(),
        "paises": g["pais_iso3"].nunique(),
        "subdivisiones": g["subdivision_codigo"].nunique(),
        "anio_min": g["_a"].min().astype("Int64"),
        "anio_max": g["_a"].max().astype("Int64"),
        "datos": g.size(),
    }).reset_index().assign(subdivisiones=lambda d: d["subdivisiones"].where(d["nivel"] == "subdivision", 0))


def main():
    print("Construyendo la base absoluta desde", MASTER.relative_to(ETL), "y los CSV complementarios")
    largo, subdiv_ident = construir()
    ancho = a_ancho(largo, subdiv_ident)
    dic = diccionario(largo)

    ancho.to_csv(AQUI / "base_absoluta.csv", index=False)
    dic.to_csv(AQUI / "diccionario_variables.csv", index=False)
    destino = AQUI / "base_absoluta.sqlite"
    destino.unlink(missing_ok=True)
    con = sqlite3.connect(destino)
    # NUMERIC: los números quedan como números y los textos (familia política, estado...) como texto
    datos = [c for c in ancho.columns if c == SIN_ANIO or c.isdigit()]
    ancho.to_sql("base_absoluta", con, index=False, chunksize=5000, dtype={c: "NUMERIC" for c in datos})
    dic.to_sql("diccionario_variables", con, index=False)
    for c in ["pais_iso3", "subdivision_codigo", "variable"]:
        con.execute(f"CREATE INDEX ix_base_{c} ON base_absoluta ({c})")
    con.commit()
    con.execute("VACUUM")
    con.close()

    filas = ancho["nivel"].value_counts()
    print(f"   {len(ancho):,} filas ({filas.get('pais', 0):,} de país y {filas.get('subdivision', 0):,} de "
          f"subdivisión), {ancho['pais_iso3'].nunique()} países, "
          f"{ancho.loc[ancho['nivel'] == 'subdivision', 'subdivision_codigo'].nunique()} subdivisiones")
    print(f"   {len(dic):,} variables, {len(largo):,} datos, años {[c for c in ancho.columns if c.isdigit()][0]}"
          f"-{[c for c in ancho.columns if c.isdigit()][-1]}")
    print("   salidas: base_absoluta.csv, base_absoluta.sqlite, diccionario_variables.csv")


if __name__ == "__main__":
    main()
