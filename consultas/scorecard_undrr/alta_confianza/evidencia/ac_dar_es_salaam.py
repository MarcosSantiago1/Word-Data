# Dar es Salaam (Dar es Salaam City Council; Comisionado Regional): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'dar_es_salaam', 'Dar es Salaam', 'TZA'
OFICINA = 'Dar es Salaam City Council'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'
F = {
    'cdp': ('https://www.cdp.net/en/responses/35893', 'CDP-ICLEI Cities 2023: respuesta oficial del Dar es Salaam City Council', '2023'),
    'bm_msimbazi': ('https://www.worldbank.org/en/country/tanzania/brief/msimbazi-basin-development-project', 'Banco Mundial: Proyecto de Desarrollo de la Cuenca del Msimbazi (200 millones de dólares aprobados en 2022)', '2022'),
    'gfdrr_msimbazi': ('https://www.gfdrr.org/en/feature-story/msimbazi-basin-long-term-integrated-approach-flood-risk-management-and-urban', 'GFDRR: cuenca del Msimbazi, enfoque integrado de largo plazo para la gestión del riesgo de inundación (la crecida de 2018 costó 100 millones de dólares, 2% del PIB de la ciudad)', 's/f'),
    'ips_msimbazi': ('https://www.ipsnews.net/2025/07/world-bank-funded-climate-resilience-project-saves-tanzanias-port-city-from-drowning/', 'IPS: el proyecto de resiliencia financiado por el Banco Mundial protege a la ciudad portuaria de inundarse', '2025'),
    'cit_evac': ('https://www.thecitizen.co.tz/tanzania/news/national/tanzania-braces-for-flood-downpours-cause-damage-evacuations-ordered-in-high-risk-areas-4983092', 'The Citizen: Tanzania se prepara para las lluvias; se ordena evacuar zonas de alto riesgo', '2025'),
    'ifrc_eap': ('https://go-api.ifrc.org/api/downloadfile/91202/MDRTZ041EAP', 'IFRC: Protocolo de Acción Temprana ante inundaciones de Tanzania (pronóstico de impacto a cinco días de la TMA, coordinación con el Departamento de Gestión de Desastres de la Oficina del Primer Ministro)', '2024'),
}
EN = {
    '1.1.1': (2, C, 'La ciudad considera el clima en algunas partidas del presupuesto (arbolado, puentes, transporte rápido) y tiene un plan de acción climática 2020-2050 (CDP 2023), sin evidencia de que el riesgo de desastres guíe el plan urbano.',
              'cdp', 'Integrar los mapas de inundación al plan maestro.', 'City Council', MED),
    '2.1.1': (2, C, 'Las evaluaciones de riesgo y vulnerabilidad que cita la ciudad son de 2007 a 2018, centradas en el sector agua y los medios de vida (CDP 2023).',
              'cdp', 'Evaluación multiamenaza actualizada.', 'City Council', CORTO),
    '2.2.1': (2, C, 'La ciudad estima la población expuesta: 20-30% a inundación urbana, 60-70% al calor extremo y 40-50% a la sequía (CDP 2023), sin escenarios.',
              'cdp', 'Escenarios por amenaza.', 'City Council', CORTO),
    '2.2.2': (2, M, 'La crecida de 2018 en la cuenca del Msimbazi causó daños por unos 100 millones de dólares, 2% del PIB de la ciudad (GFDRR).',
              'gfdrr_msimbazi', 'Estimar pérdidas por escenario.', 'City Council', MED),
    '8.1.1': (3, C, 'La ciudad construyó 1.180 m de muro marítimo que detuvo la erosión costera (CDP 2023) y el proyecto de la cuenca del Msimbazi (200 millones de dólares del Banco Mundial) reduce la inundación en la llanura baja.',
              'cdp,bm_msimbazi,ips_msimbazi', 'Completar las obras del Msimbazi.', 'TAMISEMI / City Council', LARGO),
    '4.4.1': (2, C, 'El proyecto del Msimbazi reubicó residentes de Jangwani a zonas altas (Madale) en 2024, pero en temporadas de lluvia el gobierno debe ordenar evacuar zonas de alto riesgo aún ocupadas.',
              'bm_msimbazi,cit_evac', 'Impedir la reocupación de la llanura.', 'City Council', MED),
    '5.2.2': (3, C, 'Restauración de manglares en Mbweni y Kunduchi y arborización urbana (CDP 2023); el proyecto del Msimbazi transforma la llanura inundable en espacio verde.',
              'cdp,ips_msimbazi', 'Exigir drenaje sostenible en obras nuevas.', 'City Council', MED),
    '9.1.1': (3, C, 'El servicio meteorológico (TMA) emite pronósticos estacionales y de impacto a cinco días que activan un protocolo de acción temprana con el Departamento de Gestión de Desastres; el gobierno ordena evacuar zonas de alto riesgo.',
              'ifrc_eap,cit_evac', 'Alertas a toda la población de la ciudad.', 'TMA / PMO-DMD', CORTO),
}
ES = {
    'A2.2': (2, C, 'La ciudad tiene una meta de programas de concientización sobre riesgos sanitarios prevenibles y declara falta de capacidad técnica y financiera para atender los efectos del clima en la salud (CDP 2023).',
             'cdp', 'Plan de salud ante inundación y calor.', 'Departamento de Salud de la ciudad', MED),
}
