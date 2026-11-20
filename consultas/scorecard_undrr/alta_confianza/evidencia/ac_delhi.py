# Delhi (Corporación Municipal; DDMA Delhi): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'delhi', 'Delhi (Corporación Municipal)', 'IND'
OFICINA = 'DDMA Delhi / Corporación Municipal de Delhi'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/31157', 'CDP-ICLEI Cities 2023: respuesta oficial de la Ciudad de Delhi', '2023'),
    'hap25': ('https://ddma.delhi.gov.in/sites/default/files/ddma/generic_multiple_files/hap_delhi_21.4.25_3.pdf', 'DDMA Delhi: Heat Action Plan 2025 (plan de acción ante el calor, leído completo)', '2025'),
    'trib_fco': ('https://www.tribuneindia.com/news/delhi/govt-better-prepared-to-prevent-flood-like-situation-this-year-cm', 'The Tribune: el gobierno dice estar mejor preparado ante inundaciones; Delhi no tenía Centro de Comando y Control y la Flood Control Order 2025 fija drenaje, diques, bombas, contactos y evacuación', '2025'),
    'print_hap': ('https://theprint.in/india/heatwave-alerts-water-coolers-and-dedicated-wards-in-hospitals-delhi-govt-unveils-heat-action-plan/2598003/', 'ThePrint: alertas de calor, 3.000 bebederos y salas exclusivas en hospitales: Delhi presenta su plan de calor', '2025'),
}

EN = {
    '1.1.1': (3, C, 'La ciudad considera los riesgos climáticos en su presupuesto y sus planes, y tiene una evaluación de riesgo de 2023 con sectores urbanos, población vulnerable y seguridad hídrica (CDP 2023); el plan climático integrado era de 2019-2020.',
        'cdp', 'Plan vigente con acciones por riesgo.', 'Gobierno de Delhi / MCD', MED),
    '1.1.3': (1, C, 'El plan climático integrado (2019, hasta 2020) no tiene procesos de monitoreo, evaluación ni actualización (CDP 2023).',
        'cdp', 'Fijar y publicar un ciclo de revisión.', 'Gobierno de Delhi', CORTO),
    '2.1.1': (3, C, 'Evaluación de riesgo climático de 2023 hecha por un departamento propio, con sectores, naturaleza, riesgos de transición, seguridad hídrica, consulta a socios y población vulnerable (CDP 2023); no tiene escenario de altas emisiones ni revisión externa.',
        'cdp', 'Escenario RCP 8.5 y revisión externa.', 'DDMA / Departamento de Ambiente', MED),
    '2.2.1': (2, C, 'La ciudad no tiene datos de la población expuesta al calor extremo ni a enfermedades infecciosas y estima el 20-30% expuesta a estrés hídrico (CDP 2023); el plan de calor 2025 mapea zonas vulnerables (asentamientos informales).',
        'cdp,hap25', 'Escenarios de inundación del Yamuna y de calor por distrito.', 'DDMA', MED),
    '6.2.1': (3, M, 'El plan de calor 2025 prevé carteles, folletos, medios, anuncios con altavoz, marchas, teatro callejero y capacitación de docentes y escolares, centrado en el calor.',
        'hap25,print_hap', 'Campaña para todas las amenazas.', 'DDMA / Departamento de Educación', CORTO),
    '9.2.1': (3, C, 'Hay planes por amenaza: la Flood Control Order 2025 (drenaje, diques, estaciones de bombeo, contactos y evacuación) y el plan de calor 2025 con roles por agencia y fase; no se ligan a escenarios.',
        'trib_fco,hap25', 'Ligar los planes a escenarios de la evaluación de riesgo.', 'DDMA', MED),
    '9.6.2': (1, M, 'Según la prensa, Delhi no tenía un Centro de Comando y Control que permitiera una respuesta unificada en las inundaciones del Yamuna de 2023.',
        'trib_fco', 'Crear el centro de operaciones con procedimientos probados.', 'DDMA', MED),
}
ES = {
    'A2.2': (3, C, 'La ciudad identifica efectos del calor y el estrés hídrico en la salud (golpe de calor, salud mental, enfermedad cardiovascular y respiratoria) (CDP 2023) y el plan de calor 2025 prepara a centros de salud y hospitales por fase.',
        'cdp,hap25', 'Plan de salud para inundación y otras amenazas.', 'Departamento de Salud de Delhi', MED),
    'A9.1': (3, C, 'El plan de calor 2025 tiene alertas por colores según el pronóstico del IMD, un sistema de alerta temprana de calor y salud y la notificación de todos los casos de enfermedad por calor al programa de vigilancia IDSP; cubre solo el calor.',
        'hap25,print_hap', 'Extender la vigilancia a enfermedades por agua y vectores tras inundaciones.', 'Departamento de Salud / DDMA', CORTO),
}
