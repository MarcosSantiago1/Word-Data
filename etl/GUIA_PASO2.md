# Paso 2: precios, desigualdad, salarios y felicidad

El paso 2 agrega columnas nuevas a la misma tabla del paso 1 (`datos_procesados/paises_anual.csv`), usando la misma clave: **iso3 + anio**. Se ejecuta después del paso 1:

```bash
python paso1_extraer_banco_mundial.py
python paso2_distribucion_precios_bienestar.py
```

Si vuelves a correr el paso 1, el archivo se regenera sin las columnas del paso 2: vuelve a correr el paso 2 (y el paso 3, `GUIA_PASO3.md`).

## Variables nuevas

| Columna | Qué es | Fuente |
|---|---|---|
| `tipo_cambio_lcu_por_usd` | Unidades de moneda local por 1 dólar, promedio del año (tipo de cambio **oficial**) | Banco Mundial, PA.NUS.FCRF |
| `ppa_lcu_por_usd_intl` | Unidades de moneda local que compran lo mismo que 1 dólar en EE. UU. (paridad de poder adquisitivo) | Banco Mundial, PA.NUS.PPP |
| `gini` | Índice de Gini del ingreso o consumo (0 = todos ganan lo mismo, 100 = una persona tiene todo) | Banco Mundial, SI.POV.GINI |
| `ingreso_quintil1_pct` … `ingreso_quintil5_pct` | % del ingreso total que recibe cada quinto de la población, del más pobre al más rico | Banco Mundial, SI.DST.* |
| `ingreso_decil1_pct`, `ingreso_decil10_pct` | % del ingreso del 10 % más pobre y del 10 % más rico | Banco Mundial |
| `lorenz_acum_10` … `lorenz_acum_90` | Puntos de la **curva de Lorenz**: % del ingreso que acumula el 10 %, 20 %, 40 %, 60 %, 80 % y 90 % más pobre | Cálculo propio |
| `gini_aprox_desde_lorenz` | Gini calculado a mano desde esos puntos (regla del trapecio) | Cálculo propio |
| `ratio_quintil5_quintil1` | Cuántas veces gana el 20 % más rico lo que gana el 20 % más pobre | Cálculo propio |
| `ratio_palma` | Ingreso del 10 % más rico dividido por el del 40 % más pobre | Cálculo propio |
| `dieta_saludable_lcu_dia` / `_ppa_dia` | Costo por persona y por día de la dieta saludable más barata, en moneda local y en dólares PPA | Banco Mundial, Food Prices for Nutrition 5.0 |
| `dieta_saludable_lcu_mes` / `_usd_mes` | Lo mismo por mes (× 30,4 días), en moneda local y en dólares al tipo de cambio oficial | Cálculo propio |
| `pct_no_puede_pagar_dieta_saludable` | % de la población cuyo ingreso no alcanza para esa dieta | Banco Mundial |
| `salario_promedio_mensual_lcu` / `_usd` / `_ppa` | Ingreso promedio mensual de los asalariados (ambos sexos), en moneda local, dólares y dólares PPA de 2021 | ILOSTAT (OIT), EAR_EMTA_SEX_CUR_NB_A |
| `felicidad` | Puntaje de evaluación de vida (escalera de Cantril, 0 a 10), promedio de 3 años | World Happiness Report 2025 |
| `felicidad_ranking` | Puesto del país en el ranking del informe (1 = el más feliz) | World Happiness Report 2025 |

## Ideas clave

**Curva de Lorenz y Gini.** Ordenamos a la población de la más pobre a la más rica y vamos sumando su ingreso. Si todos ganaran igual, el 40 % más pobre tendría el 40 % del ingreso y la curva sería una diagonal. Cuanto más se hunde la curva por debajo de la diagonal, más desigual es el país. El **Gini** es justamente esa área entre la diagonal y la curva, multiplicada por 2. No existe un "coeficiente de Lorenz" separado: el coeficiente que resume la curva de Lorenz es el Gini.

Ejemplo, Argentina 2021: el 40 % más pobre recibe el 14,8 % del ingreso (`lorenz_acum_40`), y el Gini es 42,4.

Nuestro `gini_aprox_desde_lorenz` da en promedio 1,3 puntos menos que el oficial, porque solo conocemos 8 puntos de la curva y la regla del trapecio supone que dentro de cada tramo todos ganan igual. Sirve para entender de dónde sale el número, no para reemplazarlo.

**Encuestas cada tantos años.** El Gini y los quintiles salen de encuestas de hogares, que muchos países no hacen todos los años. Hay datos de 168 países, pero no en todos los años. Algunos países miden ingreso y otros consumo (el consumo da Gini más bajos), así que compara con cuidado.

**Canasta básica.** No hay una canasta básica comparable entre países: cada país define la suya con alimentos y cantidades distintas. Usamos el sustituto internacional más cercano, el **costo de una dieta saludable** que calculan el Banco Mundial y la FAO con precios de cada país. Cubre solo alimentos (no vivienda ni transporte) y va de 2017 a 2024.

**Tipo de cambio oficial.** En países con cepo o varios tipos de cambio (Argentina, Venezuela, Irán...) el oficial puede estar muy lejos del que paga la gente. Para comparar poder de compra entre países conviene usar la PPA en vez del tipo de cambio. Cuba, Corea del Norte, Palestina e Islas Vírgenes Británicas no tienen tipo de cambio en el Banco Mundial.

**Salario promedio.** Es el ingreso promedio por mes de las personas asalariadas (no cuenta a cuentapropistas ni patrones). La OIT elige una fuente por país y año, que puede ser una encuesta de hogares (incluye informales) o de empresas (solo formales), así que la comparación entre países es aproximada. Hay datos de 183 países de nuestra lista, con muchos huecos por año. El script descarta valores que son menos del 10 % de la mediana del país, porque vienen en otra unidad (Malta 2000-2008 y Egipto 2008). Los territorios que no están en la lista del Banco Mundial (Guernsey, Jersey, Reunión...) quedan afuera.

**Felicidad.** Sale de la encuesta mundial de Gallup: cada persona ubica su vida en una escalera de 0 (la peor vida posible) a 10 (la mejor). El World Happiness Report publica el promedio de 3 años: el valor de 2024 promedia 2022, 2023 y 2024, y es el del ranking del informe 2025 (Finlandia primera). Hay datos de 164 países desde 2011, salvo 2013, que el informe no publica. Como el archivo trae nombres y no códigos, el script los traduce a ISO3 con la lista del Banco Mundial más 19 nombres cargados a mano. Taiwán, Chipre del Norte y Somalilandia quedan afuera porque no están en la lista del Banco Mundial.
