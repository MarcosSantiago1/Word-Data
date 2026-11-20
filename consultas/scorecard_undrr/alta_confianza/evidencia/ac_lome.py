# Lomé (Gran Lomé; ANPC Togo): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'lome', 'Lomé (Gran Lomé)', 'TGO'
OFICINA = 'Agence Nationale de la Protection Civile (ANPC)'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'aa_orsec': ('https://fr.allafrica.com/stories/202606300160.html', 'AllAfrica: el ministro de Seguridad y Protección Civil activa el plan ORSEC y la ANPC su dispositivo de vigilancia por las inundaciones en Lomé', '2026'),
    'rt_urg': ('https://www.republicoftogo.com/toutes-les-rubriques/societe/lome-declenche-son-plan-d-urgence', 'Republic of Togo: Lomé activa su plan de urgencia', '2026'),
    'gwp_sap': ('https://www.gwp.org/globalassets/global/gwp-waf_files/vfdm_mai_2023/togo_processus_sap_inondations.pdf', 'GWP África Occidental: proceso del sistema de alerta temprana de inundaciones en Togo (formación regional)', '2023'),
}

EN = {
    '1.2.2': (3, M, 'En 2026 las autoridades activaron un programa de urgencia y luego el plan ORSEC, y la ANPC activó su dispositivo de vigilancia ante las inundaciones en Lomé; no se publican roles y responsabilidades de cada institución.',
        'aa_orsec,rt_urg', 'Publicar roles y responsabilidades del plan ORSEC para Lomé.', 'ANPC / Ministerio de Seguridad y Protección Civil', CORTO),
    '9.1.1': (1, M, 'La cadena de alerta tiene a la ANPC en la difusión, pero el modelo de pronóstico hidrológico no funciona desde 2019, no hay modelo de pronóstico de inundaciones para Lomé y los datos hidrológicos y meteorológicos no son de acceso libre.',
        'gwp_sap', 'Modelo de pronóstico de inundaciones para Lomé.', 'ANPC / ANAMET / DRE', MED),
}
ES = {
}
