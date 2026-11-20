# Daca Norte (Dhaka North City Corporation, DNCC): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'dhaka_norte', 'Daca Norte', 'BGD'
OFICINA = 'DNCC (comité de gestión de desastres de la ciudad)'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/50782', 'CDP-ICLEI Cities 2023: respuesta oficial de la Dhaka North City Corporation', '2023'),
    'eoc_dncc': ('https://www.tbsnews.net/bangladesh/dhaka-norths-emergency-operation-centre-will-work-247-address-civic-problems-523434', 'TBS: el Centro de Operaciones de Emergencia de Daca Norte funcionará 24/7 (Urban Resilience Project, Banco Mundial)', '2022'),
    'urp_bm': ('https://worldbank.org/en/news/press-release/2015/12/19/bangladesh-jica-collaborate-improve-disaster-resilience-major-cities', 'Banco Mundial: Bangladés y el Banco colaboran para mejorar la resiliencia de las grandes ciudades (Urban Resilience Project)', '2015'),
    'rajuk95': ('https://www.thedailystar.net/opinion/editorial/news/follow-the-building-code-strictly-4212721', 'The Daily Star (editorial): más del 95% de las estructuras bajo RAJUK se construyeron sin aprobación (informe de 2019)', '2026'),
    'dap_humed': ('https://www.dhakatribune.com/bangladesh/dhaka/415977/three-years-on-dhaka-still-waits-for-flood', 'Dhaka Tribune: tres años después, Daca sigue esperando (zonas de retención del DAP y del plan de drenaje invadidas o rellenadas)', '2026'),
    'dap_zonas': ('https://www.thedailystar.net/opinion/editorial/news/dap-must-enhance-dhakas-liveability-3770281', 'The Daily Star: el DAP debe mejorar la habitabilidad de Daca (zonas de flujo de crecida y llanuras)', '2024'),
    'fscd_riesgo': ('https://www.bangladeshpost.net/posts/85-city-buildings-identified-as-highly-risky-409-risky-134233', 'Bangladesh Post: Bomberos identifica 85 edificios muy riesgosos y 409 riesgosos en la ciudad tras el incendio de Bailey Road', '2024'),
    'dengue23': ('https://today.thefinancialexpress.com.bd/print/14-more-die-of-dengue-1692982434', 'The Financial Express: muertes por dengue en 2023 (391 de 528 en Daca a fines de agosto, cifras de la DGHS)', '2023'),
}

EN = {
    '1.1.1': (1, C, 'La DNCC declaró ante CDP (2023) que no tiene plan de acción climática (está en preparación) y que su Plan Estratégico de Daca Norte busca financiamiento; reconoce calor e inundación urbana como amenazas.',
              'cdp', 'Plan estratégico con los riesgos de inundación, calor y sismo.', 'DNCC', MED),
    '1.2.1': (3, C, 'Las Standing Orders on Disaster 2019 asignan roles a los comités de gestión de desastres de la corporación y de cada barrio (presididos por concejales), con responsabilidades en todas las etapas.',
              'sod2019,ds_comites', 'Activar y publicar las actas de los comités de barrio.', 'DNCC', CORTO),
    '2.1.1': (1, C, 'Sin evaluación de riesgo y vulnerabilidad climática (en preparación, CDP 2023); la DNCC dice no tener datos de población expuesta.',
              'cdp', 'Completar la evaluación de riesgo con sismo.', 'DNCC', CORTO),
    '2.2.1': (0, C, 'La DNCC declara que no hay datos de la proporción de población expuesta a calor ni a inundación (CDP 2023).',
              'cdp', 'Estimar exposición por amenaza.', 'DNCC', CORTO),
    '4.4.1': (1, C, 'Las zonas de retención del DAP y del plan de drenaje fueron invadidas o rellenadas en parte; RAJUK casi no avanzó en sus parques de agua (2026).',
              'dap_humed,dap_zonas', 'Proteger las zonas de flujo de crecida.', 'RAJUK', CORTO),
    '4.4.2': (0, C, 'Más del 95% de las estructuras bajo RAJUK se construyeron sin aprobación (informe de 2019); tras el incendio de Bailey Road (46 muertos, 2024) Bomberos halló 85 edificios muy riesgosos y 409 riesgosos.',
              'rajuk95,fscd_riesgo', 'Inspección y certificación de edificios.', 'RAJUK / Bomberos', CORTO),
    '5.2.2': (2, C, 'Arbolado y plantaciones en curso como acción de adaptación (CDP 2023), sin metas de infraestructura azul.',
              'cdp', 'Infraestructura verde y azul en proyectos.', 'DNCC', MED),
    '9.6.2': (4, C, 'Centro de Operaciones de Emergencia de la DNCC creado con el Urban Resilience Project del Banco Mundial, que funciona las 24 horas.',
              'eoc_dncc,urp_bm', 'Procedimientos para sismo mayor con todos los organismos.', 'DNCC', CORTO),
    '10.2.1': (2, C, 'Tras el sismo del 21-nov-2025 (4 muertos en Daca, cientos de edificios con daños según el distrito) RAJUK anunció un relevamiento de edificios riesgosos en toda la ciudad; no se halló revisión posevento formal publicada.',
               'sismo25,sismo25_pa', 'Revisión posevento publicada del sismo de 2025.', 'RAJUK / DNCC', CORTO),
}
ES = {
    'A2.1': (2, C, 'La DNCC menciona la falta de hospitales específicos como factor que limita la adaptación (CDP); en 2023 el dengue mató a 1.705 personas en el país, la mayoría en Daca.',
             'cdp,dengue23', 'Incluir epidemias en la planificación del riesgo.', 'DNCC / DGHS', MED),
}
