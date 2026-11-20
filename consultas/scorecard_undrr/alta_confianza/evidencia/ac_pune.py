# Pune (Pune Municipal Corporation): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'pune', 'Pune', 'IND'
OFICINA = 'Pune Municipal Corporation'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'lm_cell': ('https://www.lokmattimes.com/pune/flood-alert-in-pune-pmc-activates-24x7-disaster-cell-installs-500-cctvs-in-high-risk-zones-a475', 'Lokmat Times: alerta de inundación en Pune; la corporación activa su célula de desastres 24x7 e instala 500 cámaras en zonas de alto riesgo', '2025'),
    'bc_73': ('https://www.thebridgechronicle.com/pune/punepune-identifies-73-new-flood-prone-spots-pmc-disaster-cell-shelters-monsoon', 'The Bridge Chronicle: Pune identifica 73 nuevos puntos de anegamiento; la corporación activa la célula de desastres y 71 refugios antes del monzón', '2025'),
    'fpj_caos': ('https://www.freepressjournal.in/amp/pune/pmc-in-action-mode-pune-mayor-manjusha-nagpure-pulls-up-administration-after-flood-chaos', 'Free Press Journal: la alcaldesa de Pune reprende a la administración tras el caos por inundaciones', 's/f'),
}

EN = {
    '1.2.2': (3, M, 'Antes del monzón la corporación identificó 73 nuevos puntos de anegamiento, habilitó 71 refugios y desplegó bombas y botes, pero tras las inundaciones la alcaldesa reprendió a la administración por fallas en la respuesta.',
        'bc_73,fpj_caos', 'Definir roles y rendición de cuentas en la respuesta.', 'Pune Municipal Corporation', CORTO),
    '9.6.2': (2, M, 'La célula de desastres de la corporación funciona 24x7 en el monzón y se instalaron 500 cámaras en zonas de alto riesgo; no se informan procedimientos probados.',
        'lm_cell', 'Procedimientos y participación de todas las agencias.', 'Pune Municipal Corporation', MED),
}
ES = {
}
