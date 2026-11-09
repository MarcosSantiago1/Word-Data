# Zhangzhou (gobierno popular municipal; cuartel de control de crecidas): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'zhangzhou', 'Zhangzhou', 'CHN'
OFICINA = 'Cuartel municipal de control de crecidas y sequías de Zhangzhou'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'
F = {
    'saudel_gt': ('https://globaltimes.cn/page/202609/1369862.shtml', 'Global Times: el tifón Saudel toca tierra en Zhangpu (Zhangzhou); el cuartel provincial activa respuesta de nivel III', '2026'),
    'saudel_cgtn': ('https://news.cgtn.com/news/2026-09-05/599-300-evacuated-over-rainstorms-in-southeast-China-province-1QbKjhI466Q/p.html', 'CGTN: 599.300 evacuados por las lluvias en Fujian', '2026'),
    'mekkhala': ('https://chinadailyhk.com/article/195108', 'China Daily: el tifón Mekkhala toca tierra en Zhangzhou; 12.235 residentes evacuados', '2020'),
    'lupit': ('https://www.chinadaily.com.cn/a/202108/05/WS610cc742a310efa1bd6672ce.html', 'China Daily: el tifón Lupit toca tierra en Fujian; el gobierno local activa la respuesta de emergencia por inundación', '2021'),
}
EN = {
    '1.2.2': (4, C, 'Ante cada tifón el gobierno local activa la respuesta de emergencia escalonada del sistema de control de crecidas y evacúa zonas bajas (12.235 personas en Mekkhala 2020; decenas de miles con Saudel 2026, con respuesta provincial de nivel III).',
              'mekkhala,lupit,saudel_gt,saudel_cgtn', 'Publicar la revisión posevento.', 'Cuartel de control de crecidas', CORTO),
    '9.2.1': (3, M, 'La respuesta sigue niveles de emergencia (IV a I) definidos en los planes de control de crecidas y tifones; no se halló el plan municipal publicado.',
              'saudel_gt,lupit', 'Publicar el plan municipal.', 'Cuartel de control de crecidas', CORTO),
}
ES = {}
