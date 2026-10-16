# Bases regionales: Argentina, Latinoamérica y mundo

Toda la información del proyecto, separada en **tres bases de datos SQLite**. Cada una es un
solo archivo que se abre con cualquier programa de SQLite, con Python o desde Colab.

| Archivo | Qué tiene | Tamaño aprox. |
|---|---|---|
| `base_argentina.sqlite` | Argentina: datos nacionales (2000-2024) + las 24 provincias | 5 MB |
| `base_latam.sqlite` | América Latina y el Caribe: 52 países y territorios + sus subdivisiones con datos (Argentina, Brasil, Chile, Colombia, México, Perú y 11 más con temperatura o gobernantes) | 29 MB |
| `base_mundial.sqlite` | Los 251 países y territorios + todas las subdivisiones con datos | 39 MB |

`resumen_bases.csv` dice cuántas filas tiene cada tabla en cada base.

## Cómo se arman (sin descargar nada)

El script `construir_bases_regionales.py` no baja datos de internet: parte del **master**
(`modelo_unificado/master_paises_provincias.sqlite`), que ya junta casi todo el proyecto, y
hace tres cosas:

1. **Copia el master filtrado por región.** Las tablas son las mismas, con los mismos nombres y
   columnas, pero solo con las filas de los países de esa base:
   - tablas por país (`hecho_pais_*`, `rel_pais_*`): filas cuyo `pais_id` es de la región;
   - tablas por provincia o estado (`hecho_subdivision_*`): filas de subdivisiones de la región;
   - alianzas militares: los pactos donde participa al menos un país de la región.
2. **Suma lo que el master todavía no tiene**, leyendo sus CSV:
   - `latam_subnacional/`: indicadores OCDE por región, temperatura, gobernantes (Wikidata),
     PIB de los estados de Brasil y las tablas comunes de agricultura, ganado y petróleo/gas;
   - `argentina_provincias/festivales_*.csv`: festivales por provincia y la lista completa;
   - `kpis/resultados/`: los 5 KPIs multidimensionales (filas de los países de la región).
3. **Rehace el catálogo** (`ref_catalogo_tabla`: qué tabla es, de qué fuente, cuántas filas y
   qué años) y el **diccionario** (`ref_diccionario_columna`: unidad y % de vacíos de cada
   columna) con los números de esa base. La tabla `ref_alcance_base` dice qué países entran,
   cuándo se construyó y de qué versión del master salió.

> **¿Por qué `dim_pais` tiene los 251 países también en la base de Argentina?** Porque las
> alianzas, fronteras y socios comerciales de Argentina nombran a otros países, y para leer
> esos nombres hace falta la lista completa. Los *datos* (`hecho_*`) sí son solo de Argentina.

> **¿Qué cuenta como Latinoamérica?** La región "América Latina y el Caribe" de la ONU (código
> M49 419): Sudamérica, Centroamérica, México y el Caribe, incluidos territorios como Puerto
> Rico o Malvinas. Los territorios casi no tienen datos; los 42 con panel anual son los mismos
> que el Banco Mundial pone en esa región.

## Cómo correrlo

Al final del pipeline, después del master:

```bash
cd etl/modelo_unificado && python construir_master.py      # si cambió algún dato
cd ../bases_regionales && python construir_bases_regionales.py
```

Tarda unos segundos. La actualización mensual (`actualizar_mensual.py`) ya lo corre como
último paso. Si algo sale mal, la base anterior no se pisa: se escribe primero un `.tmp` y
recién se reemplaza cuando pasaron los controles (claves foráneas válidas, todas las vistas
se pueden leer y la base mundial tiene todas las filas del master).

## Primeros pasos: consultas de ejemplo

Con Python (funciona igual en Colab):

```python
import sqlite3, pandas as pd
con = sqlite3.connect("base_argentina.sqlite")

# ¿Qué tablas hay y de qué años?
pd.read_sql("SELECT tabla, fuente, filas, anio_min, anio_max FROM ref_catalogo_tabla", con)

# Argentina año por año: población, PIB per cápita y felicidad
pd.read_sql("SELECT anio, poblacion, pib_pc_ppp, felicidad FROM v_pais_anual", con)

# Pobreza por provincia en 2024 (la vista ya trae el nombre de la provincia)
pd.read_sql("""SELECT s.nombre_es AS provincia, p.pct_personas_pobres_estimado
               FROM hecho_subdivision_pobreza p JOIN dim_subdivision s USING (subdivision_id)
               WHERE p.anio = 2024 ORDER BY 2 DESC""", con)
```

En la base de Latam, para comparar países en un año:

```sql
SELECT pais, pib_pc_ppp, esperanza_vida, felicidad
FROM v_pais_anual WHERE anio = 2021 ORDER BY pib_pc_ppp DESC;

-- Esperanza de vida por región OCDE (Brasil, Chile, Colombia, México, Perú, Argentina)
SELECT iso3, subdivision, esperanza_vida_anios
FROM v_subdivision_latam_ocde WHERE anio = 2020 ORDER BY esperanza_vida_anios DESC;
```

Cada tabla sumada desde un CSV tiene su vista `v_...` con el código ISO y el nombre ya puestos
(por ejemplo `v_subdivision_latam_agricultura`, `v_kpi1_sal_efi_iese`), así no hace falta
escribir el JOIN.

## Cosas a tener en cuenta

- **Argentina aparece dos veces en la base de Latam y en la mundial** para agricultura, stock
  bovino, temperatura y petróleo/gas: en la tabla original (`hecho_subdivision_agricultura`,
  etc.) y en la tabla de formato común (`hecho_subdivision_latam_*`), que sirve para comparar
  con otros países. En `base_argentina.sqlite` solo está la original, para no repetir.
- **Los KPIs son una foto**: salen de `kpis/resultados/` tal como los dejó la última corrida
  de `kpis/calcular_kpis.py`. Los puntajes (z) están calculados contra todos los países del
  mundo, aunque la base muestre solo los de la región.
- Una tabla puede quedar vacía en una región (por ejemplo `hecho_pais_digital_ocio`, que es de
  Eurostat y no tiene a Argentina). Se deja igual, para que las tres bases tengan las mismas
  tablas y las mismas consultas funcionen en todas.
- Para el detalle de cada tabla original (columnas, fuentes, decisiones) ver
  `modelo_unificado/GUIA_MODELO_UNIFICADO.md`.
