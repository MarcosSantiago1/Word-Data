# Antalya (Municipio Metropolitano): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'antalya', 'Antalya', 'TUR'
OFICINA = 'Municipio Metropolitano de Antalya'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/74670', 'CDP-ICLEI Cities 2023: respuesta oficial de el Municipio Metropolitano de Antalya', '2023'),
    'irap_sol': ('https://haber.sol.org.tr/haber/antalya-kent-merkezi-afet-riski-altinda-387236', 'sol haber: según el Plan Provincial de Reducción del Riesgo de Desastres (İRAP, AFAD 2021) el centro de Antalya concentra el mayor riesgo de crecidas, inundaciones y tormentas', '2023'),
}

EN = {
    '1.1.1': (4, C, 'El municipio considera los riesgos climáticos en su presupuesto, planes y estrategias, y tiene un plan climático integrado con metas de adaptación (CDP 2023).',
        'cdp', 'Llevar los escenarios futuros al plan de la ciudad.', 'Municipio Metropolitano de Antalya', MED),
    '1.1.3': (2, C, 'El plan climático integrado se aprobó en 2022 y el municipio se compromete a evaluarlo y actualizarlo al menos cada 3 años (CDP 2023); todavía no se informa una revisión hecha.',
        'cdp', 'Hacer y publicar la primera revisión.', 'Municipio Metropolitano', MED),
    '5.2.2': (2, M, 'El municipio fijó metas de adaptación con corredores verdes, infraestructura azul en áreas verdes, jardines de lluvia y techos verdes obligatorios en edificios comerciales nuevos (CDP 2023); son metas en curso, sin uso extendido documentado.',
        'cdp', 'Llevar la infraestructura verde y azul a los códigos de construcción.', 'Municipio Metropolitano, Dirección de Parques', LARGO),
    '2.1.1': (4, C, 'Evaluación de riesgo climático de 2022 con consulta a socios, sectores urbanos, naturaleza, seguridad hídrica y proceso de actualización cada cinco años (CDP 2023); el Plan Provincial de Reducción del Riesgo (İRAP, AFAD 2021) suma escenarios de inundación y sismo.',
        'cdp,irap_sol', 'Revisión externa.', 'Municipio / AFAD Antalya', MED),
    '2.2.1': (3, C, 'El municipio estima que el 70-80% de la población está expuesta al estrés térmico, el 60-70% a inundación urbana e incendios forestales y el 50-60% a estrés hídrico y tormentas (CDP 2023); el İRAP prevé pasos bajo nivel y plantas bajas inundadas en Kepez y Muratpaşa y un sismo de 6,5 en la falla Kaş-Kekova.',
        'cdp,irap_sol', 'Escenarios con daños y víctimas por barrio.', 'Municipio / AFAD Antalya', MED),
    '2.5.1': (3, C, 'Hay un proceso para actualizar la evaluación de riesgo al menos cada cinco años (CDP 2023).',
        'cdp', 'Acortar el ciclo de actualización.', 'Municipio Metropolitano', MED),
}
ES = {
    'A2.2': (3, C, 'El municipio identifica efectos de calor, tormentas, inundaciones e incendios en la salud (golpe de calor, infecciones por vectores y agua) y la falta de vigilancia y alerta temprana sanitaria informada por el clima (CDP 2023).',
        'cdp', 'Plan de salud por escenario.', 'Dirección Provincial de Salud', MED),
}
