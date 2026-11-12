# El Cairo (gobernación): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'el_cairo', 'El Cairo (gobernación)', 'EGY'
OFICINA = 'Gobernación de El Cairo (sala central de operaciones)'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'et_alerta': ('https://www.egypttoday.com/Article/1/145887/Cairo-Governor-raises-alert-level-to-maximum-in-anticipation-of', 'Egypt Today: el gobernador de El Cairo eleva la alerta al máximo ante las lluvias previstas', 's/f'),
    'ahram_2018': ('https://english.ahram.org.eg/News/298456.aspx', 'Ahram Online: el fiscal general ordena un informe sobre la "falla en la gestión" de las lluvias en Nuevo Cairo', '2018'),
}

EN = {
    '1.2.2': (3, M, 'Ante lluvias la gobernación eleva la alerta al máximo y conecta las salas de operaciones de los distritos con una sala central; tras las inundaciones de 2018 en Nuevo Cairo se suspendió a funcionarios y la fiscalía señaló falta de coordinación entre ministerios y la gobernación.',
        'et_alerta,ahram_2018', 'Plan de coordinación con roles por institución.', 'Gobernación de El Cairo', CORTO),
}
ES = {
}
