# Medán (Gobierno de la Ciudad; BPBD Kota Medan): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'medan', 'Medán', 'IDN'
OFICINA = 'BPBD Kota Medan'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/54306', 'CDP-ICLEI Cities 2023: respuesta oficial de el Gobierno de la Ciudad de Medán', '2023'),
    'rpb': ('https://ppid.medan.go.id/storage/dokumen/xA2J1WilePhhmYSfQP360gbOqzlEnQS8AwWmHUmg.pdf', 'Gobierno de la Ciudad de Medán (PPID): Rencana Penanggulangan Bencana (plan de gestión de desastres) 2022-2027, con evaluación de riesgo de julio a septiembre de 2022 (no se pudo descargar)', '2022'),
}

EN = {
    '1.1.1': (4, C, 'La ciudad considera los riesgos climáticos en sus planes, estrategias y objetivos de desempeño, y tiene metas de adaptación (CDP 2023).',
        'cdp', 'Llevar los escenarios futuros al plan de la ciudad.', 'Bappeda Kota Medan', MED),
    '2.1.1': (3, C, 'Evaluación de riesgo climático de 2023 hecha con una organización internacional y consultores, con consulta a socios, priorización de amenazas y población vulnerable (CDP 2023); la ciudad tiene además un plan de gestión de desastres 2022-2027 con evaluación de riesgo. No se informa revisión de terceros ni escenario de altas emisiones.',
        'cdp,rpb', 'Revisión externa y escenario RCP 8.5.', 'BPBD / Bappeda', MED),
    '2.2.1': (3, C, 'La ciudad estima que el 20-30% de la población está expuesta a inundación urbana y menos del 10% al calor extremo y a la inundación costera (rob) en Medan Belawan (CDP 2023).',
        'cdp', 'Escenarios "más probable" y "más grave".', 'BPBD Kota Medan', MED),
}
ES = {
    'A2.2': (3, C, 'La ciudad identifica efectos de lluvias, calor, estrés hídrico e inundación costera en la salud, incluidos la interrupción del agua y saneamiento, daños a la infraestructura sanitaria e infecciones por agua, y la falta de vigilancia y alerta sanitaria informada por el clima (CDP 2023).',
        'cdp', 'Plan de salud por escenario.', 'Dinas Kesehatan Kota Medan', MED),
}
