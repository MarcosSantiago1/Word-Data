# Depok (Pemerintah Kota Depok; BPBD Kota Depok): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'depok', 'Depok', 'IDN'
OFICINA = 'BPBD Kota Depok'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'mtv_aviso': ('https://www.metrotvnews.com/read/NleC9rBZ-pemkot-depok-ingatkan-warga-waspadai-potensi-banjir-dan-longsor', 'Metro TV: la municipalidad de Depok pide a los vecinos estar alertas ante inundaciones y deslizamientos (DPUPR moviliza grupos de tarea)', '2026'),
    'lip_ciliwung': ('https://liputan6.com/news/read/7327544/rumah-nyaris-ambruk-di-bantaran-ciliwung-motor-sempat-terbawa-longsor', 'Liputan6: casa casi derrumbada en la ribera del Ciliwung por deslizamiento', '2026'),
}

EN = {
    '1.2.2': (2, M, 'Ante la temporada de lluvias la municipalidad moviliza grupos de tarea y flota de Obras Públicas y emite avisos; no se halló plan de coordinación publicado.',
              'mtv_aviso', 'Plan de coordinación de la respuesta.', 'BPBD Kota Depok', CORTO),
    '4.4.1': (1, M, 'Hay viviendas en la ribera del Ciliwung afectadas por erosión y deslizamientos (2026).',
              'lip_ciliwung', 'Controlar la ocupación de riberas.', 'DPUPR Kota Depok', MED),
}
ES = {}
