# Brazzaville (municipalidad / Département de Brazzaville): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'brazzaville', 'Brazzaville', 'COG'
OFICINA = 'Mairie de Brazzaville'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'
F = {
    'ifrc25': ('https://go-api.ifrc.org/api/DownloadFile/93845/MDRCG026do', 'IFRC: DREF Congo, inundaciones del 18-19 de noviembre de 2025 en Brazzaville y Pointe-Noire (más de 61.500 personas afectadas)', '2025'),
    'afd_drenaje': ('https://www.afd.fr/fr/projets/ameliorer-le-drainage-des-eaux-de-pluie-pour-limiter-les-risques-lies-aux-inondations', 'AFD: mejorar el drenaje pluvial para limitar el riesgo de inundación en Brazzaville (62 millones de euros)', 's/f'),
    'afd_desechos': ('https://www.afd.fr/fr/projets/limiter-les-inondations-et-ameliorer-la-gestion-des-dechets-brazzaville', 'AFD: limitar las inundaciones y mejorar la gestión de residuos en Brazzaville (24 millones de euros, en curso)', 's/f'),
    'plan_clima': ('https://www.adiac-congo.com/print/content/plan-climat-163331', 'ADIAC: la municipalidad de Brazzaville lanza la elaboración de su plan climático territorial con la AFD', '2025'),
    'ngamakosso': ('https://fr.allafrica.com/stories/202407100478.html', 'AllAfrica (Les Dépêches de Brazzaville): Talangaï, comienzan las obras de tratamiento del barranco de Ngamakosso', '2024'),
    'aimf': ('https://cdn.aimf.asso.fr/wp-content/uploads/2022/09/Panel-4-Brazzaville.pdf', 'AIMF: presentación de Brazzaville (plan director de drenaje, plan de gestión del riesgo de inundación y planes de inversión previstos)', '2022'),
}
EN = {
    '1.1.1': (1, C, 'La municipalidad recién lanzó en 2025 la elaboración de su plan climático territorial; el plan director de drenaje y el plan de riesgo de inundación figuran como previstos.',
              'plan_clima,aimf', 'Aprobar el plan con mapas de riesgo.', 'Mairie de Brazzaville', MED),
    '8.1.1': (2, C, 'Hay proyectos de drenaje pluvial y control de barrancos financiados por la AFD (62 y 24 millones de euros) y obras en el barranco de Ngamakosso (2024), pero las lluvias de noviembre de 2025 afectaron a más de 61.500 personas en Brazzaville y Pointe-Noire.',
              'afd_drenaje,afd_desechos,ngamakosso,ifrc25', 'Completar el drenaje en los barrios de barrancos.', 'Mairie / DGGT', LARGO),
    '4.4.1': (1, C, 'La población más expuesta vive en barrios informales a lo largo de barrancos que se ocupan sin control (IFRC 2025).',
              'ifrc25', 'Zonificación que impida ocupar los bordes de barrancos.', 'Mairie de Brazzaville', MED),
}
ES = {}
