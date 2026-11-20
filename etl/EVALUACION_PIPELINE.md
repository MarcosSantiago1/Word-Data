# Evaluación de la pipeline (6 de noviembre de 2026)

Revisé `actualizar_mensual.py`, `chequear_fuentes.py`, los pasos 1 a 3, los resúmenes y logs de las corridas del 14 y 16 de octubre, el panel `datos_procesados/paises_anual.csv`, la tarea programada y el repositorio de GitHub.

**Veredicto corto:** la pipeline es sólida en lo más difícil. Nunca pisa datos buenos, se puede volver atrás y deja registro de todo. Los puntos flojos son otros cuatro:

1. Los datos más recientes quedan afuera porque el año final está fijo en 2024.
2. Los controles comparan cada versión solo contra la anterior, sin chequear que los valores tengan sentido.
3. Algunas fuentes no se vigilan.
4. GitHub quedó desactualizado respecto de los datos.

## Lo que está bien

| Aspecto | Por qué está bien |
|---|---|
| Copia de trabajo ("staging") | Todo corre en una carpeta temporal; lo publicado no se toca hasta el final. |
| Vuelta atrás por paso | Si un paso falla, ese paso y los que escriben la misma carpeta vuelven a la versión anterior, y el resto sigue. |
| Controles antes de publicar | Rechaza si desaparece un archivo, se pierden columnas, caen más de 5 % las filas o una columna pierde más de 20 % de sus datos. |
| Respaldo | Guarda lo reemplazado en `etl/historial/<fecha>/` (últimas 3 corridas). |
| Registro | Resumen en Markdown, `historial.csv` por paso y log de cada script. |
| Fuentes caídas | Varias descargas usan la copia anterior si la fuente no responde (por ejemplo, los timeouts y 429 de Wikidata del 16-10). |
| Chequeo de fuentes | `chequear_fuentes.py` prueba 40 fuentes y marca las posiblemente discontinuadas. El 16-10 respondieron todas. |
| Tarea programada | Activa; la próxima corrida es el 16-11 a las 06:46 (hora Argentina). La del 16-10 corrió bien: 10 de 10 pasos actualizados. |
| Claves | El panel no tiene duplicados `iso3 + anio` (5.425 filas, 217 países). El paso 3 lo verifica con `assert`. |

## Lo que conviene corregir, por prioridad

### Prioridad 1: afecta los datos que ves hoy

1. **El año final está fijo en 2024** (`ANIO_FIN = 2024` en el paso 1).
   - Las fuentes ya publicaron 2025: el World Happiness Report 2026 (datos de 2025) y V-Dem v16 (hasta 2025).
   - Como el panel solo tiene filas hasta 2024, esos datos nunca entran.
   - Propuesta: `ANIO_FIN = datetime.now().year - 1`.
   - Hay que revisar que los controles no rechacen la corrida por el cambio de tamaño. Las filas suben, así que no deberían.
2. **La tasa de suicidio del panel era la cruda y llegaba solo hasta 2021.**
   - `SH.STA.SUIC.P5` del Banco Mundial es "Crude suicide rate (not age-adjusted)".
   - Ya está resuelto (ver la sección "Hecho hoy").
3. **Los controles no miran los valores, solo la cantidad.**
   - Hoy un cambio de unidad o de escala pasa sin aviso si la cantidad de filas no cambia. Ejemplos: los WGI pasaron a una escala 0-100 en diciembre de 2025, o un PIB que pase de dólares a miles de dólares.
   - Propuesta: sumar rangos plausibles por variable a `controlar()`. Por ejemplo, porcentajes entre 0 y 100, tasas mayores o iguales a 0 y esperanza de vida entre 30 y 90.
   - También marcar si la mediana de una columna cambia más de 50 % de un mes a otro.

### Prioridad 2: robustez

4. **Una sola fuente caída frena 12 tablas.**
   - En `fuentes_nuevas/` e `indicadores_sociales_digitales/`, si falla una descarga el script se corta. Entonces todo el paso vuelve a la versión anterior, aunque las otras fuentes hayan respondido bien.
   - Propuesta: el mismo patrón que ya usan Argentina y Latinoamérica: usar la copia anterior de ese archivo e imprimir `AVISO_FUENTE`.
5. **El chequeo de fuentes no cubre todas las fuentes.**
   - Faltan las de `fuentes_nuevas/` e `indicadores_sociales_digitales/`: OCDE SDMX, FMI, BID, CEPALSTAT, UN Comtrade, Our World in Data, ENACOM, BCRP, Olympedia y la OMS de salud crónica.
   - El "0 % discontinuadas" del 16-10 no las incluye.
6. **Las versiones de librerías no están fijas** (`pandas>=2.0`).
   - El entorno ya instala pandas 3.0.5, que cambió el manejo de copias y de texto.
   - Hoy los scripts que probé corren bien, pero una versión nueva puede romper la corrida sin que cambie nada del proyecto.
   - Propuesta: fijar versiones exactas (`pandas==3.0.5`, etc.) y actualizarlas a propósito.
7. **API de la OMS.**
   - La OMS anunció que reemplaza la API OData (`ghoapi.azureedge.net`). Hoy sigue respondiendo y se actualizó el 15-10-2026.
   - Ya quedó vigilada en el chequeo de fuentes. Si da 404, hay que cambiar `URL_BASE` en dos scripts: `suicidio_estandarizado/` y `fuentes_nuevas/`.

### Prioridad 3: orden y publicación

8. **GitHub está atrasado.**
   - La rama `main` no tiene la base absoluta ni las regresiones: los PR #1 y #2 siguen abiertos sin unir.
   - La actualización mensual no sube nada a GitHub, así que el notebook de Colab lee datos viejos.
   - Propuesta: unir #1 y #2, y que la rutina mensual abra un PR con los CSV que cambiaron.
9. **Las variables nuevas no llegan a todas las bases.**
   - El suicidio estandarizado ya está en `paises_anual.csv`, pero todavía no en el master SQLite, las bases regionales ni la base absoluta.
   - Lo mismo pasaría con cualquier tabla nueva que no se registre en `construir_master.py`.
10. **No hay pruebas automáticas.**
    - Un archivo `pruebas_datos.py` con 15 o 20 verificaciones (claves únicas, rangos, países esperados, años esperados), corrido al final de cada paso, atraparía la mayoría de los errores silenciosos.
11. **Carpeta `codigo_python/` duplicada.**
    - Es una copia de los scripts de `etl/` y se desincroniza si alguien se olvida de correr `actualizar_copia.py`.
    - Hoy está sincronizada (la corrí después de los cambios).
    - Si es solo para leer el código, conviene que la genere la rutina mensual.

## Riesgos de método (no son errores de código)

- **PPA (paridad de poder adquisitivo).** `pib_pc_ppp` está en dólares internacionales constantes de 2021. No conviene mezclarlo con datos viejos o exportados antes de mayo de 2024, que estaban en base 2017.
- **WGI.** El script ya baja los códigos nuevos (`GOV_WGI_*`, con versión 0-100), así que la serie es coherente consigo misma. No conviene compararla con planillas viejas de WGI.
- **Factbook.** Quedó congelado (la CIA lo discontinuó el 4-2-2026). Está bien que no se chequee.
- **Datos modelados.** El suicidio de la OMS y la mortalidad materna son estimaciones de modelos, no conteos. La OMS calcula que solo unos 86 de 183 países tienen registros de buena calidad.

## Hecho hoy

- **Nuevo** `suicidio_estandarizado/extraer_suicidio_estandarizado.py`. Baja de la OMS la tasa estandarizada por edad (MH_12) y la cruda (SDGSUICIDE): 185 países, 2000-2023, por sexo y con intervalo de incertidumbre. Arma:
  - `suicidio_estandarizado_largo.csv`
  - `suicidio_estandarizado_pais_anual.csv`
  - `tabla_suicidio_2023.csv` / `.xlsx`, el ranking del último año
- **Paso 3** suma 6 columnas al panel: `suicidio_estandarizado_{total,hombres,mujeres}_x100k` y `suicidio_crudo_oms_{...}_x100k`.
- **Actualización mensual**: tiene un paso nuevo, "suicidio", antes del paso 3.
- **Chequeo de fuentes**: suma la OMS (40 fuentes en total).
