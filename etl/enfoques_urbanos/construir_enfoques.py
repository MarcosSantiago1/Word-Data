"""Cuatro enfoques teóricos del riesgo urbano medidos en las 375 ciudades de más de 2 millones.

Enfoques (ver GUIA_ENFOQUES_URBANOS.md y diccionario_indicadores.csv):
  1. Ecología política urbana   -> índice de producción del riesgo
  2. Vulnerabilidad socio-espacial -> índice de vulnerabilidad socio-espacial
       (con un subíndice de precariedad habitacional: tugurios, saneamiento, hacinamiento, vivienda baja)
  3. Metabolismo urbano          -> índice de presión metabólica
  4. Planificación y gobernanza  -> índice de déficit de gobernanza
En los cuatro, más alto = peor (más riesgo producido, más vulnerabilidad, más presión, menos gobernanza).

Lee (todo dentro de etl/):
  riesgo_ciudades_mundo/datos/ghsl_ciudades.csv, amenaza_capacidad_mundo.csv, indicadores_pais.csv
  riesgo_ciudades_mundo/crudos/ghsl/csv/GHS_UCDB_THEME_*.csv   (los baja riesgo_ciudades_mundo/bajar_ghsl.py)
  riesgo_ciudades_mundo/crudos/cdp/reporting_2023.csv
  API del Banco Mundial: tugurios (EN.POP.SLUM.UR.ZS) y saneamiento urbano (SH.STA.BASS.UR.ZS), copia en crudos/
Escribe en enfoques_urbanos/datos/:
  indicadores_enfoques.csv   una fila por ciudad, valor crudo de cada indicador
  indices_enfoques.csv       una fila por ciudad, los 4 índices (0-100), cobertura, tipología, amenaza y puntaje
  diccionario_indicadores.csv  qué mide cada indicador, enfoque, sentido, fuente, fundamento y referencia
  consistencia_indices.csv   alfa de Cronbach y correlación ítem-resto de cada indicador
  correlaciones.csv          correlaciones (Spearman) entre índices, amenaza y puntaje del scorecard (y evidencia pública de las 90)
  regresiones.csv            regresión estandarizada del puntaje y de la evidencia pública sobre los 4 índices y la amenaza
  tipologias.csv             perfil medio de cada tipo de ciudad (k-medias sobre los 4 índices)
  resumen_region.csv         mediana de cada índice por región
  cdp_ciudades.csv           ciudades que reportaron a CDP 2023 (unión por ubicación, para revisar)

uso (desde etl/): python enfoques_urbanos/construir_enfoques.py
"""
import os
import shutil
import sys
import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import vivienda_municipal   # noqa: E402  vivienda informal por municipio (Brasil, Colombia, CABA)
ETL = os.path.dirname(AQUI)
MUNDO = os.path.join(ETL, 'riesgo_ciudades_mundo')
GHSL = os.path.join(MUNDO, 'crudos', 'ghsl', 'csv')
SALIDA = os.path.join(AQUI, 'datos')

TEMAS = ['GHSL', 'EXPOSURE', 'SOCIOECONOMIC', 'EMISSIONS', 'GREENNESS', 'HEALTH', 'NATURAL_SYSTEMS', 'WATER',
         'SDG', 'INFRASTRUCTURES', 'CLIMATE']
ENFOQUES = {
    'epu': ('Ecología política urbana', 'Producción del riesgo'),
    'vse': ('Vulnerabilidad socio-espacial', 'Vulnerabilidad socio-espacial'),
    'mu': ('Metabolismo urbano', 'Presión metabólica'),
    'pg': ('Planificación y gobernanza', 'Déficit de gobernanza'),
}
MIN_COBERTURA = 0.6   # un índice se calcula si la ciudad tiene al menos el 60 % de sus indicadores

G = 'GHSL UCDB R2024A (Comisión Europea, JRC), tema '
REF = {
    'swy': 'Swyngedouw y Heynen (2003); Heynen, Kaika y Swyngedouw (2006)',
    'col': 'Collins (2010); Ranganathan (2015); Pelling (2003)',
    'ej': 'Heynen, Kaika y Swyngedouw (2006); Gandy (2004)',
    'cut': 'Cutter, Boruff y Shirley (2003)',
    'par': 'Wisner, Blaikie, Cannon y Davis (2004)',
    'adg': 'Adger (2006); Birkmann (2006)',
    'wol': 'Wolman (1965); Kennedy, Cuddihy y Engel-Yan (2007)',
    'ken': 'Kennedy, Pincetl y Bunje (2011)',
    'gan': 'Gandy (2004)',
    'tie': 'Tierney (2012); Kaufmann, Kraay y Mastruzzi (2010)',
    'hea': 'Healey (1997); Roy (2009)',
    'pel': 'Pelling (2011); Meerow, Newell y Stults (2016)',
    'hab': 'UN-Habitat (2003); Roy (2005); Davis (2006)',
}

# Precariedad habitacional (vivienda informal o precaria): subíndice dentro de la vulnerabilidad socio-espacial.
# Sigue los criterios de tugurio de ONU-Hábitat: hacinamiento, saneamiento, durabilidad y exposición de la vivienda.
SUBINDICE_VIVIENDA = ['tugurios', 'sin_saneamiento', 'hacinamiento', 'vivienda_baja', 'baja_costera_baja']
CRUDOS = os.path.join(AQUI, 'crudos')
BM_VIVIENDA = {'EN.POP.SLUM.UR.ZS': 'tugurios_pct_urbana', 'SH.STA.BASS.UR.ZS': 'saneamiento_basico_urbano_pct'}

# código, enfoque, nombre, sentido (+1: más alto = peor), unidad, fuente, fundamento, referencia
DICC = [
    # 1. Ecología política urbana: el riesgo se produce con la urbanización y las relaciones de poder sobre el suelo y el ambiente
    ('sesgo_inundable_pob', 'epu', 'Sesgo de la urbanización hacia zonas inundables (población)', +1, 'puntos porcentuales',
     G + 'EXPOSURE y GHSL', 'Parte del crecimiento de población 1975-2025 que se instaló en la zona inundable de 100 años, menos la parte que ya vivía allí en 1975. Positivo: la ciudad creció hacia el peligro; el riesgo se produjo con la urbanización.', 'col'),
    ('sesgo_inundable_constr', 'epu', 'Sesgo de la urbanización hacia zonas inundables (superficie construida)', +1, 'puntos porcentuales',
     G + 'EXPOSURE y GHSL', 'Lo mismo con la superficie construida 1975-2025: dónde se invirtió en ciudad nueva.', 'col'),
    ('pob_sin_verde', 'epu', 'Población fuera de zonas de mucho verde', +1, '%',
     G + 'SDG', 'Parte de la población que no vive en áreas de alto verdor (2025). El verde urbano es un bien ambiental que se reparte con el poder de mercado y político.', 'ej'),
    ('perdida_verde', 'epu', 'Pérdida de verdor 2000-2025', +1, 'cambio del índice de verdor',
     G + 'GREENNESS', 'Caída del verdor medio del área construida entre 2000 y 2025: transformación del ambiente por la expansión urbana.', 'swy'),
    ('muertes_pm25', 'epu', 'Muertes prematuras por PM2,5', +1, 'por 100.000 habitantes',
     G + 'EMISSIONS', 'Muertes prematuras atribuibles a PM2,5 (2020) por 100.000 habitantes: el daño ambiental que la ciudad reparte entre su población.', 'ej'),
    ('limites_superados', 'epu', 'Límites del sistema Tierra superados', +1, 'cantidad (de 9)',
     G + 'NATURAL_SYSTEMS', 'Cantidad máxima de límites ambientales seguros y justos (agua, nutrientes, biodiversidad, aire, calor húmedo, mar) que se superan en el centro urbano.', 'swy'),
    ('gini', 'epu', 'Desigualdad del ingreso (Gini del país)', +1, 'índice 0-100',
     'Banco Mundial (SI.POV.GINI), dato más reciente', 'Concentración del ingreso como aproximación a la asimetría de poder que decide quién ocupa el suelo seguro y quién el expuesto.', 'swy'),

    # 2. Vulnerabilidad socio-espacial: desigualdades sociales y territoriales que condicionan exposición y recuperación
    ('idh_bajo', 'vse', 'Déficit de desarrollo humano subnacional', +1, '1 - IDH',
     G + 'SOCIOECONOMIC', 'Uno menos el IDH subnacional (2020) de la región donde está la ciudad: salud, educación e ingreso.', 'cut'),
    ('escolaridad', 'vse', 'Años promedio de escolaridad', -1, 'años',
     G + 'SOCIOECONOMIC', 'Años de escolaridad de los adultos (2020). La educación mejora el acceso a la alerta y la recuperación.', 'cut'),
    ('pib_pc_log', 'vse', 'PIB por habitante del centro urbano (log)', -1, 'log10 USD PPA',
     G + 'SOCIOECONOMIC', 'PIB por habitante (2020, logaritmo): recursos para absorber pérdidas y reconstruir.', 'adg'),
    ('brecha_genero', 'vse', 'Brecha de género en desarrollo humano', +1, '|1 - IDG|',
     G + 'SOCIOECONOMIC', 'Distancia del índice de desarrollo de género a la paridad (2020). Las desigualdades de género agravan la vulnerabilidad.', 'par'),
    ('sin_hospital', 'vse', 'Población sin acceso a hospital', +1, '%',
     G + 'HEALTH', 'Parte de la población sin acceso a un hospital (2025): capacidad de respuesta sanitaria en el territorio.', 'par'),
    ('tugurios', 'vse', 'Población en tugurios o asentamientos informales (municipio donde hay censo; si no, país)', +1, '%',
     'Censos y mediciones municipales (IBGE 2022, DANE 2018, RENABAP 2023 + INDEC 2022, CONEVAL 2020) o, si no hay, ONU-Hábitat vía Banco Mundial (EN.POP.SLUM.UR.ZS)', 'Hogares sin al menos una de estas condiciones: agua mejorada, saneamiento mejorado, espacio suficiente, vivienda durable o tenencia segura (ODS 11.1.1). En 12 ciudades latinoamericanas se usa el dato oficial del municipio (favelas, déficit habitacional, barrios populares o carencia de calidad y espacios de la vivienda; ver vivienda_municipal.csv), que no es comparable entre países. La vivienda informal concentra exposición y dificulta la recuperación.', 'hab'),
    ('sin_saneamiento', 'vse', 'Población urbana sin saneamiento básico (país)', +1, '% de la población urbana',
     'OMS/UNICEF JMP vía Banco Mundial (SH.STA.BASS.UR.ZS), dato más reciente', 'Parte de la población urbana sin un baño mejorado propio: uno de los criterios de tugurio y un factor de riesgo sanitario tras inundaciones.', 'hab'),
    ('hacinamiento', 'vse', 'Volumen residencial construido por habitante', -1, 'm3 por habitante',
     G + 'GHSL', 'Volumen de edificios residenciales (2020) dividido por la población: poco volumen por persona indica hacinamiento, otro criterio de tugurio. Lo miden satélites, así que vale para la ciudad y no solo para el país.', 'hab'),
    ('vivienda_baja', 'vse', 'Población en vivienda residencial baja (1-2 pisos)', +1, '%',
     G + 'GHSL', 'Parte de la población en tejido residencial de 1 a 2 pisos (2020). Aproxima la vivienda autoconstruida y más frágil; es una aproximación gruesa (también incluye suburbios ricos).', 'par'),
    ('baja_costera_baja', 'vse', 'Población en vivienda baja dentro de la zona costera baja', +1, '%',
     G + 'EXPOSURE', 'Parte de la población que vive en tejido residencial de 1-2 pisos por debajo de 5 m sobre el nivel del mar (2020): el cruce entre tipo de vivienda y exposición.', 'cut'),
    ('migrantes', 'vse', 'Población migrante (país)', +1, '% de la población',
     'Banco Mundial (SM.POP.TOTL.ZS)', 'Stock de migrantes internacionales: barreras de idioma, derechos y redes que suelen aumentar la vulnerabilidad.', 'cut'),

    # 3. Metabolismo urbano: flujos de energía, agua, materiales y residuos
    ('co2_pc', 'mu', 'Emisiones de CO2 por habitante', +1, 't CO2 por habitante y año',
     G + 'EMISSIONS', 'CO2 de todos los sectores (2024) por habitante: el flujo de energía fósil que atraviesa la ciudad.', 'ken'),
    ('pm25_pc', 'mu', 'Emisiones de PM2,5 por habitante', +1, 'kg por habitante y año',
     G + 'EMISSIONS', 'PM2,5 emitido (2024) por habitante: el residuo del metabolismo que vuelve como contaminación.', 'wol'),
    ('residuos_pc', 'mu', 'Emisiones de gases del sector residuos por habitante', +1, 't CO2e por habitante y año',
     G + 'EMISSIONS', 'Gases de efecto invernadero del sector residuos (2024) por habitante: el cierre (o no) del ciclo de materiales.', 'ken'),
    ('construido_pc', 'mu', 'Superficie construida por habitante', +1, 'm2 por habitante',
     G + 'GHSL', 'Stock material construido por habitante (2025): materiales acumulados y suelo transformado.', 'wol'),
    ('agua_subterranea', 'mu', 'Límite de agua subterránea superado', +1, '0 o más',
     G + 'NATURAL_SYSTEMS', 'Si la extracción supera el límite seguro de agua subterránea (2025).', 'gan'),
    ('agua_superficial', 'mu', 'Límite de agua superficial superado', +1, '0 o más',
     G + 'NATURAL_SYSTEMS', 'Si el uso supera el límite seguro de agua superficial (2025).', 'gan'),
    ('infra_flujos', 'mu', 'Infraestructura de agua, energía y residuos', -1, 'índice 0-1 (promedio)',
     G + 'INFRASTRUCTURES', 'Promedio del índice espacial de infraestructura crítica de agua, energía y residuos (2020): la red que gestiona los flujos.', 'ken'),

    # 4. Planificación y gobernanza: instituciones y reglas que producen el espacio y gestionan el riesgo
    ('efectividad_gob', 'pg', 'Efectividad del gobierno (país)', -1, 'puntaje WGI (-2,5 a 2,5)',
     'Banco Mundial, Worldwide Governance Indicators', 'Calidad de los servicios públicos y de la aplicación de políticas.', 'tie'),
    ('calidad_regulatoria', 'pg', 'Calidad regulatoria (país)', -1, 'puntaje WGI',
     'Banco Mundial, Worldwide Governance Indicators', 'Capacidad de dictar y aplicar regulaciones, entre ellas las de uso del suelo y construcción.', 'tie'),
    ('estado_derecho', 'pg', 'Estado de derecho (país)', -1, 'índice 0-100',
     'Banco Mundial, Worldwide Governance Indicators', 'Cumplimiento de contratos, derechos de propiedad y normas.', 'tie'),
    ('control_corrupcion', 'pg', 'Control de la corrupción (país)', -1, 'índice 0-100',
     'Banco Mundial, Worldwide Governance Indicators', 'La corrupción debilita los códigos de construcción y el control del uso del suelo.', 'tie'),
    ('voz_rendicion', 'pg', 'Voz y rendición de cuentas (país)', -1, 'puntaje WGI',
     'Banco Mundial, Worldwide Governance Indicators', 'Participación y control ciudadano sobre las decisiones de planificación.', 'hea'),
    ('sociedad_civil', 'pg', 'Fortaleza de la sociedad civil (país)', -1, 'índice 0-1',
     'V-Dem, índice de participación de la sociedad civil', 'Organización social que demanda y vigila la gestión del riesgo.', 'pel'),
    ('reporta_cdp', 'pg', 'La ciudad reporta su gestión climática (CDP-ICLEI 2023)', -1, '0 o 1',
     'CDP-ICLEI Cities 2023 (lista de ciudades que reportaron)', 'Transparencia y capacidad técnica del gobierno local: publicar su evaluación de riesgo y su plan.', 'pel'),
    ('expansion_suelo', 'pg', 'Consumo de suelo sobre crecimiento de población (ODS 11.3.1)', +1, 'razón',
     G + 'SDG', 'Razón entre la tasa de consumo de suelo y la de crecimiento de población 2000-2020. Mayor a 1: la ciudad se extiende más rápido que su población (expansión no planificada o especulativa).', 'hea'),
]


def leer_tema(t, cols):
    f = os.path.join(GHSL, f'GHS_UCDB_THEME_{t}_GLOBE_R2024A.csv')
    with open(f, 'rb') as h:
        cod = 'utf-8-sig' if h.read(3) == b'\xef\xbb\xbf' else 'latin-1'   # algunos temas traen BOM UTF-8, otros vienen en Latin-1
    cab = pd.read_csv(f, nrows=0, encoding=cod).columns
    usar = ['ID_UC_G0'] + [c for c in cols if c in cab]
    return pd.read_csv(f, usecols=usar, encoding=cod, encoding_errors='replace', low_memory=False)


def num(s):
    return pd.to_numeric(s, errors='coerce')


def cdp_por_ubicacion(ciudades):
    """Une la lista de CDP 2023 con las ciudades por cercanía (<= 20 km) y población (>= 300.000)."""
    f = os.path.join(MUNDO, 'crudos', 'cdp', 'reporting_2023.csv')
    if not os.path.exists(f):
        return pd.DataFrame(columns=['id', 'cdp_org', 'cdp_nombre', 'cdp_km'])
    r = pd.read_csv(f)
    r = r[r['City Location'].notna()].copy()
    xy = r['City Location'].str.extract(r'POINT \(([-\d.]+) ([-\d.]+)\)').astype(float)
    r['lon'], r['lat'] = xy[0], xy[1]
    r['pob'] = num(r['Population'])
    r = r[r.pob >= 300000]
    filas = []
    for _, c in ciudades.iterrows():
        la1, lo1 = np.radians(c.lat), np.radians(c.lon)
        la2, lo2 = np.radians(r.lat.values), np.radians(r.lon.values)
        d = 6371 * 2 * np.arcsin(np.sqrt(np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2))
        if len(d) and d.min() <= 20:
            i = int(d.argmin())
            filas.append({'id': c.id, 'cdp_org': int(r.iloc[i]['Organization Number']), 'cdp_nombre': r.iloc[i]['Organization Name'], 'cdp_km': round(float(d[i]), 1)})
    return pd.DataFrame(filas, columns=['id', 'cdp_org', 'cdp_nombre', 'cdp_km'])


def vivienda_pais():
    """Tugurios y saneamiento urbano por país (Banco Mundial). Guarda una copia en crudos/ y la usa si la API falla."""
    f = os.path.join(CRUDOS, 'vivienda_banco_mundial.csv')
    if not os.path.exists(f) or os.environ.get('ETL_REFRESCAR') == '1':
        try:
            import requests
            filas = {}
            for cod, col in BM_VIVIENDA.items():
                r = requests.get(f'https://api.worldbank.org/v2/country/all/indicator/{cod}',
                                 params={'format': 'json', 'per_page': 20000, 'date': '2005:2030'}, timeout=120)
                r.raise_for_status()
                for d in sorted(r.json()[1] or [], key=lambda d: d['date']):   # el último año con dato queda al final
                    if d['value'] is not None and len(d.get('countryiso3code') or '') == 3:
                        filas.setdefault(d['countryiso3code'], {'iso3': d['countryiso3code']})
                        filas[d['countryiso3code']][col] = d['value']
                        filas[d['countryiso3code']][col + '_anio'] = int(d['date'])
            os.makedirs(CRUDOS, exist_ok=True)
            pd.DataFrame(filas.values()).to_csv(f, index=False)
        except Exception as e:
            if not os.path.exists(f):
                raise
            print(f'  aviso: no se pudo actualizar tugurios y saneamiento ({e}); uso la copia guardada')
    return pd.read_csv(f)[['iso3'] + list(BM_VIVIENDA.values())]


def indicadores():
    c = pd.read_csv(os.path.join(MUNDO, 'datos', 'ghsl_ciudades.csv'))
    c = c[['id', 'nombre', 'iso3', 'pob', 'lat', 'lon', 'ID_UC_G0', 'modo_union']].copy()
    c['centro_urbano_compartido'] = c.ID_UC_G0.duplicated(keep=False)

    cols = ['GH_BUV_RES_2020', 'GH_POP_TOT_1975', 'GH_POP_TOT_2025', 'GH_BUS_TOT_1975', 'GH_BUS_TOT_2025', 'GH_BPC_TOT_2025', 'GH_BUT_P11_2020', 'GH_POP_TOT_2020',
            'EX_100_POP_1975', 'EX_100_POP_2025', 'EX_100_BUS_1975', 'EX_100_BUS_2025', 'EX_L05_P11_2020',
            'SC_SEC_HDI_2020', 'SC_SEC_SYT_2020', 'SC_GDP_AVG_2020', 'SC_SEC_GDI_2020',
            'EM_CO2_TOT_2024', 'EM_PM2_TOT_2024', 'EM_GHG_WAS_2024', 'EM_PM2_MOR_2020',
            'GR_AVG_GRN_2000', 'GR_AVG_GRN_2025', 'HL_SHP_HOS_2025', 'NS_ESB_MAX_2025', 'NS_ESB_GWA_2025', 'NS_ESB_SWA_2025',
            'WA_GWS_SAL_2025', 'SD_POP_HGR_2025', 'SD_LUE_LPR_2000_2020', 'IN_CIS_WAT_2020', 'IN_CIS_ENE_2020', 'IN_CIS_WAS_2020']
    t = None
    for tema in TEMAS:
        d = leer_tema(tema, cols)
        d = d.loc[:, ~d.columns.isin(t.columns.drop('ID_UC_G0'))] if t is not None else d
        t = d if t is None else t.merge(d, on='ID_UC_G0', how='outer')
    for k in t.columns:
        if k != 'ID_UC_G0' and k != 'WA_GWS_SAL_2025':
            t[k] = num(t[k])
    x = c.merge(t, on='ID_UC_G0', how='left')

    p = pd.read_csv(os.path.join(MUNDO, 'datos', 'indicadores_pais.csv'))
    x = x.merge(p[['iso3', 'gini', 'stock_migrantes_pct_poblacion', 'efectividad_gobierno', 'calidad_regulatoria',
                   'indice_estado_derecho_0_100', 'indice_control_corrupcion_0_100', 'voz_rendicion_cuentas',
                   'indice_sociedad_civil_0_1']], on='iso3', how='left')
    x = x.merge(vivienda_pais(), on='iso3', how='left')
    cdp = cdp_por_ubicacion(c)
    x = x.merge(cdp, on='id', how='left')

    pop25 = x.GH_POP_TOT_2025
    o = x[['id', 'nombre', 'iso3', 'pob', 'ID_UC_G0', 'centro_urbano_compartido']].copy()
    # 1. ecología política urbana
    dpop = x.GH_POP_TOT_2025 - x.GH_POP_TOT_1975
    dbus = x.GH_BUS_TOT_2025 - x.GH_BUS_TOT_1975
    o['sesgo_inundable_pob'] = np.where(dpop > 0, 100 * (x.EX_100_POP_2025 - x.EX_100_POP_1975) / dpop - 100 * x.EX_100_POP_1975 / x.GH_POP_TOT_1975, np.nan)
    o['sesgo_inundable_constr'] = np.where(dbus > 0, 100 * (x.EX_100_BUS_2025 - x.EX_100_BUS_1975) / dbus - 100 * x.EX_100_BUS_1975 / x.GH_BUS_TOT_1975, np.nan)
    o['pob_sin_verde'] = 100 - x.SD_POP_HGR_2025
    o['perdida_verde'] = x.GR_AVG_GRN_2000 - x.GR_AVG_GRN_2025
    o['muertes_pm25'] = 1e5 * x.EM_PM2_MOR_2020 / x.GH_POP_TOT_2020
    o['limites_superados'] = x.NS_ESB_MAX_2025
    o['gini'] = x.gini
    # 2. vulnerabilidad socio-espacial
    o['idh_bajo'] = 1 - x.SC_SEC_HDI_2020
    o['escolaridad'] = x.SC_SEC_SYT_2020
    o['pib_pc_log'] = np.log10(x.SC_GDP_AVG_2020.where(x.SC_GDP_AVG_2020 > 0))
    o['brecha_genero'] = (1 - x.SC_SEC_GDI_2020).abs()
    o['sin_hospital'] = 100 - x.HL_SHP_HOS_2025
    # tugurios: dato del municipio (censo oficial del país) donde existe; si no, el de ONU-Hábitat para el país
    mun = vivienda_municipal.por_ciudad()
    o = o.merge(mun[['id', 'tugurios_municipal']], on='id', how='left')
    o['tugurios'] = o.tugurios_municipal.fillna(pd.Series(x.tugurios_pct_urbana.values, index=o.index))
    o['tugurios_origen'] = np.where(o.tugurios_municipal.notna(), 'municipio', np.where(o.tugurios.notna(), 'país', ''))
    o = o.drop(columns='tugurios_municipal')
    o['sin_saneamiento'] = 100 - x.saneamiento_basico_urbano_pct
    o['hacinamiento'] = x.GH_BUV_RES_2020 / x.GH_POP_TOT_2020
    o['vivienda_baja'] = 100 * x.GH_BUT_P11_2020 / x.GH_POP_TOT_2020
    o['baja_costera_baja'] = 100 * x.EX_L05_P11_2020 / x.GH_POP_TOT_2020
    o['migrantes'] = x.stock_migrantes_pct_poblacion
    # 3. metabolismo urbano
    o['co2_pc'] = x.EM_CO2_TOT_2024 / pop25
    o['pm25_pc'] = 1000 * x.EM_PM2_TOT_2024 / pop25
    o['residuos_pc'] = x.EM_GHG_WAS_2024 / pop25
    o['construido_pc'] = x.GH_BPC_TOT_2025
    o['agua_subterranea'] = x.NS_ESB_GWA_2025
    o['agua_superficial'] = x.NS_ESB_SWA_2025
    o['infra_flujos'] = x[['IN_CIS_WAT_2020', 'IN_CIS_ENE_2020', 'IN_CIS_WAS_2020']].mean(axis=1)
    # 4. planificación y gobernanza
    o['efectividad_gob'] = x.efectividad_gobierno
    o['calidad_regulatoria'] = x.calidad_regulatoria
    o['estado_derecho'] = x.indice_estado_derecho_0_100
    o['control_corrupcion'] = x.indice_control_corrupcion_0_100
    o['voz_rendicion'] = x.voz_rendicion_cuentas
    o['sociedad_civil'] = x.indice_sociedad_civil_0_1
    o['reporta_cdp'] = x.cdp_org.notna().astype(float)
    o['expansion_suelo'] = x.SD_LUE_LPR_2000_2020.where(x.SD_LUE_LPR_2000_2020.abs() < 50)
    o = o.replace([np.inf, -np.inf], np.nan)
    return o, cdp


def cronbach(m):
    m = m.dropna(axis=1, how='all').dropna()
    k = m.shape[1]
    if k < 2 or len(m) < 10:
        return np.nan
    return k / (k - 1) * (1 - m.var(ddof=1).sum() / m.sum(axis=1).var(ddof=1))


def kmedias(X, k, semillas=20):
    mejor = None
    for s in range(semillas):
        rng = np.random.default_rng(s)
        C = X[rng.choice(len(X), k, replace=False)]
        for _ in range(200):
            et = ((X[:, None, :] - C[None]) ** 2).sum(-1).argmin(1)
            nuevo = np.array([X[et == j].mean(0) if (et == j).any() else C[j] for j in range(k)])
            if np.allclose(nuevo, C):
                break
            C = nuevo
        inercia = ((X - C[et]) ** 2).sum()
        if mejor is None or inercia < mejor[0]:
            mejor = (inercia, et, C)
    return mejor[1], mejor[2]


def silueta(X, et):
    D = np.sqrt(((X[:, None, :] - X[None]) ** 2).sum(-1))
    s = []
    for i in range(len(X)):
        propio = et == et[i]
        if propio.sum() < 2:
            s.append(0)
            continue
        a = D[i, propio].sum() / (propio.sum() - 1)
        b = min(D[i, et == j].mean() for j in set(et) if j != et[i])
        s.append((b - a) / max(a, b))
    return float(np.mean(s))


def main():
    os.makedirs(SALIDA, exist_ok=True)
    ind, cdp = indicadores()
    dic = pd.DataFrame(DICC, columns=['indicador', 'enfoque_cod', 'nombre', 'sentido', 'unidad', 'fuente', 'fundamento', 'ref'])
    dic['enfoque'] = dic.enfoque_cod.map(lambda e: ENFOQUES[e][0])
    dic['referencia'] = dic.ref.map(REF)
    dic['cobertura_ciudades'] = dic.indicador.map(lambda k: int(ind[k].notna().sum()))

    # estandarización: recorte al 2,5-97,5 %, z, sentido (+ = peor)
    Z = pd.DataFrame(index=ind.index)
    for _, r in dic.iterrows():
        v = ind[r.indicador]
        if v.dropna().nunique() > 2:   # las binarias no se recortan
            v = v.clip(v.quantile(0.025), v.quantile(0.975))
        sd = v.std()
        Z[r.indicador] = r.sentido * (v - v.mean()) / sd if sd and sd > 0 else np.nan

    idx = ind[['id', 'nombre', 'iso3', 'pob', 'centro_urbano_compartido']].copy()
    cons = []
    for e, (enf, nom) in ENFOQUES.items():
        ks = dic[dic.enfoque_cod == e].indicador.tolist()
        m = Z[ks]
        cob = m.notna().mean(axis=1)
        z = m.mean(axis=1).where(cob >= MIN_COBERTURA)
        idx[f'z_{e}'] = z.round(3)
        idx[f'indice_{e}'] = (100 * z.rank(pct=True)).round(1)
        idx[f'cobertura_{e}'] = (100 * cob).round(0)
        alfa = cronbach(m)
        for k in ks:
            resto = m.drop(columns=k).mean(axis=1)
            ok = m[k].notna() & resto.notna()
            rir = m[k][ok].rank().corr(resto[ok].rank()) if ok.sum() > 10 else np.nan   # Spearman sin scipy
            # robustez: cuánto cambia el orden de las ciudades si se saca este indicador
            sin = resto.where(m.drop(columns=k).notna().mean(axis=1) >= MIN_COBERTURA)
            ok2 = z.notna() & sin.notna()
            rob = z[ok2].rank().corr(sin[ok2].rank())
            cons.append({'enfoque': enf, 'indicador': k, 'alfa_cronbach_indice': round(alfa, 3), 'corr_item_resto': round(rir, 3),
                         'corr_indice_sin_este': round(rob, 3), 'ciudades': int(m[k].notna().sum())})

    # subíndice de precariedad habitacional (sus indicadores también cuentan dentro de la vulnerabilidad)
    mv = Z[SUBINDICE_VIVIENDA]
    cobv = mv.notna().mean(axis=1)
    zv = mv.mean(axis=1).where(cobv >= MIN_COBERTURA)
    idx['z_viv'] = zv.round(3)
    idx['indice_viv'] = (100 * zv.rank(pct=True)).round(1)
    idx['cobertura_viv'] = (100 * cobv).round(0)
    alfa_v = cronbach(mv)
    for k in SUBINDICE_VIVIENDA:
        resto = mv.drop(columns=k).mean(axis=1)
        ok = mv[k].notna() & resto.notna()
        sin = resto.where(mv.drop(columns=k).notna().mean(axis=1) >= MIN_COBERTURA)
        ok2 = zv.notna() & sin.notna()
        cons.append({'enfoque': 'Subíndice: precariedad habitacional', 'indicador': k, 'alfa_cronbach_indice': round(alfa_v, 3),
                     'corr_item_resto': round(mv[k][ok].rank().corr(resto[ok].rank()), 3),
                     'corr_indice_sin_este': round(zv[ok2].rank().corr(sin[ok2].rank()), 3), 'ciudades': int(mv[k].notna().sum())})

    mundo = pd.read_csv(os.path.join(MUNDO, 'datos', 'amenaza_capacidad_mundo.csv'))
    idx = idx.merge(mundo[['id', 'ciudad', 'pais', 'region', 'indice_amenaza', 'total_590', 'metodo', 'prioridad', 'amenaza_principal']], on='id', how='left')
    idx['puntaje_pct'] = (100 * idx.total_590 / 590).round(1)

    # tipología: k-medias sobre los 4 z, k entre 3 y 6 según la silueta
    zc = [f'z_{e}' for e in ENFOQUES]
    ok = idx[zc].notna().all(axis=1)
    X = idx.loc[ok, zc].values
    X = (X - X.mean(0)) / X.std(0)
    elegido = None
    for k in range(3, 7):
        et, C = kmedias(X, k)
        s = silueta(X, et)
        if elegido is None or s > elegido[0] + 0.01:
            elegido = (s, k, et, C)
    s, k, et, C = elegido
    idx.loc[ok, 'tipo'] = et
    perf = idx[ok].groupby('tipo')[[f'indice_{e}' for e in ENFOQUES] + ['indice_amenaza', 'puntaje_pct']].median()
    perf['ciudades'] = idx[ok].groupby('tipo').size()
    # nombre de cada tipo según los índices donde su mediana es alta (>= 62) o baja (<= 38)
    etiqueta = {'epu': 'riesgo producido por la expansión', 'vse': 'vulnerabilidad social', 'mu': 'metabolismo intensivo', 'pg': 'instituciones débiles'}
    nombres = {}
    for t, r in perf.iterrows():
        altos = [etiqueta[e] for e in ENFOQUES if r[f'indice_{e}'] >= 62]
        bajos = [e for e in ENFOQUES if r[f'indice_{e}'] <= 38]
        if altos:
            n = ' con '.join(altos) if len(altos) == 2 else ', '.join(altos)
        elif len(bajos) >= 3:
            n = 'baja criticidad en casi todos los enfoques'
        else:
            n = 'perfil intermedio'
        nombres[t] = n[0].upper() + n[1:]
    perf['tipo_nombre'] = perf.index.map(nombres)
    perf['ejemplos'] = [', '.join(idx[ok & (idx.tipo == t)].sort_values('pob', ascending=False).ciudad.head(6)) for t in perf.index]
    perf['silueta'] = round(s, 3)
    idx['tipo_nombre'] = idx.tipo.map(nombres)
    idx['tipo'] = idx.tipo.astype('Int64') + 1
    perf.index = perf.index.astype(int) + 1

    # correlaciones (Spearman) entre índices, amenaza y puntaje
    cc = [f'indice_{e}' for e in ENFOQUES] + ['indice_amenaza', 'puntaje_pct']
    cor = idx[cc].rank().corr().round(3)   # Spearman = Pearson sobre rangos
    mano = idx[idx.metodo.astype(str).str.startswith('A mano')]
    cor_mano = mano[cc].rank().corr().round(3) if len(mano) >= 10 else None

    # regresión lineal estandarizada del puntaje del scorecard sobre los 4 índices y la amenaza (mínimos cuadrados)
    def mco(df, y, xs):
        d = df[[y] + xs].dropna()
        Y = (d[y] - d[y].mean()) / d[y].std()
        X = (d[xs] - d[xs].mean()) / d[xs].std()
        X = np.column_stack([np.ones(len(X)), X.values])
        b, *_ = np.linalg.lstsq(X, Y.values, rcond=None)
        e = Y.values - X @ b
        s2 = (e @ e) / (len(d) - X.shape[1])
        se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
        r2 = 1 - (e @ e) / ((Y.values - Y.values.mean()) @ (Y.values - Y.values.mean()))
        return [{'dependiente': y, 'variable': v, 'beta_estandarizado': round(b[i + 1], 3), 'error_estandar': round(se[i + 1], 3),
                 't': round(b[i + 1] / se[i + 1], 2), 'r2': round(r2, 3), 'n': len(d)} for i, v in enumerate(xs)]
    xs = [f'z_{e}' for e in ENFOQUES] + ['indice_amenaza']
    regs = mco(idx, 'puntaje_pct', xs)
    for r in regs:
        r['muestra'] = 'todas'
    if len(mano) >= 10:
        pass   # con 16 ciudades no alcanza para 5 variables; se informa solo la correlación
    # evidencia pública de gestión del riesgo (base de alta confianza, 90 ciudades): no depende del modelo del scorecard
    # se guarda una copia en entrada/ para que la actualización mensual (que trabaja sobre una copia de etl/) la encuentre
    ev_f = os.path.join(os.path.dirname(ETL), 'consultas', 'scorecard_undrr', 'alta_confianza', 'datos', 'resumen_ciudades.csv')
    ev_copia = os.path.join(AQUI, 'entrada', 'resumen_ciudades_90.csv')
    if os.path.exists(ev_f):
        os.makedirs(os.path.dirname(ev_copia), exist_ok=True)
        shutil.copyfile(ev_f, ev_copia)
    else:
        ev_f = ev_copia
    if os.path.exists(ev_f):
        ev = pd.read_csv(ev_f)[['id', 'con_evidencia', 'alta', 'fuentes']]
        e90 = idx.merge(ev, on='id')
        cc90 = [f'indice_{e}' for e in ENFOQUES] + ['indice_amenaza', 'con_evidencia', 'fuentes']
        c90 = e90[cc90].rank().corr().round(3).reset_index().rename(columns={'index': 'variable'})
        c90.insert(0, 'muestra', f'base con evidencia ({len(e90)})')
        r90 = mco(e90.assign(con_evidencia_log=np.log1p(e90.con_evidencia)), 'con_evidencia_log', xs)
        for r in r90:
            r['muestra'] = f'base con evidencia ({len(e90)})'
        regs += r90
    else:
        c90 = None
    pd.DataFrame(regs).to_csv(os.path.join(SALIDA, 'regresiones.csv'), index=False)

    reg = idx.groupby('region')[[f'indice_{e}' for e in ENFOQUES] + ['indice_viv']].median().round(1)
    reg['ciudades'] = idx.groupby('region').size()

    ind.round(4).to_csv(os.path.join(SALIDA, 'indicadores_enfoques.csv'), index=False)
    cols = ['id', 'ciudad', 'pais', 'iso3', 'region', 'pob', 'centro_urbano_compartido'] + \
           [f'indice_{e}' for e in ENFOQUES] + ['indice_viv'] + [f'z_{e}' for e in ENFOQUES] + ['z_viv'] + \
           [f'cobertura_{e}' for e in ENFOQUES] + ['cobertura_viv'] + \
           ['tipo', 'tipo_nombre', 'indice_amenaza', 'amenaza_principal', 'puntaje_pct', 'metodo', 'prioridad']
    idx[cols].to_csv(os.path.join(SALIDA, 'indices_enfoques.csv'), index=False)
    dic.drop(columns=['enfoque_cod', 'ref'])[['indicador', 'enfoque', 'nombre', 'sentido', 'unidad', 'fuente', 'fundamento', 'referencia', 'cobertura_ciudades']] \
        .to_csv(os.path.join(SALIDA, 'diccionario_indicadores.csv'), index=False)
    pd.DataFrame(cons).to_csv(os.path.join(SALIDA, 'consistencia_indices.csv'), index=False)
    out = cor.reset_index().rename(columns={'index': 'variable'})
    out.insert(0, 'muestra', 'todas (375)')
    if cor_mano is not None:
        om = cor_mano.reset_index().rename(columns={'index': 'variable'})
        om.insert(0, 'muestra', f'hechas a mano ({len(mano)})')
        out = pd.concat([out, om])
    if c90 is not None:
        out = pd.concat([out, c90])
    out.to_csv(os.path.join(SALIDA, 'correlaciones.csv'), index=False)
    perf.reset_index().round(1).to_csv(os.path.join(SALIDA, 'tipologias.csv'), index=False)
    reg.reset_index().to_csv(os.path.join(SALIDA, 'resumen_region.csv'), index=False)
    cdp.merge(ind[['id', 'nombre']], on='id').to_csv(os.path.join(SALIDA, 'cdp_ciudades.csv'), index=False)

    print(f'{len(idx)} ciudades; {len(dic)} indicadores; k={k} tipos (silueta {s:.2f}); {len(cdp)} reportan a CDP')
    for e, (enf, nom) in ENFOQUES.items():
        print(f'  {nom}: {idx[f"indice_{e}"].notna().sum()} ciudades con índice')
    print(f'  Precariedad habitacional (subíndice): {idx.indice_viv.notna().sum()} ciudades con índice')


if __name__ == '__main__':
    main()
