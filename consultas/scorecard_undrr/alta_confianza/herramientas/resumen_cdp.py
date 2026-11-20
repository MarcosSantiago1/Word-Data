"""Resume lo que cada ciudad declaró a CDP-ICLEI en 2023 (preguntas útiles para el scorecard UNDRR).
uso: python resumen_cdp.py <cdp_cities_2023_ciudades_prioridad.csv> <carpeta_salida>
Deja evidencia/cdp_<org>.txt con pregunta, fila, columna y respuesta.
"""
import sys, os
import pandas as pd
d = pd.read_csv(sys.argv[1], low_memory=False, dtype=str)
UTILES = ['0.1', '0.2', '0.4', '0.5', '1.1', '1.1a', '1.2', '1.3', '3.8', '3.10', '3.13', '4.1', '4.1a', '7.1', '7.1a', '7.2', '7.5', '7.6', '8.1', '10.1']
for org, g in d.groupby('organization_number'):
    g = g[g.question_number.isin(UTILES) & g.response_answer.notna()]
    g = g.assign(o=g.question_number.map(UTILES.index), rn=pd.to_numeric(g.row_number, errors='coerce'), cn=pd.to_numeric(g.column_number, errors='coerce')).sort_values(['o', 'rn', 'cn'])
    lin = [f"# CDP Cities 2023 - {g.organization_name.iloc[0]} (org {org}) https://www.cdp.net/en/responses/{org}"]
    for (q, rn), h in g.groupby(['question_number', 'rn'], sort=False):
        lin.append(f"\n[{q} fila {int(rn) if rn == rn else '-'}] {h.question_name.iloc[0][:120]}")
        for _, r in h.iterrows():
            lin.append(f"  - {str(r.column_name)[:70]}: {str(r.response_answer)[:900]}")
    open(os.path.join(sys.argv[2], f'cdp_{org}.txt'), 'w').write('\n'.join(lin))
    print(org, g.organization_name.iloc[0], len(g))
