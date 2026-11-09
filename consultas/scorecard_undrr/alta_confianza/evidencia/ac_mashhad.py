# Mashhad (municipio; Organización de Gestión de Crisis): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'mashhad', 'Mashhad', 'IRN'
OFICINA = 'Organización de Gestión de Crisis del Municipio de Mashhad'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'tn_flood': ('https://tn.ai/3086823', 'Tasnim: las inundaciones dejan siete muertos en el noreste de Irán (Mashhad, mayo de 2024)', '2024'),
    'ii_mal': ('https://iranintl.com/en/202405182521', 'Iran International: la catástrofe de la inundación en Irán; la mala gestión eleva el número de muertos', '2024'),
}

EN = {
    '1.2.2': (3, M, 'En la inundación repentina de mayo de 2024 (al menos 7 muertos y 12 desaparecidos) respondieron los bomberos municipales y la gestión de crisis provincial, y se convocó una sesión de crisis con el ministro del Interior; la prensa critica la mala gestión.',
        'tn_flood,ii_mal', 'Definir roles entre municipio y provincia.', 'Municipio de Mashhad / Gestión de Crisis de Razavi Jorasán', CORTO),
}
ES = {
}
