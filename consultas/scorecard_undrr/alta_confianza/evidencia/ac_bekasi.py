# Bekasi (Pemerintah Kota Bekasi; BPBD Kota Bekasi): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'bekasi', 'Bekasi', 'IDN'
OFICINA = 'BPBD Kota Bekasi'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/68337', 'CDP-ICLEI Cities 2023: respuesta oficial del gobierno de la ciudad de Bekasi', '2023'),
    'mtv_20': ('https://www.metrotvnews.com/read/kqYCYZ3A-20-titik-banjir-kepung-kota-bekasi', 'Metro TV: 20 puntos de inundación en la ciudad de Bekasi (BPBD)', '2025'),
    'rm_8m': ('https://rm.id/baca-berita/nasional/256797/bekasi-lumpuh-ketinggian-air-kali-bekasi-capai-8-meter-rumah-kantor-terendam', 'RM.id: Bekasi paralizada, el río Bekasi llega a 8 metros', '2025'),
    'ant_audit': ('https://babel.antaranews.com/berita/470993/pemerintah-audit-infrastruktur-bekasi-terkait-banjir', 'Antara: el gobierno audita la infraestructura de Bekasi tras la inundación', '2025'),
    'okz_pu': ('https://economy.okezone.com/read/2025/03/04/320/3119444/tanggap-darurat-banjir-bekasi-menteri-pu-turun-tangan', 'Okezone: emergencia por la inundación de Bekasi; interviene el ministro de Obras Públicas', '2025'),
    'ant_112': ('https://www.antaranews.com/berita/4687501/daftar-nomor-darurat-untuk-meminta-evakuasi-bencana-di-bekasi', 'Antara: números de emergencia para pedir evacuación en Bekasi', '2025'),
}

EN = {
    '1.1.1': (1, C, 'El cambio climático figura como tema estratégico en el borrador de evaluación ambiental estratégica del plan de desarrollo 2025-2045, pero la ciudad declaró que no influye en el presupuesto (CDP 2023).',
              'cdp', 'Llevar el riesgo de inundación al plan y al presupuesto.', 'Bappeda Kota Bekasi', MED),
    '2.1.1': (2, C, 'La ciudad hizo una evaluación de riesgo y vulnerabilidad climática en 2018 (más de tres años) y estima que el 60-70% de la población está expuesta a la inundación urbana (CDP 2023).',
              'cdp', 'Actualizar la evaluación con escenarios del río Bekasi.', 'BPBD / Bappeda', CORTO),
    '2.2.1': (2, C, 'Estimación de exposición a inundación urbana del 60-70% de la población (CDP 2023), sin escenarios por nivel de amenaza.',
              'cdp', 'Escenarios por nivel de crecida.', 'BPBD', CORTO),
    '3.2.1': (1, C, 'Sin metas de adaptación ni plan de acción climática al 2023 (CDP); declara que el clima no afecta el presupuesto.',
              'cdp', 'Plan financiero de reducción del riesgo.', 'Bappeda', MED),
    '1.2.2': (3, C, 'En la crecida de marzo de 2025 (20 puntos inundados, río a 8 metros) la ciudad pidió evacuar desde la noche anterior y la respuesta sumó a la BPBD provincial, el ejército y la BNPB, con números de emergencia publicados.',
              'mtv_20,rm_8m,ant_112,okz_pu', 'Revisión posevento de la crecida de 2025.', 'BPBD Kota Bekasi', CORTO),
    '4.1.1': (2, C, 'En marzo de 2025 se vieron afectadas más de 12.000 familias y unas 5.000 fueron evacuadas.',
              'rm_8m,mtv_20', 'Estimar desplazados por escenario.', 'BPBD', CORTO),
    '8.1.1': (1, C, 'Los terraplenes del río Bekasi fueron superados en 2025, en la peor crecida según el alcalde (peor que 2016 y 2020); el gobierno nacional ordenó auditar la infraestructura.',
              'rm_8m,ant_audit', 'Obras de control de crecidas aguas arriba y en la ciudad.', 'Ministerio de Obras Públicas / ciudad', LARGO),
    '10.2.1': (2, C, 'Tras la crecida de 2025 el gobierno nacional dispuso una auditoría de la infraestructura de Bekasi; no se halló revisión posevento publicada de la ciudad.',
               'ant_audit', 'Publicar la revisión posevento.', 'BPBD Kota Bekasi', CORTO),
}
ES = {
    'A2.1': (2, C, 'La ciudad asocia la inundación con más enfermedades y declara que necesita más capacidad de salud pública (CDP 2023).',
             'cdp', 'Escenarios de salud por inundación.', 'Dinas Kesehatan', MED),
}
