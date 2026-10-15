# CIA World Factbook: lo que suma al proyecto

El **World Factbook** era el anuario de países de la CIA: una ficha por país con geografía, población, gobierno, economía y más. La CIA **dejó de publicarlo el 4 de febrero de 2026**. Queda una copia de dominio público en GitHub, [factbook/factbook.json](https://github.com/factbook/factbook.json), con un archivo JSON por país que se actualizaba cada semana. Usamos la **última versión con datos: 22 de enero de 2026**.

```bash
cd etl/factbook
python extraer_factbook.py        # una sola vez: el Factbook ya no cambia
cd ../modelo_unificado
python construir_master.py        # lo suma a la base SQLite
```

Necesita `requests` y `pandas`. Los 261 JSON se bajan una sola vez a `crudos/json/` desde `raw.githubusercontent.com` (no hace falta habilitar dominios nuevos).

## Qué tomamos y qué no

El Factbook también trae esperanza de vida, mortalidad infantil, PIB per cápita, Gini, inflación, desempleo o gasto militar. **Esos no los usamos**: el Banco Mundial y la OMS dan esos mismos datos como series de 2000 a 2024, y el Factbook trae a lo sumo 3 años, casi siempre copiados de esas fuentes. Las membresías en organizaciones tampoco: ya las tenemos con años de ingreso y salida (COW y Wikidata).

Lo que sí tomamos es lo que **ninguna otra fuente del proyecto tenía**:

| Archivo | Tabla en la base | Una fila es | Filas |
|---|---|---|---|
| `factbook_perfil_pais.csv` | `hecho_pais_perfil_factbook` | un país: superficie, costa, elevación, clima, recursos, gobierno, sistema legal, independencia, sufragio, servicio militar, qué exporta e importa | 244 |
| `factbook_fronteras.csv` | `rel_pais_frontera` | un par de países vecinos, con los km de frontera | 646 |
| `factbook_composicion.csv` | `rel_pais_composicion` | un grupo religioso, étnico o de idioma de un país, con su % | 3.764 |
| `factbook_socios_comerciales.csv` | `rel_pais_socio_comercial` | uno de los 5 principales destinos de exportación u orígenes de importación | 2.317 |
| `factbook_entidades.csv` | (va a `pais_equivalencia`) | una de las 261 fichas del Factbook y su iso3 | 261 |

Es **una foto, no una serie**: cada dato trae su propio año entre paréntesis en el original (la religión de Argentina es de 2019, sus socios comerciales de 2023). Ese año queda en `anio_estimacion` o `anio`.

## Paso 1. Los códigos de la CIA no son ISO

La CIA usa sus propios códigos de dos letras (GEC): `au` es **Austria** (no Australia, que es `as`) y `gm` es Alemania. Para unir con el resto del proyecto los traducimos a **iso3**:

1. Wikidata guarda para cada país su código FIPS 10-4 (propiedad P901), que es el antecesor del GEC y coincide en casi todos los casos.
2. Seis casos se cargaron a mano (`GEC_A_ISO3` en el script): Kosovo (Wikidata dice XKS, el proyecto usa XKX), Países Bajos (sin dato en Wikidata), Svalbard (ISO lo junta con Jan Mayen en SJM), las islas menores de EE. UU. (UMI) y **Palestina**.
3. 17 fichas no tienen país ISO y quedan afuera (`motivo_sin_iso3` dice por qué): los 5 océanos, el mundo, la Unión Europea, islas en disputa (Paracel, Spratly), bases británicas en Chipre, y partes de territorios que ISO ya cubre (Jan Mayen, isla Wake, isla Navaza).

**Palestina son dos fichas** en el Factbook: Cisjordania (`we`) y Franja de Gaza (`gz`). Por eso todas las tablas llevan `codigo_gec` además del país: Palestina tiene dos filas en el perfil y dos listas de religiones. Si sumás o promediás por país, tenelo en cuenta.

Al revés, 8 de los 251 países y territorios del maestro no tienen ficha: los 5 departamentos de ultramar de Francia (el Factbook los incluye dentro de Francia), Åland, el Caribe Neerlandés e Islas del Canal (el Factbook tiene Jersey y Guernsey por separado). Del panel de 217 países solo falta Islas del Canal.

## Paso 2. De texto a números

El Factbook está escrito para leerse, no para calcular. Cada valor es texto:

```
"Area": {"total ": "2,780,400 sq km", "land": "2,736,690 sq km", ...}
"Religions": "Roman Catholic 62.9%, Evangelical 15.3% (Pentecostal 13%, other Evangelical 2.3%), ..., none 18.9% (2019 est.)"
"border countries": "Bolivia 942 km; Brazil 1,263 km; Chile 6,691 km; Paraguay 2,531 km; Uruguay 541 km"
```

El script hace tres cosas con ese texto:

- **Limpia el HTML** (`<br>`, `&nbsp;`) y saca el número de cada medida: `"2,780,400 sq km"` → `2780400`.
- **Corta las listas por comas, pero solo fuera de los paréntesis.** Así `Evangelical 15.3% (Pentecostal 13%, other Evangelical 2.3%)` queda como un solo grupo de 15,3 % y lo de adentro va a la columna `detalle`.
- **Traduce los nombres de países** de fronteras y socios a iso3 con los nombres del propio Factbook, los del maestro y una lista de alias (`USA`, `UK`, `UAE`, `S. Korea`, `Denmark (Greenland)`...). El script avisa si queda alguno sin traducir; hoy no queda ninguno.

## Las columnas que conviene conocer

**Perfil** (`hecho_pais_perfil_factbook`)

| Columna | Qué es | Ojo |
|---|---|---|
| `superficie_total_km2`, `_tierra_km2`, `_agua_km2` | superficie en km² | |
| `costa_km`, `fronteras_terrestres_km` | largo de costa y de fronteras terrestres | 0 = sin costa / isla |
| `n_paises_limitrofes` | cuántos vecinos terrestres | 81 países no tienen ninguno (islas) |
| `elevacion_maxima_m`, `_minima_m`, `_media_m`, `punto_mas_alto` | relieve | la media falta en 31 % |
| `tipo_gobierno` | "presidential republic", "parliamentary republic"... | texto en inglés tal cual |
| `anio_independencia` | primer año del texto de independencia | antes de 1500 es un año de fundación (Suiza 1291), no de independencia de una colonia; vacío si no tiene (Francia, Reino Unido, territorios) |
| `edad_minima_voto`, `es_voto_obligatorio` | la menor edad con la que se puede votar y si es obligatorio | Argentina y Brasil: 16 y 1 |
| `clima`, `terreno`, `recursos_naturales`, `sistema_legal`, `sufragio`, `servicio_militar`, `exportaciones_productos`, `importaciones_productos` | texto | sirve para fichas del dashboard, no para calcular |

**Composición** (`rel_pais_composicion`): `dimension` es `religion`, `etnia` o `idioma`; `orden` es la posición en la lista original; `poblacion_pct` es el %; `es_cota_superior = 1` cuando el original dice "<1%"; `es_oficial = 1` en idiomas oficiales.

**Fronteras** (`rel_pais_frontera`): una fila por cada vecino que **el país lista**. Casi siempre la relación está de los dos lados (Argentina-Chile y Chile-Argentina), con los mismos km. Si un vecino aparece en dos tramos (España con Ceuta y con Melilla), se suman.

**Socios** (`rel_pais_socio_comercial`): `flujo` es `exportacion` o `importacion`, `rango` va de 1 a 5, `participacion_pct` es el % del total.

## Ejemplo: Argentina

```sql
SELECT v.nombre_es AS vecino, f.frontera_km
FROM rel_pais_frontera f
JOIN dim_pais p ON p.pais_id = f.pais_id
JOIN dim_pais v ON v.pais_id = f.vecino_pais_id
WHERE p.iso3 = 'ARG' ORDER BY f.frontera_km DESC;
```

| vecino | frontera_km |
|---|---|
| Chile | 6.691 |
| Paraguay | 2.531 |
| Brasil | 1.263 |
| Bolivia | 942 |
| Uruguay | 541 |

Sus 5 primeros destinos de exportación (2023): Brasil 18 %, Estados Unidos 9 %, Chile 8 %, China 8 % e India 4 %. Importa sobre todo de Brasil (23 %) y China (20 %).

## Limitaciones (leer antes de concluir algo)

- **Los nombres de los grupos no están unificados entre países.** Argentina dice "Roman Catholic" y Chile "Catholic". Para comparar religiones entre países hay que agrupar a mano.
- **Los % de idiomas pueden sumar más de 100** (una persona habla varios) y muchos idiomas no traen % (61 % de las filas lo tienen). De las 535 listas con %, 29 suman menos de 90 o más de 110: casi siempre son idiomas, y algunas son errores del original (Andorra dice "89.5" sin el signo %, y la República Democrática del Congo dice "93/1%").
- **Algunas fronteras están de un solo lado**: Groenlandia y Canadá (isla Hans), Cuba con la base de Guantánamo (queda como frontera con EE. UU.), Sahara Occidental con sus vecinos, y Brasil y Surinam con la Guayana Francesa (que no tiene ficha propia).
- **Los textos están en inglés.** No se tradujeron para no perder precisión.
- **No se actualiza más.** El script baja siempre la misma versión (fijada por el commit), así que no hace falta en la actualización mensual.
