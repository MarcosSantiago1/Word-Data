"""Perfiles de las ciudades de China continental (municipios centrales y ciudades de nivel de prefectura).

Todas comparten el mismo marco: Ley de Respuesta a Emergencias (revisada en 2024), una Oficina de Gestión de
Emergencias (应急管理局) en cada ciudad desde la reforma de 2018, planes de emergencia por nivel de gobierno y
el sistema nacional de avisos de emergencia por celular. Lo que cambia entre ciudades sale de los datos (amenaza,
exposición, IDH, PIB) y de los hechos de esta lista. Escritos a mano desde conocimiento general (nov-2026).
"""

# ciudades con metro o tren ligero urbano en servicio (2025)
METRO = {'pekin', 'shanghai', 'guangzhou', 'shenzhen', 'tianjin', 'chongqing', 'wuhan', 'chengdu', 'nanjing', 'hangzhou', 'xi_an', 'suzhou',
         'zhengzhou', 'changsha', 'kunming', 'shenyang', 'harbin', 'changchun', 'dalian', 'qingdao', 'ningbo', 'wuxi', 'hefei', 'nanning', 'nanchang',
         'fuzhou', 'xiamen', 'dongguan', 'foshan', 'guiyang', 'shijiazhuang', 'taiyuan', 'urumqi', 'lanzhou', 'jinan', 'hohhot', 'changzhou', 'xuzhou',
         'shaoxing', 'wenzhou', 'luoyang', 'wuhu', 'nantong', 'jinhua', 'taizhou', 'jiaxing', 'huai_an', 'zhuhai', 'tianshui', 'sanya'}
# puertos marítimos o fluviales grandes (Yangtsé, Perla, Gran Canal)
PUERTO = {'shanghai', 'tianjin', 'guangzhou', 'shenzhen', 'ningbo', 'qingdao', 'dalian', 'xiamen', 'yantai', 'rizhao', 'lianyungang', 'tangshan',
          'qinhuangdao', 'cangzhou', 'weihai', 'dongying', 'yingkou', 'jinzhou', 'dandong', 'huludao', 'fuzhou', 'quanzhou', 'putian', 'ningde', 'zhangzhou',
          'shantou', 'jieyang', 'chaozhou', 'shanwei', 'huizhou', 'dongguan', 'zhongshan', 'zhuhai', 'jiangmen', 'yangjiang', 'maoming', 'zhanjiang', 'qinzhou',
          'haikou', 'wenzhou', 'taizhou', 'zhoushan', 'nantong', 'suzhou', 'wuxi', 'changzhou', 'zhenjiang', 'yangzhou', 'nanjing', 'taizhou_jiangsu', 'yancheng',
          'wuhu', 'ma_anshan', 'anqing', 'chizhou', 'jiujiang', 'wuhan', 'huangshi', 'yichang', 'jingzhou', 'yueyang', 'chongqing', 'luzhou', 'yibin', 'wuzhou',
          'guigang', 'foshan', 'zhaoqing', 'huai_an', 'xuzhou', 'jining', 'hangzhou', 'jiaxing', 'huzhou'}
# ciudades piloto de "ciudad esponja" (2015-2016) y del programa nacional de demostración (2021-2023), según el MOHURD
ESPONJA = {'chongqing', 'wuhan', 'xiamen', 'jinan', 'changde', 'nanning', 'pekin', 'tianjin', 'shanghai', 'shenzhen', 'dalian', 'qingdao', 'ningbo',
           'fuzhou', 'zhuhai', 'yuxi', 'qingyang', 'xining', 'tangshan', 'changzhi', 'siping', 'wuxi', 'suqian', 'hangzhou', 'mazhou', 'longyan', 'nanping',
           'yichun', 'ganzhou', 'weifang', 'xinxiang', 'xiaogan', 'yueyang', 'guangzhou', 'shantou', 'guilin', 'guang_an', 'anshun', 'yunnan', 'tianshui',
           'yinchuan', 'luoyang', 'zhengzhou', 'lishui', 'quzhou', 'jiaxing', 'huainan', 'wuhu', 'mianyang', 'deyang', 'kunming', 'xi_an', 'hefei', 'changsha',
           'nanchang', 'shijiazhuang', 'taiyuan', 'hohhot', 'harbin', 'changchun', 'shenyang', 'jinhua', 'zhuzhou', 'jingmen', 'huangshi', 'quanzhou'}
# miembros de 100 Resilient Cities / Resilient Cities Network y C40
REDES = {'huangshi': '100 Resilient Cities (Resilient Cities Network)', 'deyang': '100 Resilient Cities (Resilient Cities Network)',
         'pekin': 'C40', 'shanghai': 'C40', 'guangzhou': 'C40', 'shenzhen': 'C40', 'wuhan': 'C40', 'nanjing': 'C40', 'hangzhou': 'C40',
         'chengdu': 'C40', 'qingdao': 'C40', 'dalian': 'C40', 'fuzhou': 'C40', 'zhenjiang': 'C40', 'tianjin': 'C40', 'chongqing': 'C40'}

# desastres grandes desde 1990 (hechos conocidos); ov = respuestas que fija el hecho
DES = {
 'zhengzhou': ('Lluvia extrema del 20 de julio de 2021 (201,9 mm en una hora, unas 380 muertes en la ciudad, incluidas 14 en la línea 5 del metro y un túnel vial)',
               {'10.2.1': (4, 'El informe de investigación del Consejo de Estado (2022) señaló fallas de alerta y respuesta y sancionó a funcionarios; se cambiaron protocolos de cierre de metro y túneles.'),
                '8.5.3': (1, 'En 2021 el agua entró a la línea 5 del metro y murieron 14 personas en un tren detenido.')}),
 'xinxiang': ('Inundaciones de julio de 2021 en el norte de Henan', {}),
 'pekin': ('Lluvia del 21 de julio de 2012 (79 muertes), SARS (2003) e inundaciones por el tifón Doksuri (julio-agosto de 2023, decenas de muertes en Pekín y Hebei)', {}),
 'baoding': ('Inundaciones por el tifón Doksuri (2023), con Zhuozhou bajo agua tras abrir zonas de desborde', {}),
 'langfang': ('Inundaciones por el tifón Doksuri (2023), usada como zona de desborde de crecidas', {}),
 'shenzhen': ('Deslizamiento del vertedero de Guangming (diciembre de 2015, 73 muertes) y tifón Mangkhut (2018)', {}),
 'tianjin': ('Explosiones del puerto de Tianjín (agosto de 2015, 173 muertes)', {'8.5.5': (2, 'Las explosiones de 2015 en un depósito de químicos dañaron el puerto y miles de viviendas cercanas.')}),
 'wuhan': ('Inundaciones del Yangtsé (1998, 2016 y 2020) y brote inicial de COVID-19 (diciembre de 2019 a abril de 2020, cierre total de la ciudad)', {}),
 'chongqing': ('Ola de calor, sequía e incendios forestales de agosto de 2022 (cortes de luz por baja de la generación hidroeléctrica) e inundaciones del Yangtsé (2020)', {}),
 'chengdu': ('Terremoto de Wenchuan (mayo de 2008, más de 69.000 muertes en Sichuan, epicentro a unos 80 km) y sismo de Luding (2022)', {}),
 'mianyang': ('Terremoto de Wenchuan (2008): Beichuan, en esta ciudad, quedó destruido y fue reubicado', {'10.2.1': (4, 'La reconstrucción tras Wenchuan con ayuda de otras provincias (programa de contrapartes) es un caso estudiado de recuperación rápida.')}),
 'deyang': ('Terremoto de Wenchuan (2008), con miles de muertes en Mianzhu y Shifang', {}),
 'guangzhou': ('Tifón Mangkhut (2018), inundaciones de 2020 y tornado de Baiyun (abril de 2024)', {}),
 'meizhou': ('Inundaciones y deslizamientos de junio de 2024 (unas 50 muertes en Pingyuan)', {}),
 'shanghai': ('Incendio del edificio de Jing\'an (2010, 58 muertes), estampida del Bund (2014, 36 muertes), cierre por COVID-19 (abril-mayo de 2022) y tifón Bebinca (2024)', {}),
 'yueyang': ('Rotura del dique del lago Dongting (julio de 2024, miles de evacuados)', {}),
 'zhaotong': ('Terremoto de Ludian (agosto de 2014, 617 muertes)', {}),
 'ya_an': ('Terremoto de Lushan (2013)', {}),
 'qingdao': ('Explosión del oleoducto de Sinopec (noviembre de 2013, 62 muertes)', {'8.4.1': (2, 'La explosión de 2013 mostró fallas en el control de ductos bajo zonas urbanas.')}),
 'yancheng': ('Tornado de Funing (junio de 2016, 99 muertes) y explosión química de Xiangshui (marzo de 2019, 78 muertes)', {}),
 'suzhou': ('Explosión de polvo de Kunshan (agosto de 2014, 146 muertes)', {}),
 'wenzhou': ('Choque de trenes de alta velocidad (julio de 2011, 40 muertes) y tifón Lekima (2019)', {}),
 'taizhou': ('Tifón Lekima (agosto de 2019, unas 45 muertes en Zhejiang, con deslizamiento en Yongjia)', {}),
 'shiyan': ('Explosión de gas en un mercado (junio de 2021, 25 muertes)', {'8.4.1': (2, 'La explosión de 2021 en Zhangwan llevó a un programa nacional de renovación de redes de gas viejas.')}),
 'haikou': ('Tifones Rammasun (2014) y Yagi (septiembre de 2024, impacto directo con cortes de luz de días)', {}),
 'zhanjiang': ('Tifones Rammasun (2014) y Mujigae (2015)', {}),
 'jiangmen': ('Tifón Hato (2017) y Mangkhut (2018)', {}),
 'shaoguan': ('Inundaciones del río Bei (2022 y 2024)', {}),
 'harbin': ('Contaminación del río Songhua (2005, corte de agua de 4 días) y lluvias de 2023', {'8.2.1': (2, 'En 2005 la ciudad cortó el agua cuatro días por el derrame químico en el río Songhua.')}),
 'jilin': ('Explosión química de 2005 que contaminó el Songhua e inundaciones de 2010', {}),
 'shijiazhuang': ('Inundaciones de 2016 y 2023 en el oeste de la provincia', {}),
 'xingtai': ('Inundaciones de julio de 2016 (decenas de muertes)', {}),
 'tangshan': ('Terremoto de Tangshan (1976, unas 240.000 muertes), base de la norma sísmica y de la reconstrucción de la ciudad', {}),
 'lanzhou': ('Derrame de benceno en el agua potable (2014) y aludes de barro', {}),
 'linfen': ('Colapso del restaurante Juxian (2020, 29 muertes) y deslave de relaves de Xiangfen (2008, 277 muertes)', {}),
 'xining': ('Hundimiento de calle con colectivo (2020, 10 muertes)', {}),
 'dalian': ('Incendio del oleoducto del puerto (2010, gran derrame) e inundaciones', {}),
 'xi_an': ('Cierre por COVID-19 (diciembre de 2021 a enero de 2022) e inundaciones de 2021', {}),
 'xiamen': ('Tifón Meranti (2016, el más fuerte en la ciudad desde 1949)', {}),
 'quanzhou': ('Colapso del hotel de cuarentena Xinjia (2020, 29 muertes)', {}),
 'fuzhou': ('Inundaciones por el tifón Doksuri (2023)', {}),
 'nanning': ('Inundaciones de 2022', {}),
 'guilin': ('Inundaciones del río Li (junio de 2024, las mayores en décadas)', {}),
 'kunming': ('Sequía de 2009-2012 en Yunnan y crisis de agua', {}),
 'dingxi': ('Terremoto de Minxian (2013, 95 muertes)', {}),
 'tianshui': ('Inundaciones y deslizamientos de 2013 en Gansu', {}),
 'urumqi': ('Incendio de un edificio residencial (noviembre de 2022, 10 muertes, protestas por las restricciones de COVID-19) y disturbios de 2009', {}),
 'changsha': ('Colapso de un edificio residencial autoconstruido (abril de 2022, 53 muertes)', {'4.3.1': (2, 'El colapso de 2022 llevó a una inspección nacional de viviendas autoconstruidas.')}),
 'hengyang': ('Incendio de un depósito (2003, 20 bomberos muertos)', {}),
 'jieyang': ('Inundaciones y deslizamientos de 2024 en el este de Guangdong', {}),
 'yangjiang': ('Tifones e inundaciones costeras', {}),
}

INFORMAL = 3  # "aldeas urbanas" (城中村) y vivienda autoconstruida; mayor en ciudades del sur con fuerte inmigración
INFORMAL_CIUDAD = {'shenzhen': 10, 'guangzhou': 8, 'dongguan': 10, 'foshan': 6, 'zhongshan': 6, 'xiamen': 5, 'pekin': 4, 'shanghai': 4}
