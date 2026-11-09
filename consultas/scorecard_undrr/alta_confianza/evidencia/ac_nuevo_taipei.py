# Nuevo Taipéi (Gobierno de la Ciudad): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'nuevo_taipei', 'Nuevo Taipéi', 'TWN'
OFICINA = 'Gobierno de la Ciudad de Nuevo Taipéi'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/56276', 'CDP-ICLEI Cities 2023: respuesta oficial de el Gobierno de la Ciudad de Nuevo Taipéi', '2023'),
}

EN = {
    '1.1.1': (4, C, 'La ciudad considera los riesgos climáticos en sus planes, objetivos de desempeño y políticas de gestión de riesgo, y tiene planes climáticos integrados de mitigación y adaptación (CDP 2023).',
        'cdp', 'Llevar los escenarios futuros al plan de la ciudad.', 'Gobierno de la Ciudad de Nuevo Taipéi', MED),
    '1.1.3': (3, M, 'Uno de sus planes climáticos integrados se monitorea, evalúa y actualiza al menos cada 3 años, y ya tuvo actualizaciones (evaluaciones de 2016, 2020, 2021 y 2022) (CDP 2023).',
        'cdp', 'Publicar el compromiso de revisión.', 'Departamento de Protección Ambiental', MED),
    '2.1.1': (4, C, 'Cinco evaluaciones de riesgo climático entre 2016 y 2022 con escenario RCP 8.5, sectores urbanos, población vulnerable y priorización de amenazas, con consulta a socios (CDP 2023); no se informa revisión de terceros.',
        'cdp', 'Revisión externa.', 'Gobierno de la Ciudad', MED),
    '2.2.1': (3, C, 'La ciudad estima que el 30-40% de la población está expuesta al calor extremo y menos del 10% a sequía, inundación urbana, deslizamientos y enfermedades infecciosas (CDP 2023).',
        'cdp', 'Escenarios "más probable" y "más grave".', 'Gobierno de la Ciudad', MED),
    '2.5.1': (3, C, 'Hay un proceso para actualizar la evaluación de riesgo al menos cada cinco años (CDP 2023).',
        'cdp', 'Acortar el ciclo de actualización.', 'Gobierno de la Ciudad', MED),
}
ES = {
    'A2.2': (3, C, 'La ciudad identifica efectos del calor, el frío y las enfermedades por vectores en la salud (enfermedad cardiovascular, golpe de calor, salud mental) y advierte el avance del mosquito del dengue hacia el norte (CDP 2023).',
        'cdp', 'Modelar el impacto en salud por escenario.', 'Departamento de Salud', MED),
}
