# Surabaya (Pemerintah Kota Surabaya; BPBD Kota Surabaya): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'surabaya', 'Surabaya', 'IDN'
OFICINA = 'BPBD Kota Surabaya'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'perwali_112': ('https://jdih.surabaya.go.id/uploads/peraturan/2023perwali3578020.pdf', 'Perwali Surabaya 2023: Command Center 112 (centro de control integrado de emergencias y desastres)', '2023'),
    'ss_4prog': ('https://www.suarasurabaya.net/?p=589669', 'Suara Surabaya: los cuatro programas de la BPBD desde 2017 (escuelas seguras, barrios resilientes, centros de salud seguros, familias resilientes)', '2022'),
    'ss_culto': ('https://www.suarasurabaya.net/kelanakota/2025/bpbd-surabaya-targetkan-seluruh-rumah-ibadah-tangguh-bencana/', 'Suara Surabaya: la BPBD apunta a que todos los templos sean resilientes', '2025'),
    'jp_bombas': ('https://www.thejakartapost.com/news/2020/01/24/from-culverts-to-water-pumps-what-cities-can-learn-from-surabaya-in-mitigating-floods.html', 'The Jakarta Post: de alcantarillas a bombas, lo que otras ciudades pueden aprender de Surabaya contra las inundaciones', '2020'),
    'voi_75': ('https://voi.id/en/amp/336306', 'VOI: el gobierno de la ciudad optimiza 75 casas de bombas ante inundaciones', '2023'),
    'ant_bozem': ('https://jatim.antaranews.com/berita/980809/pemkot-surabaya-percepat-pembangunan-bozem-guna-antisipasi-banjir', 'Antara: Surabaya acelera la construcción de lagunas de retención (bozem)', '2024'),
    'r112_cyber': ('https://news.republika.co.id/berita/r3hleq485/pusat-data-cyber-terbakar-surabaya-alihkan-layanan-112', 'Republika: se incendia el centro de datos; Surabaya desvía el servicio 112', '2021'),
}

EN = {
    '1.2.2': (4, C, 'El Command Center 112 (desde 2016, regulado por Perwali de 2023) recibe todas las emergencias y coordina la respuesta con la BPBD, bomberos, policía y protección civil desde una sala única.',
              'perwali_112', 'Protocolos para el escenario sísmico severo.', 'BPBD Kota Surabaya', CORTO),
    '6.2.1': (3, C, 'La BPBD sostiene desde 2017 programas de escuelas seguras, barrios resilientes, centros de salud seguros y familias resilientes; en 2025 sumó templos resilientes.',
              'ss_4prog,ss_culto', 'Campaña con mensajes medibles.', 'BPBD Kota Surabaya', CORTO),
    '7.1.1': (3, C, 'Unos 1.200 de los 1.400 barrios (RW) participaron en el programa Kampung Tangguh; la BPBD apunta a cubrir los 154 kelurahan con el programa de barrio resiliente.',
              'ss_4prog', 'Completar la cobertura con planes de riesgo por barrio.', 'BPBD Kota Surabaya', MED),
    '8.1.1': (3, C, 'La ciudad baja sobre el mar se protege con casas de bombas (75 según la ciudad), compuertas y lagunas de retención (bozem); el método se cita como modelo nacional.',
              'voi_75,ant_bozem,jp_bombas', 'Diseñar para marea alta con lluvia extrema.', 'Dinas Sumber Daya Air', LARGO),
    '8.1.2': (3, M, 'Mantenimiento y ampliación continua de bombas y bozem.',
              'voi_75,ant_bozem', 'Plan de mantenimiento publicado.', 'Dinas Sumber Daya Air', CORTO),
    '8.11.1': (2, C, 'En 2021 un incendio del centro de datos obligó a desviar el servicio 112, lo que muestra una dependencia de un solo sitio.',
               'r112_cyber', 'Respaldo remoto de sistemas críticos.', 'Diskominfo Surabaya', CORTO),
    '9.6.2': (4, C, 'El Command Center 112 reúne en una sala a la BPBD, protección civil y otros organismos, y funciona como centro de operaciones de la ciudad.',
              'perwali_112', 'Procedimientos para desastre mayor.', 'BPBD Kota Surabaya', CORTO),
}
ES = {
    'A8.1': (2, M, 'La BPBD tiene un programa de puskesmas y hospitales seguros desde 2017; no se halló su grado de avance.',
             'ss_4prog', 'Publicar evaluación de seguridad de centros de salud.', 'Dinas Kesehatan', MED),
}

# Plan oficial leído completo (nov-2026): Kajian Risiko Bencana Kota Surabaya 2024-2028 (Perwali 119/2024).
F['krb24'] = ('https://jdih.surabaya.go.id/peraturan/download/4591', 'Perwali Surabaya 119/2024: Evaluación de Riesgo de Desastres de Surabaya 2024-2028 (Kajian Risiko Bencana)', '2024')
EN.update({
    '2.1.1': (4, C, 'La evaluación de riesgo 2024-2028, adoptada por decreto del alcalde, estima amenaza, vulnerabilidad, capacidad y riesgo para inundación, marea alta, licuefacción, sequía, sismo, clima extremo e incendio; no distingue escenario más probable y más severo.',
              'krb24', 'Definir escenarios más probable y más severo.', 'BPBD Surabaya', MED),
    '2.2.1': (3, C, 'La evaluación 2024-2028 calcula población expuesta por amenaza y barrio, con grupos vulnerables (edad, pobreza, discapacidad), pero sin escenarios por intensidad.',
              'krb24', 'Escenarios por intensidad de sismo e inundación.', 'BPBD Surabaya', MED),
    '2.2.2': (4, C, 'La evaluación 2024-2028 estima población expuesta, pérdidas físicas y económicas y daño ambiental por amenaza.',
              'krb24', 'Sumar empleo y producción en riesgo.', 'BPBD Surabaya', MED),
    '2.4.1': (3, C, 'Hay mapas de amenaza, vulnerabilidad, capacidad y riesgo por amenaza; la evaluación recomienda todavía un plan territorial basado en el riesgo.',
              'krb24', 'Plan territorial y de detalle basados en el riesgo.', 'Bappedalitbang / BPBD', MED),
    '2.5.1': (3, M, 'La evaluación rige 2024-2028 y se renueva por decreto en ciclos de cinco años, más largos de lo que pide la herramienta.',
              'krb24', 'Actualización intermedia de escenarios.', 'BPBD Surabaya', MED),
    '9.2.1': (1, C, 'La evaluación 2024-2028 dice que Surabaya no tiene plan de contingencia para inundación ni para sismo; la respuesta se apoya en procedimientos generales y el Command Center 112.',
              'krb24', 'Planes de contingencia de inundación y sismo.', 'BPBD Surabaya', CORTO),
    '9.6.3': (1, M, 'La evaluación 2024-2028 recomienda crear mecanismos de recuperación de infraestructura y vivienda con gobierno, comunidad y sector privado; todavía no existen.',
              'krb24', 'Mecanismo de coordinación de la recuperación.', 'BPBD Surabaya', MED),
    '10.1.1': (0, C, 'La evaluación 2024-2028 dice que Surabaya no tiene plan de rehabilitación ni de recuperación de medios de vida, ni plan para restablecer los servicios básicos del gobierno tras un desastre.',
               'krb24', 'Plan de recuperación posdesastre.', 'BPBD Surabaya', MED),
})
