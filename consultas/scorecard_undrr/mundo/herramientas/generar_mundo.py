"""Genera el scorecard UNDRR (detallado EN + adenda de salud ES) de cada ciudad del mundo de +2 millones.

Cómo se calcula cada respuesta
  1. Ancla: el puntaje medio de esa pregunta en las 16 ciudades latinoamericanas evaluadas a mano
     (CABA y las 15 de consultas/scorecard_undrr/latam).
  2. Ajuste por capacidad: cada Esencial tiene un índice de capacidad 0-1 que combina datos del país
     (efectividad del gobierno y estado de derecho del WGI, PIB por habitante, obligación legal de los gobiernos
     locales, alerta temprana, seguros, salud) y de la ciudad (IDH del centro urbano del GHSL, redes de ciudades,
     informalidad, conflicto). Puntaje = ancla + K x (capacidad de la ciudad - capacidad media de las 16).
  3. Reglas por pregunta con datos directos (gas, metro, puerto, seguros, fondo, alerta, informalidad, camas...).
  4. Hechos puntuales del perfil de la ciudad (ov) fijan la respuesta con confianza media.
Las 16 ciudades hechas a mano no se regeneran (salvo --todas); su puntaje modelado sirve para validar.

uso: python generar_mundo.py <carpeta_mundo> [--datos <carpeta de datos>] [--todas] [--solo id1,id2] [--sin-xlsm]
"""
import sys, os, json, math, importlib, zipfile, shutil, re
import pandas as pd

H = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(os.path.dirname(os.path.dirname(H)), 'herramientas')  # herramientas de CABA/Latinoamérica
sys.path.insert(0, H); sys.path.insert(0, BASE); sys.path.insert(0, os.path.join(BASE, 'detalle'))
import paises as PA, perfiles_ciudad as PC, perfiles_china as PCH, plantillas_mundo as W
import plantillas as T  # acciones, responsables y plazos
from relleno import rellenar

MUNDO = sys.argv[1]
TODAS = '--todas' in sys.argv
SOLO = sys.argv[sys.argv.index('--solo') + 1].split(',') if '--solo' in sys.argv else None
SIN_XLSM = '--sin-xlsm' in sys.argv
FECHA = '08/11/2026'
LOCAL = os.environ.get('SCORECARD_TMP', '/tmp/scorecard_mundo')  # carpeta local de trabajo
K = 4.5
HECHAS = ['sao_paulo', 'cdmx', 'lima', 'bogota', 'rio', 'brasilia', 'guayaquil', 'quito', 'medellin', 'fortaleza', 'salvador',
          'belo_horizonte', 'cali', 'caracas', 'manaus', 'caba']
# municipios centrales, ciudades subprovinciales de China y capitales nacionales con rango de provincia o estado
RANGO_ALTO = {'pekin', 'shanghai', 'tianjin', 'chongqing', 'guangzhou', 'shenzhen', 'wuhan', 'chengdu', 'nanjing', 'hangzhou', 'xi_an', 'shenyang',
              'harbin', 'changchun', 'jinan', 'qingdao', 'dalian', 'ningbo', 'xiamen', 'tokio', 'seul', 'londres', 'berlin', 'viena', 'moscu', 'bangkok',
              'yakarta', 'hong_kong', 'singapur', 'cdmx', 'bogota', 'caba', 'brasilia', 'nueva_york', 'paris', 'madrid', 'taipei'}
# capitales de provincia o estado (China) y otras capitales nacionales
CAPITALES = {'shijiazhuang', 'taiyuan', 'hohhot', 'zhengzhou', 'changsha', 'nanchang', 'hefei', 'fuzhou', 'nanning', 'haikou', 'kunming', 'guiyang',
             'lanzhou', 'xining', 'yinchuan', 'urumqi', 'roma', 'kiev', 'minsk', 'ankara', 'teheran', 'bagdad', 'riad', 'aman', 'damasco', 'sana', 'kabul',
             'taskent', 'baku', 'delhi', 'islamabad', 'dhaka_norte', 'dhaka_sur', 'hanoi', 'phnom_penh', 'el_cairo', 'jartum', 'addis_abeba', 'nairobi',
             'kinsasa', 'luanda', 'abuja', 'bamako', 'uagadugu', 'conakri', 'yaunde', 'brazzaville', 'lome', 'mogadiscio', 'lusaka', 'tshwane', 'argel',
             'pyongyang', 'lima', 'quito', 'caracas', 'rangun'}
clip = lambda x: int(max(0, min(5, x)))
nz = lambda v, d=0: d if v is None or (isinstance(v, float) and math.isnan(v)) else v

def fmt(n, dec=0):
    if n is None or (isinstance(n, float) and math.isnan(n)): return 's/d'
    s = f'{n:,.{dec}f}'
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')

# ---------------- datos ----------------
D = sys.argv[sys.argv.index('--datos') + 1] if '--datos' in sys.argv else os.path.join(MUNDO, 'datos')
ciu = pd.read_csv(os.path.join(D, 'ghsl_ciudades.csv'))
sis = pd.read_csv(os.path.join(D, 'sismos_ciudades.csv')).set_index('id')
ind = pd.read_csv(os.path.join(D, 'indicadores_pais.csv')).set_index('iso3')
PEN = json.load(open(os.path.join(BASE, 'preguntas_en.json'))); PES = json.load(open(os.path.join(BASE, 'preguntas_es.json')))
SHEET = {q['ref']: q['sheet'] for q in PEN}

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(H))))  # raíz del proyecto (tiene etl/ y consultas/)
MAESTRO = pd.read_csv(os.path.join(RAIZ, 'etl', 'maestros', 'paises_maestro.csv'), keep_default_na=False).set_index('iso3')

def pais_es(iso):
    if iso in MAESTRO.index and MAESTRO.loc[iso, 'nombre_es']: return MAESTRO.loc[iso, 'nombre_es']
    return (PA.P[iso].get('extra') or {}).get('pais', iso)

def region_es(iso):
    if iso in MAESTRO.index and MAESTRO.loc[iso, 'region_bm_es']: return MAESTRO.loc[iso, 'region_bm_es']
    return 'Asia oriental y el Pacífico'

def pais_val(iso, k):
    ex = PA.P[iso].get('extra') or {}
    if k in ex: return ex[k]
    v = ind.loc[iso, k] if iso in ind.index and k in ind.columns else None
    return None if v is None or (isinstance(v, float) and math.isnan(v)) else v

# anclas: medias de las 16 hechas a mano
def respuestas_hechas(cid):
    if cid == 'caba':
        m = importlib.import_module('respuestas')
    else:
        m = importlib.import_module('resp_' + cid)
    return m.EN, m.ES
MANO = {c: respuestas_hechas(c) for c in HECHAS}
ANCLA_EN = {q['ref']: sum(MANO[c][0][q['ref']][0] for c in HECHAS) / 16 for q in PEN}
ANCLA_ES = {q['ref']: sum(MANO[c][1][q['ref']][0] for c in HECHAS) / 16 for q in PES}

# ---------------- perfil de cada ciudad ----------------
def perfil(r):
    if r.iso3 == 'CHN':
        des, ov = PCH.DES.get(r.id, (None, {}))
        loc = r.nombre_local[:-1] if str(r.nombre_local).endswith('市') else r.nombre_local
        return dict(ag=f'Oficina de Gestión de Emergencias de {r.nombre} ({loc}应急管理局)',
                    pl=f'plan general de emergencias de {r.nombre} y plan de prevención y mitigación de desastres del 14.º Plan Quinquenal (2021-2025)',
                    red=PCH.REDES.get(r.id, ''), des=des, inf=PCH.INFORMAL_CIUDAD.get(r.id, PCH.INFORMAL),
                    me=(f'metro de {r.nombre}' if r.id in PCH.METRO else ''), pu=r.id in PCH.PUERTO, ga=True,
                    sat=None, coe=f'centro de mando de emergencias de {r.nombre}', ov=ov, esponja=r.id in PCH.ESPONJA)
    p = dict(PC.P.get(r.id, {}))
    p.setdefault('ov', {}); p.setdefault('sat', None); p.setdefault('coe', None); p['esponja'] = False
    return p

# ---------------- amenazas desde los datos ----------------
def suma3(r, h):
    return sum(nz(r.get(f'HZ_CEV_{h}_{y}')) for y in (2005, 2010, 2015))

def amenazas(r, s, des_txt=None):
    a = []  # (peso, texto corto, texto con dato)
    fl, cf, eq, utci = nz(r.EX_100_SHP_2025), nz(r.EX_CF1_SHP_2025), nz(r.EX_SHA_POP_2025), nz(r.CL_UTC_T32_2020)
    n6 = int(nz(s.get('sismos_m6_150km_desde1900'))); mx = s.get('sismo_max_mag')
    flo, tcy, lan, tsu, dro, hew, cow = (suma3(r, h) for h in ('FLO', 'TCY', 'LAN', 'TSU', 'DRO', 'HEW', 'COW'))
    if eq >= 50 or n6 >= 3:
        a.append((3 + min(n6, 30) / 10, 'sismos', f'sismos ({fmt(eq)}% de la población en zona de intensidad VI o más; {n6} sismos M6+ a menos de 150 km desde 1900'
                  + (f', el mayor M{fmt(mx, 1)} en {str(s.get("sismo_max_fecha"))[:4]}' if isinstance(mx, float) and not math.isnan(mx) else '') + ')'))
    if fl >= 3 or flo >= 4:
        a.append((1 + fl / 10 + flo / 10, 'inundaciones fluviales y urbanas', f'inundaciones ({fmt(fl, 1)}% de la población en zona inundable de 100 años; {int(flo)} eventos de inundación en el catálogo multiamenaza 2005-2015)'))
    if cf >= 1:
        a.append((1 + cf / 10, 'inundación costera y marejadas', f'inundación costera ({fmt(cf, 1)}% de la población en zona de inundación costera de 100 años)'))
    if tcy >= 3:
        a.append((1 + tcy / 10, 'ciclones tropicales', f'ciclones tropicales ({int(tcy)} eventos 2005-2015)'))
    if utci >= 60:
        a.append((0.6 + utci / 300, 'calor extremo', f'calor extremo ({int(utci)} días al año con estrés térmico fuerte, UTCI > 32 °C, en 2011-2020)'))
    if lan >= 1:
        a.append((1 + lan / 5, 'deslizamientos', f'deslizamientos ({int(lan)} eventos 2005-2015)'))
    if tsu >= 1:
        a.append((0.7 + tsu / 10, 'tsunami', f'tsunami ({int(tsu)} eventos regionales 2005-2015)'))
    if dro >= 5:
        a.append((0.6, 'sequía y escasez de agua', f'sequía ({int(dro)} eventos 2005-2015)'))
    if cow >= 4:
        a.append((0.5, 'olas de frío', f'olas de frío ({int(cow)} eventos 2005-2015)'))
    # amenazas que muestran los desastres del perfil y que los datos globales no captan (p. ej. lluvia extrema local)
    des = (des_txt or '').lower()
    ya = {c for _, c, _ in a}
    for clave, corto in ((r'inundac|lluvia|crecida|anegamiento', 'inundaciones fluviales y urbanas'), (r'sismo|terremoto', 'sismos'),
                         (r'tif[oó]n|cicl[oó]n|hurac[aá]n', 'ciclones tropicales'), (r'deslizamiento|alud|movimiento en masa', 'deslizamientos'),
                         (r'ola de calor|calor extremo', 'calor extremo'), (r'incendios? forestal', 'incendios forestales'), (r'sequ[ií]a|escasez de agua|crisis h[ií]drica', 'sequía y escasez de agua')):
        if re.search(clave, des) and corto not in ya:
            a.append((1.5, corto, f'{corto} (según los desastres registrados en el perfil de la ciudad)'))
    if not a:
        a.append((0.5, 'tormentas e inundaciones urbanas', 'tormentas e inundaciones urbanas (amenazas bajas en los datos globales)'))
    a.sort(key=lambda x: -x[0])
    return a

# ---------------- capacidad ----------------
def capacidades(r, p, pa):
    iso = r.iso3
    ge = pais_val(iso, 'efectividad_gobierno'); ge = (nz(ge, -0.5) + 2.5) / 5
    rl = nz(pais_val(iso, 'indice_estado_derecho_0_100'), 30) / 100
    pib = pais_val(iso, 'pib_pc_usd') or 1500
    inc = max(0, min(1, (math.log10(pib) - 2.5) / 2.3))
    hdi = nz(r.SC_SEC_HDI_2020, 0.6)
    hdi_n = max(0, min(1, (hdi - 0.45) / 0.5))
    loc = pa['local'] / 2
    red = min(1, len([x for x in re.split(r',\s*', p.get('red') or '') if x]) / 2)
    civ = nz(pais_val(iso, 'indice_sociedad_civil_0_1'), 0.4)
    inf = p.get('inf', 10)
    form = max(0, 1 - inf / 60)
    seg = pa['seguro'] / 3; ale = pa['alerta'] / 3
    camas = nz(pais_val(iso, 'camas_hospital_x1000'), 1.5); med = nz(pais_val(iso, 'medicos_x1000'), 1)
    salud = (min(camas, 8) / 8 + min(med, 4) / 4) / 2
    cis = min(1, nz(r.IN_CIS_ALL_2020, 0.1) / 0.6)
    inc = 0.5 * inc + 0.5 * hdi_n  # ingreso del país mezclado con el IDH subnacional del centro urbano
    tra = pa.get('trayectoria', 0) / 2  # práctica acumulada de gestión del riesgo del país
    # gobiernos locales de mayor rango tienen más presupuesto y personal técnico
    rango = 0.05 if r.id in RANGO_ALTO else 0.03 if r.id in CAPITALES else 0
    rango += 0.02 if r.pob > 8e6 else 0
    conf = 0.15 if pa.get('cambio') and re.search(r'guerra|conflict|colaps|posconflicto|golpe|invasi', pa['cambio']) else 0
    cap = {
        'E01': .40 * ge + .30 * loc + .20 * red + .10 * rl, 'E02': .40 * ge + .20 * inc + .20 * red + .20 * loc,
        'E03': .30 * ge + .30 * inc + .20 * seg + .20 * loc, 'E04': .35 * rl + .25 * inc + .25 * form + .15 * ge,
        'E05': .40 * ge + .30 * inc + .30 * red, 'E06': .40 * ge + .30 * inc + .30 * red,
        'E07': .40 * civ + .30 * inc + .30 * ge, 'E08': .30 * inc + .30 * ge + .20 * cis + .20 * hdi_n,
        'E09': .30 * ge + .30 * ale + .20 * inc + .20 * loc, 'E10': .40 * ge + .30 * inc + .30 * seg,
        'H': .30 * salud + .30 * ge + .20 * inc + .20 * hdi_n}
    for k in ('E02', 'E06', 'E07', 'E09', 'E10'): cap[k] += 0.08 * tra
    cap = {k: v - conf + rango for k, v in cap.items()}
    return cap, dict(ge=ge, rl=rl, inc=inc, hdi=hdi, loc=loc, red=red, civ=civ, seg=seg, ale=ale, salud=salud, cis=cis, conf=conf, pib=pib, camas=camas, med=med)

# ---------------- campos de texto ----------------
def campos(r, p, pa, s, am, x):
    iso = r.iso3
    f = {}
    f['nombre'] = r.nombre; f['pais'] = pais_es(iso)
    f['ley'] = pa['ley']; f['agencia_nac'] = pa['agencia']; f['codigo'] = pa['codigo']; f['salud'] = pa['salud']
    f['agencia'] = p.get('ag') or f'el área de emergencias del gobierno de {r.nombre}'
    f['agencia_c'] = f['agencia'].split(' (')[0].split(' y ')[0]
    f['plan'] = p.get('pl') or 'sin plan de gestión del riesgo identificado en el perfil'
    f['plan_corto'] = f['plan'].split(' (')[0].split(' y ')[0]
    f['coe'] = p.get('coe') or 'sin centro de operaciones de emergencia identificado en el perfil'
    f['sat'] = p.get('sat') or {3: 'sistema nacional de alertas con aviso por celular a toda la población', 2: 'alertas oficiales del servicio meteorológico y de la agencia nacional por medios, web y redes',
                                1: 'alertas básicas del servicio meteorológico nacional', 0: 'sin sistema de alerta operativo conocido'}[pa['alerta']]
    f['alerta_alcance'] = {3: 'aviso por celular (cell broadcast) a toda la red móvil', 2: 'medios, redes sociales y aplicaciones; sin aviso masivo por celular universal',
                           1: 'medios de comunicación', 0: 'sin canal oficial masivo conocido'}[pa['alerta']]
    f['redes_txt'] = p.get('red') or 'ninguna identificada en el perfil'
    f['informal'] = p.get('inf', 10)
    f['servicios'] = 'agua, energía, gas' if p.get('ga') else 'agua y energía'
    f['local_txt'] = {2: 'la ley exige unidad, plan y presupuesto locales', 1: 'la ley da roles locales generales', 0: 'sistema centralizado, poco rol local'}[pa['local']]
    f['ge_txt'] = fmt(pais_val(iso, 'efectividad_gobierno'), 2) + ' (escala -2,5 a 2,5)'
    f['rl_txt'] = fmt(pais_val(iso, 'indice_estado_derecho_0_100')) + ' sobre 100'
    f['pib_txt'] = 'USD ' + fmt(x['pib']) + ' (Banco Mundial)'
    f['pob_uc_txt'] = fmt(r.GC_POP_TOT_2025 / 1e6, 1) + ' millones'
    f['pib_uc_txt'] = 'USD ' + fmt(r.SC_GDP_AVG_2020) if not pd.isna(r.SC_GDP_AVG_2020) else 's/d'
    fl, cf, eq = nz(r.EX_100_SHP_2025), nz(r.EX_CF1_SHP_2025), nz(r.EX_SHA_POP_2025)
    f['exposicion_txt'] = (f'{fmt(fl, 1)}% de la población del centro urbano en zona inundable de 100 años ({fmt(nz(r.EX_100_POP_2025) / 1e6, 2)} millones), '
                           f'{fmt(cf, 1)}% en inundación costera de 100 años y {fmt(eq)}% en zona sísmica de intensidad VI o más (GHSL 2025).')
    f['riesgo_txt'] = '; '.join(t for _, _, t in am[:4]) + '. Fuente: GHSL UCDB R2024A (centro urbano de ' + str(r.GC_UCN_MAI_2025) + ') y catálogo sísmico del USGS.'
    f['amenazas_l'] = ', '.join(c for _, c, _ in am[:4])
    f['amenaza1'] = am[0][1]
    sev = [c for _, c, _ in am if c in ('sismos', 'ciclones tropicales', 'tsunami', 'inundación costera y marejadas')]
    f['amenaza_severa'] = (sev[0] if sev else am[0][1]) + ' de gran magnitud'
    f['des_c'] = p.get('des') or 'sin desastre grande identificado en el perfil desde 1990'
    f['cis_txt'] = fmt(r.IN_CIS_ALL_2020, 2) + ' (0 a 1; la mediana de estas ciudades es 0,10)'
    for k, c in (('wat', 'WAT'), ('ene', 'ENE'), ('tra', 'TRA'), ('tel', 'TEL'), ('hea', 'HEA'), ('edu', 'EDU')):
        f[f'cis_{k}_txt'] = fmt(r[f'IN_CIS_{c}_2020'], 2)
    f['mapas'] = ('mapas de amenaza nacionales y de la ciudad' + (' publicados en línea' if x['ge'] > 0.6 else ', sin portal público verificado'))
    rio = r.GE_MRB_MAI_2025 if isinstance(r.GE_MRB_MAI_2025, str) else None
    f['ecos'] = ', '.join(e for e in [f'cuenca del {rio}' if rio else None, 'costa y humedales costeros' if cf > 0 or p.get('pu') else None,
                                       'áreas verdes y arbolado urbano', 'suelo periurbano'] if e)
    f['transb'] = (f'organismo de cuenca del {rio} y gobiernos vecinos' if rio else 'gobiernos vecinos y organismos regionales')
    pa_f = pa.get('fondo')
    f['fondo_txt'] = (pa_f + '.') if pa_f else 'sin fondo de contingencia nacional o local identificado; la respuesta depende de reasignaciones y ayuda externa.'
    f['fondo_corto'] = pa_f.split(' (')[0] if pa_f else 'sin fondo identificado'
    f['seguro_txt'] = {3: 'penetración alta del seguro de daños, con cobertura de catástrofes difundida', 2: 'penetración media del seguro de daños',
                       1: 'penetración baja del seguro de daños', 0: 'seguro de daños casi inexistente'}[pa['seguro']] + f' en {f["pais"]} (escala propia por país).'
    f['civ_txt'] = fmt(x['civ'], 2) + ' (V-Dem, 0 a 1)'
    f['internet_txt'] = fmt(pais_val(iso, 'usuarios_internet_pct')) + '%'
    f['migr_txt'] = fmt(pais_val(iso, 'stock_migrantes_pct_poblacion'), 1) + '%'
    f['camas_txt'] = fmt(x['camas'], 1); f['medicos_txt'] = fmt(x['med'], 1)
    f['esperanza_txt'] = fmt(pais_val(iso, 'esperanza_vida'), 1) + ' años'
    f['gasto_salud_txt'] = fmt(pais_val(iso, 'gasto_salud_pct_pib'), 1) + '% del PIB'
    f['utci_txt'] = fmt(r.CL_UTC_T32_2020)
    trop = str(r.CL_KOP_CUR_2025) in ('1', '2', '3', '1.0', '2.0', '3.0')
    f['epidemias_txt'] = 'COVID-19 y arbovirosis (dengue y otras) por clima tropical' if trop else 'COVID-19, influenza y brotes de origen hídrico'
    f['agri_txt'] = ('El territorio de la ciudad-prefectura incluye condados rurales con agricultura extensa expuesta a inundación, sequía y granizo.' if r.tipo == 'Ciudad de nivel de prefectura'
                     else 'Hay poco suelo agrícola dentro de la jurisdicción; la pérdida posible es chica.')
    f['esponja_txt'] = ('ciudad del programa nacional de "ciudad esponja" del MOHURD.' if p.get('esponja') else 'proyectos puntuales de drenaje sostenible y espacio público.')
    f['proteccion_txt'] = (f'{fmt(fl, 1)}% de la población del centro urbano está en zona inundable de 100 años y {fmt(cf, 1)}% en zona de inundación costera.')
    gas, sism = p.get('ga'), (eq >= 50 or int(nz(s.get('sismos_m6_150km_desde1900'))) >= 3)
    f['gas_txt'] = (('Red de gas natural por cañería extendida' + ('; un sismo fuerte podría dañarla y cortar el servicio por días.' if sism else '; las amenazas principales casi no la afectan.'))
                    if gas else 'No hay red de gas por cañería extendida; la mayoría de los hogares usa garrafas o GLP, con riesgo en la distribución más que en la red.')
    f['metro_txt'] = (f"Transporte masivo sobre rieles: {p['me']}; interrupciones posibles por inundación o cortes eléctricos." if p.get('me')
                      else 'No hay metro ni tren urbano; no aplica (los buses se evalúan en 8.5.1 y 8.5.6).')
    f['puerto_txt'] = ('Puerto en la ciudad; temporales, crecidas o bajantes pueden suspender operaciones.' if p.get('pu')
                       else 'No hay puerto marítimo o fluvial relevante dentro de la jurisdicción; no aplica.')
    f['pob_txt'] = fmt(r.pob)
    return f

# ---------------- reglas por pregunta ----------------
def puntaje_en(ref, cap, ref_cap, x, p, pa, r, s, f):
    e = SHEET[ref]
    base = ANCLA_EN[ref] + K * (cap[e] - ref_cap[e])
    inf = p.get('inf', 10)
    sism = nz(r.EX_SHA_POP_2025) >= 50 or int(nz(s.get('sismos_m6_150km_desde1900'))) >= 3
    if ref == '3.2.4':
        if r.iso3 == 'PHL': return 4
        return clip(round(min(base, {2: 4, 1: 3, 0: 1}[pa['local']] if pa.get('fondo') else 1)))
    if ref in ('3.3.1', '3.3.2'):
        return {0: 0, 1: 1, 2: 2 if ref == '3.3.1' else 3, 3: 4}[pa['seguro']]
    if ref == '4.1.3':
        return clip(round(base)) if r.tipo == 'Ciudad de nivel de prefectura' else 5
    if ref == '4.3.1':
        return clip(round(1 + 3.5 * x['rl'] - (1 if inf > 25 else 0) - (1 if inf > 45 else 0) - x['conf'] * 5))
    if ref in ('4.4.1', '4.4.2'):
        return 4 if (inf < 3 and x['rl'] > 0.8) else 3 if inf < 10 else 2 if inf <= 25 else 1 if inf <= 45 else 0
    if ref.startswith('8.4.'):
        if not p.get('ga'): return 4
        if r.iso3 == 'JPN': return 5 if ref == '8.4.1' else clip(round(base))  # medidores con corte automático por sismo
        if sism: return {'8.4.1': clip(round(min(base, 2 + 2 * x['ge']))), '8.4.2': 3, '8.4.3': 3, '8.4.4': 3}[ref]
        return clip(round(base))
    if ref == '8.5.3' and not p.get('me'): return 5
    if ref == '8.5.5' and not p.get('pu'): return 5
    if ref == '9.1.1':
        return clip({0: 1, 1: 2, 2: 3, 3: 4}[pa['alerta']] + (1 if p.get('sat') and pa['alerta'] >= 1 else 0) - (1 if x['conf'] else 0))
    if ref == '9.1.1.1':
        return {0: 1, 1: 2, 2: 3, 3: 5}[pa['alerta']]
    if ref == '6.6.1':
        n = len([v for v in re.split(r',\s*', p.get('red') or '') if v])
        return 4 if n >= 2 else 3 if n == 1 else (1 if x['ge'] > 0.4 else 0)
    if ref == '6.5.1':
        m = nz(pais_val(r.iso3, 'stock_migrantes_pct_poblacion'), 2)
        return clip(round(base - (1 if m > 20 and x['ge'] < 0.7 else 0)))
    if ref == '10.2.1' and not p.get('des'):
        return clip(round(base - 0.5))
    if ref in ('8.7.1', '8.7.1.1', '8.7.3'):
        return clip(round(ANCLA_EN[ref] + K * (cap['H'] - ref_cap['H'])))
    if ref == '8.1.1':
        return clip(round(base - (1 if nz(r.EX_100_SHP_2025) > 25 or nz(r.EX_CF1_SHP_2025) > 10 else 0)))
    if ref in ('4.2.1', '5.2.2') and p.get('esponja'):
        return clip(round(base + 1))
    return clip(round(base))

def puntaje_es(ref, cap, ref_cap):
    return clip(round(ANCLA_ES[ref] + K * (cap['H'] - ref_cap['H'])))

# ---------------- armado ----------------
def info_ciudad(r, p, pa, f, x):
    pais = f['pais']; sd = 's/d'; ped = 'Completar con el instituto de estadística local'
    pib = x['pib']; gini = pais_val(r.iso3, 'gini')
    return {
        'D4': r.nombre + (f' ({r.nombre_local})' if isinstance(r.nombre_local, str) and r.nombre_local != r.nombre else ''), 'D5': r.tipo, 'D6': pais,
        'D7': f'{FECHA} (borrador de escritorio, modelo mundial)',
        'C10': r.autoridad, 'D10': 'Gobierno local',
        'C11': int(r.pob), 'D11': f'{r.fuente_pob} ({int(r.anio_pob) if not pd.isna(r.anio_pob) else "s/f"})',
        'C12': round(r.GC_UCA_KM2_2025), 'D12': f'km² del centro urbano GHSL "{r.GC_UCN_MAI_2025}" (mancha urbana, no la jurisdicción)',
        'C13': round(r.GC_POP_TOT_2025 / r.GC_UCA_KM2_2025), 'D13': 'hab/km² del centro urbano GHSL 2025',
        'C14': sd, 'D14': ped, 'C15': sd, 'D15': ped, 'C16': sd, 'D16': ped, 'C17': sd, 'D17': ped, 'C18': sd, 'D18': ped, 'C19': sd, 'D19': ped,
        'C20': f"{f['migr_txt']} (dato nacional)", 'D20': 'Stock de migrantes internacionales como % de la población del país (Banco Mundial, panel del proyecto)',
        'C21': f['riesgo_txt'], 'D21': 'GHSL UCDB R2024A (Comisión Europea) y USGS ComCat',
        'C22': f['des_c'], 'D22': 'Perfil de la ciudad (conocimiento general, a verificar)',
        'C25': sd, 'D25': ped, 'C26': sd, 'D26': ped, 'C27': sd, 'D27': ped,
        'C28': round(pib) if pib else sd, 'D28': f'PIB per cápita de {pais} en USD corrientes (Banco Mundial, panel del proyecto)',
        'C29': gini if gini else sd, 'D29': (f'Gini de {pais} (Banco Mundial); no es el de la ciudad' if gini else 'Sin dato del Banco Mundial'),
        'C30': (f'USD {fmt(r.SC_GDP_AVG_2020)} PPA por habitante (centro urbano, 2020)' if not pd.isna(r.SC_GDP_AVG_2020) else sd), 'D30': 'GHSL UCDB R2024A, tema socioeconómico',
        'D33': '(a completar)', 'D34': '(a completar)', 'D35': '(a completar)', 'D36': '(a completar)',
        'B40': ('Borrador de escritorio del modelo mundial (nov-2026): cada puntaje parte de la media de 16 ciudades latinoamericanas evaluadas a mano '
                'y se ajusta por indicadores de capacidad del país y de la ciudad (WGI, PIB, IDH del GHSL, marco legal, alertas, seguros, salud) '
                'y por hechos del perfil de la ciudad. No hubo talleres ni búsqueda por pregunta: sirve para comparar y priorizar, no como autoevaluación.'),
    }

def respuestas(r, ref_cap):
    pa = PA.P[r.iso3]; p = perfil(r); s = sis.loc[r.id].to_dict() if r.id in sis.index else {}
    am = amenazas(r, s, p.get('des'))
    cap, x = capacidades(r, p, pa)
    f = campos(r, p, pa, s, am, x)
    en, es = {}, {}
    for q in PEN:
        ref = q['ref']; e = SHEET[ref]
        if ref in p['ov']:
            sc, txt = p['ov'][ref]; conf = 'media'
            hecho = txt
        else:
            sc = puntaje_en(ref, cap, ref_cap, x, p, pa, r, s, f)
            hecho = W.EN[ref].format(**f)
            conf = 'media' if ref in ('1.2.1', '1.2.3', '3.2.4', '3.3.1', '3.3.2', '9.1.1', '9.1.1.1', '6.6.1', '8.5.3', '8.5.5', '4.1.3') else 'baja'
        _, acc, rk, plazo = T.EN[ref]
        txt = f"{hecho} Nivel estimado {sc} de 5: {W.BANDA[sc]}. [Modelo: capacidad {fmt(cap[e], 2)} en {e} frente a {fmt(ref_cap[e], 2)} de la media de las 16 ciudades evaluadas a mano.]"
        resp = f['agencia_c'] if rk == 'grd' else T.RESP[rk]
        en[ref] = (sc, conf, txt, 'Sin acción.' if sc == 5 or acc.startswith('Sin acción') else acc, resp if sc < 5 else '', plazo if sc < 5 else '')
    for q in PES:
        ref = q['ref']
        sc = puntaje_es(ref, cap, ref_cap)
        _, acc, rk, plazo = T.ES[ref]
        txt = f"{W.ES[ref].format(**f)} Nivel estimado {sc} de 5: {W.BANDA[sc]}. [Modelo: capacidad de salud {fmt(cap['H'], 2)} frente a {fmt(ref_cap['H'], 2)} de la media de las 16.]"
        resp = f['agencia_c'] if rk == 'grd' else T.RESP[rk]
        es[ref] = (sc, 'baja', txt, 'Sin acción.' if sc == 5 else acc, resp if sc < 5 else '', plazo if sc < 5 else '')
    return en, es, info_ciudad(r, p, pa, f, x), cap, x, f

def plantillas_xlsm():
    """Descomprime los .xlsm originales de UNDRR (subidos por la usuaria) en carpetas de trabajo."""
    up = '/mnt/project-files/uploads/hearth'
    src = {'en': os.path.join(up, 'b7352477-5507-4cd1-b3cb-1fe07032f54f'), 'es': os.path.join(up, '40097900-3919-4f9c-abc7-55dfac8dcf35')}
    work = os.path.join(LOCAL, 'trabajo'); os.makedirs(work, exist_ok=True)
    out = {}
    for k, z in src.items():
        x = os.path.join(work, f'x_{k}')
        if not os.path.exists(x):
            with zipfile.ZipFile(z) as zz: zz.extractall(x)
        out[k] = (z, x)
    return out

def main():
    ref_rows = ciu[ciu.id.isin(HECHAS)]
    caps = [capacidades(r, perfil(r), PA.P[r.iso3])[0] for _, r in ref_rows.iterrows()]
    ref_cap = {k: sum(c[k] for c in caps) / len(caps) for k in caps[0]}
    pl = plantillas_xlsm() if not SIN_XLSM else None
    salida = os.path.join(MUNDO, 'xlsm'); tmp = os.path.join(LOCAL, 'xlsm')
    if pl: os.makedirs(salida, exist_ok=True); os.makedirs(tmp, exist_ok=True)
    filas = []
    for _, r in ciu.iterrows():
        if SOLO and r.id not in SOLO: continue
        en, es, info, cap, x, f = respuestas(r, ref_cap)
        tot_en = sum(v[0] for v in en.values()); tot_es = sum(v[0] for v in es.values())
        por_e = {}
        for ref, v in en.items(): por_e[SHEET[ref]] = por_e.get(SHEET[ref], 0) + v[0]
        hecha = r.id in HECHAS
        fila = dict(id=r.id, ciudad=r.nombre, iso3=r.iso3, pais=f['pais'], region=region_es(r.iso3), poblacion=int(r.pob),
                    modelo_total_590=tot_en, modelo_salud_115=tot_es, **{f'modelo_{k}': v for k, v in sorted(por_e.items())},
                    **{f'cap_{k}': round(v, 3) for k, v in cap.items()}, amenaza_principal=f['amenaza1'], hecha_a_mano=hecha)
        if hecha:
            m_en, m_es = MANO[r.id]
            fila['mano_total_590'] = sum(v[0] for v in m_en.values()); fila['mano_salud_115'] = sum(v[0] for v in m_es.values())
        filas.append(fila)
        if pl and (not hecha or TODAS):
            pref = '[Borrador de escritorio nov-2026, modelo mundial;'
            for k, nom, resp_k in (('en', f'Scorecard_UNDRR_{r.id}_detallado_EN.xlsm', en), ('es', f'Scorecard_UNDRR_{r.id}_salud_publica_ES.xlsm', es)):
                o = os.path.join(tmp, nom)
                rellenar(pl[k][0], pl[k][1], os.path.join(BASE, f'preguntas_{k}.json'), resp_k, info, pref, o)
                shutil.move(o, os.path.join(salida, nom))
            print('ok', r.id, tot_en, tot_es, flush=True)
    out = pd.DataFrame(filas)
    if not SOLO:
        out.to_csv(os.path.join(D, 'puntajes_mundo.csv'), index=False)
    v = out[out.hecha_a_mano]
    if len(v) > 2:
        print('validación con las 16 hechas a mano: correlación', round(v.modelo_total_590.corr(v.mano_total_590), 2),
              '| error medio absoluto', round((v.modelo_total_590 - v.mano_total_590).abs().mean(), 1), 'puntos de 590')
    return out

if __name__ == '__main__':
    main()
