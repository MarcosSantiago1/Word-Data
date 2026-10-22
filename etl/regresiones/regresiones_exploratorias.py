"""Ejemplos exploratorios de regresión lineal y logística sobre el panel de países.

Uso:
    pip install statsmodels scikit-learn
    python etl/regresiones/regresiones_exploratorias.py

Lee etl/datos_procesados/paises_anual.csv (no lo modifica) y corre tres
ejemplos chicos, pensados para aprender y para ver si los datos alcanzan:

  1. Lineal (MCO): ¿qué acompaña a la felicidad de un país? (corte 2021)
  2. Logística: ¿qué acompaña a que un país sea democracia electoral? (2021)
  3. Panel: felicidad y PIB 2011-2024, con y sin efectos fijos por país.

Imprime los resultados y guarda tablas en etl/regresiones/resultados/.
Son correlaciones condicionadas, no efectos causales: ver GUIA_REGRESIONES.md.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.metrics import roc_auc_score
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import jarque_bera

AQUI = Path(__file__).resolve().parent
PANEL = AQUI.parent / "datos_procesados" / "paises_anual.csv"
SALIDA = AQUI / "resultados"
ANIO = 2021


def vif(datos, columnas):
    """VIF de cada explicativa: >5 avisa, >10 es multicolinealidad seria."""
    X = sm.add_constant(datos[columnas])
    return pd.Series(
        [variance_inflation_factor(X.values, i) for i in range(1, X.shape[1])],
        index=columnas, name="vif").round(2)


def ultimo_disponible(panel, columna, desde, hasta):
    """Último valor no nulo de cada país entre dos años (para Gini, que tiene huecos)."""
    v = panel[(panel.anio >= desde) & (panel.anio <= hasta)].dropna(subset=[columna])
    return v.sort_values("anio").groupby("iso3")[columna].last()


def titulo(texto):
    print("\n" + "=" * 78 + f"\n{texto}\n" + "=" * 78)


def preparar():
    panel = pd.read_csv(PANEL).copy()
    panel["log_pib_pc_ppp"] = np.log(panel.pib_pc_ppp)
    corte = panel[panel.anio == ANIO].set_index("iso3").copy()
    corte["gini_ultimo_2015_2021"] = ultimo_disponible(panel, "gini", 2015, ANIO)
    corte["mena"] = corte.region.str.startswith("Middle East").astype(int)
    return panel, corte


def ejemplo_lineal(corte):
    titulo(f"1. REGRESIÓN LINEAL (MCO): felicidad {ANIO}")
    y = "felicidad"
    xs = ["log_pib_pc_ppp", "esperanza_vida", "indice_control_corrupcion",
          "gasto_salud_pct_pib", "gini_ultimo_2015_2021"]
    datos = corte[[y] + xs].dropna()
    print(f"Países con felicidad: {corte[y].notna().sum()} · con todas las variables: {len(datos)}")

    # Errores estándar robustos (HC3): no exigen varianza constante del error.
    m = smf.ols(f"{y} ~ " + " + ".join(xs), data=datos).fit(cov_type="HC3")
    print(m.summary().tables[1])
    print(f"R² = {m.rsquared:.3f} · R² ajustado = {m.rsquared_adj:.3f} · n = {int(m.nobs)}")

    # Coeficientes estandarizados: comparables entre variables (en desvíos estándar).
    z = (datos - datos.mean()) / datos.std()
    beta = smf.ols(f"{y} ~ " + " + ".join(xs), data=z).fit().params.drop("Intercept")

    print("\nMulticolinealidad (VIF):")
    print(vif(datos, xs).to_string())
    _, p_bp, _, _ = het_breuschpagan(m.resid, m.model.exog)
    jb, p_jb, _, _ = jarque_bera(m.resid)
    print(f"\nBreusch-Pagan (varianza constante) p = {p_bp:.3f}  -> si p < 0,05 usar errores robustos (ya se usan)")
    print(f"Jarque-Bera (residuos normales)     p = {p_jb:.3f}")
    influencia = m.get_influence().cooks_distance[0]
    top = pd.Series(influencia, index=datos.index).sort_values(ascending=False).head(5)
    print("Países más influyentes (distancia de Cook):", ", ".join(f"{i} {v:.2f}" for i, v in top.items()))

    print("\nQué pasa si se meten tres índices de gobernanza casi iguales (r > 0,9):")
    print(vif(corte[["indice_control_corrupcion", "indice_estado_derecho",
                     "efectividad_gobierno"]].dropna(),
              ["indice_control_corrupcion", "indice_estado_derecho", "efectividad_gobierno"]).to_string())

    tabla = pd.DataFrame({"coef": m.params, "error_robusto": m.bse, "p_valor": m.pvalues,
                          "beta_estandarizado": beta}).round(4)
    tabla.to_csv(SALIDA / "lineal_felicidad_2021.csv", index_label="variable")
    pd.DataFrame({"felicidad": datos[y], "predicho": m.fittedvalues.round(3),
                  "residuo": m.resid.round(3)}).sort_values("residuo").to_csv(
        SALIDA / "lineal_felicidad_2021_residuos.csv", index_label="iso3")
    return m


def ejemplo_logistico(corte):
    titulo(f"2. REGRESIÓN LOGÍSTICA: ¿democracia electoral? {ANIO}")
    # V-Dem: índice de democracia electoral 0-1. Umbral 0,5 = convención de este ejemplo.
    corte = corte.dropna(subset=["indice_democracia_electoral_0_1"]).copy()
    corte["democracia"] = (corte.indice_democracia_electoral_0_1 >= 0.5).astype(int)
    xs = ["log_pib_pc_ppp", "gasto_educacion_pct_pib", "mena"]
    datos = corte[["democracia"] + xs].dropna()
    eventos = datos.democracia.value_counts()
    print(f"n = {len(datos)} · democracias = {eventos.get(1, 0)} · no democracias = {eventos.get(0, 0)}")
    print(f"Eventos por variable (regla práctica ≥ 10): {eventos.min() / len(xs):.0f}")

    m = smf.logit("democracia ~ " + " + ".join(xs), data=datos).fit(disp=False)
    print(m.summary().tables[1])
    odds = pd.DataFrame({"odds_ratio": np.exp(m.params),
                         "ic95_inf": np.exp(m.conf_int()[0]),
                         "ic95_sup": np.exp(m.conf_int()[1]),
                         "p_valor": m.pvalues}).round(3)
    print("\nOdds ratios (cuántas veces se multiplica la chance por cada unidad):")
    print(odds.to_string())
    prob = m.predict(datos)
    auc = roc_auc_score(datos.democracia, prob)
    predicho = (prob >= 0.5).astype(int)
    acierto = (predicho == datos.democracia).mean()
    print(f"\nPseudo R² McFadden = {m.prsquared:.3f} · AUC = {auc:.3f} · acierto con corte 0,5 = {acierto:.1%}")
    print("Matriz de confusión (filas real, columnas predicho):")
    print(pd.crosstab(datos.democracia, predicho, rownames=["real"], colnames=["predicho"]).to_string())
    print("\nVIF:")
    print(vif(datos, xs).to_string())

    odds.to_csv(SALIDA / "logistica_democracia_2021.csv", index_label="variable")
    pd.DataFrame({"democracia_real": datos.democracia, "prob_predicha": prob.round(3)}).sort_values(
        "prob_predicha").to_csv(SALIDA / "logistica_democracia_2021_probabilidades.csv", index_label="iso3")
    return m


def ejemplo_panel(panel):
    titulo("3. PANEL 2011-2024: felicidad ~ log PIB per cápita")
    datos = panel[["iso3", "anio", "felicidad", "log_pib_pc_ppp"]].dropna()
    print(f"Observaciones país-año: {len(datos)} · países: {datos.iso3.nunique()} · "
          f"años: {datos.anio.min()}-{datos.anio.max()}")
    grupos = datos.iso3
    # Errores agrupados por país: las observaciones del mismo país no son independientes.
    pooled = smf.ols("felicidad ~ log_pib_pc_ppp + C(anio)", data=datos).fit(
        cov_type="cluster", cov_kwds={"groups": grupos})
    fe = smf.ols("felicidad ~ log_pib_pc_ppp + C(anio) + C(iso3)", data=datos).fit(
        cov_type="cluster", cov_kwds={"groups": grupos})
    for nombre, m in [("Agrupado (compara países)", pooled), ("Efectos fijos (dentro de cada país)", fe)]:
        print(f"{nombre:38s} coef log PIB = {m.params['log_pib_pc_ppp']:.3f} "
              f"(error {m.bse['log_pib_pc_ppp']:.3f}, p = {m.pvalues['log_pib_pc_ppp']:.3f})")
    print(f"El modelo agrupado compara países ricos con pobres; el de efectos fijos usa solo\n"
          f"cómo cambia cada país contra sí mismo. Su error es {fe.bse['log_pib_pc_ppp'] / pooled.bse['log_pib_pc_ppp']:.0f} veces mayor porque\n"
          f"el PIB per cápita de un país se mueve poco en 14 años: hay menos variación para aprender.")


def main():
    SALIDA.mkdir(exist_ok=True)
    panel, corte = preparar()
    ejemplo_lineal(corte)
    ejemplo_logistico(corte)
    ejemplo_panel(panel)
    print(f"\nTablas guardadas en {SALIDA}")


if __name__ == "__main__":
    main()
