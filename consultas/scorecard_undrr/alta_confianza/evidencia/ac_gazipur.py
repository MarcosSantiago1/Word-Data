# Gazipur (Gazipur City Corporation): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'gazipur', 'Gazipur', 'BGD'
OFICINA = 'Gazipur City Corporation'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'tongi_quim': ('https://today.thefinancialexpress.com.bd/print/chemical-fire-in-tongi-three-victims-critical-1758565439', 'The Financial Express: incendio de depósito químico en Tongi', '2025'),
    'tongi_2016': ('https://en.prothomalo.com/bangladesh/Firefighters-battle-to-douse-blaze-at-Tongi', 'Prothom Alo: incendio de la fábrica de envases de Tongi', '2016'),
}

EN = {
    '1.2.1': (2, M, 'Las Standing Orders on Disaster 2019 obligan a la corporación a tener comités de gestión de desastres de ciudad y de barrio; no se halló evidencia de su funcionamiento en Gazipur.',
              'sod2019', 'Constituir y publicar los comités.', 'Gazipur City Corporation', CORTO),
    '2.1.1': (1, M, 'Incendios industriales recurrentes en Tongi (fábrica de envases, 2016; depósito químico, 2025) muestran una amenaza conocida, pero no se halló evaluación de riesgo de la ciudad.',
              'tongi_2016,tongi_quim', 'Evaluación de riesgo industrial e inundación.', 'Gazipur City Corporation', CORTO),
}
ES = {}
