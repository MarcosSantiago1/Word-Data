# Bombay (Brihanmumbai Municipal Corporation, BMC/MCGM): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'bombay', 'Bombay', 'IND'
OFICINA = 'Departamento de Gestión de Desastres de la BMC'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/31178', 'CDP-ICLEI Cities 2023: respuesta oficial de la ciudad de Bombay (BMC)', '2023'),
    'ddmp': ('https://divcomkonkan.gov.in/frontend/pdf/disaster/DDMP-MumbaiCity-2023-24.pdf', 'División de Konkan (gobierno de Maharashtra): District Disaster Management Plan Mumbai City 2023-24 (centro de operaciones de emergencia, respaldo y centros por distrito municipal)', '2023'),
    'eoc_dir': ('https://dm.mcgm.gov.in/assets/pdf/Final%20updated%20Final%20Connect%20Diary%202021.07.07.2021.pdf', 'BMC, Departamento de Gestión de Desastres: directorio de contactos 2021 (centro de operaciones de emergencia, línea 1916)', '2021'),
    'fpj_g20': ('https://www.freepressjournal.in/mumbai/mumbai-news-bmc-showcases-disaster-preparedness-to-g-20-delegates-at-heritage-headquarters', 'Free Press Journal: la BMC muestra su preparación ante desastres a delegados del G20 (centro de operaciones 24 horas; 1.000 voluntarios capacitados)', '2023'),
    'iflows': ('https://www.dnaindia.com/mumbai/report-flood-warning-system-for-mumbai-launched-can-predict-flooding-3-days-in-advance-at-ward-level-2827783', 'DNA: se lanza el sistema de alerta de inundación de Bombay (IFLOWS), con pronóstico a 3 días por distrito municipal', '2020'),
    'iflows_ml': ('https://www.mumbailive.com/en/civic/bmc-says-the-flood-monitoring-system-could-not-help-detect-recent-flooding-66710', 'Mumbai Live: la BMC dice que el sistema de monitoreo de inundaciones no ayudó a detectar la inundación reciente (en fase experimental, a cargo del IMD)', 's/f'),
    'apada': ('https://www.freepressjournal.in/mumbai/mumbai-disaster-preparedness-first-batch-of-bmcs-apada-mitras-successfully-complete-training', 'Free Press Journal: completa su capacitación la primera tanda de voluntarios Apada Mitra de la BMC', '2023'),
    'apada24': ('https://www.freepressjournal.in/mumbai/mumbai-bmc-set-to-mobilise-1000-aapda-mitras-for-disaster-management-in-monsoon-prone-areas', 'Free Press Journal: la BMC moviliza 1.000 Aapda Mitras en 74 zonas vulnerables al monzón', '2024'),
    'c1_25': ('https://www.freepressjournal.in/mumbai/mumbai-news-bmc-identifies-134-dilapidated-buildings-in-pre-monsoon-survey-57-vacated-77-still-occupied', 'Free Press Journal: la BMC identifica 134 edificios ruinosos (C1) en su relevamiento premonzón; 77 siguen ocupados', '2025'),
    'presup25': ('https://data.opencity.in/dataset/bmc-budget-2025-26', 'OpenCity: presupuesto de la BMC 2025-26 (documentos oficiales)', '2025'),
    'clima25': ('https://www.freepressjournal.in/mumbai/mumbai-news-bmc-unveils-17066-crore-climate-action-plan-amid-staffing-challenges-in-environment-department', 'Free Press Journal: la BMC presenta un presupuesto climático de 17.066 crore de rupias para 2025-26', '2025'),
    'calor_rfp': ('https://www.c40.org/wp-content/uploads/2026/07/RfP-Heat-Health-protocols-for-Mumbai.pdf', 'C40: licitación para protocolos de calor y salud de Bombay', '2026'),
}

EN = {
    '1.1.1': (3, C, 'El Mumbai Climate Action Plan (2022, hasta 2050) incluye una evaluación de riesgo climático que, según la ciudad, se incorporó al marco general de gestión de riesgos; los riesgos climáticos se consideran en planes y presupuesto (CDP 2023). No cubre el riesgo sísmico.',
              'cdp', 'Llevar los riesgos al plan de desarrollo y sumar el sismo.', 'BMC', MED),
    '1.1.2': (3, C, 'El plan climático se elaboró con gobierno estatal, empresas, ciudadanos y ONG (CDP 2023).',
              'cdp', 'Mantener la consulta en las actualizaciones.', 'BMC, Departamento de Ambiente', MED),
    '1.1.3': (4, C, 'El plan climático se monitorea, evalúa y actualiza cada año, y la evaluación de riesgo se actualiza al menos cada cinco años (CDP 2023).',
              'cdp', 'Sin acción prioritaria.', '', ''),
    '1.2.1': (4, C, 'Hay plan distrital de gestión de desastres 2023-24 con centro de operaciones de emergencia, centro de respaldo y centros por distrito municipal, y un Departamento de Gestión de Desastres de la BMC.',
              'ddmp,eoc_dir', 'Actualizar el plan para la ciudad suburbana con escenarios.', 'BMC / autoridad distrital', CORTO),
    '1.2.2': (4, C, 'El centro de operaciones de la BMC funciona las 24 horas los 365 días, con la línea 1916, y coordina la respuesta a inundaciones y ciclones.',
              'ddmp,fpj_g20,eoc_dir', 'Revisión posevento publicada de cada monzón.', 'BMC', CORTO),
    '2.1.1': (4, C, 'Evaluación de riesgo y vulnerabilidad climática publicada en 2022 para toda la ciudad, con escenario de altas emisiones (RCP 8.5), población vulnerable y priorización de amenazas (CDP 2023).',
              'cdp', 'Sumar el riesgo sísmico.', 'BMC', MED),
    '2.2.1': (3, C, 'La ciudad estima que el 30-40% de la población está expuesta a inundación urbana (35% vive a menos de 250 m de puntos críticos) y el 20-30% al calor extremo (CDP 2023).',
              'cdp', 'Escenarios por intensidad de lluvia y marea.', 'BMC', CORTO),
    '2.2.2': (2, C, 'La ciudad cita pérdidas por inundación de 140.000 millones de rupias entre 2005 y 2015 (estudio de USTDA y KPMG), sin estimación por escenario.',
              'cdp', 'Estimar pérdidas de empleo y producción por escenario.', 'BMC', MED),
    '2.5.1': (4, C, 'Hay un proceso para actualizar la evaluación de riesgo al menos cada cinco años (CDP 2023).',
              'cdp', 'Sin acción prioritaria.', '', ''),
    '3.2.1': (3, C, 'La ciudad financia el plan con recursos propios, asociaciones público-privadas y fondos nacionales; presentó un presupuesto climático de 17.066 crore de rupias para 2025-26 (CDP 2023; presupuesto 2025-26).',
              'cdp,clima25,presup25', 'Ligar el presupuesto a metas de reducción del riesgo.', 'BMC', MED),
    '3.2.2': (3, C, 'El presupuesto 2023-24 previó 2.570 crore de rupias para obras de drenaje pluvial y la ciudad gastó 13.910 millones de rupias contra inundaciones en años recientes (CDP 2023).',
              'cdp,presup25', 'Plan de inversión de largo plazo en drenaje y costa.', 'BMC, Departamento de Drenaje Pluvial', LARGO),
    '4.4.2': (2, C, 'En 2025 la BMC identificó 134 edificios ruinosos (C1) y 77 seguían ocupados; las auditorías estructurales son obligatorias para edificios de más de 30 años pero se cumplen de forma parcial.',
              'c1_25', 'Desalojar y reforzar los edificios C1.', 'BMC, Departamento de Edificios', CORTO),
    '5.1.1': (3, C, 'La ciudad tiene metas de cobertura vegetal y superficie permeable del 30-40% para 2030 para reducir inundación y calor, y protege y replanta manglares (CDP 2023).',
              'cdp', 'Inventario de servicios ecosistémicos.', 'BMC, Departamento de Ambiente', MED),
    '5.1.2': (1, C, 'La cobertura vegetal bajó del 46,4% en 1988 al 26,7% en 2018 y hay 1,8 m² de verde por habitante (CDP 2023).',
              'cdp', 'Revertir la pérdida de cobertura verde.', 'BMC', LARGO),
    '5.2.2': (3, C, 'Restauración del río Mithi, plantación de 377.416 árboles en 100 sitios y muros de protección de manglares, incluidos en el plan climático (CDP 2023).',
              'cdp', 'Exigir infraestructura verde y azul en obras nuevas.', 'BMC', MED),
    '6.4.1': (3, C, 'La BMC capacitó con la NDRF a 1.000 voluntarios Apada Mitra en búsqueda y rescate y primeros auxilios, y los distribuyó por distrito municipal en 74 zonas vulnerables.',
              'apada,apada24,fpj_g20', 'Capacitación anual con metas de cobertura.', 'BMC, Gestión de Desastres', CORTO),
    '7.2.2': (3, C, 'La evaluación de riesgo considera poblaciones vulnerables (hogares de bajos ingresos, trabajadores al aire libre, comunidades costeras, adultos mayores) y el 55% de la población vive en asentamientos informales (CDP 2023).',
              'cdp', 'Planes con participación de esos grupos.', 'BMC', MED),
    '8.1.1': (2, C, 'Hay obras de drenaje y defensa contra inundación que, según la ciudad, aumentan la resiliencia del 20-30% de la población; la inundación recurrente sigue siendo la amenaza principal (CDP 2023).',
              'cdp', 'Completar el drenaje pluvial y la defensa costera.', 'BMC, Drenaje Pluvial', LARGO),
    '9.1.1': (2, C, 'El sistema IFLOWS (2020) pronostica inundaciones hasta tres días antes por distrito municipal, pero la BMC dijo que no estaba plenamente operativo y que está a cargo del IMD en fase experimental.',
              'iflows,iflows_ml', 'Pasar el sistema a operación con la BMC.', 'BMC / IMD', CORTO),
    '9.2.1': (3, C, 'El plan distrital 2023-24 define activación y funciones del centro de operaciones, respaldo y centros por distrito municipal, sin escenarios cuantificados.',
              'ddmp', 'Planes por escenario más probable y más severo.', 'BMC', MED),
    '9.6.2': (5, C, 'Centro de operaciones de emergencia en la sede de la BMC, activo las 24 horas con 60 líneas, radio y centro de respaldo; reúne a los organismos de respuesta.',
              'ddmp,fpj_g20,eoc_dir', 'Sin acción prioritaria.', '', ''),
}
ES = {
    'A2.2': (2, C, 'La ciudad identifica efectos del calor, la inundación y los ciclones en la salud (lesiones, enfermedades por vectores y agua, golpe de calor) pero declara falta de capacidad técnica (CDP 2023); en 2026 C40 licitó protocolos de calor y salud para Bombay.',
             'cdp,calor_rfp', 'Aprobar el plan de calor y salud.', 'BMC, Departamento de Salud', CORTO),
    'A9.3': (3, C, 'Identifica como más expuestos a niños, mujeres, adultos mayores, trabajadores al aire libre y hogares de bajos ingresos (CDP 2023).',
             'cdp', 'Registro de personas dependientes.', 'BMC, Departamento de Salud', MED),
}

# Plan oficial leído completo (nov-2026): Mumbai Climate Action Plan 2022.
F['mcap22'] = ('https://portal.mcgm.gov.in/irj/go/km/docs/documents/Environment/Climate/Mumbai%20Climate%20Action%20Plan.pdf', 'BMC: Mumbai Climate Action Plan 2022', '2022')
EN['2.2.1'] = (3, C, 'La ciudad estima que el 30-40% de la población está expuesta a inundación urbana (35% vive a menos de 250 m de puntos críticos) y el 20-30% al calor extremo (CDP 2023); el plan climático 2022 mapea la población alrededor de cada punto de anegamiento y los asentamientos informales en zonas de deslizamiento.',
               'cdp,mcap22', 'Escenarios por intensidad de lluvia y marea.', 'BMC', CORTO)
ES['A9.1'] = (2, M, 'Hay alerta de inundación (iFLOWS) y avisos meteorológicos, pero el plan de acción de calor que el plan climático 2022 preveía para 2022-2023 sigue pendiente: en 2026 se licitaron los protocolos de calor y salud.',
              'mcap22,iflows,calor_rfp', 'Aprobar el plan de calor y salud.', 'BMC: Disaster Management Cell / Salud Pública', CORTO)
