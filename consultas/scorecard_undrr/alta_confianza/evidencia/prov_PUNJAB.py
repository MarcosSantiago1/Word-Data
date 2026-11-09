# Provincia de Punyab (Pakistán): evidencia provincial que heredan Lahore, Rawalpindi y Multán (búsqueda nov-2026).
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'r1122_cert': ('https://rescue.gov.pk/CSafety.aspx', 'Rescue 1122 Punyab: Community Safety (equipos comunitarios de respuesta y simulacros en escuelas)', 's/f'),
    'trib_cert': ('https://tribune.com.pk/story/1884241/entertainment', 'Express Tribune: Rescue 1122 movilizó a 537.712 personas de la comunidad en un año (más de 4.000 equipos comunitarios en todos los consejos de unión)', '2019'),
    'insarag': ('https://www.brecorder.com/news/40270824/pakistan-rescue-team-celebrates-4th-anniversary-of-un-certification', 'Business Recorder: el Pakistan Rescue Team de Rescue 1122 (Lahore) cumple 4 años de clasificación INSARAG de la ONU', '2023'),
    'pdma_pb_inund25': ('https://www.dawn.com/news/1937148', 'Dawn: la jefa de gobierno de Punyab ordena evacuar las riberas ante las crecidas de 2025', '2025'),
    'campos25': ('https://www.dawn.com/news/amp/1940648', 'Dawn: unos 412 campamentos de socorro en los distritos inundados de Punyab', '2025'),
    'smog24': ('https://www.dawn.com/news/1869029', 'Dawn: el gobierno declara "calamidad por smog" en Punyab', '2024'),
    'smog_salud': ('https://www.dawn.com/news/1870626/schools-colleges-closed-across-18-districts-as-smog-reigns-in-punjab', 'Dawn: emergencia sanitaria en las divisiones de Lahore y Multán y cierre de escuelas por smog', '2024'),
}

EN = {
    '6.4.1': (4, C, 'Rescue 1122 da la capacitación CADRE de tres días a voluntarios (primeros auxilios, búsqueda y rescate básicos, agua, incendio) y tiene más de 4.000 equipos comunitarios en todos los consejos de unión de Punyab.',
              'r1122_cert,trib_cert', 'Registrar la cobertura por barrio.', 'Rescue 1122', CORTO),
    '7.1.1': (4, C, 'Rescue 1122 creó equipos comunitarios de respuesta (CERT) en todos los consejos de unión de Punyab, con más de 600.000 voluntarios capacitados.',
              'trib_cert,r1122_cert', 'Mantener activos los equipos en asentamientos informales.', 'Rescue 1122', MED),
    '7.1.2.1': (3, M, 'Los equipos comunitarios tienen roles de primera respuesta y participan en simulacros anuales; no se halló un plan de reducción de riesgo por barrio.',
                'r1122_cert', 'Planes barriales de reducción del riesgo.', 'Rescue 1122 / municipio', MED),
    '9.3.2': (3, C, 'Rescue 1122 tiene dotaciones y estaciones en cada distrito y un equipo de búsqueda y rescate urbano clasificado por INSARAG (ONU) con base en Lahore.',
              'insarag,r1122_cert', 'Definir dotaciones para el escenario más severo.', 'Rescue 1122', MED),
    '9.7.1': (3, M, 'Rescue 1122 hace simulacros de evacuación en escuelas y ejercicios anuales con los equipos comunitarios; su equipo de rescate de Lahore tiene clasificación INSARAG de la ONU desde 2019.',
              'r1122_cert,insarag', 'Simulacro anual de ciudad con todos los organismos.', 'Rescue 1122 / DDMA', CORTO),
}
ES = {
    'A9.1': (3, M, 'El gobierno de Punyab declara emergencias por smog (2024: emergencia sanitaria en Lahore y Multán, cierre de escuelas y mascarilla obligatoria) a partir del índice de calidad del aire.',
             'smog24,smog_salud', 'Alertas sanitarias tempranas por calor e inundación.', 'Departamento de Salud de Punyab', MED),
}
