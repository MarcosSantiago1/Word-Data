# Damasco (gobernación y municipalidad de Damasco; Establecimiento de Agua): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'damasco', 'Damasco', 'SYR'
OFICINA = 'Gobernación de Damasco'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'
F = {
    'euronews': ('https://www.euronews.com/2025/05/20/lowest-winter-rainfall-in-syria-for-almost-70-years-triggers-water-crisis-in-damascus', 'Euronews (AP): la lluvia invernal más baja en casi 70 años desata una crisis de agua en Damasco', '2025'),
    'enab_agua': ('https://english.enabbaladi.net/archives/2025/04/damascus-faces-drinking-water-shortages/', 'Enab Baladi: Damasco enfrenta escasez de agua potable (racionamiento y pozos de emergencia)', '2025'),
    'ahram_agua': ('https://english.ahram.org.eg/News/546551.aspx', 'Ahram Online (AP): el invierno más seco en casi siete décadas provoca una grave crisis de agua en Damasco', '2025'),
}
EN = {
    '8.2.1': (1, C, 'En 2025 el manantial de Ain al-Fijeh (más del 70% del agua de la ciudad) bajó a unos 3 m³/s frente a más de 6 antes; la ciudad aplicó el racionamiento más severo desde los años cincuenta y reactivó más de 100 pozos.',
              'euronews,ahram_agua,enab_agua', 'Plan de seguridad hídrica con fuentes alternativas y reparación de redes.', 'Establecimiento de Agua de Damasco', LARGO),
    '8.2.2': (2, C, 'Ante la sequía se preparó un plan de emergencia con pozos inactivos para cubrir el faltante, con camiones cisterna en barrios centrales.',
              'enab_agua,euronews', 'Garantizar agua a hospitales y servicios críticos.', 'Establecimiento de Agua de Damasco', CORTO),
}
ES = {}
