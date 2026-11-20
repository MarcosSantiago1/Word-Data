"""Arma datos/indicadores_pais.csv: el último dato disponible de cada indicador del país, desde el panel del proyecto
(etl/datos_procesados/paises_anual.csv). Taiwán no está en el Banco Mundial: sus valores van en paises.py (extra).
uso: python indicadores_pais.py <carpeta de datos> [panel paises_anual.csv]
"""
import sys, os
import pandas as pd

D = sys.argv[1]
c = pd.read_csv(os.path.join(D, 'ciudades_mundo.csv'))
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
PANEL = sys.argv[2] if len(sys.argv) > 2 else os.path.join(RAIZ, 'etl', 'datos_procesados', 'paises_anual.csv')
p = pd.read_csv(PANEL, low_memory=False).copy()
p['pib_pc_usd'] = p.pib_usd / p.poblacion
V = ['pais', 'region', 'nivel_ingreso', 'efectividad_gobierno', 'calidad_regulatoria', 'indice_estado_derecho_0_100', 'indice_control_corrupcion_0_100',
     'voz_rendicion_cuentas', 'pib_pc_usd', 'pib_pc_ppp', 'camas_hospital_x1000', 'medicos_x1000', 'gasto_salud_pct_pib', 'gini',
     'stock_migrantes_pct_poblacion', 'usuarios_internet_pct', 'muertes_desastres_climaticos', 'personas_afectadas_desastres_climaticos',
     'indice_sociedad_civil_0_1', 'esperanza_vida']
filas = []
for iso in sorted(c.iso3.unique()):
    d = p[p.iso3 == iso].sort_values('anio')
    f = {'iso3': iso}
    for v in V:
        s = d[['anio', v]].dropna()
        f[v] = s[v].iloc[-1] if len(s) else None
        if v not in ('pais', 'region', 'nivel_ingreso'): f[v + '_anio'] = int(s.anio.iloc[-1]) if len(s) else None
    filas.append(f)
pd.DataFrame(filas).to_csv(os.path.join(D, 'indicadores_pais.csv'), index=False)
print(len(filas), 'países')
