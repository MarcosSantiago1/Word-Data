# Indonesia: evidencia nacional que heredan Surabaya, Depok, Bekasi y Bandung (búsqueda nov-2026).
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'pfb': ('https://fiskal.kemenkeu.go.id/parb/en/pfb-2/', 'Ministerio de Finanzas de Indonesia: Pooling Fund Bencana (fondo común para desastres, Perpres 75/2021)', 's/f'),
    'abmn': ('https://www.cnbcindonesia.com/news/20251202130607-4-690330/kemenkeu-ungkap-baru-24-aset-negara-diasuransikan', 'CNBC Indonesia: el Ministerio de Finanzas asegura bienes del Estado vía el Pooling Fund Bencana', '2025'),
    'gsff': ('https://www.financialprotectionforum.org/blog/global-shield-financing-facility-impact-story-supporting-governments-ambitious-disaster-risk', 'Financial Protection Forum: donación de 14 millones de dólares del Global Shield para el Pooling Fund Bencana', '2025'),
    'sni1726': ('https://ejournal2.pnp.ac.id/index.php/jirs/article/view/416', 'Jurnal Ilmiah Rekayasa Sipil: comparación del diseño sísmico con SNI 1726:2012 y SNI 1726:2019 (código vigente basado en los mapas de amenaza 2017)', '2021'),
}

EN = {
    '3.2.4': (2, C, 'El país creó el Pooling Fund Bencana (Perpres 75/2021), un fondo de dotación que complementa el presupuesto para preparación y protección de activos públicos, con apoyo del Banco Mundial y del Global Shield; no se halló fondo de contingencia propio de la ciudad.',
              'pfb,gsff', 'Acceso de la ciudad al fondo común o fondo propio.', 'Gobierno de la ciudad', MED),
    '3.3.2': (2, M, 'Los bienes del Estado nacional se aseguran contra desastres (programa desde 2019, ahora pagado vía el Pooling Fund Bencana), pero no se halló seguro de los activos municipales.',
              'abmn,pfb', 'Asegurar los activos críticos de la ciudad.', 'Gobierno de la ciudad', MED),
    '4.3.2': (4, M, 'El código sísmico SNI 1726:2019 reemplazó al de 2012 y se basa en los mapas de amenaza sísmica de 2017 (adapta ASCE 7-16).',
              'sni1726', 'Sin acción prioritaria.', '', ''),
}
ES = {}
