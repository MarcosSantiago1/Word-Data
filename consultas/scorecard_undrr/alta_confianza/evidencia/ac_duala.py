# Duala (Communauté Urbaine / Ville de Douala): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'duala', 'Duala', 'CMR'
OFICINA = 'Communauté Urbaine de Douala'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/36042', 'CDP-ICLEI Cities 2023: respuesta oficial de la Ville de Douala', '2023'),
}

EN = {
    '1.1.1': (0, C, 'La ciudad no consideró los riesgos climáticos en sus procesos ("pregunta no aplicable") y no tiene plan climático "por falta de capacidad financiera" (CDP 2023).',
        'cdp', 'Elaborar un plan con evaluación de riesgo.', 'Communauté Urbaine de Douala', MED),
    '2.1.1': (0, C, 'La ciudad no hizo una evaluación de riesgo y vulnerabilidad climática y no piensa hacerla "por falta de capacidad financiera" (CDP 2023).',
        'cdp', 'Buscar financiamiento para una evaluación de riesgo.', 'Communauté Urbaine de Douala', MED),
    '2.2.1': (1, C, 'Sin evaluación de riesgo; la ciudad solo estima que el 30-40% de la población está expuesta al estrés térmico y a la mayor demanda de agua (CDP 2023).',
        'cdp', 'Mapear población expuesta a inundación y calor.', 'Communauté Urbaine de Douala', MED),
}
ES = {
}
