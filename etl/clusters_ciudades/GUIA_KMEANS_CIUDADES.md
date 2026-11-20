# K-means de las 375 ciudades de más de 2 millones

Este paso agrupa las ciudades del scorecard UNDRR según los indicadores de los cuatro enfoques (`enfoques_urbanos`). Corre dos especificaciones, porque responden preguntas distintas.

| Especificación | Indicadores | Pregunta | Resultado hoy |
| --- | --- | --- | --- |
| `completo` | 31 (los 33 menos los dos con más del 40% de faltantes) | ¿Qué grandes perfiles de riesgo hay en el mundo? | 3 grupos, silueta 0,23, estabilidad 0,91 |
| `urbano` | 17 que cambian entre ciudades del mismo país | ¿Qué tipos de ciudad hay, sin importar el país? | 4 grupos, silueta 0,19, estabilidad 0,77 |

## Cómo se corre

```
cd etl
python clusters_ciudades/kmeans_ciudades.py
```

Necesita `scikit-learn` (ya está en `requirements.txt`) y que antes haya corrido `enfoques_urbanos/construir_enfoques.py`. Va en `actualizar_mensual.py` como paso `clusters_ciudades`, justo después de `enfoques_urbanos`. Tarda unos 20 segundos.

Para forzar una cantidad de grupos: `KMEANS_K=5 python clusters_ciudades/kmeans_ciudades.py`. Se aplica a las dos especificaciones.

## Método

1. **Faltantes.** Se descarta un indicador que falta en más del 40% de las ciudades: muertes por PM2,5 y vivienda baja en zona costera baja. El resto se completa con la mediana del país y, si el país no tiene, con la de la región.
2. **Escala.** Cada indicador se recorta en los percentiles 2,5 y 97,5 (salvo los binarios), se pasa a z y se multiplica por su sentido. Más alto siempre es más crítico. k-means usa distancias, así que sin este paso un indicador con valores extremos manda sobre los otros.
3. **Peso (completo).** Cada indicador se divide por la raíz de la cantidad de indicadores de su enfoque, así que los cuatro enfoques pesan lo mismo. Sin esto, la gobernanza (8 indicadores casi iguales entre sí) dominaría.
4. **Componentes (urbano).** Los 17 indicadores urbanos casi no se correlacionan entre sí: el primer componente explica solo el 17% de la varianza. Agrupar sobre los 17 sueltos da grupos inestables (estabilidad 0,59). Por eso primero se resumen en componentes principales, con tantos como superan al azar según el análisis paralelo de Horn (hoy, 6), y se agrupa sobre esos.
5. **Cuántos grupos.** Se prueba k de 2 a 10 con 50 arranques cada uno. Para cada k se guardan:
   - la inercia (para el gráfico del codo);
   - la silueta (de −1 a 1; más alta, grupos más separados);
   - los índices de Calinski-Harabasz (más alto, mejor) y de Davies-Bouldin (más bajo, mejor);
   - la estabilidad: 100 remuestreos bootstrap y el índice de Rand ajustado entre el agrupamiento de cada remuestreo y el de la muestra completa (1 = idéntico, 0 = al azar).
6. **Regla de elección.** El k con mejor silueta entre los que tienen al menos 3 grupos y estabilidad media de 0,75 o más.
7. **Nombres.** Los grupos se numeran de menor a mayor criticidad media. En `completo` se nombran por el enfoque en que más se apartan del promedio. En `urbano`, por sus dos indicadores más extremos de familias distintas. Los nombres se arman solos en cada corrida, así que pueden cambiar si cambian los datos.

## Qué escribe (`datos/`)

En `datos/completo/` y `datos/urbano/`:

| Archivo | Contenido |
| --- | --- |
| `seleccion_k.csv` | Métricas de cada k (inercia, silueta, CH, DB, estabilidad, tamaño del grupo más chico y más grande) y cuál se eligió |
| `asignacion_ciudades.csv` | Grupo de cada ciudad, su silueta propia, distancia al centro, z de cada enfoque, coordenadas en los dos primeros componentes (`pc1`, `pc2`) para dibujar |
| `perfil_grupos.csv` | Por grupo: ciudades, población, z de cada enfoque, mediana de precariedad habitacional, amenaza y puntaje del scorecard, las 6 ciudades más típicas y las regiones principales |
| `perfil_indicadores.csv` | Promedio z de cada indicador en cada grupo, con su peso |
| `region_por_grupo.csv` | Ciudades de cada región en cada grupo |
| `comparacion_tipologia_enfoques.csv` | Cruce con la tipología de 5 tipos de `enfoques_urbanos` |
| `componentes_principales.csv` | Varianza explicada y cargas de los dos primeros componentes |

En `datos/`: `resumen_especificaciones.csv` (una fila por especificación) e `indicadores_usados.csv` (faltantes, parte de la varianza dentro del país y en qué especificación entra cada indicador).

## Resultados de hoy

**Completo (3 grupos).** Repite las grandes regiones del mundo (índice de Rand ajustado con la región 0,69):

- Baja criticidad (26): América del Norte, Europa occidental, Japón, Corea del Sur, Singapur, Hong Kong y las ciudades del Golfo; puntaje mediano del scorecard 80.
- Perfil intermedio (245): casi todas las ciudades chinas.
- Alta vulnerabilidad (104): África, Asia meridional, Oriente Medio y las 16 latinoamericanas; puntaje mediano 44. Es un grupo heterogéneo (silueta 0,04).

**Urbano (4 grupos).** Corta a través de las regiones (índice de Rand ajustado con la región: 0,0):

1. Más ingreso y más acceso a hospitales (136): grandes metrópolis consolidadas, entre ellas Shanghái, Pekín, Cantón y las 16 latinoamericanas.
2. Poca infraestructura y dentro de los límites ambientales (108): ciudades de menos ingreso, más bajas y más hacinadas, con poca huella ambiental (ciudades chinas del interior, Kinsasa).
3. Construcción hacia lo inundable y límites ambientales superados (42): las que más crecieron hacia la zona inundable (Ciudad Ho Chi Minh, Bangkok, Hanói, El Cairo, Lahore, Suzhou y la costa de Guangdong y Fujian). Tienen la amenaza más alta (mediana 0,63).
4. Ciudad extendida y mucho CO2 por habitante (89): mucha superficie construida y espacio residencial por habitante, muchas emisiones (74 ciudades chinas, sobre todo del norte, más Sudáfrica y tres de Estados Unidos).

Los cuatro grupos urbanos tienen casi el mismo puntaje mediano del scorecard (54-55): el scorecard no distingue a las ciudades que crecen hacia lo inundable de las otras.

## Cuidado al interpretar

- Una silueta de 0,19-0,23 indica una estructura débil: los grupos existen, pero con bordes difusos y muchas ciudades en el medio. Conviene leerlos como tipos ideales, no como clases naturales. La silueta de cada ciudad (`silueta_ciudad`) dice cuán bien encaja.
- China aporta 234 de las 375 ciudades, así que pesa mucho en cómo se forman los grupos.
- En `completo`, los grupos salen sobre todo de indicadores de país; no sirve para comparar ciudades del mismo país.
- k-means supone grupos de forma más o menos esférica y de tamaño parecido. Si se quiere probar otra forma, los siguientes pasos naturales son clustering jerárquico (Ward) o modelos de mezcla gaussiana sobre los mismos componentes.
