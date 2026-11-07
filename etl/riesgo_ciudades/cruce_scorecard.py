"""
CRUCE: puntajes del scorecard UNDRR contra pérdidas reales y gasto en gestión del riesgo.

Lee (en esta carpeta):
  scorecard_puntajes.csv          puntajes detallados de las 16 ciudades (copiados de
                                  consultas/scorecard_undrr/latam/Resumen_comparativo_scorecards_UNDRR.xlsx)
  perdidas_ciudad_resumen.csv     tasas de pérdidas (salen de extraer_riesgo_ciudades.py)
  gasto_riesgo_ciudad_anual.csv   gasto municipal en gestión del riesgo

Genera:
  cruce_scorecard_perdidas.csv    una fila por ciudad con puntaje, pérdidas y gasto
  cruce_scorecard_resultados.md   correlaciones de rango (Spearman) y lectura

Con 16 ciudades una correlación necesita |rho| > 0,50 para ser significativa al 5 %, así que se
lee como orientación, no como prueba. Las pérdidas vienen de bases que cuentan distinto (ver la guía).

Cómo ejecutarlo (desde la carpeta etl/):
    python riesgo_ciudades/cruce_scorecard.py
"""
from pathlib import Path

import math

import pandas as pd

CARPETA = Path(__file__).resolve().parent


def spearmanr(x, y):
    """Spearman con valor p por aproximación t (sin scipy)."""
    rho = pd.Series(list(x)).rank().corr(pd.Series(list(y)).rank())
    n = len(x)
    if n < 4 or abs(rho) >= 1:
        return rho, 0.0
    t = rho * math.sqrt((n - 2) / (1 - rho ** 2))
    # p bilateral con la t de Student (integración numérica simple, suficiente para orientar)
    gl = n - 2
    dens = lambda u: (1 + u * u / gl) ** (-(gl + 1) / 2)
    paso, lim = 0.001, abs(t)
    area = sum(dens(i * paso) for i in range(int(lim / paso))) * paso
    total = sum(dens(i * paso) for i in range(int(60 / paso))) * paso
    return rho, max(0.0, 1 - area / total)


def main():
    sc = pd.read_csv(CARPETA / "scorecard_puntajes.csv")
    pe = pd.read_csv(CARPETA / "perdidas_ciudad_resumen.csv")
    ga = pd.read_csv(CARPETA / "gasto_riesgo_ciudad_anual.csv")
    ga = ga[ga.nota.fillna("").str.startswith("No comparable") == False]  # noqa: E712
    ga_m = (ga[ga.anio >= ga.groupby("ciudad_id").anio.transform("max") - 2]  # últimos 3 años de cada ciudad
            .groupby(["ciudad_id", "moneda"]).agg(gasto_riesgo_por_hab=("gasto_riesgo_por_hab", "mean"),
                                                 pct_gasto_total=("pct_gasto_total", "mean")).reset_index())

    df = sc.merge(pe.drop(columns=["ciudad"]), on="ciudad_id").merge(ga_m, on="ciudad_id", how="left")
    df.to_csv(CARPETA / "cruce_scorecard_perdidas.csv", index=False)

    pares = [
        ("total_pct", "muertos_x100mil_anio_comun", "Puntaje total vs muertes por 100.000 hab./año (2000-2013)"),
        ("total_pct", "muertos_x100mil_anio_todo", "Puntaje total vs muertes por 100.000 hab./año (todo el período)"),
        ("total_pct", "viv_destruidas_x100mil_anio_comun", "Puntaje total vs viviendas destruidas por 100.000 hab./año (2000-2013)"),
        ("e04_desarrollo_urbano_pct", "viv_destruidas_x100mil_anio_comun", "Esencial 4 (desarrollo urbano) vs viviendas destruidas"),
        ("e09_respuesta_pct", "muertos_x100mil_anio_todo", "Esencial 9 (respuesta y alerta) vs muertes"),
        ("e02_riesgos_pct", "muertos_x100mil_anio_todo", "Esencial 2 (conocer los riesgos) vs muertes"),
    ]
    lineas = ["# Cruce del scorecard UNDRR con pérdidas reales y gasto", "",
              "Correlación de rango de Spearman entre el puntaje de cada ciudad y sus pérdidas por desastres "
              "socionaturales. Un valor negativo quiere decir que las ciudades con mejor puntaje tuvieron menos pérdidas, "
              "que es lo esperable si el scorecard mide bien. Con 16 ciudades hace falta |rho| > 0,50 para que sea significativo al 5 %.", "",
              "| Comparación | rho | p | n |", "|---|---|---|---|"]
    for x, y, t in pares:
        d = df[[x, y]].dropna()
        rho, p = spearmanr(d[x], d[y])
        lineas.append(f"| {t} | {rho:.2f} | {p:.2f} | {len(d)} |")
    lineas += ["", "## Gasto en gestión del riesgo (solo dentro de cada país, monedas distintas)", ""]
    for mon, pais in (("BRL", "Brasil"), ("COP", "Colombia")):
        d = df[df.moneda == mon][["ciudad", "e03_finanzas_pct", "gasto_riesgo_por_hab", "pct_gasto_total"]].sort_values("gasto_riesgo_por_hab", ascending=False)
        lineas.append(f"**{pais}** (promedio de los últimos 3 años, {mon} por habitante):")
        lineas.append("")
        lineas.append("| Ciudad | Esencial 3 Finanzas (%) | Gasto por hab. | % del gasto total |")
        lineas.append("|---|---|---|---|")
        for _, r in d.iterrows():
            lineas.append(f"| {r.ciudad} | {r.e03_finanzas_pct} | {r.gasto_riesgo_por_hab:,.2f} | {r.pct_gasto_total:.3f} |")
        if len(d) >= 3:
            rho, p = spearmanr(d.e03_finanzas_pct, d.gasto_riesgo_por_hab)
            lineas.append(f"\nSpearman Esencial 3 vs gasto por habitante: rho = {rho:.2f} (n = {len(d)}).")
        lineas.append("")
    lineas += ["## Ciudades donde el puntaje y las pérdidas no coinciden", ""]
    d = df.dropna(subset=["muertos_x100mil_anio_todo"]).copy()
    d["rango_puntaje"] = d.total_detallado_590.rank(ascending=False, method="first")
    d["rango_perdidas"] = d.muertos_x100mil_anio_todo.rank(ascending=True, method="first")  # 1 = menos muertes
    d["brecha"] = d.rango_puntaje - d.rango_perdidas
    for _, r in d.reindex(d.brecha.abs().sort_values(ascending=False).index).head(5).iterrows():
        sentido = "puntaje alto pero muchas muertes" if r.brecha < 0 else "puntaje bajo pero pocas muertes"
        lineas.append(f"- {r.ciudad}: puesto {int(r.rango_puntaje)} en puntaje y {int(r.rango_perdidas)} en menos muertes ({sentido}).")
    (CARPETA / "cruce_scorecard_resultados.md").write_text("\n".join(lineas) + "\n", encoding="utf8")
    print("\n".join(lineas))


if __name__ == "__main__":
    main()
