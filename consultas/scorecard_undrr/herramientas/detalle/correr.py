"""Genera los scorecards detallados (EN + salud ES) de una o varias ciudades desde detalle/resp_<id>.py.
uso: python detalle/correr.py <carpeta_scratch> <carpeta_salida> id1 [id2 ...]
"""
import sys, os, json, importlib
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H); sys.path.insert(0, os.path.dirname(H))
import ciudades as CI
from relleno import rellenar
scr, outdir = sys.argv[1], sys.argv[2]
SRC_EN = [f for f in os.listdir(scr) if f.startswith('b7352477') and f.endswith('.xlsm')][0]
SRC_ES = [f for f in os.listdir(scr) if f.startswith('40097900') and f.endswith('.xlsm')][0]
PEN = json.load(open(os.path.join(scr, 'preguntas_en.json'))); PES = json.load(open(os.path.join(scr, 'preguntas_es.json')))
fj = os.path.join(scr, 'filas_detalle.json')
filas = json.load(open(fj)) if os.path.exists(fj) else {}
for cid in sys.argv[3:]:
    m = importlib.import_module('resp_' + cid)
    faltan = [q['ref'] for q in PEN if q['ref'] not in m.EN] + [q['ref'] for q in PES if q['ref'] not in m.ES]
    assert not faltan, (cid, faltan)
    norm = lambda d: {k: (v[0], v[1], v[2], 'Sin acción.' if v[3].startswith('Sin acción') else v[3], v[4], v[5]) for k, v in d.items()}
    c = next(x for x in CI.CIUDADES if x['id'] == cid)
    pais, pibpc, gini = CI.PAIS[c['iso']]
    info = dict(m.INFO)
    if info.get('C28') is None: info['C28'], info['D28'] = pibpc, f'PIB per cápita de {pais} en USD corrientes 2024 (Banco Mundial, panel del proyecto)'
    if info.get('C29') is None:
        info['C29'] = gini if gini else 's/d'
        info['D29'] = (f'Gini de {pais} 2024 (Banco Mundial); no es el de la ciudad' if gini else 'Sin dato reciente del Banco Mundial') + getattr(m, 'GINI_NOTA', '')
    pref = f'[Borrador detallado de escritorio nov-2026, a validar con el gobierno local;'
    o1 = os.path.join(outdir, f'Scorecard_UNDRR_{cid}_detallado_EN.xlsm')
    o2 = os.path.join(outdir, f'Scorecard_UNDRR_{cid}_salud_publica_ES.xlsm')
    r1 = rellenar(os.path.join(scr, SRC_EN), os.path.join(scr, 'x_en'), os.path.join(scr, 'preguntas_en.json'), norm(m.EN), info, pref, o1)
    r2 = rellenar(os.path.join(scr, SRC_ES), os.path.join(scr, 'x_es'), os.path.join(scr, 'preguntas_es.json'), norm(m.ES), info, pref, o2)
    por_e = {}
    for sh, ref, sc, conf in r1: por_e[sh] = por_e.get(sh, 0) + sc
    confs = [x[3] for x in r1 + r2]
    filas[cid] = [m.NOMBRE, pais, c['pob']] + [por_e.get('E%02d' % i, 0) for i in range(1, 11)] + [sum(x[2] for x in r1), sum(x[2] for x in r2), confs.count('alta'), confs.count('media'), confs.count('baja')]
    print('ok', cid, filas[cid][-5:])
json.dump(filas, open(fj, 'w'), ensure_ascii=False)
