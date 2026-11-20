"""Arma la base de alta confianza del scorecard UNDRR (141 preguntas con evidencia) y rehace los .xlsm.

Cada ciudad tiene evidencia/ac_<id>.py y cada país evidencia/pais_<ISO3>.py, con:
  F  = {clave: (url, título, fecha del documento)}               fuentes
  EN = {ref: (puntaje, confianza, texto, 'clave1,clave2', acción, responsable, plazo)}   118 preguntas de la herramienta detallada
  ES = {ref: (...)}                                              23 preguntas del anexo de salud pública
La ciudad hereda las respuestas de su provincia (evidencia/prov_<PROV>.py, si define PROV) y de su país que no responde ella misma.
Confianza:
  alta  = lo dice un documento oficial (ciudad, provincia o país), la propia ciudad ante CDP-ICLEI, o un hecho o declaración oficial
          que publican varios medios de referencia; y el puntaje sale directo de ahí
  media = una sola fuente secundaria confiable (organismo internacional, prensa de referencia, estudio académico)
          o un dato oficial que hay que interpretar para puntuar
  sin evidencia = no se encontró nada público: el puntaje queda vacío (en el .xlsm, la pregunta queda sin opción marcada)

uso: python armar_base.py <carpeta alta_confianza> [--sin-xlsm] [--solo id1,id2]
Deja: datos/base_alta_confianza.csv, datos/fuentes_alta_confianza.csv, datos/resumen_ciudades.csv,
      datos/base_alta_confianza.sqlite y xlsm/Scorecard_UNDRR_<id>_alta_confianza_{EN,salud_ES}.xlsm
"""
import sys, os, json, glob, importlib, sqlite3, zipfile, shutil
import pandas as pd

AC = os.path.abspath(sys.argv[1])
H = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(os.path.dirname(AC), 'herramientas')
MUNDO = os.path.join(os.path.dirname(AC), 'mundo')
EV = os.path.join(AC, 'evidencia')
sys.path.insert(0, EV); sys.path.insert(0, H)
SIN_XLSM = '--sin-xlsm' in sys.argv
SOLO = sys.argv[sys.argv.index('--solo') + 1].split(',') if '--solo' in sys.argv else None
FECHA = '2026-11'
PEN = json.load(open(os.path.join(BASE, 'preguntas_en.json'))); PES = json.load(open(os.path.join(BASE, 'preguntas_es.json')))
CONF_OK = {'alta', 'media'}

def opciones(q):
    return {int(o.strip()[0]) for o in q['options'] if o.strip()[:1].isdigit()}

def cargar(cid):
    m = importlib.import_module('ac_' + cid)
    p = importlib.import_module('pais_' + m.ISO3) if os.path.exists(os.path.join(EV, f'pais_{m.ISO3}.py')) else None
    pr = importlib.import_module('prov_' + m.PROV) if getattr(m, 'PROV', None) else None  # provincia o estado, si aplica
    F = {**(p.F if p else {}), **(pr.F if pr else {}), **m.F}
    filas, err = [], []
    for herr, P, dc, dr, dp in (('detallada_EN', PEN, m.EN, getattr(pr, 'EN', {}), getattr(p, 'EN', {})),
                                ('salud_ES', PES, m.ES, getattr(pr, 'ES', {}), getattr(p, 'ES', {}))):
        for q in P:
            ref = q['ref']
            r = dc.get(ref, dr.get(ref, dp.get(ref)))
            origen = 'ciudad' if ref in dc else 'provincia' if ref in dr else 'país' if ref in dp else ''
            if r is None:
                r = (None, 'sin evidencia', 'No se encontró evidencia pública verificable para esta pregunta.', '',
                     'Relevar el dato con el gobierno local y publicarlo.', m.OFICINA, 'Corto plazo (≤1 año)')
            p_, conf, txt, fu, acc, resp, plazo = (list(r) + [''] * 7)[:7]
            if p_ is not None and p_ not in opciones(q): err.append(f'{ref}: puntaje {p_} no es opción')
            if p_ is not None and conf not in CONF_OK: err.append(f'{ref}: confianza {conf}')
            claves = [k.strip() for k in str(fu).split(',') if k.strip()]
            if p_ is not None and not claves: err.append(f'{ref}: sin fuente')
            for k in claves:
                if k not in F: err.append(f'{ref}: fuente {k} no definida')
            filas.append(dict(id=m.ID, ciudad=m.NOMBRE, iso3=m.ISO3, herramienta=herr, esencial=q['sheet'], ref=ref, titulo=q['title'],
                              puntaje=p_, confianza=conf, evidencia=txt, fuentes=';'.join(claves),
                              urls=' | '.join(F[k][0] for k in claves if k in F), origen=origen,
                              accion=acc, responsable=resp, plazo=plazo, fecha_consulta=FECHA))
    fuentes = [dict(id=m.ID, clave=k, url=v[0], titulo=v[1], fecha_documento=v[2]) for k, v in F.items()]
    assert not err, (cid, err)
    return m, filas, fuentes, F

def info_de(cid):
    """Reusa la hoja Info del .xlsm del modelo mundial de esa ciudad."""
    import openpyxl
    f = os.path.join(MUNDO, 'xlsm', f'Scorecard_UNDRR_{cid}_detallado_EN.xlsm')
    if not os.path.exists(f): return {}
    ws = openpyxl.load_workbook(f, read_only=True)['Info']
    return {c.coordinate: c.value for row in ws.iter_rows(min_col=3, max_col=4) for c in row if c.value is not None}

def main():
    ids = sorted(os.path.basename(f)[3:-3] for f in glob.glob(os.path.join(EV, 'ac_*.py')))
    if SOLO: ids = [i for i in ids if i in SOLO]
    todas, fuentes, res = [], [], []
    from relleno_ac import rellenar
    up = '/mnt/project-files/uploads/hearth'
    src = {'en': os.path.join(up, 'b7352477-5507-4cd1-b3cb-1fe07032f54f'), 'es': os.path.join(up, '40097900-3919-4f9c-abc7-55dfac8dcf35')}
    tmp = os.environ.get('SCORECARD_TMP', '/tmp/scorecard_ac'); os.makedirs(tmp, exist_ok=True)
    xd = {}
    for k, z in src.items():
        x = os.path.join(tmp, f'x_{k}')
        if not os.path.exists(x):
            with zipfile.ZipFile(z) as zz: zz.extractall(x)
        xd[k] = x
    os.makedirs(os.path.join(AC, 'xlsm'), exist_ok=True)
    for cid in ids:
        m, filas, fu, F = cargar(cid)
        todas += filas; fuentes += fu
        d = pd.DataFrame(filas)
        con = d[d.puntaje.notna()]
        en = d[d.herramienta == 'detallada_EN']; es = d[d.herramienta == 'salud_ES']
        res.append(dict(id=m.ID, ciudad=m.NOMBRE, iso3=m.ISO3, preguntas=len(d), con_evidencia=len(con),
                        alta=(d.confianza == 'alta').sum(), media=(d.confianza == 'media').sum(), sin_evidencia=(d.confianza == 'sin evidencia').sum(),
                        cobertura_pct=round(100 * len(con) / len(d)),
                        puntaje_EN_con_evidencia=int(en.puntaje.sum()), maximo_EN_respondidas=5 * int(en.puntaje.notna().sum()),
                        nivel_medio_EN=round(en.puntaje.mean(), 2), puntaje_salud_con_evidencia=int(es.puntaje.sum()),
                        nivel_medio_salud=round(es.puntaje.mean(), 2), fuentes=len(F)))
        if not SIN_XLSM:
            info = info_de(cid)
            for k, herr, nom in (('en', 'detallada_EN', 'EN'), ('es', 'salud_ES', 'salud_ES')):
                P = PEN if k == 'en' else PES
                R = {}
                for f in filas:
                    if f['herramienta'] != herr: continue
                    citas = '; '.join(f'{F[c][1]} ({F[c][2]}) {F[c][0]}' for c in f['fuentes'].split(';') if c)
                    txt = f['evidencia'] + (f' Fuentes: {citas}' if citas else '')
                    R[f['ref']] = (None if pd.isna(f['puntaje']) else int(f['puntaje']), f['confianza'], txt, f['accion'] or 'Sin acción.', f['responsable'], f['plazo'])
                o = os.path.join(tmp, f'Scorecard_UNDRR_{cid}_alta_confianza_{nom}.xlsm')
                rellenar(src[k], xd[k], os.path.join(BASE, f'preguntas_{k}.json'), R, info, '[Base de alta confianza, nov-2026; confianza', o)
                shutil.move(o, os.path.join(AC, 'xlsm', os.path.basename(o)))
        print('ok', cid, res[-1]['con_evidencia'], 'de', res[-1]['preguntas'], '| alta', res[-1]['alta'], 'media', res[-1]['media'])
    D = os.path.join(AC, 'datos'); os.makedirs(D, exist_ok=True)
    b = pd.DataFrame(todas); f = pd.DataFrame(fuentes); r = pd.DataFrame(res)
    if SOLO:  # sumar a lo que ya había
        for nombre, df in (('base_alta_confianza', b), ('fuentes_alta_confianza', f), ('resumen_ciudades', r)):
            p = os.path.join(D, nombre + '.csv')
            if os.path.exists(p):
                viejo = pd.read_csv(p)
                df = pd.concat([viejo[~viejo.id.isin(ids)], df])
            if nombre == 'base_alta_confianza': b = df
            elif nombre == 'fuentes_alta_confianza': f = df
            else: r = df
    b.to_csv(os.path.join(D, 'base_alta_confianza.csv'), index=False)
    f.to_csv(os.path.join(D, 'fuentes_alta_confianza.csv'), index=False)
    r.to_csv(os.path.join(D, 'resumen_ciudades.csv'), index=False)
    s = os.path.join(D, 'base_alta_confianza.sqlite')
    if os.path.exists(s): os.remove(s)
    with sqlite3.connect(s) as c:
        b.to_sql('respuestas', c, index=False); f.to_sql('fuentes', c, index=False); r.to_sql('ciudades', c, index=False)
    print(len(r), 'ciudades;', len(b), 'respuestas;', int(b.puntaje.notna().sum()), 'con evidencia')

if __name__ == '__main__':
    main()
