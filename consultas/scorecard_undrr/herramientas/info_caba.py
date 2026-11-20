"""Perfil de CABA para la hoja Info (misma grilla en ambos libros)."""
PREFIJO = {'EN': '[Borrador de escritorio nov-2026, a validar con el GCBA;',
           'ES': '[Borrador de escritorio nov-2026, a validar con el GCBA;'}

INFO = {
    'D4': 'Ciudad Autónoma de Buenos Aires (CABA)',
    'D5': 'Ciudad autónoma, núcleo del Área Metropolitana de Buenos Aires (AMBA)',
    'D6': 'Argentina',
    'D7': '07/11/2026 (borrador preliminar de escritorio)',
    # perfil obligatorio: C = respuesta, D = fuente y fecha
    'C10': 'Jefe/a de Gobierno', 'D10': 'Constitución de la CABA (1996)',
    'C11': 3121707, 'D11': 'Censo 2022, INDEC (datos definitivos)',
    'C12': 200, 'D12': 'km²; superficie oficial aproximada (DGEyC CABA)',
    'C13': 15609, 'D13': 'hab/km²; calculado: 3.121.707 / 200 km²',
    'C14': '≈12%', 'D14': 'Estimación: 15-29 años = 18,4% en 2022 (DGEyC CABA); 15-24 ≈ dos tercios de ese grupo',
    'C15': '17,7%', 'D15': 'Censo 2022 (DGEyC CABA, "La Ciudad entre censos 2010-2022")',
    'C16': '47,9%', 'D16': 'Valor cargado antes en la planilla en español; verificar con Encuesta Anual de Hogares (DGEyC)',
    'C17': '99,6%', 'D17': 'Censo 2010: 12.403 personas analfabetas de 10 años y más (0,4%)',
    'C18': '88,0%', 'D18': 'Pobreza 12,0% de personas en 2025 (EPH-INDEC, procesado en etl/argentina_provincias/pobreza_gini_provincia_anual.csv)',
    'C19': '≈ USD 1.490 por mes (≈ USD 17.900 al año)', 'D19': 'Ingreso total familiar promedio $1.537.488/mes, 4.º trim. 2024 (ETOI, DGEyC) al tipo de cambio oficial ≈ 1.030 ARS/USD',
    'C20': '13,9%', 'D20': 'Aproximado con población nacida en el extranjero (EAH 2025, DGEyC); no mide ciudadanía',
    'C21': 'Inundación pluvial por tormentas intensas; también olas de calor con cortes de energía', 'D21': 'PAC 2050 (GCBA, 2021); PDOH / Programa de Gestión del Riesgo Hídrico',
    'C22': 'Inundación del 2 de abril de 2013: unos 155 mm en 2 horas, alrededor de 10 muertes en CABA (89 en La Plata)', 'D22': 'Prensa nacional (Diario de Cuyo, AP), 2013-2014',
    # perfil opcional
    'C25': 1406735, 'D25': 'Hogares particulares, Censo 2022 (INDEC)',
    'C26': 2.2, 'D26': 'Personas por hogar: 3.095.454 / 1.406.735, Censo 2022',
    'C27': 'Canasta Básica Total hogar tipo 4 personas (GBA): $1.150.651 por mes en 2025', 'D27': 'INDEC, procesado en etl/argentina_provincias/canastas_provincia_anual.csv; convertir a USD con el tipo de cambio del día',
    'C28': 13970, 'D28': 'USD corrientes 2024: PIB 638.365 millones / 45,70 millones de hab. (Banco Mundial, panel del proyecto)',
    'C29': 0.413, 'D29': 'CABA 2025, ingreso per cápita familiar (EPH-INDEC, procesado en el proyecto); Argentina 2024 = 42,4 (Banco Mundial)',
    'C30': '≈ USD 42.000', 'D30': 'Estimación: PBG per cápita de CABA ≈ 3,0 veces el promedio nacional (CEPAL 2023, procesado en el proyecto) × PIB per cápita nacional 2024',
    # equipo
    'D33': '(a completar)',
    'D34': '(a completar)',
    'D35': '(a completar)',
    'D36': '(a completar)',
    'B40': 'Borrador de escritorio armado con fuentes públicas (GCBA, INDEC, DGEyC, Banco Mundial, SMN, prensa). No hubo talleres con actores; cada respuesta indica su nivel de confianza y qué validar.',
}
