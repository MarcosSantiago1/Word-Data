# Shantou (gobierno popular municipal; cuartel municipal de prevención de crecidas, sequías y vientos): base de alta confianza, búsqueda nov-2026. Hereda la evidencia de Guangdong y de China.
ID, NOMBRE, ISO3 = 'shantou', 'Shantou', 'CHN'
PROV = 'GUANGDONG'
OFICINA = 'Cuartel municipal 三防 de Shantou'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'xinhua26': ('https://www.news.cn/local/20260725/84981616d4534b4296cf9e9f9bdc4f03/c.html', 'Xinhua: ante el tifón Hongxia, Guangdong evacúa preventivamente a más de 340.000 personas; 19 ciudades activan respuestas de emergencia y 12 (entre ellas Chaozhou, Shantou, Jieyang, Jiangmen y Dongguan) aplican las "cinco suspensiones"', '2026'),
    'plan_st': ('https://www.shantou.gov.cn/attachment/0/1/1461/1681965.pdf', 'Gobierno de Shantou: documento del cuartel municipal 三防 sobre las respuestas de emergencia por niveles según el plan de emergencia municipal 防汛防旱防风防冻', 's/f'),
}

EN = {
    '1.2.2': (4, C, 'Ante el tifón Hongxia (julio de 2026) Shantou activó su respuesta de emergencia ante vientos y lluvias y aplicó total o parcialmente las "cinco suspensiones" (clases, trabajo, transporte, comercios y obras), dentro de la evacuación preventiva de más de 340.000 personas en Guangdong.',
        'xinhua26', 'Publicar la revisión de la respuesta.', 'Cuartel municipal 三防 de Shantou', CORTO),
    '9.2.1': (3, M, 'Shantou tiene un plan municipal de emergencia ante crecidas, sequías, vientos y heladas con respuestas por niveles (III, II, I) que activa y ajusta el cuartel municipal 三防; no se verifica que se ligue a escenarios.',
        'plan_st', 'Publicar el plan ligado a escenarios.', 'Cuartel municipal 三防 de Shantou', MED),
}
ES = {
}
