# Taipéi (Gobierno de la Ciudad; Centro de Operaciones de Emergencia): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'taipei', 'Taipéi', 'TWN'
OFICINA = 'Centro de Operaciones de Emergencia de Taipéi'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/31446', 'CDP-ICLEI Cities 2023: respuesta oficial de el Gobierno de la Ciudad de Taipéi', '2023'),
}

EN = {
    '1.1.1': (4, C, 'La ciudad asigna responsabilidades climáticas a comités y gerencias, informa al concejo y tiene un plan de implementación de adaptación al cambio climático con metas (CDP 2023).',
        'cdp', 'Llevar los escenarios futuros a los proyectos.', 'Gobierno de la Ciudad de Taipéi', MED),
    '1.1.3': (3, C, 'Los planes climáticos se monitorean y evalúan cada año y se actualizan cada año o cada 3 años, con versiones sucesivas desde 2011 (CDP 2023).',
        'cdp', 'Publicar las lecciones de cada revisión.', 'Departamento de Protección Ambiental', CORTO),
    '2.1.1': (4, C, 'Evaluaciones de riesgo climático de 2012 y 2022 con escenario RCP 8.5, población vulnerable, seguridad hídrica y proceso de actualización cada cinco años, incorporadas a la gestión general de riesgos (CDP 2023); no se informa revisión de terceros.',
        'cdp', 'Revisión externa.', 'Gobierno de la Ciudad', MED),
    '2.2.1': (3, C, 'La ciudad estima que el 10-20% de la población está expuesta a cada una de estas amenazas: calor extremo, tifones, lluvias intensas, deslizamientos y sequía (CDP 2023).',
        'cdp', 'Escenarios "más probable" y "más grave".', 'Gobierno de la Ciudad', MED),
    '2.5.1': (3, C, 'Hay un proceso para actualizar la evaluación de riesgo al menos cada cinco años (CDP 2023).',
        'cdp', 'Acortar el ciclo.', 'Gobierno de la Ciudad', MED),
}
ES = {
    'A2.2': (3, C, 'La ciudad identifica efectos del calor, inundaciones, tifones y calidad del aire en la salud (golpe de calor, enfermedad cardiovascular y respiratoria, infecciones por vectores y agua, interrupción del agua y saneamiento) (CDP 2023).',
        'cdp', 'Plan de salud por escenario.', 'Departamento de Salud de Taipéi', MED),
}
