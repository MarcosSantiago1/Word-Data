# Base absoluta: toda la información en una sola tabla

`base_absoluta.csv` junta **todas las variables del proyecto** (países, provincias, estados y
departamentos) en una sola tabla con esta forma:

| nivel | pais_iso3 | pais | subdivision_codigo | provincia_departamento | tema | variable | apertura | unidad | fuente | sin_anio | 1945 | … | 2021 | 2022 | … | 2040 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pais | ARG | Argentina | | | panel_base | poblacion | | | Banco Mundial… | | | | 45312281 | 45407904 | | |
| subdivision | ARG | Argentina | AR-X | Córdoba | pobreza | pct_personas_pobres_estimado | | % | Cálculo propio EPH… | | | | 43.0 | 39.5 | | |
| subdivision | ARG | Argentina | AR-L | La Pampa | agricultura | produccion_tn | Soja total | toneladas | MAGyP… | | | | 1123733 | … | | |
| pais | ARG | Argentina | | | relaciones | membresia_organizacion | MERCOSUR - … | | COW IGO… | | | | pleno | pleno | | |

**Una fila = una variable de un lugar. Una columna = un año.**

## Qué es cada columna

| Columna | Qué tiene |
|---|---|
| `nivel` | `pais` (la fila es del país entero; la provincia queda vacía) o `subdivision` (provincia, estado, departamento o región). |
| `pais_iso3`, `pais` | Código ISO de 3 letras y nombre en español. |
| `subdivision_codigo`, `provincia_departamento` | Código ISO 3166-2 (AR-X = Córdoba) y nombre corto. Vacíos en las filas de país. |
| `tema` | De qué grupo es la variable (salud, educación, fiscal, agricultura…). Sirve para filtrar. |
| `variable` | El nombre de la variable, el mismo que en el resto del proyecto. |
| `apertura` | El detalle cuando la variable viene abierta: cultivo, rama de actividad, cámara, organización, país socio, religión… Vacía en el resto. |
| `unidad` | Unidad de medida, cuando el diccionario la tiene. |
| `fuente` | De dónde sale el dato. |
| `sin_anio` | Datos fijos, sin serie por año: perfil del CIA Factbook (superficie, clima…), resultados de los KPIs, festivales, coordenadas, continente y región. |
| `1945` … `2040` | El valor de cada año. Puede ser un número o un texto (por ejemplo `peronismo` o `pleno`). Los años después de 2026 son proyecciones de población del INDEC. |

## Qué hay adentro

- **91.106 filas**: 57.419 de país y 33.687 de provincias, estados y departamentos.
- **251 países** y **340 subdivisiones** de 17 países de América Latina (Argentina con sus 24
  jurisdicciones más la plataforma continental para petróleo y gas).
- **508 variables** en 56 temas. La lista completa, con unidad, fuente, cuántos países o
  provincias tienen dato y desde qué año hasta cuál, está en `diccionario_variables.csv`.

| Nivel | Temas |
|---|---|
| País | panel base (población, PIB, salud, suicidio, gasto público, Gini, felicidad, salario…), migración, emisiones, capital social, diversidad cultural, población indígena, gobernanza y democracia, deuda, salud crónica, tecnología, educación, redes y videojuegos, empleo sectorial, gasto en cultura, medallero olímpico, consolas, relaciones (organizaciones, acuerdos, aliados), membresías por organización, acuerdos comerciales, fronteras, socios comerciales, religiones/etnias/idiomas, perfil del Factbook, identificación y KPIs. |
| Provincia / estado / departamento | población, VAB y PBG, VAB por rama y por grupo de sectores, petróleo y gas, agricultura por cultivo, ganadería, censo, turismo, temperatura, salud, empresas y pymes, recaudación y alícuotas, salarios, canastas, pobreza, gobernadores y elecciones, legisladores, deuda y finanzas públicas provinciales, federalismo fiscal, emisiones, internet, festivales, OCDE regional, PIB de Brasil por estado, identificación y KPI 5. |

## Cómo usarla

**En Excel o Google Sheets**: abrir `base_absoluta.csv` y poner un filtro en la primera fila.
Filtrando `pais` + `variable` se ve la serie de un país; filtrando `variable` + `nivel = subdivision`
se comparan todas las provincias.

**En Python (pandas)**:

```python
import pandas as pd

base = pd.read_csv("base_absoluta.csv", keep_default_na=False, na_values=[""], low_memory=False)
# (keep_default_na=False porque "NA" es Namibia, no un dato faltante)

# Pobreza por provincia argentina, 2016-2025
pobreza = base.query("pais_iso3 == 'ARG' and variable == 'pct_personas_pobres_estimado'")
pobreza[["provincia_departamento"] + [str(a) for a in range(2016, 2026)]]

# Volver al formato largo (una fila por lugar, variable y año) para graficar
anios = [c for c in base.columns if c.isdigit()]
largo = base.melt(id_vars=["nivel", "pais_iso3", "pais", "provincia_departamento", "variable", "apertura"],
                  value_vars=anios, var_name="anio", value_name="valor").dropna(subset=["valor"])
```

**En SQL** (`base_absoluta.sqlite`, tabla `base_absoluta`): los años son columnas con nombre de
número, así que van entre comillas dobles.

```sql
SELECT pais, "2000", "2010", "2021"
FROM base_absoluta
WHERE variable = 'suicidio_total_x100k' AND nivel = 'pais'
ORDER BY "2021" DESC;
```

La misma base tiene la tabla `diccionario_variables`.

## Decisiones que conviene saber

1. **No se repite información.** Cuando una vista del master solo copia columnas de otras tablas,
   se toma la columna original; de las vistas entran solo los cálculos nuevos (tasas, cocientes,
   totales). Los KPIs entran con sus resultados (índices, z, cuadrantes) y no con las columnas que
   copian variables que ya están (PIB, Gini, etc.).
2. **Argentina no está dos veces.** Agro, ganado, temperatura y petróleo de Argentina salen de las
   tablas de provincias del master; los CSV de Latinoamérica aportan solo los otros países, con los
   mismos nombres de variable que Argentina (`sup_sembrada_ha`, `produccion_tn`, `petroleo_m3_total`,
   `gas_miles_m3_total`) para poder compararlos. La OCDE regional sí incluye a Argentina, porque es
   otra fuente.
3. **Nombres repetidos.** Si dos tablas tienen una columna con el mismo nombre, se le antepone el tema
   (`censo_habitantes`, `hidrocarburos_meses_con_dato`, `turismo_meses_con_dato`). En Brasil, la
   población del IBGE se llama `poblacion_ibge` para no chocar con la de la OCDE.
4. **Lo que queda afuera:** las alianzas militares de a pares (ATOP), porque son relaciones entre dos
   países y no una variable de un país; su conteo por año sí está (`n_aliados_defensa`,
   `n_aliados_cualquier_pacto`). También los gobernantes con fecha exacta de inicio y fin: entra el
   gobernante al cierre de cada año (`gobernante`).
5. **Palestina** tiene dos fichas en el Factbook: sus datos fijos llevan `Franja de Gaza` o
   `Cisjordania` en la apertura.
6. **Unidades corregidas.** El diccionario del master decía "hectáreas" para el rendimiento
   (es kg por hectárea), "m³" para el gas (son miles de m³) y "US$" para el tipo de cambio y la PPA
   (son moneda local por dólar). Acá van corregidas.
7. **Controles del script:** que no haya dos valores para el mismo lugar, variable, apertura y año, y
   que todos los países y provincias existan en el master. Se cotejaron 3.000 valores al azar contra
   `datos_procesados/paises_anual.csv` y dieron todos iguales.

## Cómo se actualiza

No baja nada: se arma con lo que ya está. Corre como último paso de `actualizar_mensual.py`, así que
se rehace sola el día 16 de cada mes. A mano:

```bash
cd etl/base_absoluta
python construir_base_absoluta.py
```

Si se suma una tabla nueva al master (`hecho_pais_*` o `hecho_subdivision_*`), entra sola. Si se suma
un CSV que no va al master, hay que agregarlo en `COMPLEMENTOS_SUBDIVISION` dentro del script.
