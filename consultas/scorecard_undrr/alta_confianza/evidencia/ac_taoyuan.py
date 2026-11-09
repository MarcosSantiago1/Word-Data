# Taoyuan (Gobierno de la Ciudad): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'taoyuan', 'Taoyuan', 'TWN'
OFICINA = 'Gobierno de la Ciudad de Taoyuan'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/54395', 'CDP-ICLEI Cities 2023: respuesta oficial de el Gobierno de la Ciudad de Taoyuan', '2023'),
}

EN = {
    '1.1.1': (4, C, 'La ciudad considera los riesgos climáticos en su presupuesto, planes y estrategias, y tiene un programa de implementación de adaptación al cambio climático 2023 con metas de adaptación (CDP 2023).',
        'cdp', 'Llevar los escenarios futuros al plan de la ciudad.', 'Gobierno de la Ciudad de Taoyuan', MED),
    '2.1.1': (4, C, 'Evaluaciones de riesgo climático de 2018 y 2023 con escenario RCP 8.5, priorización de amenazas, población vulnerable y seguridad hídrica (CDP 2023); no se informa revisión de terceros.',
        'cdp', 'Revisión externa.', 'Gobierno de la Ciudad', MED),
    '2.2.1': (3, C, 'La ciudad estima que el 90-100% de la población está expuesta a lluvias intensas y tormentas, el 50-60% a inundación urbana y menos del 10% a deslizamientos (CDP 2023).',
        'cdp', 'Escenarios "más probable" y "más grave".', 'Gobierno de la Ciudad', MED),
    '2.5.1': (3, C, 'Hay un proceso para actualizar la evaluación de riesgo al menos cada cinco años (2018 y 2023) (CDP 2023).',
        'cdp', 'Acortar el ciclo de actualización.', 'Gobierno de la Ciudad', MED),
}
ES = {
    'A2.2': (3, C, 'La ciudad identifica efectos de tormentas, calor, frío, inundaciones y estrés hídrico en la salud (lesiones y muertes, salud mental, seguridad alimentaria, sobrecarga del sistema de salud) (CDP 2023).',
        'cdp', 'Modelar el impacto en salud por escenario.', 'Departamento de Salud', MED),
}
