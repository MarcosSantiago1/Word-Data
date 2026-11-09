# Mbuji-Mayi (municipalidad; gobierno provincial de Kasai Oriental): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'mbuji_mayi', 'Mbuji-Mayi', 'COD'
OFICINA = 'Mairie de Mbuji-Mayi / gobierno provincial de Kasai Oriental'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'
F = {
    'acp_7': ('https://acp.cd/province/kasai-oriental-sept-deces-enregistres-apres-des-pluies-diluviennes-tombees-a-mbuji-mayi/', 'ACP (agencia oficial congoleña): siete muertos tras lluvias torrenciales en Mbuji-Mayi', '2025'),
    'acp_2m': ('https://acp.cd/province/mbuji-mayi-deux-millions-usd-pour-la-poursuite-des-travaux-sur-un-site-erosif/', 'ACP: dos millones de dólares para seguir las obras en un sitio de erosión de Mbuji-Mayi (Mulamba wa Mpoyi)', '2024'),
    'act_susp': ('https://actualite.cd/2025/07/16/mbuji-mayi-les-travaux-de-lutte-contre-lerosion-mulamba-wa-mpoyi-suspendus-la-population', 'Actualité.cd: suspendidas las obras contra la erosión de Mulamba wa Mpoyi', '2025'),
    'acp_12': ('https://acp.cd/province/kasai-oriental-12-de-taux-dexecution-des-travaux-de-lutte-antierosive-a-mbuji-mayi/', 'ACP: 12% de avance de las obras contra la erosión en Mbuji-Mayi', '2024'),
}
EN = {
    '8.1.1': (1, C, 'Más de 600 cabezas de erosión amenazan barrios; las obras de Mulamba wa Mpoyi (2 millones de dólares del gobierno nacional) quedaron suspendidas en 2025 y otro sitio llevaba 12% de avance.',
              'acp_2m,act_susp,acp_12', 'Retomar y terminar las obras contra la erosión.', 'Gobierno provincial / Ministerio de Obras', LARGO),
    '8.1.2': (1, C, 'Las obras contra la erosión se interrumpen por falta de fondos o continuidad (suspensión en 2025).',
              'act_susp', 'Financiamiento estable de mantenimiento.', 'Gobierno provincial', CORTO),
    '4.4.2': (1, C, 'En marzo de 2025 las lluvias dejaron siete muertos y casas destruidas en las cinco comunas, con muros que se derrumbaron sobre sus ocupantes.',
              'acp_7', 'Normas mínimas de construcción y control.', 'Mairie de Mbuji-Mayi', MED),
}
ES = {}
