"""Agrupamiento k-means de las 375 ciudades de más de 2 millones con los indicadores de los cuatro enfoques.

Corre dos especificaciones, cada una en su carpeta de datos/:
  completo  los 31 indicadores con datos suficientes. Muchos son del país (gobernanza, Gini, tugurios,
            saneamiento, migrantes), así que los grupos repiten las grandes regiones del mundo.
  urbano    solo los indicadores que cambian entre ciudades del mismo país (al menos el 25% de su
            varianza está dentro de los países). Agrupa por forma urbana, metabolismo y exposición,
            sin importar el país. Es la que sirve para comparar ciudades. Deja afuera el reporte a CDP
            (es binario y de gobernanza, no de forma urbana). Como los indicadores urbanos casi no se
            correlacionan entre sí, primero los resume en componentes principales (los que superan al
            azar según el análisis paralelo de Horn) y agrupa sobre esos componentes, para que el ruido
            de 17 indicadores sueltos no tape la estructura.

Qué hace, en orden:
  1. Lee los 33 indicadores de enfoques_urbanos/datos/indicadores_enfoques.csv y deja afuera los que
     faltan en más del 40% de las ciudades (muertes por PM2,5 y vivienda baja en zona costera baja).
     En la especificación urbana deja también afuera los que casi no cambian dentro de cada país.
  2. Completa los datos faltantes con la mediana del país y, si el país no tiene, con la de la región.
  3. Recorta cada indicador en los percentiles 2,5 y 97,5 (k-means es muy sensible a valores extremos),
     lo pasa a z y lo multiplica por su sentido, así que más alto siempre es más crítico.
  4. Pondera para que cada enfoque pese lo mismo: cada indicador se divide por la raíz de la cantidad de
     indicadores de su enfoque. Sin esto, la gobernanza (8 indicadores casi iguales entre sí) dominaría.
  5. Prueba k de 2 a 10 con 50 arranques cada uno y guarda inercia (codo), silueta, Calinski-Harabasz
     y Davies-Bouldin.
  6. Mide la estabilidad de cada k: 100 remuestreos bootstrap, y el índice de Rand ajustado entre el
     agrupamiento del remuestreo y el de la muestra completa.
  7. Elige k: el de mejor silueta entre los que tienen estabilidad media de 0,75 o más y al menos 3 grupos
     (se puede fijar con la variable de entorno KMEANS_K).
  8. Describe cada grupo: promedio de cada enfoque y de cada indicador, ciudades, regiones, puntaje del
     scorecard, y las ciudades más típicas (las más cerca del centro).
  9. Calcula dos componentes principales para dibujar el mapa de las ciudades.

uso (desde etl/): python clusters_ciudades/kmeans_ciudades.py
"""

import os

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (adjusted_rand_score, calinski_harabasz_score, davies_bouldin_score,
                             silhouette_samples, silhouette_score)

AQUI = os.path.dirname(os.path.abspath(__file__))
ETL = os.path.dirname(AQUI)
ENF = os.path.join(ETL, 'enfoques_urbanos', 'datos')
SALIDA = os.path.join(AQUI, 'datos')

FALTANTES_MAX = 0.40     # se descarta un indicador que falta en más de este porcentaje de ciudades
K_MIN, K_MAX = 2, 10
ARRANQUES = 50
REMUESTREOS = 100
ESTABILIDAD_MIN = 0.75
SEMILLA = 2026
DENTRO_PAIS_MIN = 0.25   # especificación urbana: parte mínima de la varianza que está dentro de los países

ENFOQUE_CORTO = {'Ecología política urbana': 'epu', 'Vulnerabilidad socio-espacial': 'vse',
                 'Metabolismo urbano': 'mu', 'Planificación y gobernanza': 'pg'}


def varianza_dentro_pais(ind, c):
    x = ind[[c, 'iso3']].dropna()
    tot = x[c].var(ddof=0)
    return float((x[c] - x.groupby('iso3')[c].transform('mean')).pow(2).mean() / tot) if tot else 0.0


def preparar(espec):
    ind = pd.read_csv(os.path.join(ENF, 'indicadores_enfoques.csv'))
    idx = pd.read_csv(os.path.join(ENF, 'indices_enfoques.csv'))
    dic = pd.read_csv(os.path.join(ENF, 'diccionario_indicadores.csv'))
    ind = ind.merge(idx[['id', 'region', 'pais', 'puntaje_pct', 'indice_amenaza', 'amenaza_principal', 'tipo_nombre',
                         'indice_epu', 'indice_vse', 'indice_mu', 'indice_pg', 'indice_viv']], on='id', how='left')

    falta = ind[dic.indicador].isna().mean()
    dic['varianza_dentro_pais'] = dic.indicador.map(lambda c: round(varianza_dentro_pais(ind, c), 3))
    dic['faltantes'] = dic.indicador.map(falta).round(3)
    ok = dic.faltantes <= FALTANTES_MAX
    if espec == 'urbano':
        ok &= (dic.varianza_dentro_pais >= DENTRO_PAIS_MIN) & (dic.indicador != 'reporta_cdp')
    usados = dic[ok].copy()
    descartados = dic[~ok].indicador.tolist()

    X = ind[usados.indicador].astype(float).copy()
    imputados = int(X.isna().sum().sum())
    for c in X:
        X[c] = X[c].fillna(X.groupby(ind.iso3)[c].transform('median'))
        X[c] = X[c].fillna(X.groupby(ind.region)[c].transform('median'))
        X[c] = X[c].fillna(X[c].median())

    Z = pd.DataFrame(index=X.index)
    for _, r in usados.iterrows():
        x = X[r.indicador]
        if x.nunique() > 2:   # los binarios (reporta_cdp) no se recortan
            x = x.clip(x.quantile(0.025), x.quantile(0.975))
        z = (x - x.mean()) / x.std(ddof=0)
        Z[r.indicador] = r.sentido * z.fillna(0)

    n_enfoque = usados.enfoque.value_counts()
    peso = usados.set_index('indicador').enfoque.map(lambda e: 1 / np.sqrt(n_enfoque[e]))
    W = Z * peso
    return ind, dic, usados, descartados, imputados, Z, W, peso


def elegir_k(W):
    rng = np.random.default_rng(SEMILLA)
    filas, modelos = [], {}
    for k in range(K_MIN, K_MAX + 1):
        km = KMeans(n_clusters=k, n_init=ARRANQUES, random_state=SEMILLA).fit(W)
        modelos[k] = km
        ari = []
        for _ in range(REMUESTREOS):
            m = rng.choice(len(W), len(W), replace=True)
            kb = KMeans(n_clusters=k, n_init=10, random_state=int(rng.integers(1e9))).fit(W.iloc[m])
            ari.append(adjusted_rand_score(km.labels_, kb.predict(W)))
        tam = np.bincount(km.labels_)
        filas.append({'k': k, 'inercia': round(km.inertia_, 1), 'silueta': round(silhouette_score(W, km.labels_), 3),
                      'calinski_harabasz': round(calinski_harabasz_score(W, km.labels_), 1),
                      'davies_bouldin': round(davies_bouldin_score(W, km.labels_), 3),
                      'estabilidad_ari_media': round(np.mean(ari), 3), 'estabilidad_ari_p10': round(np.quantile(ari, 0.1), 3),
                      'grupo_mas_chico': int(tam.min()), 'grupo_mas_grande': int(tam.max())})
    sel = pd.DataFrame(filas)
    if os.environ.get('KMEANS_K'):
        k = int(os.environ['KMEANS_K'])
    else:
        ok = sel[(sel.k >= 3) & (sel.estabilidad_ari_media >= ESTABILIDAD_MIN)]
        k = int((ok if len(ok) else sel[sel.k >= 3]).sort_values('silueta', ascending=False).k.iloc[0])
    sel['elegido'] = sel.k == k
    return sel, modelos[k], k


def nombrar(perf):
    """Nombre corto de cada grupo según el enfoque en que más se aparta del promedio (z por enfoque)."""
    alto = {'epu': 'producción del riesgo', 'vse': 'vulnerabilidad', 'mu': 'presión metabólica', 'pg': 'déficit de gobernanza'}
    nombres = {}
    for g, r in perf.iterrows():
        z = r[[f'z_{e}' for e in alto]]
        if z.max() < 0.25:
            nombres[g] = 'Baja criticidad' if z.mean() < -0.25 else 'Perfil intermedio'
            continue
        top = [e[2:] for e in z.sort_values(ascending=False).index if z[e] >= 0.25][:2]
        nombres[g] = 'Alta ' + ' y '.join(alto[e] for e in top)
    vistos = {}
    for g, n in nombres.items():   # si dos grupos quedan con el mismo nombre, se numeran
        vistos[n] = vistos.get(n, 0) + 1
    cuenta = {}
    for g, n in nombres.items():
        if vistos[n] > 1:
            cuenta[n] = cuenta.get(n, 0) + 1
            nombres[g] = f'{n} ({cuenta[n]})'
    return nombres


# especificación urbana: cómo se nombra un grupo según sus dos indicadores más extremos
# (el z ya tiene el sentido aplicado: positivo = más crítico; primero el texto para z alto, después para z bajo)
ETIQUETA = {
    'sesgo_inundable_pob': ('crecimiento hacia lo inundable', 'crecimiento fuera de lo inundable'),
    'sesgo_inundable_constr': ('construcción hacia lo inundable', 'construcción fuera de lo inundable'),
    'pob_sin_verde': ('poco verde', 'mucho verde'), 'perdida_verde': ('pérdida de verde', 'ganancia de verde'),
    'limites_superados': ('límites ambientales superados', 'dentro de los límites ambientales'),
    'pib_pc_log': ('menos ingreso', 'más ingreso'), 'sin_hospital': ('menos acceso a hospitales', 'más acceso a hospitales'),
    'hacinamiento': ('hacinamiento', 'mucho espacio residencial'), 'vivienda_baja': ('vivienda baja extendida', 'vivienda en altura'),
    'co2_pc': ('mucho CO2 por habitante', 'poco CO2 por habitante'), 'pm25_pc': ('mucho PM2,5 por habitante', 'poco PM2,5 por habitante'),
    'residuos_pc': ('muchas emisiones de residuos', 'pocas emisiones de residuos'),
    'construido_pc': ('ciudad extendida', 'ciudad compacta'),
    'agua_subterranea': ('estrés de agua subterránea', 'sin estrés de agua subterránea'),
    'agua_superficial': ('estrés de agua superficial', 'sin estrés de agua superficial'),
    'infra_flujos': ('poca infraestructura', 'mucha infraestructura'), 'reporta_cdp': ('no reporta a CDP', 'reporta a CDP'),
    'expansion_suelo': ('expansión del suelo', 'crecimiento compacto'),
}


def analisis_paralelo(Z, repeticiones=200):
    """Cantidad de componentes cuyo autovalor supera el percentil 95 de los de datos al azar del mismo tamaño."""
    real = np.sort(np.linalg.eigvalsh(np.corrcoef(Z.values.T)))[::-1]
    rng = np.random.default_rng(SEMILLA)
    azar = np.array([np.sort(np.linalg.eigvalsh(np.corrcoef(rng.standard_normal(Z.shape).T)))[::-1]
                     for _ in range(repeticiones)])
    return max(2, int(np.argmax(real <= np.quantile(azar, 0.95, axis=0))))


def nombrar_urbano(perf, Z, grupo):
    medias = Z.groupby(grupo).mean()
    familia = {'sesgo_inundable_pob': 'inundable', 'sesgo_inundable_constr': 'inundable', 'construido_pc': 'espacio',
               'hacinamiento': 'espacio', 'co2_pc': 'emisiones', 'pm25_pc': 'emisiones', 'residuos_pc': 'emisiones',
               'agua_subterranea': 'agua', 'agua_superficial': 'agua'}
    nombres = {}
    for g in perf.index:
        m = medias.loc[g]
        top, vistas = [], set()
        for c in m.abs().sort_values(ascending=False).index:   # dos indicadores de familias distintas
            f = familia.get(c, c)
            if f not in vistas:
                top.append(c)
                vistas.add(f)
            if len(top) == 2:
                break
        partes = [ETIQUETA.get(c, (c, c))[0 if m[c] > 0 else 1] for c in top]
        n = ' y '.join(partes)
        nombres[g] = n[0].upper() + n[1:]
    return nombres


def correr(espec):
    salida = os.path.join(SALIDA, espec)
    os.makedirs(salida, exist_ok=True)
    ind, dic, usados, descartados, imputados, Z, W, peso = preparar(espec)
    componentes = None
    if espec == 'urbano':   # se agrupa sobre los componentes principales que superan al azar
        componentes = analisis_paralelo(Z)
        W = pd.DataFrame(PCA(n_components=componentes, random_state=SEMILLA).fit_transform(Z),
                         columns=[f'cp{i + 1}' for i in range(componentes)])
    sel, km, k = elegir_k(W)

    # se ordenan los grupos de menor a mayor criticidad media, así el número tiene sentido
    crit = pd.Series(W.values.sum(axis=1)).groupby(km.labels_).mean().sort_values()
    orden = {g: i + 1 for i, g in enumerate(crit.index)}
    grupo = pd.Series(km.labels_).map(orden).values

    pca = PCA(n_components=2, random_state=SEMILLA).fit(Z if espec == 'urbano' else W)
    pc = pca.transform(Z if espec == 'urbano' else W)
    dist = np.linalg.norm(W.values - km.cluster_centers_[km.labels_], axis=1)

    zenf = pd.DataFrame({f'z_{ENFOQUE_CORTO[e]}': Z[usados[usados.enfoque == e].indicador].mean(axis=1)
                         for e in ENFOQUE_CORTO})
    base = pd.concat([ind[['id', 'nombre', 'pais', 'iso3', 'region', 'pob', 'puntaje_pct', 'indice_amenaza',
                           'amenaza_principal', 'tipo_nombre', 'indice_viv']], zenf], axis=1)
    base['grupo'] = grupo
    base['silueta_ciudad'] = silhouette_samples(W, km.labels_).round(3)
    base['distancia_centro'] = dist.round(3)
    base['pc1'], base['pc2'] = pc[:, 0].round(3), pc[:, 1].round(3)

    perf = base.groupby('grupo').agg(ciudades=('id', 'size'), poblacion_millones=('pob', lambda x: round(x.sum() / 1e6, 1)),
                                     z_epu=('z_epu', 'mean'), z_vse=('z_vse', 'mean'), z_mu=('z_mu', 'mean'),
                                     z_pg=('z_pg', 'mean'), indice_viv=('indice_viv', 'median'),
                                     amenaza=('indice_amenaza', 'median'), puntaje_scorecard=('puntaje_pct', 'median'),
                                     silueta_media=('silueta_ciudad', 'mean')).round(3)
    nombres = nombrar(perf) if espec == 'completo' else nombrar_urbano(perf, Z, grupo)
    perf.insert(0, 'nombre', perf.index.map(nombres))
    base['grupo_nombre'] = base.grupo.map(nombres)

    tip = base.sort_values('distancia_centro').groupby('grupo').head(6)
    perf['ciudades_tipicas'] = tip.groupby('grupo').nombre.apply(lambda s: ', '.join(s))
    reg = base.groupby('grupo').region.agg(lambda s: '; '.join(f'{r} {n}' for r, n in s.value_counts().head(3).items()))
    perf['regiones_principales'] = reg
    perf.to_csv(os.path.join(salida, 'perfil_grupos.csv'))

    ind_g = Z.groupby(grupo).mean().T.round(3)
    ind_g.columns = [f'grupo_{c}' for c in ind_g.columns]
    ind_g.insert(0, 'enfoque', usados.set_index('indicador').enfoque)
    ind_g.insert(1, 'peso', peso.round(3))
    ind_g.index.name = 'indicador'
    ind_g.to_csv(os.path.join(salida, 'perfil_indicadores.csv'))

    pd.crosstab(base.region, base.grupo_nombre, margins=True, margins_name='Total').to_csv(os.path.join(salida, 'region_por_grupo.csv'))
    comp = pd.crosstab(base.tipo_nombre, base.grupo_nombre)
    comp.to_csv(os.path.join(salida, 'comparacion_tipologia_enfoques.csv'))

    base.sort_values(['grupo', 'distancia_centro']).to_csv(os.path.join(salida, 'asignacion_ciudades.csv'), index=False)
    sel.to_csv(os.path.join(salida, 'seleccion_k.csv'), index=False)
    pd.DataFrame({'componente': ['pc1', 'pc2'], 'varianza_explicada': pca.explained_variance_ratio_.round(3)}).join(
        pd.DataFrame(pca.components_, columns=(Z if espec == 'urbano' else W).columns).round(3)).to_csv(os.path.join(salida, 'componentes_principales.csv'), index=False)

    print(f'[{espec}] {len(W)} ciudades, {Z.shape[1]} indicadores (descartados: {", ".join(descartados)}; '
          f'{imputados} datos imputados); k={k}, silueta {sel[sel.elegido].silueta.iloc[0]:.2f}, '
          f'estabilidad {sel[sel.elegido].estabilidad_ari_media.iloc[0]:.2f}; '
          f'ARI con la tipología de enfoques {adjusted_rand_score(base.tipo_nombre.fillna("-"), base.grupo):.2f}')
    for g, r in perf.iterrows():
        print(f'  {g}. {r.nombre}: {r.ciudades} ciudades; {r.regiones_principales}')
    e = sel[sel.elegido].iloc[0]
    return {'especificacion': espec, 'indicadores': Z.shape[1], 'componentes_principales': componentes or '', 'k': k, 'silueta': e.silueta,
            'estabilidad_ari_media': e.estabilidad_ari_media, 'datos_imputados': imputados,
            'varianza_pc1_pc2': round(float(pca.explained_variance_ratio_.sum()), 3),
            'ari_con_tipologia_enfoques': round(adjusted_rand_score(base.tipo_nombre.fillna('-'), base.grupo), 3),
            'ari_con_region': round(adjusted_rand_score(base.region, base.grupo), 3),
            'grupos': ' | '.join(f'{g}. {r.nombre} ({r.ciudades})' for g, r in perf.iterrows())}


def main():
    resumen = []
    for espec in ('completo', 'urbano'):
        r = correr(espec)
        resumen.append(r)
    pd.DataFrame(resumen).to_csv(os.path.join(SALIDA, 'resumen_especificaciones.csv'), index=False)
    # el diccionario dice qué indicadores entraron en cada especificación
    _, dic, *_ = preparar('completo')
    _, _, urb, *_ = preparar('urbano')
    dic['en_completo'] = dic.faltantes <= FALTANTES_MAX
    dic['en_urbano'] = dic.indicador.isin(urb.indicador)
    dic[['indicador', 'enfoque', 'nombre', 'sentido', 'faltantes', 'varianza_dentro_pais', 'en_completo', 'en_urbano']].to_csv(
        os.path.join(SALIDA, 'indicadores_usados.csv'), index=False)


if __name__ == '__main__':
    main()
