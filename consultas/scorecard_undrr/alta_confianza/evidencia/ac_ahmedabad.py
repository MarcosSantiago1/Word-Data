# Ahmedabad (Amdavad Municipal Corporation): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'ahmedabad', 'Ahmedabad', 'IND'
OFICINA = 'Amdavad Municipal Corporation'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/46263', 'CDP-ICLEI Cities 2023: respuesta oficial de la Amdavad Municipal Corporation (Ahmedabad)', '2023'),
    'nrdc_hap': ('https://www.nrdc.org/experts/anjali-jaiswal/5-reasons-why-ahmedabad-heat-action-plan-saves-lives', 'NRDC: cinco razones por las que el plan de acción ante el calor de Ahmedabad salva vidas (plan de la AMC desde 2013, con IIPH Gandhinagar)', 's/f'),
}

EN = {
    '1.1.1': (4, C, 'El Ahmedabad Climate Resilient City Action Plan (2023) se preparó con consulta a actores y la corporación considera los riesgos climáticos en su presupuesto y grandes inversiones; tiene metas de adaptación (CDP 2023).',
        'cdp', 'Llevar los escenarios futuros a los proyectos.', 'Amdavad Municipal Corporation', MED),
    '1.1.2': (3, C, 'En el plan participaron gobiernos local, estatal y nacional, academia, sector privado, ciudadanos y grupos vulnerables (7 grupos) (CDP 2023).',
        'cdp', 'Sumar a los grupos que faltan.', 'AMC', CORTO),
    '1.1.3': (2, C, 'El plan de 2023 se evalúa cada año y se compromete a actualizarse al menos cada cinco años (CDP 2023); todavía no tuvo revisión.',
        'cdp', 'Hacer y publicar la primera revisión.', 'AMC', MED),
    '2.1.1': (4, C, 'Evaluación de riesgo climático de 2023 con escenario RCP 8.5, priorización de amenazas, seguridad hídrica, consulta a socios y proceso de actualización cada cinco años (CDP 2023); no se informa revisión de terceros.',
        'cdp', 'Revisión externa.', 'AMC', MED),
    '2.2.1': (3, C, 'La ciudad estima que el 70-80% de la población está expuesta al calor extremo, el 50-60% a la contaminación del aire y menos del 10% a la inundación urbana (CDP 2023).',
        'cdp', 'Escenarios "más probable" y "más grave".', 'AMC', MED),
    '2.5.1': (3, C, 'Hay un proceso para actualizar la evaluación de riesgo al menos cada cinco años (CDP 2023).',
        'cdp', 'Acortar el ciclo.', 'AMC', MED),
}
ES = {
    'A2.2': (3, C, 'La ciudad identifica efectos de la inundación urbana y el calor en la salud (infecciones por agua, vectores y alimentos, golpe de calor, enfermedad respiratoria) (CDP 2023).',
        'cdp', 'Plan de salud por escenario.', 'Departamento de Salud de la AMC', MED),
    'A9.1': (3, M, 'Desde 2013 la corporación aplica el primer plan de acción ante el calor de Asia del Sur: el IMD envía un pronóstico de cinco días al responsable del plan y la AMC emite alertas por colores a hospitales, escuelas y medios; cubre solo el calor.',
        'nrdc_hap', 'Extender la alerta sanitaria a otras amenazas.', 'AMC, Departamento de Salud', CORTO),
}
