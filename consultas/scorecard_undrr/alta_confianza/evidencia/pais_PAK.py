# Pakistán: evidencia de alcance nacional o provincial que vale para las ciudades pakistaníes (búsqueda nov-2026).
# Las ciudades la heredan salvo que tengan una respuesta propia.
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'undp_seguro24': ('https://www.undp.org/node/481706', 'PNUD: Inclusive Insurance and Risk Financing in Pakistan, Snapshot 2024', '2024'),
    'bm_drf': ('https://www.financialprotectionforum.org/sites/default/files/PakistanWorkshop.pdf', 'Banco Mundial / Ministerio de Finanzas: taller de financiamiento del riesgo de desastres en Pakistán', 's/f'),
    'adb_fondos': ('https://tribune.com.pk/story/2375328/adb-points-to-insufficient-funds', 'Express Tribune: el BAsD señala fondos de contingencia insuficientes', '2022'),
    'pnud_bcp': ('https://undp.org/node/140846', 'PNUD: Seismic Design in Pakistan, the building code, bylaws and recommendations', 's/f'),
    'bm_sismo15': ('https://blogs.worldbank.org/en/endpovertyinsouthasia/building-seismic-resilience-pakistan-15-years-after-2005-earthquake', 'Banco Mundial: Building seismic resilience in Pakistan, 15 years after the 2005 earthquake', '2020'),
    'ndma_neoc': ('https://www.arabnews.pk/node/2541351/pakistan', 'Arab News: Pakistán instala el Centro Nacional de Operaciones de Emergencia (NEOC) de la NDMA', '2024'),
    'ndma_app': ('https://pid.gov.pk/site/press_detail/32144', 'PID (gobierno de Pakistán): la NDMA lanza la aplicación Pak NDMA Disaster Alert', '2024'),
    'ndma_sms': ('https://www.arabnews.com/node/2607594', 'Arab News: Pakistán lanza alertas por SMS según ubicación (sistema DEW-3 de la NDMA con operadoras)', '2025'),
}

EN = {
    '3.3.1': (1, M, 'La penetración del seguro en Pakistán es de apenas 0,87% del PIB (PNUD 2024) y en las inundaciones de 2010 las pérdidas aseguradas no pasaron del 1% de los 10.000 millones de dólares de daño. La cobertura de vivienda frente a desastres es mínima.',
              'undp_seguro24,bm_drf', 'Programa de seguro paramétrico o microseguro de vivienda con el gobierno provincial.', 'Gobierno provincial / SECP', LARGO),
    '3.3.2': (1, M, 'El seguro contra desastres se concentra en el sector financiero (primas por 48.800 millones de rupias en 2022) y el seguro inclusivo es marginal; el país tiene acceso limitado a la transferencia de riesgo a nivel soberano y de hogares.',
              'undp_seguro24,bm_drf', 'Relevar la cobertura de activos públicos y comerciales de la ciudad.', 'Gobierno provincial', MED),
    '3.2.4': (1, M, 'Los fondos federales de contingencia rondan los 15-20 millones de dólares (BAsD) frente a pérdidas de miles de millones en eventos mayores; existe el National Disaster Risk Management Fund y una estrategia nacional de financiamiento del riesgo aprobada, pero sin fondo municipal propio documentado.',
              'adb_fondos,bm_drf', 'Fondo de contingencia municipal o acceso garantizado a fondos provinciales.', 'Gobierno provincial / ciudad', MED),
    '4.3.2': (2, M, 'El Building Code of Pakistan - Seismic Provisions 2007 fue el primer código sísmico nacional (tras el sismo de 2005); el Pakistan Engineering Council inició su actualización, sin fecha de aprobación encontrada. Los reglamentos locales de edificación no lo citan ni están coordinados con él (PNUD).',
              'pnud_bcp,bm_sismo15', 'Incorporar el código sísmico vigente a los reglamentos locales.', 'Autoridad de control de edificación', MED),
}
EN.update({
    '7.4.2': (3, C, 'La NDMA envía alertas por SMS según ubicación con las operadoras (2025) y tiene la aplicación Pak NDMA Disaster Alert con avisos y consejos; no se halló medición de uso en la ciudad.',
              'ndma_sms,ndma_app', 'Sumar avisos de la ciudad a esos canales.', 'NDMA / autoridad local', CORTO),
    '9.1.1.1': (3, C, 'Las alertas de la NDMA llegan por SMS según ubicación, la aplicación oficial, redes y medios; no hay dato de cobertura del 100% de la población.',
                'ndma_sms,ndma_app', 'Difusión celular (cell broadcast) a toda la población.', 'NDMA / PTA', CORTO),
})
ES = {}
