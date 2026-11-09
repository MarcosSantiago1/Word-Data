# Taiwán: evidencia nacional que heredan Kaohsiung, Nuevo Taipéi y Taoyuan (búsqueda nov-2026).
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'treif_tn': ('https://www.taiwannews.com.tw/en/news/6021049', 'Taiwan News (datos del fondo TREIF): el 38,89% de las viviendas tiene seguro básico de terremoto a fin de 2024', '2025'),
    'treif25': ('https://wfcatprogrammes.com/documents/20142/34347/TREIF_System_Summary_Update_Aug2025.pdf/60e5c164-2b06-d158-4eb4-8663459c6fd8', 'TREIF (fondo de seguro residencial de terremoto de Taiwán): resumen del sistema, agosto de 2025', '2025'),
    'pts_codigo': ('https://news.pts.org.tw/article/609630', 'PTS: el Ministerio del Interior revisa el código de diseño sísmico de edificios después de 11 años', '2022'),
    'pws': ('https://www.taipeitimes.com/News/taiwan/archives/2024/09/21/2003824124', 'Taipei Times: prueba nacional de alerta de sismo enviada a los teléfonos por el sistema público de alerta por difusión celular', '2024'),
    'pws16': ('https://www.taipeitimes.com/News/taiwan/archives/2016/04/28/2003645022', 'Taipei Times: las cinco operadoras 4G lanzan el sistema público de alerta por difusión celular', '2016'),
}

EN = {
    '3.3.1': (1, M, 'El 38,9% de las viviendas tiene el seguro básico de terremoto (fin de 2024) y la póliza tiene un tope fijo, así que la parte cubierta de las pérdidas probables es menor al 25%.',
              'treif_tn,treif25', 'Promover el seguro de vivienda en los barrios de más riesgo.', 'Gobierno de la ciudad / TREIF', LARGO),
    '4.3.2': (4, C, 'El código de diseño sísmico de edificios se revisó en 2022, 11 años después de la versión de 2011, y subió la resistencia exigida cerca de fallas activas.',
              'pts_codigo', 'Sin acción prioritaria.', '', ''),
    '7.4.2': (4, C, 'Desde 2016 el sistema público de alerta envía avisos de sismo, tsunami y lluvia por difusión celular a los teléfonos 4G y 5G, y se prueba en el simulacro nacional anual.',
              'pws,pws16', 'Sumar canales de reporte ciudadano.', 'Gobierno central / ciudad', CORTO),
    '9.1.1.1': (4, M, 'La difusión celular llega a todos los teléfonos 4G y 5G de la zona sin registro previo; los teléfonos solo 2G o certificados antes de 2016 pueden no recibirla.',
                'pws,pws16', 'Medir el alcance real en la ciudad.', 'Gobierno central', CORTO),
}
ES = {}
