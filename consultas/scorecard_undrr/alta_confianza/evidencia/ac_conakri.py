# Conakri (Ville de Conakry; ANGUCH): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'conakri', 'Conakri', 'GIN'
OFICINA = 'ANGUCH / Gouvernorat de Conakry'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'gn_plan': ('https://guineenews.org/2025/07/15/inondations-a-conakry-le-gouvernement-decline-son-plan-durgence/', 'Guinéenews: inundaciones en Conakri, el gobierno presenta su plan de urgencia', '2025'),
    'gn_bilan': ('https://guineenews.org/2025/07/14/inondations-a-conakry-et-ses-environs-plus-de-4-000-sinistres-et-six-morts-bilan-provisoire/', 'Guinéenews: inundaciones en Conakri y alrededores, más de 4.000 damnificados y seis muertos (balance provisorio de la ANGUCH)', '2025'),
}

EN = {
    '1.2.2': (2, M, 'En julio de 2025, con más de 4.000 damnificados, el gobierno adoptó un plan de acción inmediato (limpieza de canales, drenaje pluvial) y decretó la movilización general; la agencia ANGUCH hace los balances. No se publica un plan de coordinación con roles definidos.',
        'gn_plan,gn_bilan', 'Plan de coordinación de la respuesta con roles por institución.', 'ANGUCH / Gouvernorat de Conakry', CORTO),
}
ES = {
}
