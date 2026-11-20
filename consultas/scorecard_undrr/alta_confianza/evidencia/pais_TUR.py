# Türkiye: evidencia nacional que heredan Antalya y las demás ciudades turcas (búsqueda nov-2026).
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'dask25': ('https://meinsurancereview.com/News/ViewNewsLetterArticle/id/92588/Type/MiddleEast/Turkiye-Compulsory-earthquake-insurance-coverage-rate-hovers-at-57-', 'Middle East Insurance Review (datos del pool DASK/TCIP): la cobertura del seguro obligatorio de terremoto ronda el 57%', '2025'),
    'dask26': ('https://www.dailysabah.com/turkiye/42-of-turkiyes-homes-remain-without-earthquake-insurance/news', 'Daily Sabah: el 42% de las viviendas de Türkiye sigue sin seguro de terremoto', '2026'),
    'tbdy18': ('https://www.preventionweb.net/quick/26386', 'PreventionWeb: Türkiye adopta un nuevo reglamento de construcción sismorresistente (TBDY 2018, vigente desde enero de 2019)', '2018'),
}

EN = {
    '3.3.1': (2, M, 'El seguro de terremoto es obligatorio (DASK) pero solo lo tiene cerca del 57-58% de las viviendas, con un tope de cobertura; la parte cubierta de las pérdidas probables queda entre 25% y 50%.',
              'dask25,dask26', 'Hacer cumplir el seguro obligatorio en los barrios de más riesgo.', 'Gobierno nacional / municipio', MED),
    '4.3.2': (4, C, 'El Reglamento Turco de Edificios Sismorresistentes (TBDY 2018) reemplazó al de 2007 y rige desde el 1 de enero de 2019, con el nuevo mapa de amenaza sísmica.',
              'tbdy18', 'Controlar su aplicación en obra.', 'Ministerio de Ambiente y Urbanismo / municipio', CORTO),
}
ES = {}
