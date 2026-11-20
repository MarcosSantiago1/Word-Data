# Bagdad (Secretaría de Bagdad / Amanat Baghdad; gobernación): base de alta confianza, búsqueda nov-2026.
ID, NOMBRE, ISO3 = 'bagdad', 'Bagdad', 'IRQ'
OFICINA = 'Amanat Baghdad'
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'
F = {
    'ahram_apagon': ('https://english.ahram.org.eg/NewsContent/2/8/551064/World/Region/Iraq-announces-nationwide-power-outage-amid-;recor.aspx', 'Ahram Online (AFP): Irak anuncia un apagón nacional en medio de un calor récord (pérdida súbita de más de 6.000 MW; 48-50 °C en Bagdad)', '2025'),
    'gma_apagon': ('https://www.gmanetwork.com/news/topstories/world/955564/iraq-announces-nationwide-power-outage-amid-record-heat/story/', 'GMA News: Irak anuncia un apagón nacional por calor récord', '2025'),
    'an_red': ('https://www.arabnews.pk/node/2646442', 'Arab News: cómo la inestabilidad y la dependencia del gas iraní vaciaron el sector eléctrico de Irak (29 GW de producción frente a 40 GW de demanda)', '2026'),
}
EN = {
    '8.3.1': (1, C, 'En agosto de 2025 la red eléctrica nacional colapsó por completo con 48-50 °C en Bagdad, tras perder más de 6.000 MW; la producción (29 GW) no cubre la demanda normal (40 GW).',
              'ahram_apagon,gma_apagon,an_red', 'Respaldo eléctrico de servicios críticos en olas de calor.', 'Ministerio de Electricidad / Amanat Baghdad', LARGO),
}
ES = {
    'A2.2': (1, M, 'Las olas de calor de 48-50 °C coinciden con cortes de electricidad generalizados; no se halló plan de calor y salud de la ciudad.',
             'ahram_apagon', 'Plan de calor y salud con centros de enfriamiento.', 'Dirección de Salud de Bagdad', CORTO),
}
