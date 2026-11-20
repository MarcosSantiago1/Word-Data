# Islamabad (Territorio Capital; CDA, Metropolitan Corporation Islamabad y administración del ICT): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'islamabad', 'Islamabad (Territorio Capital)', 'PAK'
OFICINA = 'CDA (Dirección de Emergencias y Desastres) / administración del ICT'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'mhvra_unh': ('https://www.dawn.com/news/amp/1270289', 'Dawn: ONU-Hábitat y la NDMA lanzan una evaluación multiamenaza de Rawalpindi, Islamabad y Nowshera', '2016'),
    'unh_clima': ('https://www.slideshare.net/slideshow/islamabad-pakistan-climate-change-vulnerability-assessment-unhabitat-abridged-version-3/51490854', 'ONU-Hábitat / CADD / ICT / CDA: Islamabad climate change vulnerability assessment', '2014'),
    'cda_monzon25': ('https://dailytimes.com.pk/1325591/cda-activates-monsoon-2025-emergency-plan-to-avert-flash-floods/', 'Daily Times: la CDA activa su plan de emergencia del monzón 2025 (célula de inundaciones de la Dirección de Emergencias y Desastres)', '2025'),
    'cda_sismo23': ('https://propakistani.pk/2023/03/24/cda-reveals-the-extent-of-structural-damage-in-buildings-after-6-8-magnitude-earthquake/', 'ProPakistani: la CDA informa daños estructurales en edificios tras el sismo de magnitud 6,8', '2023'),
    'dawn_cert': ('https://www.dawn.com/news/1507384', 'Dawn: la mayoría de los edificios altos de la capital funcionan sin certificado final de obra', '2019'),
    'dawn_ocup': ('https://www.dawn.com/news/1743645', 'Dawn: decenas de edificios funcionan sin certificado de ocupación por negligencia de la CDA', '2023'),
    'margalla': ('https://tribune.com.pk/story/969471/entertainment', 'Express Tribune: ¿por qué se derrumbó Margalla Towers? (2005, unos 70 muertos)', '2015'),
    'ndma_neoc_ib': ('https://www.app.com.pk/?p=1177229', 'APP: diputados visitan el NEOC de la NDMA en Islamabad (tableros y monitoreo en tiempo real)', '2026'),
}

EN = {
    '2.1.1': (2, C, 'Hay una evaluación multiamenaza de ONU-Hábitat con la NDMA (2016) y una evaluación de vulnerabilidad climática publicada con la CDA y la administración del ICT; ambas con más de tres años.',
              'mhvra_unh,unh_clima', 'Actualizar la evaluación con sismo y crecidas repentinas.', 'CDA / ICT', MED),
    '2.2.1': (2, C, 'La evaluación de vulnerabilidad climática de ONU-Hábitat analiza exposición y vulnerabilidad de la ciudad, sin escenarios sísmicos actualizados.',
              'unh_clima', 'Escenarios de exposición por amenaza.', 'CDA', MED),
    '1.2.1': (3, M, 'La CDA tiene una Dirección de Emergencias y Desastres con una célula de inundaciones, y la CDA, la Metropolitan Corporation y la administración del ICT reciben instrucciones de preparación cada monzón.',
              'cda_monzon25', 'Plan de gestión del riesgo del Territorio Capital con roles definidos.', 'CDA / ICT', CORTO),
    '4.3.1': (3, M, 'La CDA dice aplicar el código sísmico de 2007 y haber auditado los edificios antes de su vigencia.',
              'margalla,pnud_bcp', 'Publicar el estado de cumplimiento.', 'CDA', MED),
    '4.4.2': (1, C, 'La mayoría de los edificios altos funciona sin certificado final de obra y decenas sin certificado de ocupación; el sismo de 2023 agrietó edificios y la CDA ordenó inspecciones.',
              'dawn_cert,dawn_ocup,cda_sismo23', 'Inspección sísmica de edificios altos y certificación.', 'CDA', CORTO),
    '9.6.2': (4, C, 'En Islamabad funciona el Centro Nacional de Operaciones de Emergencia de la NDMA, con tableros y monitoreo en tiempo real; la CDA tiene su célula de inundaciones.',
              'ndma_neoc,ndma_neoc_ib,cda_monzon25', 'Centro de operaciones propio del Territorio Capital conectado al NEOC.', 'CDA / ICT', MED),
    '9.2.1': (3, M, 'La CDA activa cada año un plan de emergencia del monzón contra crecidas repentinas; no se halló plan multiamenaza ligado a escenarios.',
              'cda_monzon25', 'Plan por escenarios con sismo.', 'CDA / ICT', MED),
}
ES = {}
