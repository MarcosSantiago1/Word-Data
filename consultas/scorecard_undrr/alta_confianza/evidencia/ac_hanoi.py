# Hanói (Comité Popular; Comité Directivo de Defensa Civil y Prevención de Desastres): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'hanoi', 'Hanói', 'VNM'
OFICINA = 'Comité Directivo de Defensa Civil y Prevención de Desastres de Hanói'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/31158', 'CDP-ICLEI Cities 2023: respuesta oficial de la Ciudad de Hanói', '2023'),
    'yagi_it': ('https://www.irishtimes.com/world/asia-pacific/2024/09/11/red-river-floods-vietnams-hanoi-as-typhoon-yagi-kills-more-than-150', 'Irish Times (Reuters): el río Rojo inunda Hanói tras el tifón Yagi; el nivel en la capital llega al máximo en 20 años y miles son evacuados', '2024'),
}

EN = {
    '1.1.1': (1, C, 'La ciudad considera los riesgos climáticos en sus planes, pero su evaluación de 2021 no incluye escenarios, población vulnerable ni priorización ("ninguno de los anteriores") y no informa la proporción de población expuesta; no tiene metas de adaptación (CDP 2023).',
        'cdp', 'Integrar una evaluación de riesgo completa al plan de la ciudad.', 'Comité Popular de Hanói', MED),
    '1.2.2': (4, M, 'Con el tifón Yagi (septiembre de 2024) el río Rojo llegó a su nivel más alto en 20 años en Hanói; policía, soldados y voluntarios evacuaron casa por casa a miles de vecinos y se restringió el tránsito en los puentes.',
        'yagi_it', 'Publicar la revisión de la respuesta y los roles de cada agencia.', 'Comité Directivo de Defensa Civil de Hanói', CORTO),
    '2.1.1': (2, C, 'Hay una evaluación de riesgo climático de 2021 para toda la ciudad, hecha por el gobierno provincial, pero sin escenario de altas emisiones, priorización ni proceso de actualización (CDP 2023).',
        'cdp', 'Actualizar la evaluación con escenarios y revisión externa.', 'Comité Popular / Departamento de Recursos Naturales y Ambiente', MED),
    '2.2.1': (1, C, 'Para tormentas, calor extremo y sequía la ciudad declara magnitud alta pero "datos no disponibles" sobre la población expuesta y no conoce la probabilidad (CDP 2023).',
        'cdp', 'Mapear población y bienes expuestos por amenaza.', 'Comité Popular', MED),
}
ES = {
    'A2.2': (3, C, 'La ciudad identifica efectos del calor, lluvias, tormentas y enfermedades infecciosas en la salud (golpe de calor, enfermedades por frío, infecciones por agua y vectores, enfermedad cardiovascular y respiratoria) (CDP 2023).',
        'cdp', 'Plan de salud por escenario.', 'Departamento de Salud de Hanói', MED),
}
