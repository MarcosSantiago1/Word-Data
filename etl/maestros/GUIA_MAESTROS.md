# Tablas maestras: países y provincias

Una **tabla maestra** es la lista "oficial" de entidades del proyecto: cada país (o cada provincia) aparece una sola vez, con sus códigos y nombres. Sirve para tres cosas:

1. **Unir** tablas que vienen de fuentes distintas usando el mismo código.
2. **Traducir** códigos a nombres legibles en el dashboard ("ARG" → "Argentina").
3. **Filtrar o agrupar** (por región, por nivel de ingreso, por tipo de subdivisión).

```bash
cd etl/maestros
python crear_maestros.py              # usa los crudos ya bajados
python crear_maestros.py --descargar  # vuelve a bajar todo
```

Necesita `requests`, `pandas` y `pycountry`.

## Las dos tablas

| Archivo | Una fila es | Filas | Clave |
|---|---|---|---|
| `paises_maestro.csv` | un país o territorio | 251 (217 del panel + 34 territorios con código ISO) | `iso3` |
| `subdivisiones_maestro.csv` | una subdivisión de primer nivel (provincia, estado, región, departamento…) | 3.590, de 200 países | `subdivision_iso` |

Se relacionan por `iso3`: un país tiene muchas subdivisiones (relación uno a muchos).

### paises_maestro.csv

| Columna | Qué es |
|---|---|
| `iso3`, `iso2`, `iso_numerico` | códigos ISO 3166-1 (alfa-3, alfa-2 y numérico). Kosovo (XKX) e Islas del Canal (CHI) son códigos del Banco Mundial, no de ISO |
| `nombre_es` | nombre corto en español (Wikidata, con algunas correcciones a mano: "China", "Taiwán", "Esuatini") |
| `nombre_es_banco_mundial` | nombre en español como lo escribe el Banco Mundial ("Corea, República de") |
| `nombre_en` | mismo texto que la columna `pais` del panel |
| `nombre_oficial_en` | nombre oficial largo ("Argentine Republic") |
| `region_bm`, `region_bm_es` | región del Banco Mundial (la de `region_bm` es idéntica a la del panel) |
| `nivel_ingreso_bm`, `nivel_ingreso_bm_es` | grupo de ingreso del Banco Mundial (clasificación actual, no la de cada año) |
| `capital`, `latitud_capital`, `longitud_capital` | capital y sus coordenadas, según el Banco Mundial |
| `en_panel` | 1 si el país está en `datos_procesados/paises_anual.csv` |
| `tiene_codigo_iso` | 0 para Kosovo e Islas del Canal |
| `n_subdivisiones`, `tipo_subdivision_principal` | cuántas subdivisiones de primer nivel tiene y de qué tipo son en su mayoría |

### subdivisiones_maestro.csv

| Columna | Qué es |
|---|---|
| `subdivision_iso` | código ISO 3166-2 (`AR-X` = Córdoba, `US-CA` = California, `ES-MD` = Comunidad de Madrid) |
| `iso2`, `iso3` | país al que pertenece |
| `nombre` | nombre corto y limpio. **En Argentina es el mismo que usa `etl/argentina_provincias/`** ("Ciudad de Buenos Aires", "Tierra del Fuego") |
| `nombre_iso` | nombre oficial tal como lo publica ISO, en el idioma local ("Bayern", "Tōkyō") |
| `nombre_es`, `nombre_en` | etiquetas de Wikidata ("Provincia de Córdoba", "Baviera") |
| `tipo_iso`, `tipo_es` | qué es: provincia, estado, región, departamento, condado… (95 tipos distintos en el mundo) |
| `tambien_pais_iso3` | si ISO también la lista como país aparte (ver "Cuidado al sumar") |
| `latitud`, `longitud` | punto de referencia de Wikidata (sirve para un mapa de burbujas) |
| `wikidata_id` | identificador en Wikidata, por si hace falta buscar más datos |

## Qué es "primer nivel"

ISO 3166-2 publica las divisiones de cada país en uno o dos niveles. Nos quedamos con las que **no dependen de otra**:

- **Argentina**: 23 provincias + la Ciudad de Buenos Aires = 24.
- **Brasil**: 26 estados + Distrito Federal = 27.
- **Estados Unidos**: 50 estados + Distrito de Columbia + 6 áreas de ultramar (Puerto Rico, Guam…) = 57.
- **España**: 17 comunidades autónomas + Ceuta y Melilla = 19. Las 50 provincias españolas dependen de las comunidades, así que **no** están.
- **Francia**: 13 regiones metropolitanas + territorios de ultramar. Los departamentos quedan afuera.
- **Reino Unido**: Inglaterra, Escocia, Gales e Irlanda del Norte.

En algunos países el primer nivel de ISO son muchas unidades chicas (Eslovenia: 212 municipios) o regiones geográficas sin gobierno propio (Uganda: 4 regiones). Es la convención de ISO, no un error.

**22 países del panel no tienen subdivisiones en ISO**: territorios chicos (Aruba, Bermudas, Hong Kong, Macao, Puerto Rico…), Kosovo e Islas del Canal.

## Cuidado al sumar

Algunas subdivisiones también son "países" en el panel. Puerto Rico es `US-PR` dentro de Estados Unidos **y** `PRI` en el panel; Hong Kong es `CN-HK` y `HKG`. Si sumás población por subdivisión y además por país, la contás dos veces. La columna `tambien_pais_iso3` marca estos 30 casos para poder filtrarlos:

```python
sub_sin_duplicar = sub[sub["tambien_pais_iso3"].isna()]
```

## Cuidado al leer: Namibia se llama "NA"

El código de Namibia es `NA`, y pandas lo lee como dato faltante. Leé siempre así:

```python
import pandas as pd

paises = pd.read_csv("etl/maestros/paises_maestro.csv",
                     keep_default_na=False, na_values=[""],
                     dtype={"iso_numerico": str})   # "032" y no 32
sub = pd.read_csv("etl/maestros/subdivisiones_maestro.csv",
                  keep_default_na=False, na_values=[""])
```

## Ejemplos

**Agregar nombre en español y región al panel**

```python
panel = pd.read_csv("etl/datos_procesados/paises_anual.csv")
panel = panel.merge(paises[["iso3", "nombre_es", "region_bm_es", "nivel_ingreso_bm_es"]],
                    on="iso3", how="left", validate="many_to_one")
```

`validate="many_to_one"` hace que pandas avise si la maestra tuviera un país repetido.

**Unir datos de provincias argentinas con la maestra**

```python
pob = pd.read_csv("etl/argentina_provincias/poblacion_provincia_anual.csv")
pob = pob.merge(sub[["subdivision_iso", "tipo_es", "latitud", "longitud"]],
                left_on="provincia_iso", right_on="subdivision_iso", how="left")
```

**En SQL**

```sql
SELECT p.nombre_es, COUNT(*) AS provincias
FROM paises_maestro p
JOIN subdivisiones_maestro s ON s.iso3 = p.iso3
WHERE p.region_bm = 'Latin America & Caribbean'
GROUP BY p.nombre_es
ORDER BY provincias DESC;
```

## Fuentes y cuánto confiar

- **ISO 3166-1 y 3166-2**, a través del paquete `pycountry` (versión 26.2.16, que copia la base iso-codes de Debian y sigue los cambios que publica ISO). Es la fuente de los códigos, los nombres oficiales y la jerarquía.
- **API del Banco Mundial** (`api.worldbank.org/v2/es/country` y `/en/country`): región, grupo de ingreso, capital. El nivel de ingreso es la clasificación vigente hoy; el panel anual también usa esa.
- **Wikidata** (`query.wikidata.org`): nombres en español e inglés y coordenadas. A veces hay dos ítems con el mismo código (por ejemplo, la provincia de Santa Cruz y el Parque Nacional Los Glaciares figuran con `AR-Z`); el script se queda con el que se parece más al nombre de ISO. Algunos nombres en español quedan desactualizados: Burkina Faso cambió los nombres de sus regiones en 2025 y Wikidata en español todavía tiene los viejos. 16 subdivisiones nuevas (como las regiones nuevas de República Dominicana) no están en Wikidata y usan el nombre de ISO.

Los crudos quedan en `crudos/` para que el resultado se pueda repetir sin internet.
