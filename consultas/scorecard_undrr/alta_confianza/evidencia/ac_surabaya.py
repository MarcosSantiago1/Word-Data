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
