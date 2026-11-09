# Base de alta confianza del scorecard UNDRR (30 ciudades)

Noviembre de 2026. Es la versión "con pruebas" del scorecard de resiliencia ante desastres de UNDRR para las 30 ciudades de más prioridad del mundo (amenaza × brecha de capacidad) que no se habían hecho a mano. Cada ciudad tiene las 141 preguntas: 118 de la herramienta detallada y 23 del anexo de salud pública.

## La regla

- **Cada respuesta con puntaje lleva su fuente**: enlace, título y fecha del documento.
- **Si no hay prueba pública, no se puntúa.** La pregunta queda como "sin evidencia", con el puntaje vacío, y en el .xlsm queda sin ninguna opción marcada. Nada se estima ni se copia del modelo.
- **Confianza alta**: lo dice un documento oficial (de la ciudad, la provincia o el país), la respuesta de la propia ciudad a CDP-ICLEI 2023, o un hecho o declaración oficial que publican varios medios de referencia, y el puntaje sale directo de ahí.
- **Confianza media**: una sola fuente secundaria confiable (organismo internacional, prensa de referencia, estudio académico, agencia estatal sin verificación independiente) o un dato oficial que hay que interpretar para puntuar.
- Lo que la ciudad misma dice que **no tiene** (por ejemplo, "no tenemos evaluación de riesgo" ante CDP) cuenta como prueba de un puntaje bajo, con confianza alta.

## Resultado

| | |
|---|---|
| Ciudades | 30 |
| Respuestas | 4.230 (30 × 141) |
| Con evidencia | 354 (8%) |
| Confianza alta | 239 |
| Confianza media | 115 |
| Sin evidencia | 3.876 |
| Fuentes distintas citadas | 243 |

**Cobertura por ciudad** (respuestas con evidencia de 141): Karachi 52, Quezón 31, Lahore 30, Bombay 29, Rawalpindi 19, Surabaya 19, Calcuta 16, Multán 16, Daca Norte 15, Daca Sur 15, Chittagong 13, Islamabad 13, Bekasi 12, Dar es Salaam 9, Hai Phong 8, Kinsasa 8, Bandung 7, Gazipur 7, Depok 5, Jartum 4, Omdurmán 4, Brazzaville 3, Mbuji-Mayi 3, Mosul 3, Zhangzhou 3, Bagdad 2, Damasco 2, Kabul 2, Pionyang 2, Rangún 2.

### Por qué la cobertura es baja

Es lo esperable y no un defecto del método:

- **Muchas preguntas piden datos internos que ninguna ciudad publica**: días de servicio perdidos por escenario, camas de hospital en riesgo, brecha de refugios, días de combustible. Unas 50 de las 118 preguntas detalladas son de este tipo. Solo se pueden contestar con el gobierno local.
- **Las ciudades con respuesta a CDP-ICLEI 2023 tienen mucha más cobertura**: Karachi, Bombay, Quezón, Calcuta, las dos Daca, Bekasi, Kinsasa y Dar es Salaam. Esa respuesta oficial cubre planificación, evaluación de riesgo, metas, ecosistemas y salud.
- **En ciudades en guerra o cerradas casi no hay información pública verificable**: Jartum, Omdurmán, Kabul, Damasco, Bagdad, Mosul, Pionyang y Rangún. Lo poco que hay es sobre servicios colapsados (agua, energía, hospitales).
- Los sitios de UNDRR (tablero MCR2030, PreventionWeb, Sendai Monitor) bloquean las consultas automáticas, así que no se pudieron leer los scorecards que algunas ciudades hayan cargado ahí.

**Cómo leer el nivel medio**: el nivel medio de cada ciudad se calcula solo sobre las preguntas respondidas. Por eso no es comparable con el puntaje total del modelo ni entre ciudades con distinta cobertura.

## Planes oficiales leídos

Se buscaron los planes oficiales de gestión del riesgo, contingencia, calor y clima de las 30 ciudades y se leyeron completos los que se pudieron descargar. Los textos están en `planes/` (PDF original y texto extraído).

| Ciudad | Plan | Qué sumó |
|---|---|---|
| Quezón | Plan DRRM 2021-2027, volumen 1 (112 páginas) | Estimación de daños y pérdidas, sector privado, seguros, inventario de recursos, refugios, recuperación y aprendizaje (7 respuestas nuevas o corregidas) |
| Surabaya | Evaluación de riesgo de desastres 2024-2028, Perwali 119/2024 (143 páginas) | Amenazas, exposición, pérdidas, mapas y actualización; el propio documento dice que no hay plan de contingencia de inundación ni de sismo ni plan de recuperación (8 respuestas) |
| Lahore | Heatwave Management Plan 2025-2028 (88 páginas) | Escenario de calor, campaña de difusión, alerta sanitaria en tres niveles y evaluación posterior a la temporada (4 respuestas) |
| Bombay | Mumbai Climate Action Plan 2022 (240 páginas) | Exposición a anegamiento y deslizamiento; el plan de calor previsto para 2022-2023 sigue pendiente (2 respuestas) |
| Hai Phong | Plan 2025 de prevención de desastres de Cát Hải (11 páginas) | Plan de evacuación por tifón y difusión de avisos, a nivel de distrito (2 respuestas) |
| Karachi | Karachi Climate Action Plan 2025 (202 páginas) | Ya estaba citado; la lectura completa confirmó las respuestas y no sumó nuevas: es sobre todo un plan de emisiones |

**No se pudieron obtener**:

- Los planes distritales de gestión de desastres 2025 de Lahore, Rawalpindi y Multán: el sitio de la PDMA de Punyab rechaza las descargas automáticas. Si se suben los PDF a mano, se pueden leer.
- El plan de gestión de desastres de Calcuta 2020: está detrás de una suscripción paga.
- El plan distrital de la ciudad de Bombay: el enlace oficial da error 404.
- Los planes de acción climática de Daca Norte y Daca Sur (2024), el plan de contingencia multiamenaza de Chittagong, el plan climático de Dar es Salaam, los planes de Bandung, Bekasi, Depok y Zhangzhou: se anunciaron pero no están publicados en línea.
- Kinsasa no tiene plan de contingencia (lo dice la prensa local; en 2024 se creó una comisión de inundaciones).
- Kabul, Bagdad, Mosul, Damasco, Pionyang, Rangún, Jartum, Omdurmán, Mbuji-Mayi y Brazzaville: no hay planes municipales publicados.

## Archivos

| Carpeta o archivo | Qué tiene |
|---|---|
| `datos/base_alta_confianza.csv` | Una fila por ciudad y pregunta (4.230). Columnas: id, ciudad, iso3, herramienta, esencial, ref, titulo, puntaje, confianza, evidencia, fuentes, urls, origen (ciudad, provincia o país), accion, responsable, plazo, fecha_consulta. |
| `datos/fuentes_alta_confianza.csv` | Cada fuente citada: ciudad, clave, url, título, fecha del documento. |
| `datos/resumen_ciudades.csv` | Una fila por ciudad: preguntas con evidencia, alta, media, sin evidencia, cobertura, nivel medio y cantidad de fuentes. |
| `datos/base_alta_confianza.sqlite` | Lo mismo en SQLite (tablas respuestas, fuentes, ciudades). |
| `xlsm/Scorecard_UNDRR_<id>_alta_confianza_EN.xlsm` y `..._salud_ES.xlsm` | 60 planillas oficiales de UNDRR: la detallada en inglés y el anexo de salud en español. Solo las preguntas con prueba tienen opción marcada. El comentario de cada pregunta dice la confianza, la evidencia y las fuentes. |
| `Scorecards_alta_confianza_xlsm.zip` | Las 60 planillas juntas (70 MB). |
| `evidencia/ac_<id>.py` | La evidencia de cada ciudad, editable a mano. |
| `evidencia/pais_<ISO3>.py`, `prov_PUNJAB.py` | Evidencia nacional o provincial que heredan las ciudades: seguros, código sísmico, alertas por celular, fondos de desastre. |
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
