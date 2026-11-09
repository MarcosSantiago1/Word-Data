# Hai Phong (ciudad de rango provincial; Comité Popular y Comité Directivo de Prevención y Control de Desastres): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'hai_phong', 'Hai Phong', 'VNM'
OFICINA = 'Comité Directivo de Prevención y Control de Desastres de Hai Phong'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'
F = {
    'ld_despacho': ('https://news.laodong.vn/xa-hoi/hai-phong-ban-hanh-cong-dien-khan-ung-pho-bao-so-3-1389059.ldo', 'Lao Dong: Hai Phong emite despacho urgente ante la tormenta n.º 3 (Yagi), con planes de evacuación de zonas bajas, ribereñas y costeras', '2024'),
    'dti_5400': ('https://dtinews.dantri.com.vn/en/news/024/90490/northern-coastal-localities-evacuate-13-000-households-as-typhoon-nears.html', 'Dân Trí: las localidades costeras del norte evacúan 13.000 hogares ante el tifón (Hai Phong: 5.400 hogares de edificios viejos y zonas vulnerables)', '2024'),
    'ld_danos': ('https://news.laodong.vn/xa-hoi/thiet-hai-sau-bao-cua-hai-phong-chua-the-danh-gia-thong-ke-chinh-xac-1390995.ldo', 'Lao Dong: los daños de la tormenta en Hai Phong aún no se pueden evaluar con precisión', '2024'),
    'vnn_yagi': ('https://vietnamnet.vn/en/power-outages-and-disruptions-as-typhoon-yagi-makes-landfall-in-northern-vietnam-2319421.html', 'VietNamNet: cortes de energía e interrupciones al tocar tierra el tifón Yagi en el norte de Vietnam', '2024'),
    'dique_ndv': ('https://en.haiphong.gov.vn/news/progress-of-nam-dinh-vu-sea-dike-project-668862', 'Portal de Hai Phong: avance del dique marítimo de Nam Dinh Vu (12,8 km, 2.284.000 millones de VND)', 's/f'),
    'resol24': ('https://haiphongnews.gov.vn/news/hai-phong-evaluating-and-summarizing-over-13-years-of-implementing-resolution-no-24-nqtw-on-climate-change-response-and-environmental-protection-ct12971.html', 'Hai Phong News: balance de 13 años de aplicación de la Resolución 24 sobre cambio climático (incluye refuerzo del dique de Cat Hai)', '2025'),
    'wv_diques': ('https://www.wvi.org/vietnam/article/preparing-natural-disasters', 'World Vision: proyecto Hai Phong resiliente al cambio climático; capacitación en mantenimiento de diques con la autoridad de diques', 's/f'),
}
EN = {
    '1.2.2': (3, C, 'Ante el tifón Yagi (2024) el presidente del Comité Popular emitió un despacho urgente con planes de evacuación y la ciudad trasladó 5.400 hogares de edificios viejos y zonas vulnerables a escuelas y edificios públicos.',
              'ld_despacho,dti_5400', 'Revisión posevento publicada.', 'Comité Directivo de Desastres', CORTO),
    '8.1.1': (3, C, 'La ciudad construye y refuerza diques marítimos (Nam Dinh Vu, 12,8 km; Cat Hai) contra tormentas, crecidas y suba del mar.',
              'dique_ndv,resol24', 'Completar los diques y evaluar su nivel de protección.', 'Departamento de Agricultura / Gestión de Diques', LARGO),
    '8.1.2': (3, M, 'Existe un departamento de gestión de diques con programas de mantenimiento y capacitación.',
              'wv_diques', 'Plan de mantenimiento publicado.', 'Gestión de Diques', CORTO),
    '8.3.1': (2, M, 'El tifón Yagi dejó cortes de energía extendidos en la región y bloqueó calles y comunicaciones en Hai Phong.',
              'vnn_yagi,dti_5400', 'Plan de restitución de energía.', 'EVN / ciudad', MED),
    '10.2.1': (2, C, 'Tras el tifón Yagi la ciudad no pudo evaluar con precisión los daños y el primer ministro ordenó reevaluarlos y registrarlos.',
               'ld_danos', 'Protocolo de evaluación de daños y revisión posevento.', 'Comité Popular', CORTO),
}
ES = {}

# Plan oficial leído completo (nov-2026): plan 2025 de la zona especial Cát Hải (Hai Phong), según la Directiva 07/CT-UBND de la ciudad.
F['cathai25'] = ('https://cdn.haiphong.gov.vn/gov-hpg/5889/tintuc/2025/7/kh-pctt-tkcnptds-2025.signed638883603045827967.pdf', 'Comité Popular de Cát Hải (Hai Phong): Plan 2025 de prevención de desastres, búsqueda y rescate y defensa civil', '2025')
EN.update({
    '9.2.1': (2, M, 'Por directiva de la ciudad, cada distrito prepara su plan anual: el de Cát Hải fija la evacuación al menos 5 horas antes de la llegada del tifón, la seguridad de embarcaciones y los cuatro "en el lugar" (mando, fuerzas, medios y logística); solo se publicó este distrito y no hay escenarios.',
              'cathai25', 'Plan de la ciudad por escenario.', 'Comando de Prevención de Desastres de Hai Phong', MED),
    '6.2.1': (4, M, 'El plan de Cát Hải difunde avisos y conocimientos por diario, radio, TV, sitios web, Facebook, correo y SMS, y los jefes de aldea movilizan a los vecinos; es un solo distrito.',
              'cathai25', 'Campaña de toda la ciudad con escuelas.', 'Comité Popular de Hai Phong', CORTO),
})
