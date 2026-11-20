# Bandung (Pemerintah Kota Bandung; BPBD Kota Bandung): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'bandung', 'Bandung', 'IDN'
OFICINA = 'BPBD Kota Bandung'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'bgs_lembang': ('https://www.bgs.ac.uk/news/nearly-three-million-people-in-indonesias-second-city-could-be-affected-by-an-earthquake/', 'Servicio Geológico Británico: casi tres millones de personas del área de Bandung podrían sufrir un sismo de la falla Lembang', '2023'),
    'nhess': ('https://nhess.copernicus.org/articles/23/3185/2023/nhess-23-3185-2023-metrics.html', 'Natural Hazards and Earth System Sciences 23, 3185 (2023): escenarios sísmicos de la falla Lembang para Bandung', '2023'),
    'ui_m7': ('https://dara.ui.ac.id/research-output/f8c78694-69a4-4396-9fee-b47551df5ce3', 'Universitas Indonesia: la falla Lembang puede generar un sismo de magnitud 7,0', '2024'),
    'tirto_sim': ('https://tirto.id/antisipasi-sesar-lembang-bpbd-bandung-simulasi-mitigasi-bencana-hgCA', 'Tirto: la BPBD de Bandung hace simulacros por la falla Lembang (10 por semana por falta de personal)', 's/f'),
    'jp_adra': ('https://www.thejakartapost.com/front-row/2024/07/29/retrofitting-houses-to-mitigate-potential-earthquake-in-west-bandung', 'The Jakarta Post: refuerzo de viviendas en Bandung Occidental (ADRA: 70% de 1.000 casas sobre la falla con daño grave, más que el escenario del plan de contingencia de Java Occidental 2019)', '2024'),
}

EN = {
    '2.1.1': (4, M, 'La amenaza sísmica de la falla Lembang (a unos 10 km) está estimada en estudios revisados: Mw 6,5-7,0 con recurrencia de 170-670 años y 1,9-2,7 millones de personas expuestas a sacudidas fuertes (BGS, NHESS 2023).',
              'bgs_lembang,nhess,ui_m7', 'Adoptar estos escenarios como oficiales de la ciudad.', 'BPBD Kota Bandung', CORTO),
    '2.2.1': (3, M, 'Hay escenarios de exposición al sismo de Lembang para el área metropolitana (BGS/NHESS), no adoptados formalmente por la ciudad.',
              'bgs_lembang,nhess', 'Escenarios oficiales de exposición y vulnerabilidad.', 'BPBD Kota Bandung', CORTO),
    '9.2.1': (2, M, 'El escenario del plan de contingencia de Java Occidental 2019 subestima el daño frente a un relevamiento de ADRA (70% de casas con daño grave), que pidió actualizarlo.',
              'jp_adra', 'Actualizar el plan de contingencia sísmica.', 'BPBD Kota Bandung / BPBD Jabar', CORTO),
    '9.7.1': (3, M, 'La BPBD hace simulacros de sismo en escuelas, limitados a unos 10 por semana por falta de personal.',
              'tirto_sim', 'Simulacro anual de ciudad.', 'BPBD Kota Bandung', CORTO),
}
ES = {}
