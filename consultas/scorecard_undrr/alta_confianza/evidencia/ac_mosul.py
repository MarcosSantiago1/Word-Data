# Mosul (municipalidad de Mosul; gobernación de Nínive): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'mosul', 'Mosul', 'IRQ'
OFICINA = 'Municipalidad de Mosul / gobernación de Nínive'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'
F = {
    'jrc_presa': ('https://publications.jrc.ec.europa.eu/repository/bitstream/JRC101555/lbna27923enn.pdf', 'Centro Común de Investigación de la Comisión Europea: estudio hidrodinámico de la rotura de la presa de Mosul (ola de hasta 25 m que llega a la ciudad en 1 h 40 min)', '2016'),
    'rferl_presa': ('https://www.rferl.org/amp/iraq-mosul-dam-seen-high-risk-failing-deluging-millions-us-army-corps-engineers/27542359.html', 'RFE/RL: la presa de Mosul, con alto riesgo de falla según el Cuerpo de Ingenieros de EE. UU.', '2016'),
    'rew_inyeccion': ('https://www.renewableenergyworld.com/energy-business/energy-finance/inspector-faults-grouting-effort-safety-of-iraqs-750-mw-mosul-dam/', 'Renewable Energy World: un inspector cuestiona las inyecciones de mantenimiento y la seguridad de la presa de Mosul', '2018'),
    'unh_marco': ('https://unhabitat.org/the-initial-planning-framework-for-the-reconstruction-of-mosul-0', 'ONU-Hábitat y UNESCO: marco inicial de planificación para la reconstrucción de Mosul', '2019'),
    'unesco_fin': ('https://www.archdaily.com/1034216/image/jpeg', 'ArchDaily: la UNESCO culmina el programa de restauración de Mosul (Revive the Spirit of Mosul)', '2025'),
}
EN = {
    '2.2.1': (3, M, 'Hay un escenario de rotura de la presa de Mosul (CCI de la Comisión Europea) con ola de hasta 25 m que llega a la ciudad en 1 h 40 min; EE. UU. estima entre 500.000 y 1,47 millones de personas en el camino de la ola.',
              'jrc_presa,rferl_presa', 'Plan de evacuación oficial para el escenario de rotura.', 'Ministerio de Recursos Hídricos / gobernación', CORTO),
    '8.1.2': (1, M, 'El mantenimiento por inyecciones de la fundación de la presa se retomó tras 2017 pero con menos frecuencia de la necesaria, según evaluaciones de 2016-2018; no se halló dato más reciente.',
              'rferl_presa,rew_inyeccion', 'Publicar el estado de la presa y su mantenimiento.', 'Ministerio de Recursos Hídricos', CORTO),
    '10.1.1': (3, M, 'La reconstrucción posguerra se guió por un marco de planificación de ONU-Hábitat y UNESCO; el programa Revive the Spirit of Mosul terminó en 2025 tras restaurar la mezquita Al-Nuri, iglesias y 124 casas patrimoniales.',
               'unh_marco,unesco_fin', 'Incorporar la reducción del riesgo en la reconstrucción pendiente.', 'Municipalidad de Mosul', MED),
}
ES = {}
