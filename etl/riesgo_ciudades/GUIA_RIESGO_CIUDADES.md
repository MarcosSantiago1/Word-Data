# Riesgo de desastres en ciudades: pérdidas reales y gasto municipal

Esta carpeta junta datos para **comprobar los scorecards UNDRR** de las 16 ciudades latinoamericanas
(las 15 con gobierno local de más de 2 millones de habitantes, más CABA). Los scorecards están en
`/mnt/project-files/consultas/scorecard_undrr/`.

Hay dos preguntas:

1. ¿Las ciudades con mejor puntaje pierden menos vidas y viviendas en desastres?
2. ¿Las ciudades que puntúan mejor en finanzas (Esencial 3) gastan más en gestión del riesgo?

## Cómo se corre

Desde la carpeta `etl/`:

```
python riesgo_ciudades/extraer_riesgo_ciudades.py   # baja las fuentes y arma las tablas (unos 4 minutos)
python riesgo_ciudades/cruce_scorecard.py           # cruza con los puntajes
```

Las descargas quedan en `crudos/`. Si un archivo ya está, no se vuelve a bajar. Con `ETL_REFRESCAR=1`
(lo pone `actualizar_mensual.py`) se baja todo de nuevo.

Dominios que tienen que estar habilitados en el entorno: `www.desinventar.net`, `atlasdigital.mdr.gov.br`,
`apidatalake.tesouro.gov.br` y `www.datos.gov.co`.

## Qué tablas salen

| Archivo | Una fila por | Qué tiene |
|---|---|---|
| `perdidas_ciudad_eventos.csv` | evento | fecha, tipo de evento, muertos, heridos, desaparecidos, damnificados, afectados, viviendas destruidas y afectadas, fuente |
| `perdidas_ciudad_anual.csv` | ciudad + año + tipo + fuente | lo mismo sumado; `tipo` separa lo **socionatural** (lluvias, inundaciones, deslizamientos, sismos, sequías, incendios forestales, etc.) de lo **otro** (accidentes, incendios estructurales, epidemias, explosiones) |
| `perdidas_ciudad_resumen.csv` | ciudad | cobertura de años y tasas anuales por 100.000 habitantes, en la ventana común 2000-2013 y en todo el período desde 2000 |
| `eventos_2026_documentados.csv` | evento | terremotos de Colombia (agosto) y Venezuela (junio) y lluvias de Caracas (agosto), con cifras de prensa y fuente; todavía no están en las bases oficiales y **no entran en las tasas** |
| `gasto_riesgo_ciudad_anual.csv` | ciudad + año | gasto en gestión del riesgo, gasto total, % del total, por habitante y nota de comparabilidad |
| `scorecard_puntajes.csv` | ciudad | puntajes detallados de los scorecards (total, salud y cada Esencial en %) |
| `cruce_scorecard_perdidas.csv` | ciudad | todo junto |
| `cruce_scorecard_resultados.md` | — | correlaciones y lectura |

## Fuentes y qué cubre cada una

| Ciudades | Fuente | Años |
|---|---|---|
| Bogotá, Medellín, Cali | DesInventar (hasta 2018) + Emergencias UNGRD en datos.gov.co (2019-2025) | 2000-2025 |
| Ciudad de México | DesInventar (entidad 09) | hasta 2013 |
| Lima Metropolitana | DesInventar (provincia 1501) | hasta 2015 |
| Guayaquil, Quito | DesInventar (cantones 0901 y 1701) | hasta 2023 |
| Caracas | DesInventar (Distrito Capital = Municipio Libertador) | hasta 2015 |
| CABA | DesInventar (Capital Federal) | hasta 2015 |
| 7 ciudades de Brasil | Atlas Digital de Desastres (S2iD, versión del 6-ago-2026) | 1991-2025 |

Gasto:

- **Brasil:** SICONFI, DCA Anexo I-E, gasto liquidado en la subfunción 06.182 "Defesa Civil", 2015-2024.
- **Colombia:** CUIPO, obligaciones del programa MGA 4503 "Prevención y atención de desastres y emergencias" (incluye bomberos), 2023-2025.

## Cuidados al leer

- **Las bases no cuentan igual.** DesInventar junta eventos chicos de prensa y de organismos; el atlas de
  Brasil solo trae los desastres que el municipio registró ante el gobierno federal. Por eso las ciudades
  brasileñas tienen pocos eventos por año. Las **muertes** y las **viviendas destruidas** son lo más
  comparable entre países; la cantidad de eventos no lo es.
- **Ecuador registra mucho más desde 2012** (Quito pasa de 79 registros en 2011 a 2.616 en 2012).
  Las comparaciones de eventos en el tiempo dentro de Ecuador están afectadas por eso.
- **Caracas:** dos tercios de sus viviendas destruidas entre 2000 y 2013 vienen de registros de enero de 2000 ligados a la
  tragedia de Vargas (diciembre de 1999). DesInventar Venezuela tiene algunos años mal cargados (2102-2104)
  que se descartan.
- **La población es fija** (la de los scorecards, alrededor de 2022-2024), así que las tasas de años viejos
  quedan un poco subestimadas en ciudades que crecieron mucho.
- **Gasto:** Brasília y Salvador no son comparables (la Defensa Civil del DF se paga con el Fondo
  Constitucional federal; Codesal no usa la subfunción 06.182). En el resto de Brasil, la subfunción 06.182
  deja afuera las obras de drenaje y de contención de laderas, que están en urbanismo o vivienda. Las monedas
  son distintas: comparar solo dentro de cada país.
- **El terremoto de Cali de 2026** (unas 154 muertes) no está en las tasas: si se sumara, Cali pasaría a
  estar entre las ciudades con más muertes por habitante.

## Primeros resultados (7-nov-2026)

- **El puntaje total no se relaciona con las muertes** (Spearman cerca de 0) ni claramente con las viviendas
  destruidas (−0,24, no significativo). El scorecard mide capacidades de gestión; las pérdidas dependen
  mucho de la amenaza y de dónde vive la gente. Medellín y Quito, ciudades de montaña con barrios en laderas,
  tienen muchas muertes aun con capacidades buenas o medias.
- **En Brasil, el gasto en Defesa Civil por habitante sigue al puntaje de finanzas** (Belo Horizonte
  primero en los dos). En Colombia, Cali gasta más por habitante que Medellín y Bogotá, aunque su puntaje de
  finanzas es más bajo.
- Para que la comparación sea más justa falta **controlar por la amenaza** (lluvias extremas, pendiente,
  sismicidad): es el grupo 5 de indicadores propuesto.
