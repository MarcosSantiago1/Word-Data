"""
Suma del PIB por grupo internacional (G7, G20, Mercosur, UE, BRICS, OCDE, ASEAN, OTAN, ...).

Une dos tablas que ya arma el pipeline:
  - etl/alianzas/alianzas_pais_anual.csv   -> miembro_<grupo> = 1 si el país es miembro PLENO ese año
  - etl/datos_procesados/paises_anual.csv  -> pib_usd (NY.GDP.MKTP.CD), pib_pc_ppp (NY.GDP.PCAP.PP.KD), poblacion

y suma, para cada grupo y año, el PIB de los países que eran miembros plenos ESE año
(así BRICS 2023 tiene 5 países y BRICS 2024 tiene 9; el Reino Unido sale de la UE en 2020).

Dos medidas de PIB:
  - pib_usd_corriente: US$ corrientes a tipo de cambio de mercado (Banco Mundial NY.GDP.MKTP.CD).
  - pib_ppa_2021: dólares internacionales constantes de 2021 (paridad de poder adquisitivo),
    calculado como pib_pc_ppp x poblacion (equivale a NY.GDP.MKTP.PP.KD).

No se imputan datos: si un miembro no tiene PIB ese año queda fuera de la suma y se lista
en miembros_sin_dato_*. El "mundo" es la suma de los 217 países del panel con dato
(no incluye Taiwán ni territorios fuera del panel), y se usa para el % del mundo.

Salidas (en etl/pib_grupos/):
  - pib_por_grupo_anual.csv  : grupo x año (serie completa 2000-último año)
  - pib_por_grupo_resumen.csv: un año de referencia (el último en que los países sin dato
                               pesan menos del 0,5 % del PIB mundial)

Correr después de paso 1-3 y de alianzas:  python etl/pib_grupos/sumar_pib_grupos.py
"""
from pathlib import Path

import pandas as pd

ETL = Path(__file__).resolve().parent.parent
SALIDA = Path(__file__).resolve().parent

ALIANZAS = ETL / "alianzas" / "alianzas_pais_anual.csv"
MEMBRESIAS = ETL / "alianzas" / "membresias_organizaciones.csv"
PANEL = ETL / "datos_procesados" / "paises_anual.csv"

# Nombre corto para mostrar (el largo sale de membresias_organizaciones.csv).
NOMBRE_CORTO = {
    "g7": "G7", "g8": "G8", "g20": "G20 (solo países)", "brics": "BRICS", "ue": "Unión Europea",
    "eurozona": "Eurozona", "ocde": "OCDE", "otan": "OTAN", "mercosur": "Mercosur",
    "asean": "ASEAN", "apec": "APEC", "omc": "OMC", "opep": "OPEP", "opep_plus": "OPEP+",
    "tmec": "T-MEC", "tlcan": "TLCAN", "cptpp": "CPTPP", "rcep": "RCEP", "can": "CAN",
    "aladi": "ALADI", "alianza_pacifico": "Alianza del Pacífico", "caricom": "CARICOM",
    "sica": "SICA", "aelc": "AELC (EFTA)", "uee": "Unión Económica Euroasiática",
    "ccg": "Consejo de Cooperación del Golfo", "ocs": "Org. de Cooperación de Shanghái",
    "otsc": "OTSC", "aukus": "AUKUS", "quad": "Quad", "ua": "Unión Africana",
    "oea": "OEA", "alba": "ALBA", "liga_arabe": "Liga Árabe", "oci": "OCI",
    "consejo_europa": "Consejo de Europa", "commonwealth": "Commonwealth", "cei": "CEI",
    "saarc": "SAARC", "cedeao": "CEDEAO", "uemoa": "UEMOA", "cemac": "CEMAC", "sadc": "SADC",
    "sacu": "SACU", "comesa": "COMESA", "eac": "EAC", "aes": "Alianza de Estados del Sahel",
    "mnna_eeuu": "Aliados principales no OTAN de EE. UU.",
}


def main():
    alianzas = pd.read_csv(ALIANZAS)
    panel = pd.read_csv(PANEL, usecols=["iso3", "anio", "pib_usd", "pib_pc_ppp", "poblacion"])
    panel["pib_ppa_2021"] = panel["pib_pc_ppp"] * panel["poblacion"]

    anio_max = int(panel.loc[panel["pib_usd"].notna(), "anio"].max())
    alianzas = alianzas[alianzas["anio"] <= anio_max]
    datos = alianzas.merge(panel[["iso3", "anio", "pib_usd", "pib_ppa_2021"]],
                           on=["iso3", "anio"], how="left")

    nombres_largos = (pd.read_csv(MEMBRESIAS)[["organizacion", "organizacion_nombre"]]
                      .drop_duplicates("organizacion")
                      .assign(organizacion=lambda d: d["organizacion"].str.lower())
                      .set_index("organizacion")["organizacion_nombre"].to_dict())

    mundo = panel.groupby("anio").agg(
        mundo_pib_usd=("pib_usd", "sum"), mundo_pib_ppa_2021=("pib_ppa_2021", "sum"),
        paises_con_dato=("pib_usd", "count"), paises_panel=("iso3", "nunique"))

    filas = []
    for col in [c for c in alianzas.columns if c.startswith("miembro_")]:
        grupo = col.removeprefix("miembro_")
        miembros = datos[datos[col] == 1]
        for anio, d in miembros.groupby("anio"):
            filas.append({
                "grupo": grupo,
                "grupo_nombre": NOMBRE_CORTO.get(grupo, grupo.upper()),
                "grupo_nombre_largo": nombres_largos.get(grupo, ""),
                "anio": anio,
                "n_miembros": len(d),
                "n_con_dato_usd": int(d["pib_usd"].notna().sum()),
                "n_con_dato_ppa": int(d["pib_ppa_2021"].notna().sum()),
                "pib_usd_corriente": d["pib_usd"].sum(min_count=1),
                "pib_ppa_2021": d["pib_ppa_2021"].sum(min_count=1),
                "miembros": " ".join(sorted(d["iso3"])),
                "miembros_sin_dato_usd": " ".join(sorted(d.loc[d["pib_usd"].isna(), "iso3"])),
                "miembros_sin_dato_ppa": " ".join(sorted(d.loc[d["pib_ppa_2021"].isna(), "iso3"])),
            })

    tabla = pd.DataFrame(filas).merge(mundo, left_on="anio", right_index=True, how="left")
    tabla["pct_mundo_usd"] = 100 * tabla["pib_usd_corriente"] / tabla["mundo_pib_usd"]
    tabla["pct_mundo_ppa"] = 100 * tabla["pib_ppa_2021"] / tabla["mundo_pib_ppa_2021"]
    tabla["pib_usd_billones"] = tabla["pib_usd_corriente"] / 1e12      # billones = 10^12 (trillions)
    tabla["pib_ppa_2021_billones"] = tabla["pib_ppa_2021"] / 1e12
    tabla = tabla.drop(columns=["paises_con_dato", "paises_panel"])
    orden = ["grupo", "grupo_nombre", "grupo_nombre_largo", "anio", "n_miembros",
             "n_con_dato_usd", "n_con_dato_ppa", "pib_usd_corriente", "pib_usd_billones",
             "pct_mundo_usd", "pib_ppa_2021", "pib_ppa_2021_billones", "pct_mundo_ppa",
             "mundo_pib_usd", "mundo_pib_ppa_2021", "miembros", "miembros_sin_dato_usd",
             "miembros_sin_dato_ppa"]
    tabla = tabla[orden].sort_values(["grupo", "anio"])
    tabla.to_csv(SALIDA / "pib_por_grupo_anual.csv", index=False, float_format="%.6g")

    # Año de referencia: el último en que los países SIN dato pesan menos del 0,5 % del PIB
    # mundial (medido con su último PIB conocido). Así no se elige un año donde falta,
    # por ejemplo, Emiratos o Líbano solo porque el Banco Mundial aún no los publicó.
    ultimo_conocido = (panel.sort_values("anio").groupby("iso3")["pib_usd"].ffill())
    panel["pib_usd_relleno"] = ultimo_conocido
    faltante = (panel[panel["pib_usd"].isna()].groupby("anio")["pib_usd_relleno"].sum()
                .reindex(mundo.index, fill_value=0))
    peso_faltante = faltante / (mundo["mundo_pib_usd"] + faltante)
    anio_ref = int(peso_faltante[peso_faltante < 0.005].index.max())
    resumen = (tabla[tabla["anio"] == anio_ref]
               .sort_values("pib_usd_corriente", ascending=False))
    resumen.to_csv(SALIDA / "pib_por_grupo_resumen.csv", index=False, float_format="%.6g")

    print(f"Año de referencia: {anio_ref}  (series {tabla['anio'].min()}-{tabla['anio'].max()})")
    print(f"Mundo (suma del panel): US$ {mundo.loc[anio_ref, 'mundo_pib_usd']/1e12:.1f} billones")
    print(resumen[["grupo_nombre", "n_miembros", "pib_usd_billones", "pct_mundo_usd",
                   "pib_ppa_2021_billones", "pct_mundo_ppa", "miembros_sin_dato_usd"]]
          .to_string(index=False, float_format=lambda x: f"{x:,.1f}"))


if __name__ == "__main__":
    main()
