# Yakarta (Gobierno Provincial de DKI Jakarta; BPBD DKI): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'yakarta', 'Yakarta', 'IDN'
OFICINA = 'BPBD DKI Jakarta'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/31166', 'CDP-ICLEI Cities 2023: respuesta oficial de el Gobierno de la Ciudad de Yakarta', '2023'),
    'dws': ('https://smartcity.jakarta.go.id/en/blog/teknologi-peringatan-dini-bencana-banjir-di-jakarta', 'Jakarta Smart City: tecnología de alerta temprana de inundaciones en Yakarta (Disaster Warning System con altavoces en 15 puntos de 5 barrios inundables)', 's/f'),
    'bj_rob': ('https://www.beritajakarta.id/en/read/61044/potret-jakarta', 'Berita Jakarta: BPBD alerta de inundación por marea en el norte de Yakarta del 1 al 10 de diciembre de 2025, según la BMKG', '2025'),
}

EN = {
    '1.1.1': (4, C, 'La provincia incorporó los riesgos climáticos a su planificación (plan de desarrollo de largo y mediano plazo y Pergub 90/2021 de desarrollo bajo en carbono y resiliente al clima), con metas de adaptación (CDP 2023).',
        'cdp', 'Llevar los escenarios futuros a los proyectos.', 'Bappeda DKI Jakarta', MED),
    '1.1.2': (4, C, 'En los planes climáticos participaron gobiernos local, provincial y nacional, academia, sector privado, ONG, ciudadanos, sindicatos y grupos vulnerables (9 grupos) (CDP 2023).',
        'cdp', 'Sumar a los grupos que faltan.', 'Bappeda DKI Jakarta', CORTO),
    '1.1.3': (3, C, 'Los planes climáticos integrados se evalúan y actualizan cada año, y hubo versiones sucesivas aprobadas entre 2010 y 2023 (CDP 2023).',
        'cdp', 'Publicar las lecciones de cada revisión.', 'Bappeda DKI Jakarta', CORTO),
    '2.1.1': (4, C, 'Doce evaluaciones de riesgo entre 2012 y 2022, varias con escenario RCP 8.5, consulta a socios, población vulnerable y proceso de actualización cada cinco años (CDP 2023); no se informa revisión de terceros.',
        'cdp', 'Revisión externa.', 'BPBD / Bappeda DKI', MED),
    '2.2.1': (3, C, 'La provincia estima que el 90-100% de la población está expuesta a la inundación fluvial y el 60-70% al calor extremo; inundación urbana y costera, menos del 10% (CDP 2023).',
        'cdp', 'Escenarios "más probable" y "más grave".', 'BPBD DKI Jakarta', MED),
    '2.5.1': (3, C, 'Hay un proceso para actualizar las evaluaciones de riesgo al menos cada cinco años (CDP 2023).',
        'cdp', 'Acortar el ciclo.', 'BPBD / Bappeda DKI', MED),
    '9.1.1': (4, M, 'El sistema de alerta de inundaciones tiene altavoces en 15 puntos de 5 barrios inundables que se activan cuando el río sube a nivel de alerta aguas arriba, monitoreo público del nivel de agua y avisos de marea y clima extremo de la BPBD con datos de la BMKG.',
        'dws,bj_rob', 'Extender los altavoces a todos los barrios inundables.', 'BPBD DKI Jakarta', MED),
}
ES = {
    'A2.2': (3, C, 'La provincia identifica efectos de lluvias, inundaciones fluviales y costeras, calor y enfermedades infecciosas en la salud (infecciones por vectores y agua, interrupción del agua y saneamiento) (CDP 2023).',
        'cdp', 'Plan de salud por escenario.', 'Dinas Kesehatan DKI', MED),
}
