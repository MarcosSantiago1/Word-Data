# Pionyang (Comité Popular de Pionyang; Comité Estatal de Emergencias y Desastres): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'pyongyang', 'Pionyang', 'PRK'
OFICINA = 'Comité Popular de Pionyang'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'
F = {
    'kcna240801': ('https://www.globalsecurity.org/wmd/library/news/dprk/2024/dprk-240801-kcna01.htm', 'KCNA (agencia estatal norcoreana), vía GlobalSecurity: el grupo de prevención de inundaciones del río Taedong analiza datos hidrometeorológicos en tiempo real con un sistema integrado', '2024'),
    'kcna240802': ('https://www.globalsecurity.org/wmd/library/news/dprk/2024/dprk-240802-kcna01.htm', 'KCNA, vía GlobalSecurity: el Comité Estatal de Emergencias y Desastres asegura que regiones y unidades reciban los pronósticos en tiempo real', '2024'),
    'kcna2307': ('https://www.globalsecurity.org/wmd/library/news/dprk/2023/dprk-230703-kcna02.htm', 'KCNA, vía GlobalSecurity: medidas para minimizar daños por inundación en la cuenca del Taedong (compuertas ligadas al servicio hidrometeorológico)', '2023'),
}
EN = {
    '9.1.1': (3, M, 'Según la agencia estatal, la cuenca del río Taedong tiene un sistema integrado de prevención de inundaciones con datos hidrometeorológicos en tiempo real y compuertas operadas según los pronósticos; no hay verificación independiente.',
              'kcna240801,kcna2307', 'Verificación independiente del sistema.', 'Administración Hidrometeorológica Estatal', CORTO),
    '9.6.1': (3, M, 'El Comité Estatal de Emergencias y Desastres coordina con regiones y unidades la recepción de pronósticos en tiempo real (agencia estatal).',
              'kcna240802', 'Sin dato verificable adicional.', 'Comité Estatal de Emergencias', CORTO),
}
ES = {}
