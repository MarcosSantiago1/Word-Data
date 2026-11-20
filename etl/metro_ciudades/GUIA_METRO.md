# Kilómetros de subte / metro por ciudad

Script: `extraer_metro.py` (paso `metro_ciudades` de la actualización mensual, después de los k-means de ciudades y antes del modelo unificado).

## Qué mide

`metro_km` (y `metro_m`, lo mismo en metros) es el **largo de la red de metro** que sirve a cada ciudad: subte, metro o "tránsito rápido" de alta capacidad, separado del tránsito, sea subterráneo, a nivel o elevado. No incluye tranvías, trenes suburbanos ni la mayoría de los trenes ligeros (por eso Buenos Aires da 56,7 km: líneas A a H, sin Premetro ni trenes metropolitanos).

Es el largo de la red (cada tramo una vez), no la suma de vías ni de recorridos de ida y vuelta.

## De dónde sale

1. **Wikipedia, [List of metro systems](https://en.wikipedia.org/wiki/List_of_metro_systems)**: 234 sistemas en 65 países (consulta del 20-11-2026, revisión 1386705868). Da ciudad, país, apertura, última ampliación, estaciones, largo y pasajeros por año. Es la referencia más pareja a nivel mundial y se actualiza seguido; cada fila cita su fuente oficial.
2. **Wikidata**: código y coordenadas de la ciudad de cada sistema, para ubicarlo.

Se probó primero Wikidata sola: tiene el largo cargado en solo un tercio de los metros y muchos desactualizados (Delhi 277 km contra 395 reales), por eso el largo viene de Wikipedia.

Necesita `en.wikipedia.org` y `query.wikidata.org` habilitados en la red del entorno (los dos lo están desde el 20-11-2026).

## Cómo se une a las 375 ciudades

Cada sistema se asigna a una ciudad de `riesgo_ciudades_mundo/datos/ciudades_mundo.csv`:

1. **A mano** (`ASIGNACION` en el script) cuando hace falta. Regla: un sistema cuenta para una ciudad si tiene estaciones dentro de su gobierno local. Si cruza varias ciudades de la lista cuenta completo en cada una (Daca Norte y Sur, El Cairo y Guiza, Yakarta con Bekasi y Depok). Ejemplos de exclusión: Noida y Gurugram no son Delhi; Navi Mumbai no es Gran Mumbai.
2. **Código Wikidata** de la ciudad, si coincide.
3. **Ciudad más cercana del mismo país** a menos de 25 km.

Las 234 asignaciones se revisaron una por una el 20-11-2026. Si la tabla de Wikipedia suma un sistema nuevo, entra solo por los pasos 2 y 3. La columna `asignacion` de `sistemas_metro_mundo.csv` dice cómo se unió cada uno.

Una ciudad sin metro queda con `metro_km = 0` y `tiene_metro = 0` (249 de las 375, por ejemplo Bogotá, cuyo metro está en obra).

## Archivos (`datos/`)

| Archivo | Qué tiene |
|---|---|
| `metro_ciudades.csv` | Las 375 ciudades: `tiene_metro`, `metro_km`, `metro_m`, sistemas, estaciones, apertura, última ampliación, pasajeros, `metro_km_por_millon_hab`, `pasajeros_por_hab` |
| `metro_paises.csv` | Por país: km de todos sus metros (estén o no en una de las 375), sistemas, ciudades con metro, km por millón de habitantes |
| `pais_metro_anual.csv` | Lo mismo por país y año: entra al master como `hecho_pais_metro` y de ahí a la base absoluta y a las bases regionales |
| `metro_subdivision_anual.csv` | Latinoamérica por provincia/estado (ISO 3166-2): 21 redes en 21 subdivisiones (CABA = AR-C). Entra a la base absoluta y a las bases regionales como `hecho_subdivision_metro` |
| `sistemas_metro_mundo.csv` | Los 234 sistemas con su ciudad asignada, coordenadas y códigos Wikidata |
| `historial_metro_sistemas.csv` | Foto por año de cada sistema |
| `diccionario_metro.csv` | Qué es cada columna |

## La serie por año

Wikipedia da solo el largo **actual**. Cada corrida mensual guarda el último dato del año en `historial_metro_sistemas.csv`, así que la serie anual se arma sola a partir de 2026 (2026, 2027, …). Los años anteriores no se reconstruyen.

## Algunos resultados (noviembre de 2026)

- Mundo: 24.676 km en 234 sistemas. En las 375 ciudades, 126 tienen metro y suman 20.708 km.
- Más largos: Pekín 909 km, Shanghái 890, Cantón 780, Chengdu 716, Nankín 658. Fuera de China: Moscú 542, Nueva York 444, Londres 436.
- Latinoamérica: Ciudad de México 201 km, São Paulo 117, Caracas 67, Río 58, **CABA 56,7 km (56.700 m, 78 estaciones, desde 1913)**, Brasília 42, Lima 39. Santiago de Chile tiene 149 km, pero la comuna de Santiago no está entre las ciudades de +2 millones: aparece en la base por provincia (Región Metropolitana).
- Por habitante: París 117 km por millón de habitantes, Madrid 89; CABA 18, Ciudad de México 22.

## Cuidado al usarlo

- El largo es el del **sistema completo**, aunque una parte salga del municipio (el metro de Ciudad de México entra al Estado de México). `metro_km_por_millon_hab` divide por la población del gobierno local, así que en ciudades chicas dentro de áreas metropolitanas grandes (París, 2,1 millones) da alto.
- La definición de "metro" es la de Wikipedia: algunos trenes que localmente se llaman metro quedan afuera por ser suburbanos o ligeros (el Metro de Valparaíso no está en la lista), y otros ligeros con vía exclusiva sí entran (SITEUR de Guadalajara).
- Pasajeros: cada sistema informa un año distinto (`anio_pasajeros`).
