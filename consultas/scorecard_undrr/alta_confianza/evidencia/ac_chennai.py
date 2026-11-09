# Chennai (Greater Chennai Corporation): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'chennai', 'Chennai', 'IND'
OFICINA = 'Greater Chennai Corporation'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/35905', 'CDP-ICLEI Cities 2023: respuesta oficial de la Corporation of Chennai', '2023'),
    'dt_ward': ('https://www.dtnext.in/news/chennai/ward-level-flood-forecast-system-in-gcc-control-room', 'DT Next: sistema de pronóstico de inundación por barrio (ward) en la sala de control de la GCC, con anegamientos previstos tres días antes', 's/f'),
    'cfm': ('https://chennaifloodmonitor.tn.gov.in/Master/AboutUs', 'Gobierno de Tamil Nadu: proyecto de monitoreo de inundaciones de Chennai (antecedentes)', 's/f'),
    'dt_iccc': ('https://www.dtnext.in/news/chennai/mayor-inspects-gcc-integrated-command-and-control-center-for-monsoon-preparedness-745771', 'DT Next: la alcaldesa inspecciona el Centro Integrado de Comando y Control de la GCC para el monzón', 's/f'),
}

EN = {
    '1.1.1': (4, C, 'La corporación considera los riesgos climáticos en su presupuesto, planes y estrategias, y tiene un plan climático integrado con metas de adaptación (CDP 2023).',
        'cdp', 'Llevar los escenarios futuros a los proyectos de infraestructura.', 'Greater Chennai Corporation', MED),
    '1.1.3': (3, C, 'El plan climático se evalúa cada año (CDP 2023).',
        'cdp', 'Publicar las lecciones de cada revisión.', 'Greater Chennai Corporation', CORTO),
    '2.1.1': (4, C, 'Evaluación de riesgo climático de 2023 para toda la ciudad, hecha por consultores, con escenario RCP 8.5, población vulnerable y seguridad hídrica, incorporada a la gestión general de riesgos (CDP 2023); no se informa revisión de terceros.',
        'cdp', 'Revisión externa.', 'Greater Chennai Corporation', MED),
    '2.2.1': (2, C, 'En CDP 2023 la ciudad solo informa exposición a inundación costera (menos del 10% de la población) y ninguna otra amenaza, pese a las inundaciones por lluvia.',
        'cdp', 'Escenarios de inundación pluvial y fluvial por barrio.', 'Greater Chennai Corporation', MED),
    '9.1.1': (4, M, 'La sala de control usa un pronóstico de inundación por barrio que anticipa anegamientos tres días antes, y el sistema C-FLOWS y el monitoreo estatal envían alertas al centro de comando.',
        'dt_ward,cfm', 'Medir la exactitud del pronóstico tras cada evento.', 'GCC / Revenue Administration', CORTO),
    '9.6.2': (3, C, 'El Centro Integrado de Comando y Control (ICCC) recibe las alertas de inundación y se fusionó con la sala de control de lluvias; la línea 1913 pasó de 5 a 15 conexiones y 22 pasos bajo nivel tienen cámaras.',
        'dt_iccc,dt_ward', 'Cámaras en toda la ciudad y procedimientos probados.', 'Greater Chennai Corporation', MED),
}
ES = {
    'A2.2': (2, C, 'La corporación solo identifica enfermedades por vectores y por agua asociadas a lluvias intensas y agua estancada (CDP 2023).',
        'cdp', 'Plan de salud por escenario, incluido el calor.', 'Departamento de Salud de la GCC', MED),
}
