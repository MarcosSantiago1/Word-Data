# Surat (Surat Municipal Corporation): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'surat', 'Surat', 'IND'
OFICINA = 'Surat Municipal Corporation'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'dmp26': ('https://www.suratmunicipal.gov.in/Content/Documents/Downloads/DMP_English.pdf', 'Surat Municipal Corporation: Disaster Management & Preparedness Plan, edición 2026 (se actualiza cada año desde 2002; leído completo)', '2026'),
    'hap23': ('https://heathealth.info/wp-content/uploads/Climate-Adaptive-and-Gender-Integrated-Heat-Wave-Action-Plan-of-Surat-City.pdf', 'UHCRCE Surat / IRADe / APN: plan de acción ante olas de calor de Surat, adaptado al clima y con enfoque de género (leído completo)', '2023'),
    'pw_ews': ('https://www.preventionweb.net/quick/45591', 'PreventionWeb: sistema de alerta temprana de inundación de punta a punta para Surat (cuenca del Tapi y crecida mareal del arroyo Khadi), a cargo del Surat Climate Change Trust', 's/f'),
}

EN = {
    '1.2.1': (4, C, 'El plan de desastres asigna tareas antes del monzón a cada departamento y zona (instrucciones permanentes, plan de contingencia, combustible en stock al 15 de junio, áreas bajas y centros de refugio por zona).',
        'dmp26', 'Aclarar responsabilidades entre agencias fuera de la corporación.', 'Surat Municipal Corporation', CORTO),
    '6.1.2': (2, M, 'El plan lista proveedores privados de paquetes de comida, botes y grúas para emergencias, sin acuerdos formales informados.',
        'dmp26', 'Firmar acuerdos formales con proveedores.', 'Surat Municipal Corporation', MED),
    '6.1.4': (3, M, 'El plan lista organizaciones voluntarias con las que la corporación coordina la ayuda en inundaciones.',
        'dmp26', 'Acuerdos con roles definidos para las ONG.', 'Surat Municipal Corporation', MED),
    '9.1.1': (4, M, 'Hay un sistema de alerta de inundación de punta a punta para el Tapi y la crecida mareal, con estaciones meteorológicas y de nivel, y el plan fija sirenas al llegar el Tapi a 7,5, 8,5 y 9,5 m, que se prueban con toques de simulacro.',
        'pw_ews,dmp26', 'Evaluar el tiempo real de aviso.', 'Surat Climate Change Trust / SMC', CORTO),
    '9.2.1': (3, C, 'El plan de desastres 2026 cubre inundación del Tapi y de arroyos, ciclón, lluvias y calor, con tareas por departamento y zona, pero no se liga a escenarios "más probable" y "más grave".',
        'dmp26', 'Ligar el plan a escenarios.', 'Surat Municipal Corporation', MED),
    '9.6.2': (3, C, 'La corporación tiene una Sala Central de Control de Inundaciones con contactos de las salas de control estatal, distrital y de otras agencias, red de radio entre departamentos y procedimientos del plan para el monzón; no se informa cobertura de cámaras.',
        'dmp26', 'Probar los procedimientos ante el escenario más grave.', 'Surat Municipal Corporation', MED),
}
ES = {
    'A2.1': (3, C, 'El plan de desastres incluye planes de prevención de enfermedades por agua y por vectores, un capítulo de calor y primeros auxilios, con hospitales listados.',
        'dmp26', 'Modelar los efectos de brotes epidémicos.', 'Departamento de Salud de la SMC', MED),
    'A2.2': (3, C, 'El plan de desastres prevé vigilancia activa de malaria y casos de gastroenteritis, stock de medicamentos y atención de golpe de calor; el plan de calor 2023 suma salas y refugios para vulnerables.',
        'dmp26,hap23', 'Plan de salud integral por escenario.', 'Departamento de Salud de la SMC', MED),
    'A9.1': (3, M, 'El plan de calor 2023 fija alertas por colores con umbrales propios de Surat basados en la mortalidad (rojo desde 39 °C), recibe el pronóstico de 5 días del IMD y avisa por SMS, WhatsApp y altavoces; el plan de desastres hace vigilancia activa de malaria.',
        'hap23,dmp26', 'Unificar las alertas de salud para todas las amenazas.', 'Departamento de Salud de la SMC', CORTO),
}
