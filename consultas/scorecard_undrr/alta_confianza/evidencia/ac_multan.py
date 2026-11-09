# Multán (distrito y Metropolitan Corporation): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3, PROV = 'multan', 'Multán', 'PAK', 'PUNJAB'
OFICINA = 'DDMA Multán / PDMA Punyab'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'dawn_doble': ('https://www.dawn.com/news/1939554', 'Dawn: doble amenaza de crecidas sobre Muzaffargarh y Multán', '2025'),
    'dawn_diques': ('https://www.dawn.com/news/1939252', 'Dawn: se rompen diques con el Chenab y el Ravi en niveles críticos (más de 100 aldeas de Multán bajo riesgo)', '2025'),
    'pp_voladura': ('https://propakistani.pk/2025/08/30/embankments-destroyed-to-save-multan-from-floods/amp/', 'ProPakistani: plan de voladura de terraplenes para salvar a Multán; evacuación de 300.000 ribereños', '2025'),
    'dawn_calmos': ('https://www.dawn.com/news/1940092', 'Dawn: los ríos bajan; no se volará Head Muhammad Wala', '2025'),
    'nukta_1122': ('https://nukta.com/punjab-flooding-displaces-millions', 'Nukta: Rescue 1122 evacúa a residentes de Head Muhammad Wala', '2025'),
    'arab_nishtar': ('https://www.arabnews.pk/node/2521306/pakistan', 'Arab News: aumentan los golpes de calor en Multán (hospital Nishtar)', '2024'),
    'eu_gastro': ('https://www.energyupdate.com.pk/2025/04/27/heatwave-intensifies-across-southern-punjab-gastroenteritis-cases-surge-in-multan/', 'Energy Update: 120 casos de gastroenteritis en 24 horas en el Nishtar y sala aparte', '2025'),
}

EN = {
    '1.2.2': (3, C, 'En las crecidas de 2025 la administración planificó evacuar a unos 300.000 ribereños, Rescue 1122 evacuó Head Muhammad Wala y se preparó una voladura controlada de terraplenes para proteger la ciudad (que no hizo falta).',
              'pp_voladura,nukta_1122,dawn_calmos', 'Revisión posevento de la crecida de 2025.', 'DDMA / PDMA', CORTO),
    '4.1.1': (2, C, 'En 2025 la amenaza de crecida del Chenab obligó a planificar la evacuación de unos 300.000 ribereños y una voladura que iba a inundar más de 100 aldeas del distrito.',
              'pp_voladura,dawn_diques', 'Estimar desplazados por escenario.', 'DDMA', CORTO),
    '8.1.1': (2, M, 'La ciudad depende de terraplenes y estructuras de cabecera sobre el Chenab que estuvieron al límite en 2025; se rompieron diques en la zona.',
              'dawn_diques,dawn_doble', 'Reforzar los terraplenes del Chenab.', 'Departamento de Riego', LARGO),
}
ES = {
    'A8.2': (2, M, 'El hospital Nishtar recibe golpes de calor a diario en las olas de calor y en 2025 abrió una sala aparte tras 120 casos de gastroenteritis en 24 horas.',
             'arab_nishtar,eu_gastro', 'Plan de reacción hospitalaria al calor.', 'Departamento de Salud', CORTO),
}
