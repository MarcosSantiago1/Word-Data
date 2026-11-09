# India: evidencia nacional que heredan Bombay y Calcuta (búsqueda nov-2026).
C, M = 'alta', 'media'
CORTO, MED, LARGO = 'Corto plazo (≤1 año)', 'Mediano plazo (1-3 años)', 'Largo plazo (>3 años)'

F = {
    'cbs26': ('https://www.freepressjournal.in/india/india-launches-indigenous-cell-broadcast-system-for-geo-targeted-disaster-alerts-on-may-2-nationwide', 'Free Press Journal: India lanza su sistema propio de difusión celular para alertas georreferenciadas (2 de mayo de 2026)', '2026'),
    'cbs_nic': ('https://informatics.nic.in/files/websites/april-2026/india-launches-nationwide-cell-broadcast-system-for-disaster-alerts.php', 'NIC (gobierno de India), eGov Update: India lanza el sistema nacional de difusión celular para alertas de desastre (integrado a la plataforma SACHET)', '2026'),
    'swissre': ('https://www.reinsurancene.ws/indian-insurance-sector-to-be-fastest-growing-among-g20-swiss-re/', 'Reinsurance News (sobre Swiss Re): el 93% de la exposición a catástrofes de India no está asegurada', 's/f'),
    'bgr': ('https://www.outlookbusiness.com/personal-finance/insurance/bharat-griha-raksha-irdai-to-introduce-standard-home-insurance-policy-5829', 'Outlook Business: Bharat Griha Raksha, la póliza estándar de vivienda que la IRDAI obliga a ofrecer (cubre inundación, tormenta y ciclón)', '2021'),
    'bt_1pct': ('https://www.businesstoday.in/personal-finance/insurance/story/rs-500-a-year-could-save-your-home-uttarkashi-disaster-shows-under-1-are-insured-488503-2025-08-08', 'Business Today: menos del 1% de las viviendas están aseguradas', '2025'),
    'iisee': ('https://iisee.kenken.go.jp/worldlist/Web/26_India.htm', 'IISEE (Japón): Regulations for Seismic Design, World List 2024, India (IS 1893 parte 1:2016 y Código Nacional de Edificación 2016)', '2024'),
}

EN = {
    '3.3.1': (1, C, 'Menos del 1% de las viviendas tiene seguro y el 93% de la exposición a catástrofes no está asegurada (Swiss Re); desde 2021 las aseguradoras deben ofrecer la póliza estándar Bharat Griha Raksha con cobertura de inundación y ciclón.',
              'bt_1pct,swissre,bgr', 'Promover el seguro de vivienda o un seguro paramétrico municipal.', 'Gobierno estatal / IRDAI', LARGO),
    '3.3.2': (1, M, 'La brecha de protección no vida de India es del 85-93% de la exposición (Swiss Re); no se halló dato de cobertura de activos públicos o comerciales de la ciudad.',
              'swissre', 'Relevar la cobertura de activos críticos de la ciudad.', 'Corporación municipal', MED),
    '4.3.2': (4, M, 'La norma sísmica IS 1893 (parte 1) se revisó en 2016 y el Código Nacional de Edificación en 2016; es un código modelo que cada ciudad adopta en su reglamento.',
              'iisee', 'Verificar que el reglamento local cite las versiones vigentes.', 'Corporación municipal', CORTO),
    '7.4.2': (4, C, 'Desde mayo de 2026 India tiene difusión celular georreferenciada, integrada a la plataforma SACHET de alertas por SMS que ya llega a todos los estados.',
              'cbs26,cbs_nic', 'Sumar avisos de la ciudad al canal nacional.', 'NDMA / autoridad estatal', CORTO),
    '9.1.1.1': (4, C, 'La difusión celular nacional (2026) llega a todos los teléfonos de la zona sin registro previo, y complementa los SMS de SACHET.',
                'cbs26,cbs_nic', 'Medir el alcance real en la ciudad.', 'NDMA / DoT', CORTO),
}
ES = {}
