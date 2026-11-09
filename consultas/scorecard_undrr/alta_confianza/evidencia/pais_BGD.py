# Bangladés: evidencia nacional que heredan Daca Norte, Daca Sur, Chittagong y Gazipur (búsqueda nov-2026).
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'sod2019': ('https://www.adrc.asia/documents/dm_information/BGD_SOD2019_English_FINAL.pdf', 'Ministerio de Gestión de Desastres y Socorro: Standing Orders on Disaster 2019 (texto en inglés)', '2019'),
    'ds_comites': ('https://www.thedailystar.net/opinion/views/news/local-government-effective-disaster-management-3443296', 'The Daily Star: Local government for effective disaster management (comités de ciudad y de barrio bajo las SOD)', '2023'),
    'bnbc_gaceta': ('https://www.tbsnews.net/node/207469', 'TBS: entra en vigor el Código Nacional de Edificación actualizado (BNBC 2020)', '2021'),
    'bnbc_bbra': ('https://b.bssnews.net/js-session/380695', 'BSS (agencia estatal): construcción sismorresistente con el BNBC 2020; ley de la Autoridad Reguladora de la Edificación aprobada el 10-abr-2026', '2026'),
    'bnbc_sinente': ('https://www.thedailystar.net/news/bangladesh/news/revised-building-code-no-dedicated-body-yet-enforce-3253936', 'The Daily Star: código revisado sin organismo dedicado a hacerlo cumplir', '2023'),
    'fscd_vol': ('https://www.newkerala.com/news/a/major-earthquake-could-trigger-devastating-fires-across-dhaka-108.htm', 'New Kerala/IANS: el director de Bomberos y Defensa Civil dice que 55.000 voluntarios urbanos completaron la capacitación', '2026'),
    'vol_100k': ('https://b.bssnews.net/others/367415', 'BSS: el gobierno capacitará a 100.000 voluntarios para la respuesta a sismos en Daca', '2026'),
    'cpp_mocha': ('https://www.thedailystar.net/environment/cyclone-mocha/news/over-1000-shelters-ready-ctg-3318551', 'The Daily Star: más de 1.000 refugios listos en Chattogram ante el ciclón Mocha (8.880 voluntarios del CPP)', '2023'),
    'seguro_041': ('https://www.thedailystar.net/node/3556131', 'The Daily Star: Día Nacional del Seguro 2024 (penetración del 0,41% del PIB en 2024)', '2024'),
    'lloyds_brecha': ('https://thefinancialexpress.com.bd/economy/bangladesh/lower-ins-coverage-poses-major-risk-for-economy-1543032131', 'The Financial Express: Lloyd\'s considera a Bangladés el país más subasegurado (brecha de 2,1% del PIB)', '2018'),
    'calor24': ('https://www.tbsnews.net/bangladesh/education/school-reopening-bangladesh-delayed-till-27-april-amid-heatwave-concerns-832281', 'TBS: escuelas cerradas una semana por la ola de calor tras las alertas de 72 horas del servicio meteorológico', '2024'),
    'sismo25': ('https://en.wikipedia.org/wiki/2025_Bangladesh_earthquake', 'Wikipedia: sismo de Bangladés del 21-nov-2025 (M5,5 cerca de Narsingdi; unos 10 muertos, 4 en Daca)', '2025'),
    'sismo25_pa': ('https://en.prothomalo.com/bangladesh/fuou5hewiu', 'Prothom Alo: el sismo mata a 10 y hiere a más de 600; pánico en el país', '2025'),
}

EN = {
    '4.3.2': (4, C, 'El Código Nacional de Edificación 2020 (BNBC 2020), con disposiciones sísmicas actualizadas, entró en vigor por gaceta en 2021, y en abril de 2026 se aprobó la ley de la Autoridad Reguladora de la Edificación.',
              'bnbc_gaceta,bnbc_bbra', 'Poner en marcha la autoridad reguladora.', 'Ministerio de Vivienda / autoridad de desarrollo', MED),
    '6.4.1': (3, C, 'Bomberos y Defensa Civil forma voluntarios urbanos (meta nacional de 62.000; 55.000 capacitados según su director) en búsqueda y rescate, primeros auxilios e incendio; en 2026 se lanzó un programa para 100.000 voluntarios en Daca.',
              'fscd_vol,vol_100k', 'Registro de cobertura por barrio.', 'Bomberos y Defensa Civil', CORTO),
}
EN.update({
    '3.3.1': (1, C, 'La penetración del seguro bajó a 0,41% del PIB en 2024 y Lloyd\'s considera a Bangladés el país más subasegurado; la cobertura de vivienda frente a desastres es mínima.',
              'seguro_041,lloyds_brecha', 'Programa de seguro de vivienda o microseguro.', 'IDRA / gobierno', LARGO),
    '3.3.2': (1, M, 'Con una penetración de 0,41% del PIB y una tasa de pago de siniestros no vida del 41% (2023), la cobertura de activos no residenciales es baja.',
              'seguro_041', 'Relevar la cobertura de activos públicos y comerciales.', 'IDRA', MED),
    '9.1.1': (3, C, 'El servicio meteorológico emite alertas de calor de 72 horas (2024, con cierre de escuelas) y señales de ciclón; no hay alerta sísmica, aunque el sismo de noviembre de 2025 mató a unas 10 personas cerca de Daca.',
              'calor24,sismo25', 'Alerta de inundación urbana por barrio.', 'Servicio meteorológico / ciudad', MED),
})
ES = {}
