"""Resumen mundial de los scorecards UNDRR y cruce con la amenaza de cada ciudad.

Lee datos/puntajes_mundo.csv (generar_mundo.py), datos/ghsl_ciudades.csv y datos/sismos_ciudades.csv.
Para las 16 ciudades latinoamericanas hechas a mano usa su puntaje a mano (el de sus archivos).
Genera:
  Resumen_scorecards_UNDRR_mundo.xlsx  hojas Ranking, Por país, Amenaza vs capacidad, Validación y Método
  datos/amenaza_capacidad_mundo.csv    índice de amenaza, puntaje y prioridad por ciudad
uso: python resumen_mundo.py <carpeta_mundo> [--datos <carpeta de datos>]   (datos por defecto: <carpeta_mundo>/datos)
"""
import sys, os, math
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import ColorScaleRule

M = sys.argv[1]
D = sys.argv[sys.argv.index('--datos') + 1] if '--datos' in sys.argv else os.path.join(M, 'datos')
p = pd.read_csv(os.path.join(D, 'puntajes_mundo.csv'))
g = pd.read_csv(os.path.join(D, 'ghsl_ciudades.csv'))
s = pd.read_csv(os.path.join(D, 'sismos_ciudades.csv'))
ESEN = ['E01', 'E02', 'E03', 'E04', 'E05', 'E06', 'E07', 'E08', 'E09', 'E10']
NOM = ['1 Organizar', '2 Riesgos', '3 Finanzas', '4 Desarrollo urbano', '5 Ecosistemas', '6 Capacidad institucional',
       '7 Capacidad social', '8 Infraestructura', '9 Respuesta', '10 Recuperación']
import json, collections
_PEN = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'herramientas', 'preguntas_en.json')))
MAX = {e: 5 * n for e, n in collections.Counter(q['sheet'] for q in _PEN).items()}

# puntaje final: el hecho a mano donde existe
p['total_590'] = p.mano_total_590.where(p.hecha_a_mano, p.modelo_total_590).astype(int)
p['salud_115'] = p.mano_salud_115.where(p.hecha_a_mano, p.modelo_salud_115).astype(int)
p['total_pct'] = (100 * p.total_590 / 590).round(0).astype(int)
p['metodo'] = p.hecha_a_mano.map({True: 'A mano (141 respuestas con búsqueda web)', False: 'Modelo mundial'})

# ---- índice de amenaza (0-1): promedio de rangos percentiles de exposición y ocurrencia ----
x = g[['id', 'EX_100_SHP_2025', 'EX_CF1_SHP_2025', 'EX_SHA_POP_2025', 'CL_UTC_T32_2020']].merge(s[['id', 'sismos_m6_150km_desde1900']], on='id')
for h in ('TCY', 'LAN', 'FLO'):
    x[f'ev_{h}'] = g[[f'HZ_CEV_{h}_{y}' for y in (2005, 2010, 2015)]].fillna(0).sum(axis=1)
comp = {'EX_100_SHP_2025': 'inundación fluvial', 'EX_CF1_SHP_2025': 'inundación costera', 'EX_SHA_POP_2025': 'zona sísmica',
        'sismos_m6_150km_desde1900': 'sismos históricos', 'CL_UTC_T32_2020': 'calor', 'ev_TCY': 'ciclones', 'ev_LAN': 'deslizamientos', 'ev_FLO': 'eventos de inundación'}
x = x.fillna(0)
x['indice_amenaza'] = sum(x[k].rank(pct=True) for k in comp) / len(comp)
p = p.merge(x[['id', 'indice_amenaza'] + list(comp)], on='id')
p['prioridad'] = (p.indice_amenaza * (1 - p.total_590 / 590)).round(3)  # amenaza alta y capacidad baja
p.sort_values('prioridad', ascending=False).to_csv(os.path.join(D, 'amenaza_capacidad_mundo.csv'), index=False)

def spearman(a, b):
    return round(pd.Series(a).rank().corr(pd.Series(b).rank()), 2)

wb = openpyxl.Workbook()
cab = PatternFill('solid', fgColor='1F4E78'); blanco = Font(bold=True, color='FFFFFF')
escala = lambda: ColorScaleRule(start_type='num', start_value=0, start_color='F8696B', mid_type='num', mid_value=50, mid_color='FFEB84',
                                end_type='num', end_value=100, end_color='63BE7B')
def encabezar(ws, cols, alto=45):
    ws.append(cols)
    for c in ws[1]: c.font = blanco; c.fill = cab; c.alignment = Alignment(wrap_text=True, vertical='center')
    ws.row_dimensions[1].height = alto; ws.freeze_panes = 'C2'

ws = wb.active; ws.title = 'Ranking'
encabezar(ws, ['Puesto', 'Ciudad', 'País', 'Región', 'Población'] + [n + ' (%)' for n in NOM] +
          ['Total (de 590)', 'Total %', 'Salud pública (de 115)', 'Salud %', 'Amenaza principal', 'Índice de amenaza (0-1)', 'Cómo se evaluó'])
r = p.sort_values('total_590', ascending=False).reset_index(drop=True)
for i, f in r.iterrows():
    if f.hecha_a_mano:
        pct = [None] * 10  # el detalle por Esencial a mano está en latam/Resumen_comparativo_scorecards_UNDRR.xlsx
    else:
        pct = [round(100 * f[f'modelo_{e}'] / MAX[e]) for e in ESEN]
    ws.append([i + 1, f.ciudad, f.pais, f.region, int(f.poblacion)] + pct +
              [int(f.total_590), int(f.total_pct), int(f.salud_115), round(100 * f.salud_115 / 115), f.amenaza_principal, round(f.indice_amenaza, 2), f.metodo])
    if f.hecha_a_mano:
        for c in ws[ws.max_row]: c.font = Font(bold=True)
n = ws.max_row
ws.conditional_formatting.add(f'F2:O{n}', escala()); ws.conditional_formatting.add(f'Q2:Q{n}', escala()); ws.conditional_formatting.add(f'S2:S{n}', escala())
for c in ws['E'][1:]: c.number_format = '#,##0'
for col, w in zip('ABCDE', (7, 30, 18, 26, 12)): ws.column_dimensions[col].width = w
for col in 'FGHIJKLMNOPQRS': ws.column_dimensions[col].width = 11
ws.column_dimensions['T'].width = 28; ws.column_dimensions['U'].width = 12; ws.column_dimensions['V'].width = 34

ws2 = wb.create_sheet('Por país')
encabezar(ws2, ['País', 'Región', 'Ciudades', 'Población total', 'Total % promedio', 'Mejor ciudad', 'Peor ciudad'])
for pais, d in p.groupby('pais'):
    d = d.sort_values('total_590', ascending=False)
    ws2.append([pais, d.region.iloc[0], len(d), int(d.poblacion.sum()), round(d.total_pct.mean()), f'{d.ciudad.iloc[0]} ({d.total_pct.iloc[0]}%)', f'{d.ciudad.iloc[-1]} ({d.total_pct.iloc[-1]}%)'])
ws2.conditional_formatting.add(f'E2:E{ws2.max_row}', escala())
for c in ws2['D'][1:]: c.number_format = '#,##0'
for col, w in zip('ABCDEFG', (24, 30, 10, 16, 12, 34, 34)): ws2.column_dimensions[col].width = w

ws3 = wb.create_sheet('Amenaza vs capacidad')
ws3.append(['¿Las ciudades más amenazadas tienen más capacidad? Correlación de rango (Spearman) entre el puntaje total y cada componente de la amenaza, en las 375 ciudades.'])
ws3['A1'].font = Font(bold=True)
ws3.append([])
ws3.append(['Componente', 'Spearman con el puntaje total', 'Lectura'])
for c in ws3[3]: c.font = blanco; c.fill = cab
for k, nom in list(comp.items()) + [('indice_amenaza', 'índice de amenaza combinado')]:
    rho = spearman(p[k], p.total_590)
    ws3.append([nom, rho, 'más amenaza va con más capacidad' if rho > 0.1 else 'más amenaza va con menos capacidad' if rho < -0.1 else 'sin relación clara'])
ws3.append([])
ws3.append(['Las 30 ciudades con más prioridad: amenaza alta y puntaje bajo (prioridad = índice de amenaza x (1 - puntaje/590))'])
ws3.cell(ws3.max_row, 1).font = Font(bold=True)
ws3.append(['Ciudad', 'País', 'Población', 'Índice de amenaza', 'Total %', 'Prioridad', 'Amenaza principal'])
for c in ws3[ws3.max_row]: c.font = blanco; c.fill = cab
for _, f in p.sort_values('prioridad', ascending=False).head(30).iterrows():
    ws3.append([f.ciudad, f.pais, int(f.poblacion), round(f.indice_amenaza, 2), int(f.total_pct), f.prioridad, f.amenaza_principal])
for col, w in zip('ABCDEFG', (34, 30, 14, 16, 10, 10, 30)): ws3.column_dimensions[col].width = w

ws4 = wb.create_sheet('Validación')
v = p[p.hecha_a_mano].sort_values('mano_total_590', ascending=False)
ws4.append([f'El modelo mundial aplicado a las 16 ciudades evaluadas a mano: correlación {round(v.modelo_total_590.corr(v.mano_total_590), 2)} '
            f'y error medio de {round((v.modelo_total_590 - v.mano_total_590).abs().mean())} puntos de 590 '
            f'({round(100 * (v.modelo_total_590 - v.mano_total_590).abs().mean() / 590)} puntos porcentuales).'])
ws4['A1'].font = Font(bold=True); ws4.append([])
ws4.append(['Ciudad', 'A mano (de 590)', 'Modelo (de 590)', 'Diferencia', 'Salud a mano (de 115)', 'Salud modelo (de 115)'])
for c in ws4[3]: c.font = blanco; c.fill = cab
for _, f in v.iterrows():
    ws4.append([f.ciudad, int(f.mano_total_590), int(f.modelo_total_590), int(f.modelo_total_590 - f.mano_total_590), int(f.mano_salud_115), int(f.modelo_salud_115)])
ws4.column_dimensions['A'].width = 46
for col in 'BCDEF': ws4.column_dimensions[col].width = 16

ws5 = wb.create_sheet('Método')
txt = [
 'Scorecard UNDRR para los gobiernos locales del mundo con más de 2 millones de habitantes (borrador de escritorio, 8-nov-2026)', None,
 '1. Ciudades: 375 gobiernos locales en 66 países (234 son ciudades de nivel de prefectura o municipios centrales de China). Misma definición que en Latinoamérica: gobierno local, no área metropolitana. Lista semilla de Wikidata depurada a mano.',
 '2. Las 16 ciudades latinoamericanas (CABA y 15 más) tienen sus 141 respuestas escritas a mano con búsqueda web; están en latam/ y no se tocaron.',
 '3. Las otras 359 salen de un modelo: cada respuesta parte de la media de esa pregunta en las 16 hechas a mano y se ajusta por un índice de capacidad del Esencial, que combina:',
 '   - país: efectividad del gobierno y estado de derecho (WGI), PIB por habitante, obligación legal de los gobiernos locales de tener unidad, plan y fondo de gestión del riesgo, alerta temprana, seguros, camas y médicos, sociedad civil (V-Dem), trayectoria en gestión del riesgo y conflicto armado;',
 '   - ciudad: IDH subnacional del centro urbano (GHSL), redes de ciudades (C40, Resilient Cities Network, MCR2030), rango del gobierno local, informalidad estimada y hechos del perfil.',
 '4. Reglas directas por pregunta: gas por cañería y sismicidad (8.4), metro (8.5.3), puerto (8.5.5), seguros (3.3), fondo de contingencia (3.2.4), alerta (9.1), informalidad (4.3 y 4.4), redes (6.6.1), salud (8.7).',
 '5. Hechos puntuales del perfil de cada ciudad (desastres recientes, obras, cortes de servicios) fijan algunas respuestas con confianza media; el resto queda con confianza baja.',
 '6. Datos de amenaza de cada ciudad: GHSL Urban Centre Database R2024A de la Comisión Europea (exposición a inundación fluvial y costera, zona sísmica, ciclones, calor, catálogo multiamenaza 2005-2015, infraestructura crítica) y catálogo sísmico del USGS (sismos M6+ a menos de 150 km desde 1900).',
 '7. Validación: el modelo aplicado a las 16 hechas a mano tiene correlación de alrededor de 0,6 con los puntajes a mano (ver hoja Validación). Sirve para ordenar y comparar grupos de ciudades; la diferencia en una ciudad puntual puede ser grande.',
 None,
 'Limitaciones: no hubo talleres ni búsqueda por pregunta en las 359 ciudades del modelo. Los perfiles de ciudad se escribieron con conocimiento general y conviene verificarlos. En China, las ciudades de nivel de prefectura incluyen condados rurales; los datos de amenaza son los del centro urbano principal. Los datos de población tienen años distintos (India usa el censo 2011).',
 'Cada archivo .xlsm lleva en el comentario de cada respuesta el hecho usado, el nivel estimado y la capacidad del modelo frente a la media de las 16.',
]
for t in txt: ws5.append([t])
ws5['A1'].font = Font(bold=True, size=13); ws5.column_dimensions['A'].width = 160
for row in ws5.iter_rows():
    for c in row: c.alignment = Alignment(wrap_text=True, vertical='top')
wb.save(os.path.join(M, 'Resumen_scorecards_UNDRR_mundo.xlsx'))
print('ok', len(p), 'ciudades;', 'Spearman puntaje vs índice de amenaza', spearman(p.indice_amenaza, p.total_590))
print(p.sort_values('prioridad', ascending=False)[['ciudad', 'pais', 'indice_amenaza', 'total_pct', 'prioridad']].head(12).to_string())
