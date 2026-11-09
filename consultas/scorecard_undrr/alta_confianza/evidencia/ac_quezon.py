# Quezón (Quezon City Government; QC DRRMO): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'quezon', 'Quezón', 'PHL'
OFICINA = 'Quezon City DRRMO'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/54348', 'CDP-ICLEI Cities 2023: respuesta oficial del gobierno local de Quezon City', '2023'),
    'manual': ('https://ptvnews.ph/qc-adopts-local-drrm-operations-manual/', 'PTV News: Quezon City adopta su manual local de operaciones de gestión del riesgo', 's/f'),
    'charter24': ('https://quezoncity.gov.ph/wp-content/uploads/2020/09/QCDRRMO-CITIZENS-CHARTER-2024.pdf', 'Quezon City DRRMO: Carta de servicios al ciudadano 2024', '2024'),
    'inq_cero': ('https://newsinfo.inquirer.net/1947268/qc-aims-for-zero-casualty-ready-for-typhoon-season-and-la-nina/amp', 'Inquirer: Quezon City apunta a cero víctimas en la temporada de tifones (consejo activado, centro de operaciones monitorea)', '2024'),
    'mb_lluvias': ('https://mb.com.ph/2024/5/30/qc-is-ready-for-the-rainy-season-mayor-joy', 'Manila Bulletin: Quezon City está lista para la temporada de lluvias', '2024'),
    'mt_eoc': ('https://www.pressreader.com/philippines/manila-times/20170323/281861528327528', 'Manila Times: Quezon City comparte buenas prácticas de gestión de desastres (centro de operaciones con video wall)', '2017'),
    'ord_sismo': ('https://www.gmanetwork.com/news/news/metro/654894/qc-imposes-quake-drills-in-all-buildings/story/', 'GMA News: Quezon City impone simulacros de sismo en todos los edificios (Ordenanza 2674-2018, dos veces al año)', '2018'),
    'nsed25': ('https://quezoncity.gov.ph/2nd-quarter-nationwide-simultaneous-earthquake-drill-nsed-2', 'Quezon City: segundo simulacro nacional simultáneo de sismo en la municipalidad (escenario de magnitud 7,2)', '2025'),
    'falla': ('https://quezoncity.gov.ph/walk-the-fault-activity/', 'Quezon City: recorrido y marcado de la Falla del Valle Oeste (QC DRRMO)', 's/f'),
}

EN = {
    '1.1.1': (4, C, 'Los riesgos climáticos se consideran en planes y presupuestos, el Plan Local de Acción Climática Mejorado 2021-2050 está aprobado y las amenazas están incorporadas al marco de gestión de riesgo de la ciudad (CDP 2023).',
              'cdp', 'Sumar el escenario sísmico al plan de uso del suelo.', 'Gobierno de la ciudad', MED),
    '1.1.2': (3, C, 'El plan se elaboró con el gobierno nacional, los 142 barangays y ONG (CDP 2023).',
              'cdp', 'Consulta con el sector privado.', 'CCESD', MED),
    '1.1.3': (4, C, 'El plan climático se monitorea, evalúa y actualiza al menos cada tres años (CDP 2023).',
              'cdp', 'Sin acción prioritaria.', '', ''),
    '1.2.1': (4, C, 'Hay una oficina de gestión del riesgo (QC DRRMO) creada por ley, un consejo local con todas las dependencias y un manual de operaciones aprobado.',
              'ra10121,manual,charter24', 'Actualizar el manual con el escenario sísmico.', 'QC DRRMO', CORTO),
    '1.2.2': (4, C, 'En la temporada de tifones se activa el consejo local con todas sus dependencias y el centro de operaciones monitorea y coordina la respuesta, con evacuación preventiva.',
              'inq_cero,mb_lluvias,cdp', 'Revisión posevento publicada.', 'QC DRRMO', CORTO),
    '2.1.1': (3, C, 'Hay una evaluación de amenazas, vulnerabilidad y riesgo con atlas de riesgo sísmico, de licuefacción e inundación (2013, con EMI) y una evaluación cualitativa de riesgo climático (2020) (CDP 2023).',
              'cdp', 'Actualizar la evaluación cuantitativa de 2013.', 'QC DRRMO / CCESD', CORTO),
    '2.2.1': (3, C, 'El atlas de riesgo estima el impacto del sismo y la inundación sobre la población y los activos; la ciudad estima que el 20-30% de la población está expuesta a tifones, inundación urbana y sequía (CDP 2023).',
              'cdp', 'Actualizar los escenarios.', 'QC DRRMO', CORTO),
    '2.3.1': (3, C, 'El atlas de riesgo analiza la exposición de las instalaciones esenciales y críticas de la ciudad (CDP 2023).',
              'cdp', 'Mapear dependencias entre activos críticos.', 'QC DRRMO', MED),
    '2.4.1': (4, C, 'Existen mapas de amenaza sísmica, de licuefacción e inundación de la ciudad, y la Falla del Valle Oeste está marcada en el terreno (13 barangays).',
              'cdp,falla', 'Publicar los mapas actualizados.', 'QC DRRMO', CORTO),
    '2.5.1': (3, C, 'Hay un plan de gestión de la evaluación de riesgo climático (2020) con roles, inventario de mapas y fuentes para mantenerla (CDP 2023).',
              'cdp', 'Calendario fijo de actualización.', 'CCESD', MED),
    '3.2.4': (4, C, 'Por ley la ciudad reserva al menos el 5% de sus ingresos para el fondo local de gestión del riesgo (30% de respuesta rápida); además rastrea su gasto climático en el programa anual de inversiones (CDP 2023).',
              'ra10121,cdp', 'Publicar el saldo y uso del fondo.', 'QC DRRMO', CORTO),
    '5.2.2': (3, C, 'Una meta de adaptación promueve infraestructura verde y gris con soluciones basadas en la naturaleza contra la inundación (CDP 2023).',
              'cdp', 'Exigir drenaje sostenible en obras nuevas.', 'CCESD', MED),
    '6.4.1': (4, C, 'La ciudad capacita a su personal y a los 142 barangays con simulacros y ejercicios anuales (CDP 2023).',
              'cdp', 'Medir cobertura de la capacitación.', 'QC DRRMO', CORTO),
    '7.2.2': (4, C, 'La planificación identifica y atiende a niños, adultos mayores y personas con discapacidad en evacuación y refugios, con una meta de vivienda segura para los más vulnerables (CDP 2023).',
              'cdp', 'Registro de personas dependientes.', 'QC DRRMO', MED),
    '8.1.1': (3, C, 'La ciudad construye muros de contención, canales, enrocados y alcantarillas en comunidades expuestas (CDP 2023).',
              'cdp', 'Plan de obras ligado al atlas de riesgo.', 'Departamento de Ingeniería', LARGO),
    '9.1.1': (4, C, 'La ciudad invirtió en sistemas de alerta temprana y estaciones meteorológicas automáticas en barangays expuestos para avisos localizados de tormenta e inundación (CDP 2023).',
              'cdp', 'Medir la anticipación lograda.', 'QC DRRMO', CORTO),
    '9.2.1': (3, C, 'Manual de operaciones y planes de respuesta a tifón e inundación con evacuación preventiva; los simulacros siguen el escenario nacional de sismo de magnitud 7,2.',
              'manual,cdp,nsed25', 'Plan de contingencia sísmica propio.', 'QC DRRMO', MED),
    '9.5.1': (3, C, 'La ciudad tiene depósitos con alimentos y suministros para población desplazada (CDP 2023).',
              'cdp', 'Calcular días de autonomía.', 'Departamento de Bienestar Social', MED),
    '9.5.2': (3, C, 'Hay centros de evacuación identificados, raciones y carpas de partición para la evacuación preventiva (CDP 2023).',
              'cdp', 'Capacidad para el escenario sísmico.', 'QC DRRMO', MED),
    '9.6.2': (4, C, 'La ciudad tiene un centro de operaciones de emergencia con video wall y línea 122, que monitorea los tifones y coordina con el consejo local.',
              'mt_eoc,inq_cero', 'Centro de respaldo.', 'QC DRRMO', MED),
    '9.7.1': (4, C, 'La Ordenanza 2674-2018 obliga a todos los establecimientos a hacer simulacros de sismo dos veces al año, y la ciudad participa de los simulacros nacionales trimestrales.',
              'ord_sismo,nsed25', 'Evaluar los simulacros.', 'QC DRRMO', CORTO),
}
ES = {
    'A2.2': (3, C, 'La ciudad identifica efectos de tifones, inundación y calor en la salud, y declara falta de capacidad financiera y técnica para abordarlos (CDP 2023).',
             'cdp', 'Fortalecer la vigilancia sanitaria.', 'Departamento de Salud', MED),
}
