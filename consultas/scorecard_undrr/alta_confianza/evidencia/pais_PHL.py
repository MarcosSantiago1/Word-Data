# Filipinas: evidencia nacional que hereda Quezón (búsqueda nov-2026).
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'ra10121': ('https://www.officialgazette.gov.ph/2010/05/27/republic-act-no-10121/', 'Official Gazette: Ley de la República 10121, Ley de Reducción y Gestión del Riesgo de Desastres de Filipinas (2010)', '2010'),
    'ra10639': ('https://www.officialgazette.gov.ph/2014/06/20/republic-act-no-10639/', 'Official Gazette: Ley de la República 10639, Ley de Alertas Gratuitas de Desastre por Celular (2014)', '2014'),
    'gsis_lgu': ('https://ptvnews.ph/?p=11070', 'PTV News: el GSIS cubre a gobiernos locales y organismos nacionales con seguro de riesgo catastrófico', '2017'),
    'niip24': ('https://www.philstar.com/business/2024/01/02/2322813/philippines-indemnity-program-covers-p800-billion-state-assets', 'Philstar: el Programa Nacional de Seguro de Indemnización cubre 800.000 millones de pesos de activos del Estado', '2024'),
}

EN = {
    '3.2.4': (4, C, 'Por ley (RA 10121, sección 21) cada gobierno local debe reservar al menos el 5% de sus ingresos ordinarios estimados para el fondo local de gestión del riesgo, con 30% como fondo de respuesta rápida; el saldo no usado se acumula para obras de reducción del riesgo.',
              'ra10121', 'Publicar el saldo y uso del fondo.', 'Oficina local de gestión del riesgo', CORTO),
    '3.3.2': (3, M, 'El Estado asegura sus activos con el Programa Nacional de Seguro de Indemnización (800.000 millones de pesos desde 2024) y el GSIS ofrece seguro catastrófico a gobiernos locales; no se halló la cobertura de la ciudad.',
              'niip24,gsis_lgu', 'Asegurar los activos municipales críticos.', 'Gobierno de la ciudad / GSIS', MED),
    '7.4.2': (4, C, 'La ley RA 10639 obliga a las operadoras a enviar alertas gratuitas de desastre a todos los celulares de la zona afectada.',
              'ra10639', 'Sumar avisos de la ciudad al canal nacional.', 'NDRRMC / gobierno local', CORTO),
    '9.1.1.1': (4, C, 'Las alertas gratuitas por celular (RA 10639) llegan a todos los suscriptores de la zona afectada.',
                'ra10639', 'Canales para quien no tiene celular.', 'NDRRMC / NTC', CORTO),
}
ES = {}
