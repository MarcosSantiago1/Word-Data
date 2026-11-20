# Gujranwala (distrito; DDMA Gujranwala / PDMA Punyab): base de alta confianza, búsqueda nov-2026. Hereda la evidencia de Punyab (Rescue 1122) y de Pakistán.
ID, NOMBRE, ISO3 = 'gujranwala', 'Gujranwala', 'PAK'
PROV = 'PUNJAB'
OFICINA = 'DDMA Gujranwala / PDMA Punyab'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'trib_lluvia': ('https://tribune.com.pk/story/2619568/record-rains-inundate-gujranwala-gujrat', 'Express Tribune: lluvias récord (250 mm) inundan Gujranwala y Gujrat; obras de WASA sin terminar antes del monzón', '2025'),
    'dawn_245': ('https://www.dawn.com/news/1926354', 'Dawn: récord de 245 mm de lluvia en Gujranwala según WASA', '2025'),
}

EN = {
    '8.1.1': (1, M, 'Con la lluvia récord de 245-250 mm del primer temporal del monzón de 2025 varias zonas quedaron anegadas porque las obras de drenaje de WASA no estaban terminadas; murieron al menos cinco personas.',
        'trib_lluvia,dawn_245', 'Terminar y dimensionar el drenaje pluvial para el escenario más probable.', 'WASA Gujranwala', LARGO),
}
ES = {
}
