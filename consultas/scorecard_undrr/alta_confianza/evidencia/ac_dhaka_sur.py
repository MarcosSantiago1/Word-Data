# Daca Sur (Dhaka South City Corporation, DSCC): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'dhaka_sur', 'Daca Sur', 'BGD'
OFICINA = 'DSCC (comité de gestión de desastres de la ciudad)'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/884005', 'CDP-ICLEI Cities 2023: respuesta oficial de la Dhaka South City Corporation', '2023'),
    'eoc_dscc': ('https://epfs.thedailystar.net/TDS/2023/06/27/Bangladesh/MAI/5_04/d50fdff3cfb5e984_04.pdf', 'The Daily Star (edición impresa): la DSCC inaugura su Centro de Operaciones de Emergencia en Nagar Bhaban (Urban Resilience Project)', '2023'),
    'urp_bm': ('https://worldbank.org/en/news/press-release/2015/12/19/bangladesh-jica-collaborate-improve-disaster-resilience-major-cities', 'Banco Mundial: Urban Resilience Project para las grandes ciudades de Bangladés', '2015'),
    'tbs_14': ('https://www.tbsnews.net/node/193339', 'TBS: Knowledge sharing is the key to disaster resilience (comités de gestión de desastres en 14 barrios de la DSCC)', '2021'),
    'rajuk95': ('https://www.thedailystar.net/opinion/editorial/news/follow-the-building-code-strictly-4212721', 'The Daily Star (editorial): más del 95% de las estructuras bajo RAJUK se construyeron sin aprobación', '2026'),
    'bailey': ('https://thefinancialexpress.com.bd/home/fire-service-dg-finds-no-safety-measures-at-tragic-bailey-road-building', 'The Financial Express: el director de Bomberos no halló medidas de seguridad en el edificio de Bailey Road (46 muertos)', '2024'),
    'fscd_riesgo': ('https://www.bangladeshpost.net/posts/85-city-buildings-identified-as-highly-risky-409-risky-134233', 'Bangladesh Post: 85 edificios muy riesgosos y 409 riesgosos; la DSCC clausuró edificios y multó locales', '2024'),
    'dengue23': ('https://today.thefinancialexpress.com.bd/print/14-more-die-of-dengue-1692982434', 'The Financial Express: muertes por dengue en 2023 (cifras de la DGHS)', '2023'),
}

EN = {
    '1.2.1': (3, C, 'Las Standing Orders on Disaster 2019 asignan roles a los comités de gestión de desastres de la corporación y de cada barrio; en la DSCC se formaron comités en 14 barrios.',
              'sod2019,tbs_14', 'Formar comités en todos los barrios.', 'DSCC', CORTO),
    '1.2.3': (1, C, 'La DSCC declaró ante CDP que por capacidad financiera insuficiente y falta de base de datos no tiene actividades específicas de cambio climático.',
              'cdp', 'Presupuesto propio de gestión del riesgo.', 'DSCC', MED),
    '1.4.1': (0, C, 'La DSCC declara no tener una base de datos específica (CDP 2023).',
              'cdp', 'Base de datos única de riesgo.', 'DSCC', CORTO),
    '2.1.1': (1, C, 'Sin evaluación de riesgo y vulnerabilidad climática (en preparación, CDP 2023).',
              'cdp', 'Completar la evaluación de riesgo con sismo e incendio.', 'DSCC', CORTO),
    '2.2.1': (1, C, 'La DSCC estima que el 30-40% de la población está expuesta al estrés térmico y el 40-50% a la inundación urbana (CDP 2023), sin escenarios.',
              'cdp', 'Escenarios de exposición por amenaza.', 'DSCC', CORTO),
    '4.4.2': (0, C, 'Más del 95% de las estructuras bajo RAJUK se construyeron sin aprobación; el edificio de Bailey Road no tenía medidas de seguridad pese a tres avisos de Bomberos; la DSCC clausuró dos edificios y multó a siete locales.',
              'rajuk95,bailey,fscd_riesgo', 'Inspección y certificación de edificios.', 'RAJUK / Bomberos / DSCC', CORTO),
    '5.2.2': (2, C, 'Renovación de parques con más verde, captación de agua de lluvia y mejor drenaje (CDP 2023).',
              'cdp', 'Ampliar a toda la ciudad.', 'DSCC', MED),
    '9.6.2': (4, C, 'La DSCC inauguró su Centro de Operaciones de Emergencia en Nagar Bhaban con el Urban Resilience Project del Banco Mundial.',
              'eoc_dscc,urp_bm', 'Procedimientos para sismo mayor con todos los organismos.', 'DSCC', CORTO),
    '10.2.1': (2, C, 'Tras el sismo del 21-nov-2025 (4 muertos en Daca, cientos de edificios con daños según el distrito) RAJUK anunció un relevamiento de edificios riesgosos en toda la ciudad; no se halló revisión posevento formal publicada.',
               'sismo25,sismo25_pa', 'Revisión posevento publicada del sismo de 2025.', 'RAJUK / DSCC', CORTO),
}
ES = {
    'A2.1': (2, M, 'En 2023 el dengue mató a 1.705 personas en el país, la mayoría en Daca; no se halló plan de la DSCC para epidemias.',
             'dengue23', 'Incluir epidemias en la planificación del riesgo.', 'DSCC / DGHS', MED),
}
