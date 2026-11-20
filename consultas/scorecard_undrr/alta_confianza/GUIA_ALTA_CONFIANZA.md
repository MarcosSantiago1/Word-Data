# Base de alta confianza del scorecard UNDRR (90 ciudades)

Noviembre de 2026. Es la versión "con pruebas" del scorecard de resiliencia ante desastres de UNDRR para las 90 ciudades de más prioridad del mundo (amenaza × brecha de capacidad) que no se habían hecho a mano. Se hizo en tres tandas de 30, todas el 9 de noviembre de 2026: la segunda va de Kaohsiung a Antalya en el orden de prioridad y la tercera de Wuzhou a Luanda. Las otras 269 ciudades de más de 2 millones siguen solo en el modelo. Cada ciudad tiene las 141 preguntas: 118 de la herramienta detallada y 23 del anexo de salud pública.

## La regla

- **Cada respuesta con puntaje lleva su fuente**: enlace, título y fecha del documento.
- **Si no hay prueba pública, no se puntúa.** La pregunta queda como "sin evidencia", con el puntaje vacío, y en el .xlsm queda sin ninguna opción marcada. Nada se estima ni se copia del modelo.
- **Confianza alta**: lo dice un documento oficial (de la ciudad, la provincia o el país), la respuesta de la propia ciudad a CDP-ICLEI 2023, o un hecho o declaración oficial que publican al menos dos medios de referencia distintos, y el puntaje sale directo de ahí.
- **Confianza media**: una sola fuente secundaria confiable (organismo internacional, prensa de referencia, estudio académico, agencia estatal sin verificación independiente). Varias notas del mismo medio cuentan como una sola fuente o un dato oficial que hay que interpretar para puntuar.
- Lo que la ciudad misma dice que **no tiene** (por ejemplo, "no tenemos evaluación de riesgo" ante CDP) cuenta como prueba de un puntaje bajo, con confianza alta.

## Resultado

| | |
|---|---|
| Ciudades | 90 |
| Respuestas | 12.690 (90 × 141) |
| Con evidencia | 627 (5%) |
| Confianza alta | 343 |
| Confianza media | 284 |
| Sin evidencia | 12.063 |
| Fuentes distintas citadas | 337 |

La segunda tanda suma 175 respuestas con evidencia y la tercera 98. La tercera tiene menos porque 17 de sus 30 ciudades son chinas de nivel prefectura, que casi no publican información verificable en línea, y solo 6 respondieron a CDP 2023.

**Cobertura por ciudad** (respuestas con evidencia de 141): Karachi 52, Quezón 31, Lahore 30, Bombay 29, Rawalpindi 19, Surabaya 19, Calcuta 16, Multán 16, Daca Norte 15, Daca Sur 15, Delhi 14, Surat 14, Ahmedabad 13, Chittagong 13, Gujranwala 13, Islamabad 13, Bekasi 12, Chennai 12, Faisalabad 12, Kaohsiung 12, Yakarta 11, Nuevo Taipéi 10, Taipéi 10, Antalya 9, Dar es Salaam 9, Taoyuan 9, Cần Thơ 8, Hai Phong 8, Kinsasa 8, Bandung 7, Gazipur 7, Lagos 7, Medán 7, Pune 7, Hanói 6, Hyderabad 6, Lucknow 6, Ciudad Ho Chi Minh 5, Depok 5, Kanpur 5, Da Nang 4, Jartum 4, Omdurmán 4, Adana 3, Brazzaville 3, Chaozhou 3, Dongguan 3, Duala 3, Fuzhou (Fujian) 3, Heyuan 3, Huizhou 3, Jiangmen 3, Jieyang 3, Mbuji-Mayi 3, Mosul 3, Shantou 3, Wenzhou 3, Wuzhou 3, Yangjiang 3, Zhangzhou 3, Zhuhai 3, Alejandría 2, Bagdad 2, Bamako 2, Damasco 2, Foshan 2, Kabul 2, Lomé 2, Mogadiscio 2, Ningde 2, Pionyang 2, Rangún 2, Taizhou 2, Zhongshan 2, Conakri 1, El Cairo 1, Fuzhou (Jiangxi) 1, Guiza 1, Jiaxing 1, Luanda 1, Mashhad 1, Nantong 1, Nom Pen 1, Putian 1, Qinzhou 1, Saná 1, Taskent 1, Wuxi 1, Yibin 1, Argel 0. Gujranwala, Faisalabad y Kanpur heredan casi todo de su provincia o su país; las ciudades de Cantón, de Guangdong y de China; Argel no tiene ninguna prueba pública verificable.

### Por qué la cobertura es baja

Es lo esperable y no un defecto del método:

- **Muchas preguntas piden datos internos que ninguna ciudad publica**: días de servicio perdidos por escenario, camas de hospital en riesgo, brecha de refugios, días de combustible. Unas 50 de las 118 preguntas detalladas son de este tipo. Solo se pueden contestar con el gobierno local.
- **Las ciudades con respuesta a CDP-ICLEI 2023 tienen mucha más cobertura**: Karachi, Bombay, Quezón, Calcuta, las dos Daca, Bekasi, Kinsasa y Dar es Salaam; en la segunda tanda, Kaohsiung, Nuevo Taipéi, Taoyuan, Antalya, Delhi, Chennai, Hanói, Cần Thơ, Medán y Duala; en la tercera, Ahmedabad, Yakarta, Taipéi, Lagos, Ciudad Ho Chi Minh y Fuzhou (Fujian). Esa respuesta oficial cubre planificación, evaluación de riesgo, metas, ecosistemas y salud.
- **En ciudades en guerra o cerradas casi no hay información pública verificable**: Jartum, Omdurmán, Kabul, Damasco, Bagdad, Mosul, Pionyang, Rangún, Saná y Mogadiscio. Lo poco que hay es sobre servicios colapsados (agua, energía, hospitales).
- Los sitios de UNDRR (tablero MCR2030, PreventionWeb, Sendai Monitor) bloquean las consultas automáticas, así que no se pudieron leer los scorecards que algunas ciudades hayan cargado ahí.

**Cómo leer el nivel medio**: el nivel medio de cada ciudad se calcula solo sobre las preguntas respondidas. Por eso no es comparable con el puntaje total del modelo ni entre ciudades con distinta cobertura.

## Revisión de calidad (9 de noviembre de 2026)

- **Confianza revisada con la regla.** 40 respuestas tenían confianza alta con un solo medio (a veces varias notas del mismo diario) o solo con medios estatales (Xinhua, China Daily, CGTN, ACP, PTS). Pasaron a confianza media; como algunas están en la evidencia nacional o provincial (Taiwán, Punyab), en la base son 49 filas menos de confianza alta. Siguen en alta las que citan el documento oficial aunque esté alojado en otro sitio: el comunicado del Consejo de Ministros de Malí, la evaluación de ONU-Hábitat y la CDA de Islamabad, el plan de olas de calor del Comisionado de Karachi y los decretos de Vietnam.
- **Mismo hecho, mismo puntaje.** La pregunta 2.5.1 tenía la misma prueba de CDP ("proceso de actualización al menos cada cinco años") con 4 en Bombay y 3 en otras cinco ciudades; Bombay quedó en 3.
- **Fechas.** Se comparó el año que dice cada respuesta con el de sus fuentes. En Punyab (9.7.1) se sacó un ejercicio de INSARAG en 2024 que la fuente de 2023 no podía respaldar.
- **Lo que no se pudo hacer.** Se intentó abrir las 65 páginas de prensa de la segunda y la tercera tanda para comparar cada dato con el texto, pero el acceso a internet de este entorno está limitado a una lista de sitios y no las alcanza. Esas respuestas se apoyan en lo que muestran los buscadores sobre cada página. Las que dependen solo de prensa quedan ahora en confianza media, salvo Kaohsiung (1.2.2) y Da Nang (1.2.2 y 9.2.1), que tienen dos o tres medios distintos. Si se habilita el acceso completo a internet en el entorno, se puede hacer esta comparación página por página.

## Planes oficiales leídos

Se buscaron los planes oficiales de gestión del riesgo, contingencia, calor y clima de las 90 ciudades y se leyeron completos los que se pudieron descargar. Los textos están en `planes/` (PDF original y texto extraído).

| Ciudad | Plan | Qué sumó |
|---|---|---|
| Quezón | Plan DRRM 2021-2027, volumen 1 (112 páginas) | Estimación de daños y pérdidas, sector privado, seguros, inventario de recursos, refugios, recuperación y aprendizaje (7 respuestas nuevas o corregidas) |
| Surabaya | Evaluación de riesgo de desastres 2024-2028, Perwali 119/2024 (143 páginas) | Amenazas, exposición, pérdidas, mapas y actualización; el propio documento dice que no hay plan de contingencia de inundación ni de sismo ni plan de recuperación (8 respuestas) |
| Lahore | Heatwave Management Plan 2025-2028 (88 páginas) | Escenario de calor, campaña de difusión, alerta sanitaria en tres niveles y evaluación posterior a la temporada (4 respuestas) |
| Bombay | Mumbai Climate Action Plan 2022 (240 páginas) | Exposición a anegamiento y deslizamiento; el plan de calor previsto para 2022-2023 sigue pendiente (2 respuestas) |
| Hai Phong | Plan 2025 de prevención de desastres de Cát Hải (11 páginas) | Plan de evacuación por tifón y difusión de avisos, a nivel de distrito (2 respuestas) |
| Karachi | Karachi Climate Action Plan 2025 (202 páginas) | Ya estaba citado; la lectura completa confirmó las respuestas y no sumó nuevas: es sobre todo un plan de emisiones |
| Surat | Disaster Management & Preparedness Plan, edición 2026 (se actualiza cada año desde 2002) | Tareas por departamento y zona, sirenas por nivel del Tapi, sala de control, proveedores privados, voluntarios, enfermedades por agua y vectores, calor (9 respuestas) |
| Surat | Plan de acción ante olas de calor 2023 (UHCRCE, IRADe, APN) | Alertas por colores con umbrales propios basados en mortalidad, refugios y avisos por SMS (2 respuestas) |
| Delhi | Heat Action Plan 2025 (DDMA) | Alertas por colores, vigilancia IDSP, preparación de hospitales, campaña de difusión y escuelas (5 respuestas) |

**No se pudieron obtener**:

- Los planes distritales de gestión de desastres 2025 de Lahore, Rawalpindi y Multán: el sitio de la PDMA de Punyab rechaza las descargas automáticas. Si se suben los PDF a mano, se pueden leer.
- El plan de gestión de desastres de Calcuta 2020: está detrás de una suscripción paga.
- El plan distrital de la ciudad de Bombay: el enlace oficial da error 404.
- Los planes de acción climática de Daca Norte y Daca Sur (2024), el plan de contingencia multiamenaza de Chittagong, el plan climático de Dar es Salaam, los planes de Bandung, Bekasi, Depok y Zhangzhou: se anunciaron pero no están publicados en línea.
- Kinsasa no tiene plan de contingencia (lo dice la prensa local; en 2024 se creó una comisión de inundaciones).
- Kabul, Bagdad, Mosul, Damasco, Pionyang, Rangún, Jartum, Omdurmán, Mbuji-Mayi y Brazzaville: no hay planes municipales publicados.
- Segunda tanda: el plan de gestión de desastres 2022-2027 de Medán y el plan de emergencia de Chaozhou (el servidor corta la conexión), el plan climático de Chennai y la revisión local voluntaria de Kaohsiung (los enlaces oficiales dan 404), y el plan distrital 2021 de Faisalabad (PDMA de Punyab, mismo bloqueo). Se citan con confianza media cuando hay otra prueba de su contenido.
- Duala declara ante CDP que no tiene evaluación de riesgo ni plan climático por falta de fondos; Conakri, Lomé, Mogadiscio, Bamako, Guiza, Alejandría y Saná no publican planes municipales.
- Tercera tanda: no se encontraron en línea los planes municipales de Kanpur, Argel, Luanda, Mashhad, El Cairo ni de las ciudades chinas (salvo la mención del plan de emergencia de Wenzhou); el plan provincial de Adana (İRAP 2022) se cita por referencias de prensa. Ahmedabad tiene el plan de calor más antiguo de Asia del Sur (2013), citado por fuentes secundarias.

## Archivos

| Carpeta o archivo | Qué tiene |
|---|---|
| `datos/base_alta_confianza.csv` | Una fila por ciudad y pregunta (12.690). Columnas: id, ciudad, iso3, herramienta, esencial, ref, titulo, puntaje, confianza, evidencia, fuentes, urls, origen (ciudad, provincia o país), accion, responsable, plazo, fecha_consulta. |
| `datos/fuentes_alta_confianza.csv` | Cada fuente citada: ciudad, clave, url, título, fecha del documento. |
| `datos/resumen_ciudades.csv` | Una fila por ciudad: preguntas con evidencia, alta, media, sin evidencia, cobertura, nivel medio y cantidad de fuentes. |
| `datos/base_alta_confianza.sqlite` | Lo mismo en SQLite (tablas respuestas, fuentes, ciudades). |
| `xlsm/Scorecard_UNDRR_<id>_alta_confianza_EN.xlsm` y `..._salud_ES.xlsm` | 180 planillas oficiales de UNDRR: la detallada en inglés y el anexo de salud en español. Solo las preguntas con prueba tienen opción marcada. El comentario de cada pregunta dice la confianza, la evidencia y las fuentes. |
| `Scorecards_alta_confianza_xlsm.zip` | Las 180 planillas juntas (209 MB). |
| `evidencia/ac_<id>.py` | La evidencia de cada ciudad, editable a mano. |
| `evidencia/pais_<ISO3>.py`, `prov_PUNJAB.py`, `prov_GUANGDONG.py` | Evidencia nacional o provincial que heredan las ciudades: seguros, código sísmico, alertas por celular, fondos de desastre. |
| `evidencia/cdp_<org>.txt` | Resúmenes de las respuestas a CDP 2023 usadas. |
| `planes/` | Los planes oficiales leídos: texto extraído (`txt/`); los PDF originales están en los archivos del proyecto. |
| `herramientas/armar_base.py` | Rearma todo desde `evidencia/`. |

## Cómo sumar o corregir evidencia

1. Abrí `evidencia/ac_<id>.py`.
2. Agregá la fuente en `F`, con el formato `'clave': ('url', 'título', 'año')`.
3. Agregá la respuesta en `EN` (preguntas como `'9.6.2'`) o en `ES` (preguntas como `'A2.2'`), con el formato `(puntaje, 'alta' o 'media', 'texto', 'clave1,clave2', 'acción', 'responsable', plazo)`.
4. Para algo que vale para todo el país, usá `pais_<ISO3>.py`. La ciudad lo hereda salvo que tenga respuesta propia.
5. Corré `python herramientas/armar_base.py .` desde esta carpeta. Para no rehacer los .xlsm, agregá `--sin-xlsm`. Para rehacer solo algunas ciudades, agregá `--solo karachi,bombay`.

El script rechaza un puntaje que no sea una opción válida, una respuesta sin fuente o una clave de fuente que no exista.

## Cómo subir la cobertura

- **Pedir los datos al gobierno local.** Es la vía principal para las preguntas cuantitativas. La columna `accion` dice qué relevar.
- **Sumar la respuesta a CDP 2024 o 2025** cuando se publique en datos abiertos (data.cdp.net).
- **Habilitar el acceso al tablero MCR2030** desde un navegador con sesión, para leer los scorecards que hayan cargado ciudades como Karachi, Bombay o Quezón.
