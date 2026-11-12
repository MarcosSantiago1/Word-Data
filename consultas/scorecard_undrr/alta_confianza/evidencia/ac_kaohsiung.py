# Kaohsiung (Gobierno de la Ciudad; Centro de Operaciones de Emergencia): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'kaohsiung', 'Kaohsiung', 'TWN'
OFICINA = 'Centro de Operaciones de Emergencia de Kaohsiung'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/31112', 'CDP-ICLEI Cities 2023: respuesta oficial de el Gobierno de la Ciudad de Kaohsiung', '2023'),
    'ft_kongrey': ('https://focustaiwan.tw/society/202410300021', 'Focus Taiwan: Kaohsiung abre su centro de prevención de desastres de nivel 1 y evacúa preventivamente distritos de montaña ante el tifón Kong-rey', '2024'),
    'ftv_444': ('https://english.ftvnews.com.tw/news/2024A31W0BEA', 'FTV News: el alcalde de Kaohsiung presenta 444 refugios de evacuación con provisiones para dos a tres semanas en zonas que pueden quedar aisladas', '2024'),
    'tvbs_krathon': ('https://news.tvbs.com.tw/english/2638023', 'TVBS: el alcalde de Kaohsiung informa al primer ministro unas 2.670 personas evacuadas por el tifón Krathon', '2024'),
    'eoc_bailu': ('https://data.gov.tw/en/datasets/122144', 'Portal de datos abiertos de Taiwán: apertura del centro de operaciones de emergencia de Kaohsiung ante el tifón Bailu', '2019'),
}

EN = {
    '1.1.1': (4, C, 'La ciudad declara que los riesgos climáticos se consideran en sus planes y estrategias, y que las amenazas de sus evaluaciones de 2021 y 2022 se incorporaron a la gestión general de riesgos; tiene un plan climático integrado con metas de adaptación (CDP 2023).',
        'cdp', 'Llevar los escenarios futuros al plan de la ciudad.', 'Gobierno de la Ciudad de Kaohsiung', MED),
    '1.1.3': (2, C, 'El plan climático se evalúa al menos cada cinco años (CDP 2023); no hay compromiso publicado de revisión cada 3 años.',
        'cdp', 'Revisión del plan cada 3 años.', 'Oficina de Protección Ambiental', MED),
    '1.2.2': (4, C, 'Ante los tifones Krathon y Kong-rey (octubre de 2024) la ciudad activó su centro de prevención de desastres de nivel 1, evacuó unas 2.670 personas y luego más de 2.000, y preparó 444 refugios con provisiones.',
        'ft_kongrey,ftv_444,tvbs_krathon', 'Publicar roles y responsabilidades de cada agencia en la respuesta.', 'Centro de Operaciones de Emergencia de Kaohsiung', CORTO),
    '2.1.1': (4, C, 'Evaluaciones de riesgo y vulnerabilidad climática de 2021 y 2022 con escenario de altas emisiones (RCP 8.5), priorización de amenazas y proceso de actualización al menos cada cinco años (CDP 2023); no se informa revisión de terceros.',
        'cdp', 'Revisión externa de las estimaciones.', 'Gobierno de la Ciudad', MED),
    '2.2.1': (3, C, 'La ciudad estima que el 90-100% de la población está expuesta a lluvias intensas y tifones, el 60-70% a sequía y el 20-30% a enfermedades infecciosas, e identifica a los grupos vulnerables (CDP 2023); no se publican escenarios "más probable" y "más grave".',
        'cdp', 'Escenarios por amenaza con daños y víctimas.', 'Gobierno de la Ciudad', MED),
    '2.5.1': (3, C, 'Hay un proceso para actualizar la evaluación de riesgo al menos cada cinco años (CDP 2023).',
        'cdp', 'Acortar el ciclo de actualización.', 'Gobierno de la Ciudad', MED),
    '9.6.2': (3, M, 'La ciudad tiene un centro de operaciones de emergencia que abre por niveles ante tifones (Bailu 2019, Kong-rey 2024); no se informa la cobertura de cámaras ni procedimientos probados para el escenario más grave.',
        'eoc_bailu,ft_kongrey', 'Publicar los procedimientos del centro.', 'Centro de Operaciones de Emergencia', MED),
}
ES = {
    'A2.2': (3, C, 'La ciudad identifica efectos del calor, tifones, lluvias y enfermedades infecciosas en la salud (golpe de calor, infecciones por vectores, agua y alimentos, salud mental, sobrecarga del sistema de salud) (CDP 2023).',
        'cdp', 'Modelar el impacto en salud por escenario.', 'Secretaría de Salud', MED),
}
