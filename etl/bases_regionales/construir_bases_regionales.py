"""
BASES REGIONALES: separa toda la información del proyecto en tres bases SQLite.

    base_argentina.sqlite   Argentina: datos nacionales + las 24 provincias
    base_latam.sqlite       América Latina y el Caribe (región M49 419 de la ONU, 52 países
                            y territorios): datos por país + por subdivisión (estados, provincias...)
    base_mundial.sqlite     todos los países (251) y todas las subdivisiones con datos

De dónde sale cada cosa:
  1. El master (modelo_unificado/master_paises_provincias.sqlite) ya junta casi todo. De él se
     copian las mismas tablas y vistas, quedándose solo con las filas de los países de la región:
       - tablas con pais_id          -> filas de esos países
       - tablas con subdivision_id   -> filas de subdivisiones de esos países
       - alianzas militares (diadas) -> pactos en los que participa al menos un país de la región
       - dim_pais, pais_equivalencia y el resto de los catálogos (dim_*) quedan completos,
         porque las alianzas, fronteras y socios comerciales nombran países de afuera.
  2. Lo que el master todavía no tiene se carga desde sus CSV (tabla COMPLEMENTOS):
       latam_subnacional/*.csv (OCDE, temperatura, gobernantes, Brasil, agro, ganado, petróleo),
       argentina_provincias/festivales_*.csv y los resultados de kpis/resultados/*.csv.
  3. Se rehacen el catálogo (ref_catalogo_tabla) y el diccionario (ref_diccionario_columna) con
     las filas y los nulos de cada base, y se agrega ref_alcance_base, que dice qué hay adentro.

Orden de ejecución: al final del pipeline, después de modelo_unificado/construir_master.py.

    cd etl/bases_regionales
    python construir_bases_regionales.py

Salidas (en esta carpeta): las tres .sqlite y resumen_bases.csv (filas de cada tabla por base).
"""

import ast
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
ETL = AQUI.parent
MASTER = ETL / "modelo_unificado" / "master_paises_provincias.sqlite"
LEER = dict(keep_default_na=False, na_values=[""], low_memory=False)  # "NA" es Namibia, no un nulo

# nombre de archivo, descripción, SQL que elige los países (pais_id) de la base
BASES = [
    ("base_argentina.sqlite", "Argentina: datos nacionales y de las 24 provincias",
     "SELECT pais_id FROM m.dim_pais WHERE iso3 = 'ARG'"),
    ("base_latam.sqlite", "América Latina y el Caribe (M49 419): países y subdivisiones",
     """SELECT p.pais_id FROM m.dim_pais p
        JOIN m.dim_region_geografica r ON r.region_geografica_id = p.region_geografica_id
        WHERE r.region_padre_id = 419"""),
    ("base_mundial.sqlite", "Mundo: todos los países y todas las subdivisiones con datos",
     "SELECT pais_id FROM m.dim_pais"),
]

# Tablas que no se filtran: son catálogos que las demás necesitan para unir y nombrar países
COMPLETAS = {"dim_pais", "pais_equivalencia"}

# CSV que no están en el master: tabla nueva, archivo (relativo a etl/), clave, fuente
COMPLEMENTOS = [
    ("hecho_subdivision_latam_ocde", "latam_subnacional/indicadores_ocde_subdivision_anual.csv",
     ["subdivision_id", "anio"], "OCDE, Regional Database (TL2)"),
    ("hecho_subdivision_latam_temperatura", "latam_subnacional/temperatura_subdivision_anual.csv",
     ["subdivision_id", "anio"], "Banco Mundial, Climate Change Knowledge Portal"),
    ("hecho_subdivision_latam_gobierno", "latam_subnacional/gobierno_subdivision_anual.csv",
     ["subdivision_id", "anio"], "Wikidata (gobernante al cierre de cada año)"),
    ("rel_subdivision_gobernante", "latam_subnacional/gobernantes_subdivision.csv",
     ["subdivision_id", "persona_wikidata", "inicio"], "Wikidata"),
    ("hecho_subdivision_brasil_pib", "latam_subnacional/brasil_pib_poblacion_estado_anual.csv",
     ["subdivision_id", "anio"], "IBGE (SIDRA)"),
    ("hecho_subdivision_latam_agricultura", "latam_subnacional/agricultura_subdivision_anual.csv",
     ["subdivision_id", "anio", "cultivo_original"], "MAGyP, IBGE, DANE y otros (formato común)"),
    ("hecho_subdivision_latam_ganaderia", "latam_subnacional/ganaderia_subdivision_anual.csv",
     ["subdivision_id", "anio", "especie_original"], "MAGyP/SENASA, IBGE y otros (formato común)"),
    ("hecho_subdivision_latam_petroleo_gas", "latam_subnacional/petroleo_gas_subdivision_anual.csv",
     ["subdivision_id", "anio"], "Secretaría de Energía, ANP y otros (formato común)"),
    ("hecho_subdivision_festivales", "argentina_provincias/festivales_provincia.csv",
     ["subdivision_id"], "Festivales Argentinos 2023 y relevamientos provinciales"),
    ("ref_festival", "argentina_provincias/festivales_lista.csv",
     ["festival_id"], "Festivales Argentinos 2023 y relevamientos provinciales"),
    ("kpi1_sal_efi_iese", "kpis/resultados/KPI1_SAL_EFI_IESE.csv", ["pais_id"], "calcular_kpis.py"),
    ("kpi2_psi_paradoja_ipfs", "kpis/resultados/KPI2_PSI_PARADOJA_IPFS.csv", ["pais_id"], "calcular_kpis.py"),
    ("kpi3_geo_expo_ieg", "kpis/resultados/KPI3_GEO_EXPO_IEG.csv", ["pais_id"], "calcular_kpis.py"),
    ("kpi4_soc_tension_itid", "kpis/resultados/KPI4_SOC_TENSION_ITID.csv", ["pais_id"], "calcular_kpis.py"),
    ("kpi5_prov_rentismo_irfh", "kpis/resultados/KPI5_PROV_RENTISMO_IRFH.csv", ["subdivision_id"],
     "calcular_kpis.py"),
]
# Tablas latam en "formato común" cuyos datos de Argentina son copia de una tabla del master con la
# misma fuente (agricultura, stock bovino, temperatura, petróleo y gas): en la base de Argentina
# sobran; en la de Latam y la mundial quedan, porque sirven para comparar Argentina con otros países.
REPETIDAS_EN_ARGENTINA = {"hecho_subdivision_latam_agricultura", "hecho_subdivision_latam_ganaderia",
                          "hecho_subdivision_latam_temperatura", "hecho_subdivision_latam_petroleo_gas"}
# Resúmenes de KPIs que no tienen país ni provincia: van solo a la base donde tienen sentido
RESUMENES_KPI = [
    ("kpi4b_itid_por_cuartil_y_forma_estado", "kpis/resultados/KPI4b_ITID_POR_CUARTIL_Y_FORMA_ESTADO.csv",
     {"base_mundial.sqlite"}),
    ("kpi5b_correlacion_rentismo_continuidad", "kpis/resultados/KPI5b_CORRELACION_RENTISMO_CONTINUIDAD.csv",
     {"base_argentina.sqlite", "base_latam.sqlite", "base_mundial.sqlite"}),
]
# Columnas que pasan a ser un id (se borran porque el id ya las trae, vía dim_pais / dim_subdivision)
SE_VUELVEN_ID = ["iso3", "pais", "subdivision_iso", "subdivision", "provincia_iso", "provincia", "codigo"]
COLUMNAS_ANIO = ("anio", "decada_censal", "anio_cosecha", "anio_censo", "anio_eleccion", "anio_ingreso",
                 "anio_entrada_vigor")


def unidades_del_master():
    """Lee la lista UNIDADES de construir_master.py sin importarlo (así no hacen falta sus librerías)."""
    codigo = (ETL / "modelo_unificado" / "construir_master.py").read_text(encoding="utf-8")
    for nodo in ast.parse(codigo).body:
        if isinstance(nodo, ast.Assign) and getattr(nodo.targets[0], "id", None) == "UNIDADES":
            return ast.literal_eval(nodo.value)
    return []


UNIDADES = unidades_del_master()


def unidad(columna):
    for sufijo, u in UNIDADES:
        if columna.endswith(sufijo) or f"{sufijo}_" in columna:
            return u
    return "%" if columna.startswith("pct_") else None


def tipo_sql(serie):
    if pd.api.types.is_bool_dtype(serie) or pd.api.types.is_integer_dtype(serie):
        return "INTEGER"
    if pd.api.types.is_float_dtype(serie):
        return "REAL"
    return "TEXT"


def columnas(con, tabla, esquema="main"):
    return [r[1] for r in con.execute(f'PRAGMA {esquema}.table_info("{tabla}")')]


# ---------------------------------------------------------------------------
# 1. Copia filtrada del master
# ---------------------------------------------------------------------------
def filtro(tabla, cols):
    """WHERE que deja solo las filas de los países de la base (tabla temp.alcance)."""
    en = "IN (SELECT pais_id FROM temp.alcance)"
    if tabla in COMPLETAS or tabla.startswith("ref_"):
        return ""
    if tabla == "dim_subdivision":  # sus países + las que reclama un país de la región
        return (f"WHERE pais_id {en} OR subdivision_id IN (SELECT subdivision_reclamante_id FROM "
                f"m.rel_reclamo_territorial WHERE pais_id {en} OR pais_reclamante_id {en})")
    if tabla == "rel_alianza_militar_anual":
        return f"WHERE pais_a_id {en} OR pais_b_id {en}"
    if tabla == "rel_reclamo_territorial":
        return f"WHERE pais_id {en} OR pais_reclamante_id {en}"
    if "pais_id" in cols:
        return f"WHERE pais_id {en}"
    if "subdivision_id" in cols:
        return "WHERE subdivision_id IN (SELECT subdivision_id FROM main.dim_subdivision)"
    return ""  # catálogos sin país (dim_region_bm, dim_rama_cepal, dim_organizacion...)


def copiar_master(con):
    objetos = con.execute("SELECT type, name, sql FROM m.sqlite_master WHERE sql IS NOT NULL "
                          "AND name NOT LIKE 'sqlite_%' ORDER BY rowid").fetchall()
    tablas = [n for t, n, _ in objetos if t == "table"]
    for t, n, sql in objetos:  # primero el esquema, igual al del master
        if t in ("table", "index"):
            con.execute(sql)
    for n in tablas:
        if n.startswith("ref_"):
            continue  # se rehacen al final
        con.execute(f'INSERT INTO main."{n}" SELECT * FROM m."{n}" {filtro(n, columnas(con, n, "m"))}')
    for t, n, sql in objetos:
        if t in ("view", "trigger"):
            con.execute(sql)
    return tablas


# ---------------------------------------------------------------------------
# 2. Complementos que el master todavía no tiene
# ---------------------------------------------------------------------------
def preparar_complemento(tabla, archivo, clave, ids_sub, ids_pais):
    d = pd.read_csv(ETL / archivo, **LEER)
    if "subdivision_id" in clave:
        cod = d["subdivision_iso"] if "subdivision_iso" in d else d.get("provincia_iso", d.get("codigo"))
        d.insert(0, "subdivision_id", cod.map(ids_sub))
        faltan = sorted(set(cod[d.subdivision_id.isna()]))
        assert not faltan, f"{archivo}: códigos que no están en dim_subdivision: {faltan[:10]}"
        d["subdivision_id"] = d.subdivision_id.astype(int)
    elif "pais_id" in clave:
        d.insert(0, "pais_id", d.iso3.map(ids_pais))
        assert d.pais_id.notna().all(), f"{archivo}: iso3 que no están en dim_pais"
        d["pais_id"] = d.pais_id.astype(int)
    else:  # una fila por festival, sin clave natural: se numeran
        d.insert(0, "festival_id", range(1, len(d) + 1))
        d.insert(1, "subdivision_id", d.provincia_iso.map(ids_sub).astype(int))
    d = d.drop(columns=[c for c in SE_VUELVEN_ID if c in d])
    assert not d.duplicated(clave).any(), f"{tabla}: clave repetida {clave}"
    return d


def crear_tabla(con, tabla, d, clave):
    fk = {"pais_id": "dim_pais(pais_id)", "subdivision_id": "dim_subdivision(subdivision_id)"}
    lineas = [f"    {c} {tipo_sql(d[c])}" + (" NOT NULL" if c in clave else "") +
              (f" REFERENCES {fk[c]}" if c in fk else "") for c in d.columns]
    if clave:
        lineas.append(f"    PRIMARY KEY ({', '.join(clave)})")
    con.execute(f"CREATE TABLE {tabla} (\n" + ",\n".join(lineas) + "\n)")
    d = d.astype(object).where(d.notna(), None)
    con.executemany(f"INSERT INTO {tabla} ({', '.join(d.columns)}) VALUES ({', '.join('?' * len(d.columns))})",
                    d.itertuples(index=False, name=None))


def crear_vista_con_nombres(con, tabla, d):
    """Vista v_... con el código y el nombre a la vista, para no tener que hacer el JOIN a mano."""
    resto = ", ".join(f"t.{c}" for c in d.columns if c not in ("pais_id", "subdivision_id"))
    vista = "v_" + tabla.removeprefix("hecho_").removeprefix("rel_").removeprefix("ref_")
    if "subdivision_id" in d:
        con.execute(f"""CREATE VIEW {vista} AS
            SELECT p.iso3, s.codigo, COALESCE(s.nombre_es, s.nombre) AS subdivision, {resto}
            FROM {tabla} t JOIN dim_subdivision s USING (subdivision_id) JOIN dim_pais p ON p.pais_id = s.pais_id""")
    else:
        con.execute(f"""CREATE VIEW {vista} AS
            SELECT p.iso3, p.nombre_es AS pais, {resto} FROM {tabla} t JOIN dim_pais p USING (pais_id)""")


def sumar_complementos(con, nombre_base, alcance):
    ids_sub = dict(con.execute("SELECT codigo, subdivision_id FROM m.dim_subdivision"))
    ids_pais = dict(con.execute("SELECT iso3, pais_id FROM m.dim_pais"))
    sub_alcance = {i for (i,) in con.execute("SELECT subdivision_id FROM main.dim_subdivision")}
    nuevas = {}
    for tabla, archivo, clave, fuente in COMPLEMENTOS:
        if nombre_base == "base_argentina.sqlite" and tabla in REPETIDAS_EN_ARGENTINA:
            continue
        if not (ETL / archivo).exists():
            print(f"   (falta {archivo}: {tabla} no se suma)")
            continue
        d = preparar_complemento(tabla, archivo, clave, ids_sub, ids_pais)
        d = d[d.subdivision_id.isin(sub_alcance)] if "subdivision_id" in d else d[d.pais_id.isin(alcance)]
        if d.empty:
            continue
        crear_tabla(con, tabla, d, clave)
        crear_vista_con_nombres(con, tabla, d)
        nuevas[tabla] = (d, clave, fuente, archivo)
    for tabla, archivo, bases in RESUMENES_KPI:
        if nombre_base in bases and (ETL / archivo).exists():
            d = pd.read_csv(ETL / archivo, **LEER)
            crear_tabla(con, tabla, d, [])
            nuevas[tabla] = (d, [], "calcular_kpis.py", archivo)
    return nuevas


# ---------------------------------------------------------------------------
# 3. Catálogo, diccionario y alcance de cada base
# ---------------------------------------------------------------------------
def rehacer_catalogo(con, tablas_master, nuevas):
    cat_m = pd.read_sql("SELECT * FROM m.ref_catalogo_tabla", con).set_index("tabla")
    dic_m = pd.read_sql("SELECT * FROM m.ref_diccionario_columna", con).set_index(["tabla", "columna"])
    catalogo, diccionario = [], []
    hechas = [t for t in tablas_master if not t.startswith("ref_")]
    for t in hechas + list(nuevas):
        d = pd.read_sql(f'SELECT * FROM "{t}"', con)
        anio = next((c for c in COLUMNAS_ANIO if c in d and d[c].notna().any()), None)
        if t in nuevas:
            _, clave, fuente, archivo = nuevas[t]
            tipo = "kpi" if t.startswith("kpi") else t.split("_")[0]
            fila = dict(tabla=t, tipo=tipo, grano=", ".join(clave) or "una fila por grupo", fuente=fuente,
                        archivo_origen=archivo)
        elif t in cat_m.index:
            fila = dict(tabla=t, **cat_m.loc[t, ["tipo", "grano", "fuente", "archivo_origen"]].to_dict())
        else:
            fila = dict(tabla=t, tipo=t.split("_")[0], grano=None, fuente=None, archivo_origen=None)
        fila |= dict(filas=len(d), anio_min=int(d[anio].min()) if anio else None,
                     anio_max=int(d[anio].max()) if anio else None)
        catalogo.append(fila)
        for c in d.columns:
            previo = dic_m.loc[(t, c)] if (t, c) in dic_m.index else None
            diccionario.append(dict(tabla=t, columna=c,
                                    tipo_sql=previo.tipo_sql if previo is not None else tipo_sql(d[c]),
                                    unidad=previo.unidad if previo is not None else unidad(c),
                                    pct_nulos=round(100 * d[c].isna().mean(), 1) if len(d) else None))
    for nombre, filas in (("ref_catalogo_tabla", catalogo), ("ref_diccionario_columna", diccionario)):
        filas = pd.DataFrame(filas)
        filas = filas.astype(object).where(filas.notna(), None)
        con.executemany(f"INSERT INTO {nombre} ({', '.join(filas.columns)}) VALUES "
                        f"({', '.join('?' * len(filas.columns))})", filas.itertuples(index=False, name=None))
    return pd.DataFrame(catalogo)


def subdivisiones_con_datos(con):
    tablas = [t for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name <> "
                                        "'dim_subdivision' AND name NOT LIKE 'subdivision_%'")
              if "subdivision_id" in columnas(con, t)]
    union = " UNION ".join(f'SELECT subdivision_id FROM "{t}"' for t in tablas)
    return con.execute(f"SELECT COUNT(*) FROM ({union})").fetchone()[0] if tablas else 0


def escribir_alcance(con, nombre, descripcion, alcance):
    paises = con.execute(f"SELECT group_concat(iso3, ' ') FROM (SELECT iso3 FROM dim_pais WHERE pais_id IN "
                         f"({','.join(map(str, alcance))}) ORDER BY iso3)").fetchone()[0]
    con.execute("CREATE TABLE ref_alcance_base (clave TEXT PRIMARY KEY, valor TEXT NOT NULL)")
    con.executemany("INSERT INTO ref_alcance_base VALUES (?, ?)", [
        ("base", nombre), ("descripcion", descripcion), ("paises_iso3", paises),
        ("cantidad_paises", str(len(alcance))),
        ("subdivisiones_con_datos", str(subdivisiones_con_datos(con))),
        ("construida", datetime.now().strftime("%Y-%m-%d %H:%M")),
        ("master_de_origen", f"modelo_unificado/{MASTER.name} del "
                             f"{datetime.fromtimestamp(MASTER.stat().st_mtime):%Y-%m-%d %H:%M}"),
    ])


def construir(nombre, descripcion, sql_alcance):
    ruta = AQUI / nombre
    temporal = ruta.with_suffix(".tmp")
    temporal.unlink(missing_ok=True)
    con = sqlite3.connect(temporal)
    con.execute("ATTACH DATABASE ? AS m", (str(MASTER),))
    con.execute(f"CREATE TEMP TABLE alcance AS {sql_alcance}")
    alcance = [i for (i,) in con.execute("SELECT pais_id FROM temp.alcance")]
    tablas_master = copiar_master(con)
    nuevas = sumar_complementos(con, nombre, set(alcance))
    catalogo = rehacer_catalogo(con, tablas_master, nuevas)
    escribir_alcance(con, nombre, descripcion, alcance)
    con.commit()
    # Controles: claves foráneas válidas y vistas que se pueden leer
    errores = con.execute("PRAGMA main.foreign_key_check").fetchall()
    assert not errores, f"{nombre}: claves foráneas rotas, por ejemplo {errores[:5]}"
    for (v,) in con.execute("SELECT name FROM main.sqlite_master WHERE type = 'view'").fetchall():
        con.execute(f'SELECT * FROM "{v}" LIMIT 1').fetchall()
    con.execute("DETACH DATABASE m")
    con.execute("VACUUM")
    con.close()
    temporal.replace(ruta)  # recién acá se pisa la base anterior
    vacias = catalogo[catalogo.filas == 0].tabla.tolist()
    print(f"   {nombre}: {len(alcance)} países, {len(catalogo)} tablas ({len(nuevas)} complementos), "
          f"{ruta.stat().st_size / 1e6:.1f} MB")
    if vacias:
        print(f"      tablas sin filas para esta región: {', '.join(vacias)}")
    return catalogo.set_index("tabla").filas.rename(nombre.removesuffix(".sqlite"))


def main():
    assert MASTER.exists(), f"Falta {MASTER}: correr antes modelo_unificado/construir_master.py"
    print("Construyendo las bases regionales desde", MASTER.relative_to(ETL))
    resumen = pd.concat([construir(*b) for b in BASES], axis=1).fillna(0).astype(int)
    resumen.index.name = "tabla"
    resumen.to_csv(AQUI / "resumen_bases.csv")
    # Control: la base mundial no pierde ninguna fila del master
    con = sqlite3.connect(f"{MASTER.as_uri()}?mode=ro", uri=True)
    for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'ref_%'"):
        n = con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        assert resumen.loc[t, "base_mundial"] == n, f"base_mundial perdió filas de {t}"
    con.close()
    print("   control: la base mundial tiene todas las filas del master")
    print(f"   resumen por tabla en {(AQUI / 'resumen_bases.csv').relative_to(ETL)}")


if __name__ == "__main__":
    main()
