# Dongguan (gobierno popular municipal; cuartel municipal de prevención de crecidas, sequías y vientos): base de alta confianza, búsqueda nov-2026. Hereda la evidencia de Guangdong y de China.
ID, NOMBRE, ISO3 = 'dongguan', 'Dongguan', 'CHN'
PROV = 'GUANGDONG'
OFICINA = 'Cuartel municipal 三防 de Dongguan'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'xinhua26': ('https://www.news.cn/local/20260725/84981616d4534b4296cf9e9f9bdc4f03/c.html', 'Xinhua: ante el tifón Hongxia, Guangdong evacúa preventivamente a más de 340.000 personas; 19 ciudades activan respuestas de emergencia y 12 (entre ellas Chaozhou, Shantou, Jieyang, Jiangmen y Dongguan) aplican las "cinco suspensiones"', '2026'),
    'plan_dg': ('https://gdjt.dg.gov.cn/attachment/0/236/236302/4141406.pdf', 'Oficina de Transporte de Dongguan: plan especial de emergencia que cita como base el plan general de emergencias de la ciudad y su plan 防汛防旱防风防冻', 's/f'),
}

EN = {
    '1.2.2': (4, C, 'Ante el tifón Hongxia (julio de 2026) Dongguan activó su respuesta de emergencia ante vientos y lluvias y aplicó total o parcialmente las "cinco suspensiones" (clases, trabajo, transporte, comercios y obras), dentro de la evacuación preventiva de más de 340.000 personas en Guangdong.',
        'xinhua26', 'Publicar la revisión de la respuesta.', 'Cuartel municipal 三防 de Dongguan', CORTO),
    '9.2.1': (3, M, 'Dongguan tiene un plan general de emergencias y un plan municipal ante crecidas, sequías, vientos y heladas, citados como base por los planes sectoriales; no se publica su texto ligado a escenarios.',
        'plan_dg', 'Publicar el plan ligado a escenarios.', 'Cuartel municipal 三防 de Dongguan', MED),
}
ES = {
}
