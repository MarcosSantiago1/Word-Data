# Lahore (distrito y Metropolitan Corporation; planificación de la LDA): base de alta confianza, búsqueda nov-2026.
# Siglas: DDMA = District Disaster Management Authority (bajo el Deputy Commissioner); LDA = Lahore Development Authority;
# RUDA = Ravi Urban Development Authority; WASA = agua y drenaje; PDMA = autoridad provincial de Punyab.
ID, NOMBRE, ISO3, PROV = 'lahore', 'Lahore', 'PAK', 'PUNJAB'
OFICINA = 'DDMA Lahore / PDMA Punyab'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'ddmp25': ('https://pdma.punjab.gov.pk/system/files/Review%20DDMP%20plan%202025%20%20Final%20Lahore.pdf', 'PDMA Punyab: District Disaster Management Plan Lahore 2025 (aprobado por el Deputy Commissioner)', '2025'),
    'flood21': ('https://pdma.punjab.gov.pk/system/files/Lahore%20Flood%20plan-2021.pdf', 'PDMA Punyab: Lahore Flood Plan 2021', '2021'),
    'mp2050': ('https://www.dawn.com/news/1715613/lahore-master-plan-approved', 'Dawn: aprobado el Lahore Master Plan 2050', '2022'),
    'mp_limbo': ('https://www.dawn.com/news/1952429/lahores-master-plan-in-limbo-since-2023', 'Dawn: el plan maestro de Lahore en el limbo desde 2023 (sigue rigiendo el de 2016 enmendado)', '2025'),
    'ravi_ilegal': ('https://tribune.com.pk/story/2564010/new-housing-societies-in-shahdara-inundated', 'Express Tribune: urbanizaciones nuevas inundadas en Shahdara; el gobierno las declara ilegales', '2025'),
    'ravi_irreg': ('https://www.dawn.com/news/1938766', 'Dawn: urbanizaciones en zona inundable del Ravi con irregularidades en su aprobación', '2025'),
    'ravi_5': ('https://www.dawn.com/news/1938079/five-lahore-localities-flooded-by-the-ravi', 'Dawn: cinco barrios de Lahore inundados por el Ravi', '2025'),
    'ravi_llanura': ('https://www.dawn.com/news/2012349', 'Dawn: Encroachment risks (llanura de inundación notificada del Ravi de 230 km²; las costaneras de RUDA quedaron a salvo)', '2025'),
    'tanques': ('https://www.thenews.pk/print/1410515-18-underground-water-storage-tanks-developed', 'The News: 18 tanques subterráneos de agua de lluvia desarrollados en Lahore', '2025'),
    'tanque_lr': ('https://www.geo.tv/latest/297749-pakistan-set-up-its-first-underground-water-storage-as-monsoons-hits', 'Geo: primer tanque subterráneo de agua de lluvia en Lawrence Road (WASA/LDA)', '2020'),
    'hwmp_lhr': ('https://urbanunit.gov.pk/Download/publications/Files/8/2025/Heatwave%20Management%20Plan%20of%20Lahore_06_2025%5B1%5D.pdf', 'Urban Unit: Heatwave Management Plan of Lahore 2025-2028', '2025'),
    'calor_sop': ('https://tribune.com.pk/story/2467388/punjab-hospitals-ordered-to-enforce-sops-ahead-of-predicted-temperature-surge', 'Express Tribune: los hospitales de Punyab deben aplicar protocolos y puestos de atención por calor', '2024'),
}

EN = {
    '1.1.1': (1, M, 'El Lahore Master Plan 2050 se aprobó en 2022 pero quedó en el limbo (la justicia ordenó rehacerlo) y sigue rigiendo el plan de 2016 enmendado; no se halló que presente los riesgos de la ciudad.',
              'mp2050,mp_limbo', 'Nuevo plan maestro con mapas de inundación del Ravi, calor y smog.', 'LDA', MED),
    '1.1.3': (1, M, 'El plan maestro no se actualiza desde 2016 pese a la preparación del de 2050.',
              'mp_limbo', 'Ciclo de revisión del plan.', 'LDA', MED),
    '1.2.1': (3, C, 'Lahore tiene un District Disaster Management Plan 2025 preparado con plantilla de la PDMA y aprobado por el Deputy Commissioner (13 millones de habitantes, 10 tehsils, 274 consejos de unión), y un plan de inundaciones.',
              'ddmp25,flood21', 'Definir roles entre DDMA, Metropolitan Corporation, LDA y WASA.', 'DDMA Lahore', CORTO),
    '1.2.2': (3, C, 'En las crecidas de 2025 la provincia ordenó evacuar las riberas y abrió campamentos; Rescue 1122 y la DDMA coordinan la respuesta según el plan distrital.',
              'pdma_pb_inund25,ddmp25', 'Revisión posevento de la crecida del Ravi.', 'DDMA / PDMA', CORTO),
    '2.1.1': (2, C, 'El plan distrital 2025 describe las amenazas (inundación, sismo, incendio, calor, smog) y la llanura de inundación del Ravi está notificada (230 km², 2016), pero no se halló evaluación probabilística revisada.',
              'ddmp25,ravi_llanura', 'Evaluación multiamenaza con probabilidades.', 'DDMA / Urban Unit', MED),
    '2.4.1': (3, M, 'Existe la llanura de inundación notificada del Ravi (2016), que el Departamento de Riego amplió unos 3 km² tras 2025.',
              'ravi_llanura', 'Publicar mapas de inundación urbana y del Ravi.', 'Departamento de Riego / LDA', CORTO),
    '4.4.1': (1, C, 'En 2025 el Ravi inundó urbanizaciones construidas en el lecho y la llanura (Park View, Shahdara, Theme Park); el gobierno las declaró ilegales y anunció acciones contra quienes dieron los permisos.',
              'ravi_ilegal,ravi_irreg,ravi_5', 'Aplicar la zonificación de la llanura de inundación.', 'LDA / RUDA / Departamento de Riego', CORTO),
    '5.2.2': (3, C, 'WASA y la LDA construyeron tanques subterráneos de agua de lluvia (Lawrence Road desde 2020; 18 tanques en 2025) que reducen el anegamiento.',
              'tanque_lr,tanques', 'Ampliar el drenaje sostenible a nuevas urbanizaciones.', 'WASA Lahore', MED),
    '8.1.1': (2, C, 'Hay costaneras y diques de RUDA que protegieron sus zonas en 2025 y tanques pluviales, pero cinco barrios y varias urbanizaciones se inundaron con el Ravi.',
              'ravi_llanura,ravi_5,tanques', 'Protección contra crecidas del Ravi para los barrios expuestos.', 'Departamento de Riego / RUDA', LARGO),
    '9.2.1': (3, C, 'Plan distrital de desastres 2025, plan de inundaciones y plan de olas de calor 2025-2028, no ligados a escenarios cuantificados.',
              'ddmp25,flood21,hwmp_lhr', 'Planes por escenario más probable y más severo.', 'DDMA Lahore', MED),
    '9.5.2': (3, M, 'En las crecidas de 2025 Punyab abrió unos 412 campamentos de socorro en los distritos afectados; no hay dato propio de Lahore.',
              'campos25', 'Inventario de refugios de la ciudad.', 'DDMA Lahore', CORTO),
    '10.2.1': (2, M, 'El plan distrital se revisa cada año con la plantilla de la PDMA; no se halló revisión posevento publicada de la crecida de 2025.',
               'ddmp25', 'Publicar la revisión posevento de 2025.', 'DDMA / PDMA', CORTO),
}

ES = {
    'A2.2': (3, C, 'El Heatwave Management Plan of Lahore 2025-2028 define alerta, declaración de emergencia y respuesta sanitaria al calor.',
             'hwmp_lhr', 'Sumar escenarios de inundación y smog.', 'Departamento de Salud', MED),
    'A8.2': (2, M, 'Los hospitales deben abrir puestos de atención por calor según protocolos que el Departamento de Salud envió a hospitales terciarios y distritales (2024).',
             'calor_sop', 'Probar la capacidad de reacción para el escenario severo.', 'Departamento de Salud de Punyab', CORTO),
    'A9.2': (3, M, 'El Departamento de Salud participa en la respuesta al calor con protocolos y en las emergencias por smog.',
             'calor_sop,smog_salud', 'Salud en el centro de operaciones distrital.', 'Departamento de Salud', MED),
}

# Plan oficial leído completo (nov-2026): Heatwave Management Plan of Lahore 2025-2028.
EN.update({
    '2.2.1': (2, C, 'El plan de calor 2025-2028 evalúa el riesgo de calor en toda la ciudad (amenaza, exposición y vulnerabilidad con adultos mayores, niños, asentamientos informales y acceso a salud); no hay escenarios equivalentes publicados para inundación ni sismo.',
              'hwmp_lhr', 'Escenarios de inundación del Ravi y lluvia urbana.', 'DDMA Lahore', MED),
    '6.2.1': (4, M, 'El plan de calor prevé una campaña antes y durante la temporada con folletos, redes sociales, carteles, SMS, TV, radio, app y anuncios en mezquitas, con concejales de barrio que difunden la información.',
              'hwmp_lhr', 'Sumar la difusión en escuelas y medir el alcance.', 'Departamento de Información / EPD', CORTO),
})
ES.update({
    'A9.1': (3, C, 'El plan de calor fija una alerta en tres niveles (40 °C, 42 °C, y 42 °C con noches de 30 °C por dos días), con pronóstico a 7 días y vigilancia de casos y muertes en hospitales; Punyab además declara emergencias por smog.',
             'hwmp_lhr,smog24', 'Alertas sanitarias por inundación.', 'Departamento de Salud / PMD', MED),
    'A10.2': (3, M, 'Tras el aviso de fin de temporada, el coordinador de emergencias reúne a los actores para evaluar el desempeño y las recomendaciones se incorporan al plan revisado; todavía no se publicó una evaluación.',
              'hwmp_lhr', 'Publicar la evaluación de cada temporada.', 'EPD / Departamento de Salud', CORTO),
})
