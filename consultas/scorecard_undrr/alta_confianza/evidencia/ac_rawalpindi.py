# Rawalpindi (distrito y Metropolitan Corporation; RDA y WASA): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3, PROV = 'rawalpindi', 'Rawalpindi', 'PAK', 'PUNJAB'
OFICINA = 'DDMA Rawalpindi / PDMA Punyab'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'jica_leh': ('https://openjicareport.jica.go.jp/pdf/11734027_25.pdf', 'JICA: estudio del sistema de pronóstico y alerta de crecidas del Nullah Leh', '2005'),
    'trib_leh_sat': ('https://tribune.com.pk/story/714589/entertainment', 'Express Tribune: el sistema de alerta de crecidas de alta tecnología de Rawalpindi (PMD pronostica, la administración local alerta y evacua)', '2014'),
    'dawn_sirenas25': ('https://www.dawn.com/news/1939017/heavy-rain-batters-rawalpindi-islamabad', 'Dawn: lluvias intensas; se activan las sirenas de alerta del Nullah Leh', '2025'),
    'trib_robo': ('https://tribune.com.pk/story/2613065/flood-risk-churns-leh-waters', 'Express Tribune: robaron el sistema de alerta temprana instalado en el Nullah y hubo que reponerlo', '2026'),
    'trib_mejora': ('https://tribune.com.pk/story/2625356/joint-measures-afoot-to-tackle-leh-flooding', 'Express Tribune: medidas conjuntas contra las crecidas del Leh (modernizar la alerta, vigilancia de vertidos)', '2026'),
    'dawn_leh_neoc': ('https://dawn.com/news/1576602/rescue-teams-on-red-alert-after-ndma-pmd-issue-flood-warnings-for-leh-nullah', 'Dawn: equipos de rescate en alerta roja tras avisos de la NDMA y el PMD por el Nullah Leh', '2020'),
    'leh_exp': ('https://dawn.com/news/1898116/rda-seeks-consultant-for-leh-nullah-expressway-project-again', 'Dawn: la RDA vuelve a buscar consultor para el proyecto de autopista y canal de crecidas del Leh', '2025'),
    'leh_abandono': ('https://dawn.com/news/1831532/cash-strapped-punjab-govt-abandons-leh-expressway-project', 'Dawn: Punyab sin fondos abandona el proyecto de 110.000 millones de rupias', '2024'),
    'mhvra_unh': ('https://www.dawn.com/news/amp/1270289', 'Dawn: ONU-Hábitat y la NDMA lanzan una evaluación multiamenaza de Rawalpindi, Islamabad y Nowshera', '2016'),
}

EN = {
    '2.1.1': (2, C, 'Existe una evaluación multiamenaza de vulnerabilidad y riesgo de ONU-Hábitat con la NDMA que cubre Rawalpindi (lanzada en 2016), con más de tres años; el riesgo de crecida del Leh está estudiado desde el diseño de JICA (2005).',
              'mhvra_unh,jica_leh', 'Actualizar la evaluación multiamenaza.', 'DDMA / NDMA', MED),
    '2.4.1': (3, M, 'Hay puntos de control con niveles de peligro definidos en el Nullah Leh (Katarian 18 pies, Gawalmandi 17 pies) y la evaluación multiamenaza de ONU-Hábitat; no se halló mapa de amenaza público actualizado.',
              'trib_mejora,mhvra_unh', 'Mapa de inundación del Leh público y actualizado.', 'RDA / WASA', CORTO),
    '3.2.2': (1, C, 'El proyecto de canal de crecidas del Leh lleva casi dos décadas sin empezar: abandonado por falta de fondos en 2024 y con un nuevo estudio de factibilidad en 2025.',
              'leh_exp,leh_abandono', 'Financiar la obra de control de crecidas.', 'Gobierno de Punyab / RDA', LARGO),
    '8.1.1': (1, C, 'No existe el canal de crecidas previsto para el Leh; el defensor del pueblo de Punyab atribuye pérdidas y víctimas a la demora del proyecto.',
              'leh_exp,leh_abandono', 'Obra de control de crecidas y retiro de vertidos.', 'RDA / WASA', LARGO),
    '8.1.2': (2, M, 'Se limpia el cauce antes del monzón y se vigila con cámaras el vertido de basura (2026), pero el sistema de alerta llegó a ser robado.',
              'trib_mejora,trib_robo', 'Mantenimiento y vigilancia permanentes del cauce y los sensores.', 'WASA / Metropolitan Corporation', CORTO),
    '9.1.1': (3, C, 'Sistema de pronóstico y alerta de crecidas del Nullah Leh (JICA, unos 5,5 millones de dólares): el PMD pronostica y la administración local alerta con sirenas y evacúa; se activó en septiembre de 2025. Se planea modernizarlo (2026).',
              'jica_leh,trib_leh_sat,dawn_sirenas25,trib_mejora', 'Modernizar sensores y sumar avisos por celular.', 'PMD / administración distrital', CORTO),
    '9.1.1.1': (3, C, 'Las sirenas cubren las orillas del Leh y la NDMA envía SMS por ubicación; no se halló dato de alcance total.',
                'dawn_sirenas25,ndma_sms', 'Cubrir toda la población expuesta.', 'Administración distrital', CORTO),
    '9.4.1': (2, C, 'El equipo de alerta instalado en el Nullah fue robado y hubo que reponerlo (2026).',
              'trib_robo', 'Inventario y resguardo de equipos.', 'Administración distrital', CORTO),
}
ES = {}
