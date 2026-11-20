# Alejandría (gobernación): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'alejandria', 'Alejandría (gobernación)', 'EGY'
OFICINA = 'Gobernación de Alejandría'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'dne_alerta': ('https://www.dailynewsegypt.com/?p=832640', 'Daily News Egypt: Alejandría eleva la alerta de emergencia al máximo por tormenta con granizo, crecidas repentinas y cortes de luz', '2025'),
    'ahram_2015': ('https://english.ahram.org.eg/News/162035.aspx', 'Ahram Online: las inundaciones de Alejandría; la ciudad no tiene drenaje pluvial, solo cloacas (2015, tras la renuncia del gobernador)', '2015'),
}

EN = {
    '1.2.2': (3, M, 'Ante la tormenta de 2025 la gobernación elevó la alerta al máximo, su sala de operaciones atendió reclamos día y noche, la empresa de saneamiento desplegó 180 camiones de succión y el Ministerio de Solidaridad activó una sala central; no se publican roles de cada institución.',
        'dne_alerta', 'Plan de coordinación con roles por institución.', 'Gobernación de Alejandría', CORTO),
    '8.1.1': (1, M, 'Alejandría no tiene red de drenaje pluvial, solo cloacas, según la autoridad de drenaje; en 2015 las lluvias mataron a varias personas y llevaron a la renuncia del gobernador.',
        'ahram_2015,dne_alerta', 'Red de drenaje pluvial para el escenario más probable.', 'Gobernación / Empresa de Saneamiento de Alejandría', LARGO),
}
ES = {
}
