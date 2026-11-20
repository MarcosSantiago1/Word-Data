# Kabul (municipalidad de Kabul; ANDMA): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'kabul', 'Kabul', 'AFG'
OFICINA = 'Municipalidad de Kabul / ANDMA'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'
F = {
    'aj_agua': ('https://aljazeera.com/features/2025/7/5/end-is-near-will-kabul-become-first-big-city-without-water-by-2030', 'Al Jazeera: ¿será Kabul la primera gran ciudad sin agua en 2030? (informe de Mercy Corps)', '2025'),
    'kn_agua': ('https://kabulnow.com/2025/06/report-warns-kabul-could-run-out-of-water-within-5-years/', 'KabulNow: un informe advierte que Kabul podría quedarse sin agua en cinco años (UNICEF: la mitad de los pozos ya se secaron)', '2025'),
    'swn24': ('https://swn.af/en/2024/04/devastating-flash-floods-in-some-afghan-provinces-claim-33-lives-injure-27', 'SWN: crecidas repentinas en 17 provincias, incluida Kabul, dejan 33 muertos; la ANDMA pide trasladarse a zonas seguras', '2024'),
}
EN = {
    '8.2.1': (1, M, 'La extracción de agua subterránea supera la recarga en 44 millones de m³ por año, casi la mitad de los pozos se secaron y los acuíferos podrían agotarse hacia 2030 (Mercy Corps, UNICEF).',
              'aj_agua,kn_agua', 'Plan de seguridad hídrica y fuentes alternativas.', 'Municipalidad / empresa de agua', LARGO),
    '9.1.1': (2, M, 'La autoridad nacional de desastres emite avisos generales y pide a la población de zonas expuestas que se traslade antes de lluvias pronosticadas; no se halló sistema de alerta de la ciudad.',
              'swn24', 'Sistema de alerta de crecidas para la ciudad.', 'ANDMA / municipalidad', MED),
}
ES = {}
