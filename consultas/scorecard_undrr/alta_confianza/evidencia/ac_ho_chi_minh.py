# Ciudad Ho Chi Minh (Comité Popular; Comité Directivo de Prevención de Desastres): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'ho_chi_minh', 'Ciudad Ho Chi Minh', 'VNM'
OFICINA = 'Comité Directivo de Prevención de Desastres, Búsqueda y Rescate de Ciudad Ho Chi Minh'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/31164', 'CDP-ICLEI Cities 2023: respuesta oficial de la Ciudad Ho Chi Minh', '2023'),
    'sggp_rev': ('https://en.sggp.org.vn/hcmc-reviews-finalizes-disaster-prevention-and-response-plans-for-2026-post123533.html', 'SGGP: la Ciudad Ho Chi Minh revisa 2025 y cierra sus planes de prevención y respuesta ante desastres para 2026', '2026'),
}

EN = {
    '1.1.3': (2, C, 'El Plan de Acción ante el Cambio Climático 2021-2030 (Decisión 3273/QD-UBND) se monitorea cada año y se evalúa al menos cada cinco años (CDP 2023); no se informa revisión hecha.',
        'cdp', 'Revisar y publicar.', 'Comité Popular', MED),
    '2.2.1': (3, C, 'La ciudad estima que el 70-80% de la población está expuesta al estrés térmico, el 60-70% a lluvias intensas y el 10-20% a inundación costera, tormentas y deslizamientos (CDP 2023); no informa escenarios.',
        'cdp', 'Escenarios por amenaza.', 'Comité Popular', MED),
    '10.2.1': (3, M, 'En enero de 2026 la ciudad revisó la respuesta a los desastres de 2025 y cerró sus planes para 2026, advirtiendo contra la complacencia; no se publica un informe de lecciones.',
        'sggp_rev', 'Publicar las lecciones aprendidas.', 'Comité Directivo de Prevención de Desastres', CORTO),
}
ES = {
    'A2.2': (2, C, 'La ciudad identifica la exposición al calor, lluvias e inundación costera de los hogares de bajos ingresos y los adultos mayores, pero no tiene metas de adaptación (CDP 2023).',
        'cdp', 'Plan de salud por escenario.', 'Departamento de Salud', MED),
}
