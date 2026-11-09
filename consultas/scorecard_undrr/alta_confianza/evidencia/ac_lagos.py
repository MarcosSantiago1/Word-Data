# Lagos (Gobierno del Estado de Lagos; LASEMA): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'lagos', 'Lagos', 'NGA'
OFICINA = 'Lagos State Emergency Management Agency (LASEMA)'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cdp': ('https://www.cdp.net/en/responses/31167', 'CDP-ICLEI Cities 2023: respuesta oficial de la City of Lagos (Gobierno del Estado de Lagos)', '2023'),
    'cra21': ('https://moelagos.gov.ng/wp-content/uploads/2021/09/Geo-Solutions-Lagos-CRA-Feb-Final-Report-V4-April-23-2021.pdf', 'Ministerio de Ambiente de Lagos: evaluación de riesgo climático de Lagos (Geo-Solutions, informe final, abril de 2021)', '2021'),
    'lasema_comite': ('https://guardian.ng/?p=2397516', 'The Guardian (Nigeria): Lagos se prepara para las lluvias de 2024; se reúne el comité técnico de actores de LASEMA "Lagos sin inundaciones"', '2024'),
    'rnl_ccc': ('https://radionigerialagos.gov.ng/?p=41328', 'Radio Nigeria Lagos: LASEMA y NEMA refuerzan la preparación ante inundaciones; el centro de comando y control 24 horas recibe datos en tiempo real de NiMet y NIHSA', '2026'),
}

EN = {
    '1.1.1': (4, C, 'El Estado considera los riesgos climáticos en sus planes y estrategias, formó un Consejo Estatal de Cambio Climático y tiene un plan climático integrado (2020) con metas de adaptación (CDP 2023).',
        'cdp', 'Llevar los escenarios futuros a los proyectos de infraestructura.', 'Gobierno del Estado de Lagos', MED),
    '1.1.2': (4, C, 'En el plan climático participaron gobiernos local, estatal y nacional, academia, sector privado, ONG, ciudadanos y grupos vulnerables (8 grupos) (CDP 2023).',
        'cdp', 'Sumar a los grupos que faltan.', 'Ministerio de Ambiente de Lagos', CORTO),
    '1.2.1': (4, M, 'Antes de cada temporada de lluvias el comité técnico de actores de LASEMA "Lagos sin inundaciones" coordina la mitigación según el pronóstico de NiMet, y LASEMA trabaja con NEMA en la preparación.',
        'lasema_comite,rnl_ccc', 'Publicar roles y responsabilidades de cada agencia.', 'LASEMA', CORTO),
    '2.1.1': (2, C, 'Evaluación de riesgo climático de 2021 para todo el Estado, hecha por consultores, con priorización de amenazas; no incluye escenarios de altas emisiones ni proceso de actualización (CDP 2023) y tiene más de 3 años.',
        'cdp,cra21', 'Actualizar con escenarios y revisión externa.', 'Ministerio de Ambiente de Lagos', MED),
    '2.2.1': (3, C, 'El Estado estima que el 90-100% de la población está expuesta al calor extremo y el 60-70% a inundación costera y urbana (CDP 2023).',
        'cdp', 'Escenarios "más probable" y "más grave".', 'Gobierno del Estado de Lagos', MED),
    '9.6.2': (3, M, 'LASEMA tiene un centro de comando y control 24 horas (línea 112), convertido en agencia propia, que en 2026 recibe datos en tiempo real de los servicios meteorológico e hidrológico; no se informa cobertura de cámaras ni procedimientos probados.',
        'rnl_ccc', 'Procedimientos probados para el escenario más grave.', 'LASEMA', MED),
}
ES = {
    'A2.2': (3, C, 'El Estado identifica efectos del calor, enfermedades infecciosas y lluvias en la salud (seguridad alimentaria, sobrecarga e interrupción de servicios de salud, agua y saneamiento) y la falta de vigilancia sanitaria informada por el clima (CDP 2023).',
        'cdp', 'Plan de salud por escenario.', 'Ministerio de Salud de Lagos', MED),
}
