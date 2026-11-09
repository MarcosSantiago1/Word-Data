# Calcuta (Kolkata Municipal Corporation, KMC): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'calcuta', 'Calcuta', 'IND'
OFICINA = 'Kolkata Municipal Corporation'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/35904', 'CDP-ICLEI Cities 2023: respuesta oficial de la Kolkata Municipal Corporation', '2023'),
    'adb_ffews': ('https://www.adb.org/news/kolkata-gets-indias-first-comprehensive-city-level-flood-forecasting-and-warning-system', 'BAsD: Calcuta tiene el primer sistema integral de pronóstico y alerta de inundación de una ciudad india', '2018'),
    'adb_pub': ('https://www.adb.org/publications/toward-resilient-kolkata', 'BAsD: Toward Resilient Kolkata, el sistema de pronóstico y alerta temprana de inundaciones', '2018'),
    'sep25_dawn': ('https://www.dawn.com/news/1944310', 'Dawn (AFP): al menos 12 muertos por la lluvia récord en Calcuta', '2025'),
    'sep25_bt': ('https://www.businesstoday.in/india/story/torrential-rain-overnight-inundates-kolkata-ahead-of-durga-puja-four-dead-services-come-to-halt-vehicles-stranded-495252-2025-09-23', 'Business Today: la lluvia torrencial inunda Calcuta; muertos por electrocución y compuertas abiertas desde las 4', '2025'),
    'sep25_cesc': ('https://www.theweek.in/wire-updates/national/2025/09/23/cal38-wb-rains-ld-mamata.html', 'The Week (PTI): la jefa de gobierno culpa a la distribuidora eléctrica CESC por las muertes por electrocución', '2025'),
    'remal': ('https://www.millenniumpost.in/bengal/cyclone-remal-civic-bodies-take-prep-measures-to-tackle-impact-565396', 'Millennium Post: ciclón Remal, los municipios toman medidas de preparación (sala de control y refugios de la KMC)', '2024'),
    'remal_lal': ('https://obeta.ttef.in/west-bengal/cyclone-remal-unified-command-centre-at-lalbazar/cid/2022269', 'The Telegraph: ciclón Remal, centro de comando unificado en Lalbazar (policía, KMC, eléctricas, NDRF, bomberos)', '2024'),
}

EN = {
    '1.1.1': (1, C, 'La ciudad declaró no tener plan de acción climática ni metas de adaptación (en elaboración) y que la planificación urbana corresponde a la KMDA (CDP 2023).',
              'cdp', 'Integrar el riesgo en el plan de desarrollo con la KMDA.', 'KMC / KMDA', MED),
    '1.2.1': (1, C, 'La ciudad se propone crear una célula de gestión de desastres en el área metropolitana con procedimientos y personal dedicado, lo que indica que hoy no existe (CDP 2023).',
              'cdp', 'Crear la unidad de gestión de desastres.', 'KMC', CORTO),
    '1.2.2': (3, C, 'Ante el ciclón Remal (2024) la KMC abrió su sala de control y refugios en escuelas y salones comunitarios, y participó del centro de comando unificado de la policía en Lalbazar.',
              'remal,remal_lal', 'Plan de coordinación escrito con la policía y la eléctrica.', 'KMC / Policía de Calcuta', CORTO),
    '2.1.1': (1, C, 'No tiene evaluación de riesgo y vulnerabilidad climática; prevé hacerla en dos años (CDP 2023).',
              'cdp', 'Evaluación multiamenaza.', 'KMC', CORTO),
    '2.2.1': (1, C, 'Solo estima rangos de población expuesta: 10-20% a lluvia intensa e inundación urbana y menos del 10% a ciclones y calor (CDP 2023), sin escenarios.',
              'cdp', 'Escenarios de exposición.', 'KMC', CORTO),
    '3.2.1': (1, C, 'Sin plan climático ni metas de adaptación; financia con recursos propios, asociaciones público-privadas y fondos nacionales (CDP 2023).',
              'cdp', 'Plan financiero de reducción del riesgo.', 'KMC', MED),
    '4.4.1': (2, C, 'La ciudad se propone revisar el reglamento para restringir la construcción en zonas bajas y exigir pisos sobre la cota de inundación (CDP 2023); aún no está aplicado.',
              'cdp', 'Aprobar y aplicar la restricción.', 'KMC, Departamento de Edificios', MED),
    '9.1.1': (3, C, 'Desde 2018 la KMC tiene un sistema de pronóstico y alerta de inundaciones (BAsD) con sensores en puntos críticos, canales y estaciones de bombeo, y avisos al celular.',
              'adb_ffews,adb_pub', 'Medir la anticipación lograda en eventos reales.', 'KMC, Drenaje', CORTO),
    '8.3.1': (1, C, 'En la lluvia récord de septiembre de 2025 (más de 247 mm en una noche) murieron unas 9 personas electrocutadas por cables en calles inundadas y la distribuidora CESC tuvo que cortar la energía en amplias zonas.',
              'sep25_dawn,sep25_bt,sep25_cesc', 'Protocolo de corte preventivo y cableado elevado.', 'CESC / KMC', CORTO),
    '8.1.1': (2, C, 'El drenaje depende de compuertas al río Hooghly que no alcanzan con marea alta: en septiembre de 2025 la ciudad quedó inundada pese a abrirlas desde las 4 de la mañana.',
              'sep25_bt', 'Ampliar bombeo y almacenamiento pluvial.', 'KMC, Drenaje', LARGO),
}
ES = {
    'A2.2': (2, C, 'La ciudad prevé un plan de calor y salud y fortalecer la salud pública para responder a brotes; identifica enfermedades infecciosas como amenaza de alto impacto (CDP 2023).',
             'cdp', 'Aprobar el plan de calor y salud.', 'KMC, Departamento de Salud', CORTO),
}
