"""Genera los scorecards UNDRR (detallado EN + adenda salud ES) para cada ciudad de ciudades.py.

uso: python generar.py <carpeta_scratch> <carpeta_salida>
"""
import sys, os, json, csv
sys.path.insert(0, os.path.dirname(__file__))
import respuestas as base, plantillas as T, ciudades as CI
from relleno import rellenar

scr, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
SRC_EN = [f for f in os.listdir(scr) if f.startswith('b7352477') and f.endswith('.xlsm')][0]
SRC_ES = [f for f in os.listdir(scr) if f.startswith('40097900') and f.endswith('.xlsm')][0]
MIGR = {'BRA': 0.7, 'MEX': 1.3, 'PER': 5.4, 'COL': 5.8, 'ECU': 4.1, 'VEN': 4.4}
FECHA = '07/11/2026'
clip = lambda x: max(0, min(5, x))

def fmt(n): return f'{n:,}'.replace(',', '.')

def campos(c):
    am = c['amenazas']
    f = dict(c)
    f['pais'] = CI.PAIS[c['iso']][0]
    f['ley'] = CI.LEY[c['iso']]
    f['amenazas_l'] = am[0].lower() + am[1:]
    f['amenaza1'] = am.split(',')[0].strip().lower()
    f['plan_corto'] = c['plan'].split(' (')[0].split(' y ')[0]
    f['agencia_c'] = c['agencia'].split(' (')[0].split(' y ')[0].split(', ')[0]
    f['pob_txt'] = fmt(c['pob'])
    f['desastre_c'] = c['desastre'].split(' (')[0].split(';')[0]
    f['fondo_txt'] = (f"Existe {c['fondo']}; no hay evidencia de que alcance para el escenario más probable." if c['fondo']
                      else 'No se encontró un fondo de contingencia específico para recuperación post desastre; se responde con reasignaciones presupuestarias y transferencias de otros niveles de gobierno.')
    f['agri_txt'] = ('No aplica: la ciudad no tiene superficie agrícola relevante. Se marca 5 por no haber pérdida posible.' if c['agricola'] == 'na'
                     else 'Hay suelo rural productivo dentro del territorio, expuesto a inundación, sequía o incendio; sin estimación publicada de la superficie en riesgo.')
    f['gas_txt'] = ('Red de gas natural por cañería en buena parte de la ciudad' + ('; un sismo podría dañar tramos y cortar el servicio por días.' if c['sismica'] else '; las inundaciones casi no la afectan.')) if c['gas'] \
        else 'No hay red de gas por cañería extendida; la mayoría de los hogares usa GLP envasado, con riesgo en la cadena de distribución más que en la red.'
    f['metro_txt'] = (f"Transporte masivo: {c['metro']}; interrupciones de horas por inundación o cortes eléctricos." if c['metro']
                      else 'No hay metro ni tren urbano; no aplica (los buses se evalúan en 8.5.1 y 8.5.6).')
    f['puerto_txt'] = ('Puerto en la ciudad; temporales, crecidas o sequías pueden suspender operaciones por horas o días.' if c['puerto']
                       else 'No hay puerto marítimo o fluvial relevante dentro de la jurisdicción; no aplica.')
    return f

def score_en(ref, c, f):
    b = base.EN[ref][0]
    e = 'E%02d' % int(ref.split('.')[0])
    if ref in c['ov']: return c['ov'][ref][0], c['ov'][ref][1], 'media'
    inf = c['informal']
    if ref in ('4.4.1', '4.4.2'): return (3 if inf < 10 else 2 if inf <= 25 else 1 if inf <= 45 else 0), None, None
    if ref == '4.3.1': return (4 if inf < 10 else 3 if inf <= 25 else 2 if inf <= 45 else 1), None, None
    if ref == '4.1.3': return (5 if c['agricola'] == 'na' else c['agricola']), None, None
    if ref == '3.2.4': return (2 if c['fondo'] else 0), None, None
    if ref.startswith('8.4.'):
        if not c['gas']: return 4, None, None
        if c['sismica']: return {'8.4.1': 1, '8.4.2': 3, '8.4.3': 3, '8.4.4': 3}[ref], None, None
        return b, None, None
    if ref == '8.5.3' and not c['metro']: return 5, None, None
    if ref == '8.5.5' and not c['puerto']: return 5, None, None
    return clip(b + c['delta'].get(e, 0)), None, None

def respuestas_ciudad(c):
    f = campos(c)
    en, es = {}, {}
    for ref, (tpl, acc, rk, plazo) in T.EN.items():
        sc, txt_ov, conf_ov = score_en(ref, c, f)
        txt = txt_ov or tpl.format(**f)
        conf = conf_ov or ('media' if ref in T.CONF_MEDIA else 'baja')
        resp = f['agencia_c'] if rk == 'grd' else T.RESP[rk]
        en[ref] = (sc, conf, txt, acc if acc != 'Sin acción prioritaria.' else 'Sin acción.', resp, plazo)
    for ref, (tpl, acc, rk, plazo) in T.ES.items():
        sc = clip(base.ES[ref][0] + c['H'])
        resp = f['agencia_c'] if rk == 'grd' else T.RESP[rk]
        es[ref] = (sc, 'baja', tpl.format(**f), acc, resp, plazo)
    return en, es

def info_ciudad(c):
    pais, pibpc, gini = CI.PAIS[c['iso']]
    sd = 's/d'; ped = 'Completar con el instituto de estadística local'
    return {
        'D4': c['nombre'], 'D5': c['tipo'], 'D6': pais, 'D7': f'{FECHA} (borrador preliminar de escritorio)',
        'C10': c['autoridad'], 'D10': 'Gobierno local',
        'C11': c['pob'], 'D11': c['pob_fuente'], 'C12': c['area'], 'D12': 'km², superficie aproximada de la jurisdicción',
        'C13': round(c['pob'] / c['area']), 'D13': 'hab/km², calculado (población / superficie; incluye zonas rurales si las hay)',
        'C14': sd, 'D14': ped, 'C15': sd, 'D15': ped, 'C16': sd, 'D16': ped, 'C17': sd, 'D17': ped,
        'C18': sd, 'D18': ped, 'C19': sd, 'D19': ped,
        'C20': f"{MIGR[c['iso']]}% (dato nacional)", 'D20': 'Stock de migrantes internacionales como % de la población del país (Banco Mundial, panel del proyecto)',
        'C21': c['amenazas'], 'D21': 'Perfil de la ciudad (búsquedas web, nov-2026)',
        'C22': c['desastre'], 'D22': 'Perfil de la ciudad (búsquedas web y prensa)',
        'C25': sd, 'D25': ped, 'C26': sd, 'D26': ped, 'C27': sd, 'D27': ped,
        'C28': pibpc, 'D28': f'PIB per cápita de {pais} en USD corrientes 2024 (Banco Mundial, panel del proyecto)',
        'C29': gini if gini else sd, 'D29': f'Gini de {pais} 2024 (Banco Mundial); no es el de la ciudad' if gini else 'Sin dato reciente del Banco Mundial',
        'C30': sd, 'D30': ped,
        'D33': '(a completar)', 'D34': '(a completar)', 'D35': '(a completar)', 'D36': '(a completar)',
        'B40': 'Borrador de escritorio con fuentes públicas y un modelo de puntaje por perfil de ciudad (ver resumen comparativo). No hubo talleres con actores; cada respuesta indica su confianza y qué validar.',
    }

PREF = '[Borrador de escritorio nov-2026, puntaje modelado por perfil de ciudad;'
filas = []
for c in CI.CIUDADES:
    en, es = respuestas_ciudad(c)
    info = info_ciudad(c)
    o1 = os.path.join(outdir, f"Scorecard_UNDRR_{c['id']}_detallado_EN.xlsm")
    o2 = os.path.join(outdir, f"Scorecard_UNDRR_{c['id']}_salud_publica_ES.xlsm")
    r1 = rellenar(os.path.join(scr, SRC_EN), os.path.join(scr, 'x_en'), os.path.join(scr, 'preguntas_en.json'), en, info, PREF, o1)
    r2 = rellenar(os.path.join(scr, SRC_ES), os.path.join(scr, 'x_es'), os.path.join(scr, 'preguntas_es.json'), es, info, PREF, o2)
    por_e = {}
    for sh, ref, sc, conf in r1: por_e[sh] = por_e.get(sh, 0) + sc
    filas.append([c['nombre'], CI.PAIS[c['iso']][0], c['pob']] + [por_e.get('E%02d' % i, 0) for i in range(1, 11)] + [sum(x[2] for x in r1), sum(x[2] for x in r2)])
    print('ok', c['nombre'], filas[-1][-2], filas[-1][-1])
json.dump(filas, open(os.path.join(scr, 'filas_resumen.json'), 'w'), ensure_ascii=False)
