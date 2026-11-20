# Adana (Municipio Metropolitano; AFAD Adana): base de alta confianza, búsqueda nov-2026. Hereda la evidencia de Turquía.
ID, NOMBRE, ISO3 = 'adana', 'Adana', 'TUR'
OFICINA = 'AFAD Adana / Municipio Metropolitano de Adana'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'sozcu_irap': ('https://www.sozcu.com.tr/en-iyisini-umalim-ama-en-kotusune-de-hazir-olalim-p137471', 'Sözcü (columna de un ex secretario general del municipio): el Plan Provincial de Reducción del Riesgo de Adana (İRAP), de septiembre de 2022, ya modelaba con escenarios los riesgos del sismo de 2023', 's/f'),
}

EN = {
    '2.1.1': (2, M, 'El Plan Provincial de Reducción del Riesgo de Desastres (İRAP) de Adana, de septiembre de 2022, incluye análisis de escenarios; tiene más de 3 años y no se informa revisión de terceros.',
        'sozcu_irap', 'Actualizar el İRAP con revisión externa.', 'AFAD Adana / Municipio', MED),
}
ES = {
}
