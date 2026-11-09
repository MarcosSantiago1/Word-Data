# Kinsasa (Hôtel de Ville de Kinshasa; gobierno provincial): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'kinsasa', 'Kinsasa', 'COD'
OFICINA = 'Hôtel de Ville de Kinshasa'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'
F = {
    'cdp': ('https://www.cdp.net/en/responses/36002', 'CDP-ICLEI Cities 2023: respuesta oficial de la Ville de Kinshasa', '2023'),
    'aj_ndjili': ('https://www.aljazeera.com/news/2025/4/6/heavy-floods-in-dr-congos-kinshasa-leave-dozens-dead-destroy-homes', 'Al Jazeera: inundaciones en Kinsasa dejan decenas de muertos y casas destruidas', '2025'),
    'npr_33': ('https://www.kunc.org/npr-news/2025-04-07/flooding-death-toll-in-congos-capital-reaches-33-as-officials-race-to-help-victims', 'NPR (AP): suben a 33 los muertos por la crecida del río Ndjili en Kinsasa; el gobierno abre refugios', '2025'),
    'nbc_mitad': ('https://www.nbcnews.com/news/world/33-killed-floods-leave-half-congos-capital-water-rcna200152', 'NBC News: 33 muertos; las inundaciones dejan a media capital sin agua', '2025'),
}
EN = {
    '1.1.1': (1, C, 'La ciudad declaró no tener plan de acción climática (en elaboración) y no respondió sobre la consideración del clima en planes y presupuestos (CDP 2023).',
              'cdp', 'Plan con mapas de inundación y erosión.', 'Hôtel de Ville', MED),
    '2.1.1': (2, C, 'La evaluación que cita la ciudad (2018) cuantificó efectos de una catástrofe y necesidades de recuperación por sector; estima que el 50-60% de la población está expuesta a crecidas de ríos e inundación urbana (CDP 2023).',
              'cdp', 'Evaluación multiamenaza con probabilidades.', 'Hôtel de Ville', CORTO),
    '2.2.1': (2, C, 'Solo rangos de exposición: 50-60% a inundación fluvial y urbana, 40-50% al calor y la sequía (CDP 2023).',
              'cdp', 'Escenarios de exposición por comuna.', 'Hôtel de Ville', CORTO),
    '4.4.1': (1, C, 'La ley prohíbe construir junto a los cursos de agua (CDP 2023), pero en abril de 2025 la crecida del Ndjili mató a 33 personas en 13 de las 24 comunas y el presidente y el gobernador atribuyeron muertes a construcciones ilegales junto al río.',
              'cdp,npr_33,aj_ndjili', 'Aplicar la prohibición y reubicar viviendas en riberas.', 'Hôtel de Ville', MED),
    '1.2.2': (2, C, 'En abril de 2025 el gobierno abrió al menos cuatro refugios para familias desplazadas, pero los residentes criticaron la lentitud de la respuesta.',
              'npr_33,aj_ndjili', 'Plan de coordinación de la respuesta.', 'Hôtel de Ville / gobierno nacional', CORTO),
    '8.2.1': (1, C, 'La crecida de abril de 2025 dejó a media capital sin agua corriente.',
              'nbc_mitad', 'Plan de continuidad del agua.', 'REGIDESO', MED),
    '8.1.1': (2, C, 'La ciudad construye diques en varios cursos de agua y planta árboles en las riberas (CDP 2023), insuficientes ante la crecida de 2025.',
              'cdp,npr_33', 'Obras de control de crecidas del Ndjili.', 'Hôtel de Ville', LARGO),
}
ES = {
    'A2.2': (2, C, 'La ciudad identifica enfermedades ligadas al agua (diarrea, cólera, tifoidea) y al paludismo como efectos del clima (CDP 2023), sin plan sanitario de emergencia hallado.',
             'cdp', 'Plan de salud ante inundación.', 'División Provincial de Salud', MED),
}
