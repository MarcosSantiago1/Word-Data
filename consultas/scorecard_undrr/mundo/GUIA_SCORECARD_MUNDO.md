# Scorecard UNDRR para las ciudades del mundo de más de 2 millones

Hay dos archivos de la UNDRR (Making Cities Resilient 2030) para cada gobierno local de más de 2 millones de habitantes. Los dos están completos, con puntaje, comentario, acción, responsable y plazo en cada pregunta:

- `Scorecard_UNDRR_<id>_detallado_EN.xlsm` es la herramienta detallada, con 118 preguntas sobre los 10 Esenciales.
- `Scorecard_UNDRR_<id>_salud_publica_ES.xlsm` es el anexo de salud pública, con 23 preguntas.

Son 375 ciudades en 66 países, 234 de ellas en China. Con dos excepciones, las 16 ciudades latinoamericanas ya hechas a mano (CABA y las 15 de `../detalle/`) se dejan como estaban:

- en `xlsm/` están las 359 restantes (718 archivos);
- en el resumen, esas 16 entran con su puntaje a mano.

## Qué ciudades entran

Entra el gobierno local, no la aglomeración. Es el mismo criterio que en Latinoamérica.

- **Fuera de China** hay unas 125 ciudades, tomadas de Wikidata y revisadas a mano. La lista está en `herramientas/lista_ciudades.py` e incluye municipio, distrito metropolitano o ciudad-estado, autoridad, población, año y fuente.
- **En China** entran las ciudades de nivel prefectura (Wikidata Q748149) de más de 2 millones, más los 4 municipios centrales y Harbin. Allí el gobierno local abarca la prefectura entera, y por eso hay tantas.
- La población es la del gobierno local según su censo o estimación oficial.

## Cómo se completó cada respuesta

Un modelo de reglas completó las 141 respuestas de cada ciudad. No hubo una búsqueda web por ciudad como en las 16 hechas a mano. El modelo combina datos reales con perfiles:

1. **Datos de la ciudad**
   - GHSL Urban Centre Database R2024A (Comisión Europea, JRC):
     - eventos de inundación, ciclón y deslizamiento (2005, 2010 y 2015);
     - superficie inundable fluvial y costera;
     - población en zona sísmica MMI ≥ 6;
     - días de calor (UTCI > 32);
     - infraestructura crítica;
     - IDH subnacional;
     - cuenca.
   - USGS ComCat:
     - sismos M6+ a menos de 150 km desde 1900;
     - sismos M5+ a menos de 100 km desde 1975;
     - el mayor sismo registrado.
   - Cada ciudad se une a su centro urbano GHSL, con este orden:
     1. el centro que contiene el punto, si tiene 1 millón de habitantes o más;
     2. si no, el centro más poblado del mismo país a 25 km o menos;
     3. si no, el centro más cercano a 50 km o menos.
2. **Datos del país**, tomados del panel del proyecto (`etl/datos_procesados/paises_anual.csv`):
   - efectividad del gobierno y estado de derecho;
   - PIB per cápita;
   - camas y médicos;
   - sociedad civil;
   - Gini;
   - internet.
3. **Perfil del país** (`herramientas/paises.py`): ley de gestión del riesgo, agencia nacional, autonomía local, fondo de emergencias, código sísmico, alerta temprana, seguros, sistema de salud y trayectoria.
4. **Perfil de la ciudad**:
   - Fuera de China (`perfiles_ciudad.py`): oficina de riesgo, plan, redes (MCR2030, C40, 100RC), desastres notables, informalidad, metro, puerto, sistema de alerta y centro de operaciones.
   - En China (`perfiles_china.py`): el perfil común de la prefectura, más metro, puerto, «ciudad esponja», redes y desastres notables (Zhengzhou 2021, Tianjin 2015, Wenchuan 2008 y otros).

### Fórmula del puntaje

**Capacidad.** Para cada Esencial (E01 a E10, más salud) se calcula un índice de capacidad entre 0 y 1. Es una combinación ponderada de los factores del país y de la ciudad que figuran en `capacidades()` de `generar_mundo.py`. Al índice se le aplican tres ajustes:

- una bonificación por rango (capital provincial o ciudad de rango alto);
- una bonificación por tamaño;
- una penalización de 0,15 en países en guerra o colapso estatal.

**Puntaje de cada pregunta.**

`puntaje = ancla + 4,5 × (capacidad de la ciudad − capacidad media de las 16)`

- El ancla es el promedio de esa pregunta en las 16 ciudades hechas a mano.
- El resultado se redondea y se recorta a la escala de 0 a 5.
- Después se aplican reglas propias de cada pregunta. Por ejemplo:
  - sin metro ni puerto, ciertas preguntas no aplican;
  - un código sísmico vigente sube E04;
  - un desastre notable reciente sube la experiencia de recuperación.
- Por último se aplican correcciones del perfil (`ov`).

**Texto de cada respuesta.** Tiene tres partes:

- un hecho neutro con datos de la ciudad;
- «Nivel estimado s de 5», con la descripción de la escala;
- una nota `[Modelo: …]`, que dice qué capacidad se usó y cómo se compara con las 16.

La confianza figura casi siempre como **baja**. Solo es media cuando el dato viene directamente de una fuente (GHSL o USGS).

### Validación

Se corrió el modelo sobre las 16 ciudades hechas a mano y se comparó con su puntaje real:

- la correlación del total (sobre 590) es de **0,61**;
- el error medio absoluto es de **37 puntos**.

El modelo ordena razonablemente bien a las ciudades de un mismo país. Entre países distintos tiende a comprimir las diferencias. Ver la hoja «Validación» del resumen.

## Archivos

| Ruta | Qué es |
|---|---|
| `Resumen_scorecards_UNDRR_mundo.xlsx` | Hojas Ranking, Por país, Amenaza vs capacidad, Validación y Método. Es la foto que acompaña a los .xlsm (08-11-2026); la actualización mensual deja la versión al día en `etl/riesgo_ciudades_mundo/` |
| `xlsm/` | Los 718 archivos .xlsm (359 ciudades × 2) |
| `Scorecards_UNDRR_mundo_<región>.zip` | Los mismos .xlsm empaquetados por región, para descargar |
| `etl/riesgo_ciudades_mundo/datos/ciudades_mundo.csv` | Lista de ciudades: gobierno, autoridad, población, fuente y coordenadas |
| `etl/riesgo_ciudades_mundo/datos/ghsl_ciudades.csv` | Variables GHSL de cada ciudad y cómo se unió (`modo_union`, `dist_uc_km`) |
| `etl/riesgo_ciudades_mundo/datos/sismos_ciudades.csv` | Historial sísmico USGS |
| `etl/riesgo_ciudades_mundo/datos/indicadores_pais.csv` | Último dato de cada indicador del país |
| `etl/riesgo_ciudades_mundo/datos/puntajes_mundo.csv` | Puntaje total, salud, por Esencial y capacidades del modelo |
| `etl/riesgo_ciudades_mundo/datos/amenaza_capacidad_mundo.csv` | Índice de amenaza (0 a 1), puntaje y prioridad = amenaza × (1 − puntaje/590) |
| `herramientas/` | Código del modelo (ver abajo) |

Los datos crudos (zips GHSL, Wikidata y caché USGS) están en `etl/riesgo_ciudades_mundo/crudos/`.

## Cómo se rehace

Desde `etl/`:

```
python riesgo_ciudades_mundo/actualizar_mundo.py
```

Ese comando hace siete pasos, en este orden:

1. Baja GHSL.
2. Arma la lista.
3. Une las ciudades con GHSL.
4. Actualiza los sismos USGS.
5. Actualiza los indicadores del país.
6. Recalcula los puntajes (`--sin-xlsm`).
7. Rehace el resumen.

Lo corre `actualizar_mensual.py` cada mes. No rehace los .xlsm, que tardan unos 15 minutos y pesan cerca de 1 GB. Para rehacerlos:

```
python ../consultas/scorecard_undrr/mundo/herramientas/generar_mundo.py ../consultas/scorecard_undrr/mundo --datos riesgo_ciudades_mundo/datos
python ../consultas/scorecard_undrr/mundo/herramientas/generar_mundo.py ../consultas/scorecard_undrr/mundo --datos riesgo_ciudades_mundo/datos --solo tokio,kinsasa
```

El primero rehace todas las ciudades. El segundo rehace solo las que se nombran, separadas por comas.

Para los .xlsm hacen falta las planillas originales de la UNDRR que subió la usuaria (`uploads/hearth/`). Hace falta tener instalados `pyogrio`, `shapely` y `pyproj`. Los dominios jeodpp.jrc.ec.europa.eu y earthquake.usgs.gov tienen que estar habilitados.

## Límites

- **Es una estimación.** No es la autoevaluación de cada ciudad. Los textos dicen «Nivel estimado» y la nota del modelo muestra de dónde sale cada puntaje. Antes de citar una ciudad, conviene revisarla a mano como se hizo con las 16, y empezar por las de mayor prioridad.
- **Mucho del puntaje viene del país.** Dentro de un mismo país, las ciudades se diferencian por cuatro cosas: IDH subnacional, infraestructura, rango, y perfil y desastres propios. En China, 234 prefecturas comparten casi todo el perfil, y sus puntajes caen entre 310 y 410.
- **La amenaza viene de datos globales** con resolución de 1 km y de eventos registrados. No incluye estudios locales de riesgo.
- **La lista de ciudades** depende de cómo define cada país a su gobierno local. Una aglomeración grande puede quedar fuera si está dividida en municipios de menos de 2 millones. Por ejemplo, de Manila solo entra Ciudad Quezón, y de la región del Ruhr ninguna ciudad. París entra solo como comuna (2,1 millones), no como Gran París.
