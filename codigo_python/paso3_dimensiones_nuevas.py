"""
PASO 3 DEL ETL: sumar al dataset país-año las seis dimensiones nuevas
(migración y remesas, emisiones y energía, capital social, constituciones,
gobernanza, deuda y riesgo, salud crónica y tecnología).

No descarga nada: toma las tablas por país que deja
fuentes_nuevas/extraer_dimensiones_nuevas.py y las une al panel del paso 1
(datos_procesados/paises_anual.csv) con la misma clave: iso3 + anio.
Se conservan exactamente las filas del panel (217 países, 2000-2024).

Queda afuera el % de población indígena, que es por censo y no por año
(fuentes_nuevas/pais_poblacion_indigena.csv).

Cómo ejecutarlo (desde la carpeta etl/, después de los pasos 1 y 2):
    python fuentes_nuevas/extraer_dimensiones_nuevas.py   # baja los datos (si no se bajaron)
    python paso3_dimensiones_nuevas.py

Se puede volver a ejecutar las veces que quieras: antes de unir, borra las
columnas que él mismo agregó la vez anterior. El paso 1 reescribe el panel,
así que después de cada paso 1 hay que volver a correr los pasos 2 y 3.
"""

from pathlib import Path

import pandas as pd

CARPETA = Path(__file__).resolve().parent
ARCHIVO_PANEL = CARPETA / "datos_procesados" / "paises_anual.csv"
NUEVAS = CARPETA / "fuentes_nuevas"

# Tablas país-año, en el orden en que quedan sus columnas en el panel
TABLAS = [
    "pais_migracion_anual.csv",
    "pais_emisiones_energia_anual.csv",
    "pais_capital_social_anual.csv",
    "pais_diversidad_cultural_anual.csv",
    "pais_gobernanza_anual.csv",
    "pais_financiero_deuda_anual.csv",
    "pais_salud_cronica_anual.csv",
    "pais_tecnologia_anual.csv",
]
# Conteos y 0/1: enteros aunque falten datos
ENTEROS = ("es_", "saldo_", "personas_", "muertes_", "veto_", "avad_total", "spread_embi_meses")


def columnas_nuevas():
    return [c for t in TABLAS for c in pd.read_csv(NUEVAS / t, nrows=0).columns if c not in ("iso3", "anio")]


def main():
    faltan = [t for t in TABLAS if not (NUEVAS / t).exists()]
    assert not faltan, f"Faltan {faltan}: correr antes fuentes_nuevas/extraer_dimensiones_nuevas.py"
    nuevas = columnas_nuevas()

    panel = pd.read_csv(ARCHIVO_PANEL)
    panel["poblacion"] = panel["poblacion"].astype("Int64")
    for c in ("felicidad_ranking",):
        if c in panel:
            panel[c] = panel[c].astype("Int64")
    panel = panel.drop(columns=[c for c in nuevas if c in panel.columns])
    filas = len(panel)
    print(f"Panel de los pasos 1 y 2: {filas} filas, {panel.shape[1]} columnas")

    for t in TABLAS:
        d = pd.read_csv(NUEVAS / t)
        assert not d.duplicated(["iso3", "anio"]).any(), t
        # LEFT JOIN: conservamos exactamente las filas del panel
        panel = panel.merge(d, on=["iso3", "anio"], how="left")
        print(f"   + {t}: {d.shape[1] - 2} columnas")
    assert len(panel) == filas
    for c in nuevas:
        if c.startswith(ENTEROS):
            panel[c] = panel[c].round().astype("Int64")

    panel.to_csv(ARCHIVO_PANEL, index=False)
    print(f"\nListo: {len(panel)} filas x {panel.shape[1]} columnas -> {ARCHIVO_PANEL}")
    print("\nPaíses con al menos un dato, por variable nueva:")
    print(panel.groupby("iso3")[nuevas].count().gt(0).sum().to_string())


if __name__ == "__main__":
    main()
