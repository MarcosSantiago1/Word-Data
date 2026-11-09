# Chaozhou (gobierno popular municipal; cuartel municipal de prevención de crecidas, sequías y vientos): base de alta confianza, búsqueda nov-2026. Hereda la evidencia de Guangdong y de China.
ID, NOMBRE, ISO3 = 'chaozhou', 'Chaozhou', 'CHN'
PROV = 'GUANGDONG'
OFICINA = 'Cuartel municipal 三防 de Chaozhou'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'xinhua26': ('https://www.news.cn/local/20260725/84981616d4534b4296cf9e9f9bdc4f03/c.html', 'Xinhua: ante el tifón Hongxia, Guangdong evacúa preventivamente a más de 340.000 personas; 19 ciudades activan respuestas de emergencia y 12 (entre ellas Chaozhou, Shantou, Jieyang, Jiangmen y Dongguan) aplican las "cinco suspensiones"', '2026'),
    'plan_cz': ('https://www.chaozhou.gov.cn/attachment/0/543/543053/3891425.pdf', 'Gobierno de Chaozhou: plan de emergencia ante desastres por crecidas, sequías, vientos y heladas (prioriza la evacuación de personas; incluye tifones y mareas de tormenta) (no se pudo descargar)', 's/f'),
}

EN = {
    '1.2.2': (4, C, 'Ante el tifón Hongxia (julio de 2026) Chaozhou activó su respuesta de emergencia ante vientos y lluvias y aplicó total o parcialmente las "cinco suspensiones" (clases, trabajo, transporte, comercios y obras), dentro de la evacuación preventiva de más de 340.000 personas en Guangdong.',
        'xinhua26', 'Publicar la revisión de la respuesta.', 'Cuartel municipal 三防 de Chaozhou', CORTO),
    '9.2.1': (3, M, 'Chaozhou tiene su propio plan de emergencia ante crecidas, sequías, vientos y heladas, centrado en evacuar personas y controlar la seguridad, que se aplica a tifones y mareas de tormenta; no se pudo leer completo ni verificar si se liga a escenarios.',
        'plan_cz', 'Publicar el plan ligado a escenarios.', 'Cuartel municipal 三防 de Chaozhou', MED),
}
ES = {
}
