# Rangún (Yangon City Development Committee; gobierno de la Región de Yangon): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'rangun', 'Rangún', 'MMR'
OFICINA = 'Yangon City Development Committee'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'
F = {
    'dvb_ff': ('https://english.dvb.no/overflowing-dams-and-rising-creeks-trigger-flash-flood-warnings-across-yangon/', 'DVB: represas desbordadas y arroyos crecidos activan alertas de crecida repentina en nueve municipios de Rangún', '2026'),
    'dmh': ('https://www.moezala.gov.mm/en?page=7', 'Departamento de Meteorología e Hidrología de Myanmar: avisos de inundación, boletines y guía de crecidas repentinas', '2026'),
    'tohoku': ('https://irides.tohoku.ac.jp/media/files/myanmar-session_20250425_KyawSwarMyintThein_rev.pdf', 'IRIDeS, Universidad de Tohoku: sesión sobre el sismo de Myanmar 2025 (Rangún a unos 35 km de la falla activa de Sagaing)', '2025'),
    'adrc': ('https://www.adrc.asia/publications/disaster_report/pdf/2025/Myanmar_EQ_20250328_en.pdf', 'Centro Asiático de Reducción de Desastres: informe del sismo de Myanmar del 28 de marzo de 2025', '2025'),
}
EN = {
    '2.1.1': (2, M, 'La amenaza sísmica de la falla de Sagaing (a unos 35 km) está estudiada por la academia tras el sismo de magnitud 7,7 de 2025, sin evaluación oficial de la ciudad publicada.',
              'tohoku,adrc', 'Evaluación oficial multiamenaza.', 'YCDC / gobierno regional', MED),
    '9.1.1': (3, C, 'El servicio meteorológico nacional emite avisos de inundación y de crecida repentina por municipio (por ejemplo, nueve municipios de Rangún en 2026).',
              'dmh,dvb_ff', 'Llevar los avisos a toda la población.', 'DMH / YCDC', CORTO),
}
ES = {}
