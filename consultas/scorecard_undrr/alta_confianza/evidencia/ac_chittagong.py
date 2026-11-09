# Chittagong / Chattogram (Chattogram City Corporation, CCC; CDA): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'chittagong', 'Chittagong', 'BGD'
OFICINA = 'CCC / administración del distrito de Chattogram'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'ds_5617': ('https://images.thedailystar.net/node/3386716', 'The Daily Star: el proyecto de 5.617 crore de takas no evita el anegamiento', '2023'),
    'pa_100b': ('https://en.prothomalo.com/bangladesh/jzg4y6l3bx', 'Prothom Alo: Chattogram se inunda pese a gastar cerca de 100.000 millones de takas en 8 años', '2024'),
    'fe_fracaso': ('https://thefinancialexpress.com.bd/home/chattograms-costly-failure-waterlogging-persists-despite-mega-drainage-projects', 'The Financial Express: el costoso fracaso de Chattogram (36 de 56 canales en el proyecto; la CCC y la CDA se culpan)', '2024'),
    'ds_cerros': ('https://www.thedailystar.net/slow-reads/big-picture/news/how-chattogram-can-end-its-recurring-waterlogging-crisis-4225336', 'The Daily Star: cómo terminar con el anegamiento (el corte de cerros obstruye canales y sigue pese a las prohibiciones)', '2026'),
    'desalojo': ('https://www.thedailystar.net/backpage/rain-brings-pain-port-city-dwellers-1768657', 'The Daily Star: la administración desaloja familias de laderas de riesgo y hace campañas por altavoz en ocho cerros', '2019'),
}

EN = {
    '1.2.2': (3, C, 'Ante cada ciclón la administración del distrito activa refugios (más de 1.000 en Mocha, 2023) y despliega voluntarios del Programa de Preparación ante Ciclones; en lluvias desaloja familias de laderas de riesgo hacia refugios.',
              'cpp_mocha,desalojo', 'Coordinar CCC, CDA y distrito con un plan único.', 'Administración distrital / CCC', CORTO),
    '1.2.1': (2, C, 'Las Standing Orders on Disaster 2019 asignan roles a la corporación, pero la CCC y la CDA se culpan entre sí por el anegamiento y no hay coordinación clara del drenaje.',
              'sod2019,fe_fracaso', 'Acuerdo de roles CCC-CDA para drenaje y laderas.', 'Gobierno / CCC / CDA', CORTO),
    '3.2.2': (1, C, 'Se gastaron cerca de 100.000 millones de takas en 8 años en proyectos de drenaje (el mayor, de 5.617 crore, desde 2017, prometido para 2020) y el anegamiento persiste.',
              'pa_100b,ds_5617', 'Evaluar y reorientar la inversión en drenaje.', 'CDA / CCC', MED),
    '4.4.1': (1, C, 'El corte de cerros continúa pese a reiteradas prohibiciones y obstruye canales; hay familias viviendo en laderas de riesgo.',
              'ds_cerros,desalojo', 'Hacer cumplir la prohibición del corte de cerros.', 'Departamento de Medio Ambiente / CDA', CORTO),
    '8.1.1': (1, C, 'El proyecto de drenaje cubre 36 de 56 canales y la ciudad se sigue anegando, con pérdida de vidas.',
              'fe_fracaso,pa_100b', 'Completar el drenaje de los 56 canales.', 'CDA / CCC', LARGO),
    '8.1.2': (1, C, 'La CDA atribuye el anegamiento a que la CCC no limpia bien los desagües.',
              'fe_fracaso', 'Mantenimiento programado de desagües.', 'CCC', CORTO),
    '9.1.1': (4, C, 'El servicio meteorológico emite señales de ciclón y el Programa de Preparación ante Ciclones las difunde casa por casa; el puerto iza señales locales. Para deslizamientos hay campañas por altavoz.',
              'cpp_mocha,desalojo', 'Alerta de deslizamientos con umbrales de lluvia.', 'BMD / CPP / distrito', MED),
    '9.5.2': (3, C, 'Más de 1.000 refugios preparados en el distrito de Chattogram para el ciclón Mocha (2023).',
              'cpp_mocha', 'Refugios suficientes y cercanos en la ciudad.', 'Administración distrital', MED),
    '7.1.1': (3, C, 'El Programa de Preparación ante Ciclones movilizó 8.880 voluntarios y la Media Luna Roja 8.000 en el distrito (2023).',
              'cpp_mocha', 'Cubrir los barrios de laderas.', 'CPP / CCC', MED),
}
ES = {}
