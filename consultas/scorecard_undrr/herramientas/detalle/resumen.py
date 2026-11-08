"""Arma Resumen_comparativo_scorecards_UNDRR.xlsx con los puntajes detallados de las 15 ciudades + CABA.
uso: python detalle/resumen.py <carpeta_scratch> <xlsx_viejo_modelado> <xlsx_salida>
"""
import sys, os, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H); sys.path.insert(0, os.path.dirname(H))
from collections import Counter
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import ColorScaleRule
import respuestas as CABA

scr, viejo, salida = sys.argv[1:4]
PEN = json.load(open(os.path.join(scr, 'preguntas_en.json')))
n_e = Counter(q['sheet'] for q in PEN)
MAX = {e: 5 * n for e, n in n_e.items()}
ESEN = ['1 Organizar', '2 Riesgos', '3 Finanzas', '4 Desarrollo urbano', '5 Ecosistemas', '6 Capacidad institucional',
        '7 Capacidad social', '8 Infraestructura', '9 Respuesta', '10 Recuperación']
filas = json.load(open(os.path.join(scr, 'filas_detalle.json')))

# CABA desde respuestas.py
sec = {q['ref']: q['sheet'] for q in PEN}
por_e = Counter()
for ref, v in CABA.EN.items(): por_e[sec[ref]] += v[0]
confs = [v[1] for v in list(CABA.EN.values()) + list(CABA.ES.values())]
filas['caba'] = ['Buenos Aires (CABA)', 'Argentina', 3121707] + [por_e['E%02d' % i] for i in range(1, 11)] + \
    [sum(v[0] for v in CABA.EN.values()), sum(v[0] for v in CABA.ES.values()), confs.count('alta'), confs.count('media'), confs.count('baja')]

# totales modelados anteriores (para comparar)
old = {}
wbo = openpyxl.load_workbook(viejo)
for r in wbo['Resumen'].iter_rows(min_row=2, values_only=True):
    if r[0]: old['Santiago de Cali' if r[0].startswith('Cali') else r[0].split(' (Municipio')[0]] = (r[13], r[15])

wb = openpyxl.Workbook()
neg = Font(bold=True); cab = PatternFill('solid', fgColor='1F4E78'); blanco = Font(bold=True, color='FFFFFF')
def encabezar(ws, cols):
    ws.append(cols)
    for c in ws[1]: c.font = blanco; c.fill = cab; c.alignment = Alignment(wrap_text=True, vertical='center')
    ws.row_dimensions[1].height = 45; ws.freeze_panes = 'B2'

ws = wb.active; ws.title = 'Resumen'
encabezar(ws, ['Ciudad', 'País', 'Población'] + [e + ' (%)' for e in ESEN] +
          ['Total detallado (de 590)', 'Total %', 'Salud pública (de 115)', 'Salud %', 'Nota'])
orden = sorted(filas.items(), key=lambda kv: -kv[1][13])
for cid, f in orden:
    pct = [round(100 * f[3 + i] / MAX['E%02d' % (i + 1)]) for i in range(10)]
    nota = 'Línea de base (evaluación original)' if cid == 'caba' else ''
    ws.append([f[0], f[1], f[2]] + pct + [f[13], round(100 * f[13] / 590), f[14], round(100 * f[14] / 115), nota])
    if cid == 'caba':
        for c in ws[ws.max_row]: c.font = neg
n = ws.max_row
ws.conditional_formatting.add(f'D2:M{n}', ColorScaleRule(start_type='num', start_value=0, start_color='F8696B',
                              mid_type='num', mid_value=50, mid_color='FFEB84', end_type='num', end_value=100, end_color='63BE7B'))
for col in ('O', 'Q'):
    ws.conditional_formatting.add(f'{col}2:{col}{n}', ColorScaleRule(start_type='num', start_value=0, start_color='F8696B',
                                  mid_type='num', mid_value=50, mid_color='FFEB84', end_type='num', end_value=100, end_color='63BE7B'))
for c in ws['C'][1:]: c.number_format = '#,##0'
ws.column_dimensions['A'].width = 32; ws.column_dimensions['B'].width = 12; ws.column_dimensions['C'].width = 12
for col in 'DEFGHIJKLMNOPQ': ws.column_dimensions[col].width = 12
ws.column_dimensions['R'].width = 34

ws2 = wb.create_sheet('Confianza')
encabezar(ws2, ['Ciudad', 'Respuestas con confianza alta', 'Media', 'Baja', '% baja (de 141)'])
for cid, f in orden:
    ws2.append([f[0], f[15], f[16], f[17], round(100 * f[17] / 141)])
ws2.column_dimensions['A'].width = 32
for col in 'BCDE': ws2.column_dimensions[col].width = 16

ws3 = wb.create_sheet('Modelado vs detallado')
encabezar(ws3, ['Ciudad', 'Total modelado (versión anterior)', 'Total detallado', 'Diferencia', 'Salud modelado', 'Salud detallado', 'Diferencia salud'])
for cid, f in orden:
    if cid == 'caba': continue
    k = f[0].split(' (Municipio')[0]
    om = old.get(k) or next((v for kk, v in old.items() if kk.split(' (')[0] == k.split(' (')[0]), (None, None))
    ws3.append([f[0], om[0], f[13], (f[13] - om[0]) if om[0] is not None else None, om[1], f[14], (f[14] - om[1]) if om[1] is not None else None])
ws3.column_dimensions['A'].width = 32
for col in 'BCDEFG': ws3.column_dimensions[col].width = 16

ws4 = wb.create_sheet('Método')
txt = [
    'Cómo se armaron estos puntajes (borrador detallado de escritorio, 7-nov-2026)', None,
    '1. Ciudades: gobiernos locales de América Latina con más de 2 millones de habitantes (municipio, distrito o entidad con gobierno propio), más CABA como línea de base.',
    '2. Cada ciudad tiene sus 141 respuestas propias (118 de la herramienta detallada en inglés y 23 de la adenda de salud pública en español), escritas una por una con evidencia de la ciudad, igual que CABA.',
    '3. Fuentes: la base del proyecto (población, PIB per cápita y Gini del país) más 2 a 4 búsquedas web por ciudad sobre el organismo y el plan de gestión del riesgo, los desastres recientes, el agua y la energía, la salud y los datos de población. Los textos citan la fuente cuando es puntual.',
    '4. Eventos de 2026 incorporados: terremoto de Colombia del 10-ago (M7,4; Cali con unas 154 muertes, Medellín y Bogotá con daños leves) y terremotos de Venezuela del 24-jun (Mw 7,2 y 7,5; edificios colapsados en Caracas).',
    '5. Cada respuesta trae su confianza: alta (dato oficial verificado), media (fuente secundaria o dato parcial) o baja (inferencia o estimación). Ver la hoja Confianza.',
    '6. Cada respuesta trae una acción sugerida, el organismo responsable y el plazo (filas de acción de cada pregunta).',
    '7. La hoja Info de cada archivo tiene el perfil de la ciudad; los datos que no se encontraron quedan como "s/d" o "≈ ... (estimación)" con qué fuente usar para validarlos.',
    None,
    'Limitaciones: sigue siendo un borrador de escritorio, no la autoevaluación que pide UNDRR (que se hace en talleres con el gobierno local). La mayoría de las respuestas tiene confianza baja. Sirve para priorizar dónde mirar y para preparar los talleres, no para afirmar el nivel de resiliencia de una ciudad.',
    'Las cifras de los terremotos de 2026 cambian según la fecha de corte y la fuente; conviene revisarlas antes de citarlas.',
    None,
    'Ciudades evaluadas y descartadas:',
    '- Santiago de Chile: ninguna comuna supera 2 millones; la Región Metropolitana tiene gobierno regional, no municipal',
    '- La Habana: 1,81 millones de habitantes en 2023 (ONEI)',
    '- Monterrey, Guadalajara, Puebla, Tijuana: ningún municipio supera 2 millones (Tijuana 1,92 millones en 2020)',
    '- Santo Domingo, Guatemala, Montevideo, Asunción, Santa Cruz de la Sierra: el gobierno local no llega a 2 millones',
    '- Recife, Curitiba, Porto Alegre, Goiânia: el municipio no llega a 2 millones; sí las áreas metropolitanas',
]
for t in txt: ws4.append([t])
ws4['A1'].font = Font(bold=True, size=13); ws4.column_dimensions['A'].width = 150
for r in ws4.iter_rows():
    for c in r: c.alignment = Alignment(wrap_text=True, vertical='top')
wb.save(salida)
for cid, f in orden: print(f[0], f[13], f[14], f[17])
