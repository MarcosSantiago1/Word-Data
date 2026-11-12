# Wenzhou (gobierno popular municipal; cuartel municipal de prevención de crecidas, sequías y vientos): base de alta confianza, búsqueda nov-2026. Hereda la evidencia de China.
ID, NOMBRE, ISO3 = 'wenzhou', 'Wenzhou', 'CHN'
OFICINA = 'Cuartel municipal 三防 de Wenzhou'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'ifeng_bavi': ('https://news.ifeng.com/c/8ug0q43Qk8K', 'Ifeng: Wenzhou eleva al nivel I la respuesta ante el tifón Bavi y traslada preventivamente a más de un millón de personas; 2.801 puntos de refugio', '2026'),
    'pp_plan': ('https://www.thepaper.cn/newsDetail_forward_33557962', 'The Paper: el cuartel de Wenzhou eleva la respuesta ante el tifón Bavi según el plan de emergencia municipal de crecidas, tifones y sequías', '2026'),
}

EN = {
    '1.2.2': (4, M, 'Ante el tifón Bavi (julio de 2026) Wenzhou subió su respuesta al nivel I, trasladó preventivamente a más de un millón de personas y habilitó 2.801 puntos de refugio.',
        'ifeng_bavi', 'Publicar la revisión de la respuesta.', 'Cuartel municipal de Wenzhou', CORTO),
    '9.2.1': (3, M, 'Wenzhou tiene un plan municipal de emergencia ante crecidas, tifones y sequías con respuestas por niveles que el cuartel activa tras consulta y evaluación; no se verifica que se ligue a escenarios.',
        'pp_plan,ifeng_bavi', 'Publicar el plan ligado a escenarios.', 'Cuartel municipal de Wenzhou', MED),
}
ES = {
}
