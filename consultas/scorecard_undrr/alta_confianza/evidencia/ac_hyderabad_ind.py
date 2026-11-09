# Hyderabad, India (Greater Hyderabad Municipal Corporation; HYDRAA): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'hyderabad_ind', 'Hyderabad (India)', 'IND'
OFICINA = 'GHMC / HYDRAA'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'si_hydraa': ('https://www.siasat.com/ghmc-hydraa-to-deploy-130-monsoon-emergency-teams-to-tackle-waterlogging-3231799/', 'Siasat: GHMC e HYDRAA despliegan 130 equipos de emergencia para el monzón contra anegamientos', '2025'),
    'dc_drf': ('https://deccanchronicle.com/nation/in-other-news/080623/ghmc-ready-to-face-monsoons.html', 'Deccan Chronicle: la GHMC lista para el monzón (Fuerza de Respuesta a Desastres de 27 equipos y 450 personas; sala de comando móvil)', '2023'),
}

EN = {
    '9.3.2': (3, M, 'La ciudad definió equipos de primera respuesta para el monzón: la Fuerza de Respuesta a Desastres de la GHMC (27 equipos, 450 personas en 2023) y, desde 2025, 130 equipos de respuesta de HYDRAA coordinados con 51 equipos de la fuerza; no se ligan a escenarios.',
        'si_hydraa,dc_drf', 'Dimensionar los equipos por escenario.', 'GHMC / HYDRAA', MED),
}
ES = {
}
