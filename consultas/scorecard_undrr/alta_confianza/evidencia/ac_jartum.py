# Jartum (Estado de Jartum; localidad de Jartum): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'jartum', 'Jartum', 'SDN'
OFICINA = 'Gobierno del Estado de Jartum'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'
F = {
    'unicef_colera': ('https://www.unicef.org/sudan/press-releases/over-1-million-children-risk-cholera-spreads-sudans-khartoum-state', 'UNICEF: más de un millón de niños en riesgo por el cólera en el Estado de Jartum (7.700 casos y 185 muertes desde enero de 2025)', '2025'),
    'msf_colera': ('https://www.doctorswithoutborders.org/latest/sudan-cholera-spreading-widely-khartoum', 'Médicos Sin Fronteras: el cólera se expande en Jartum; las plantas potabilizadoras sin electricidad no pueden tratar el agua del Nilo', '2025'),
    'nat_colera': ('https://www.thenationalnews.com/news/mena/2025/05/27/sudan-says-a-cholera-epidemic-has-killed-172', 'The National: Sudán dice que el cólera mató a 172 personas; ataques con drones a centrales eléctricas dejan sin luz ni agua a la capital', '2025'),
}
EN = {
    '8.2.1': (0, C, 'En 2025 los ataques con drones a centrales eléctricas dejaron sin energía a las plantas potabilizadoras y la población pasó a beber agua del Nilo sin tratar.',
              'msf_colera,nat_colera', 'Restituir la potabilización con energía de respaldo.', 'Corporación de Agua del Estado de Jartum', CORTO),
    '8.3.1': (0, C, 'Los ataques a tres centrales eléctricas provocaron un apagón masivo en la capital en 2025.',
              'nat_colera', 'Restituir el servicio eléctrico.', 'Compañía eléctrica de Sudán', MED),
    '8.7.3': (0, C, 'Hasta el 90% de los hospitales de las zonas de combate quedaron fuera de servicio.',
              'nat_colera,msf_colera', 'Rehabilitar la red hospitalaria.', 'Ministerio de Salud del Estado', MED),
}
ES = {
    'A2.1': (1, C, 'El brote de cólera de 2025 (más de 7.700 casos y 185 muertes en el Estado de Jartum hasta mayo) se concentró en Jartum, Omdurmán y Bahri, sin preparación previa.',
             'unicef_colera,msf_colera', 'Plan de respuesta a brotes.', 'Ministerio de Salud del Estado', CORTO),
}
