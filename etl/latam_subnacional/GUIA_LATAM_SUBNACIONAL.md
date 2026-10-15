# Latinoamérica por estado, departamento y región

Esta carpeta hace para toda América Latina lo que `argentina_provincias/` hace para Argentina: tablas con **una fila por subdivisión y año**. La clave de unión es `subdivision_iso`, el código ISO 3166-2 (ej. `BR-SP` São Paulo, `MX-JAL` Jalisco, `CO-ANT` Antioquia), el mismo de `maestros/subdivisiones_maestro.csv`. Cada tabla trae también `iso3`, así que se puede unir con el panel de países (`iso3 + anio`).

```bash
cd etl
python latam_subnacional/extraer_latam_subnacional.py
```

Tarda unos 5 minutos la primera vez. Los archivos originales quedan en `crudos/` y no se vuelven a bajar (con `ETL_REFRESCAR=1` se renuevan; si una fuente falla se sigue con la copia anterior y se imprime `AVISO_FUENTE`).

## Qué países y qué subdivisiones

Los 20 países de América Latina: Argentina, Bolivia, Brasil, Chile, Colombia, Costa Rica, Cuba, Ecuador, El Salvador, Guatemala, Haití, Honduras, México, Nicaragua, Panamá, Paraguay, Perú, República Dominicana, Uruguay y Venezuela (el Caribe angloparlante queda afuera). Suman 381 subdivisiones de primer nivel según ISO. Ojo con dos casos:

- **República Dominicana**: para ISO el primer nivel son 10 *regiones de desarrollo*, no las 32 provincias.
- **Perú**: ISO separa la *Municipalidad Metropolitana de Lima* (`PE-LMA`) del *departamento de Lima* (`PE-LIM`). Casi todas las fuentes dan "Lima" con la capital adentro: va a `PE-LIM` y `PE-LMA` queda vacío.

## Las tablas

| Archivo | Una fila por | Países | Años | Fuente |
|---|---|---|---|---|
| `indicadores_ocde_subdivision_anual.csv` | subdivisión + año | BRA, CHL, COL, MEX, PER (+ARG parcial) | 1990-2025 | OCDE, estadísticas regionales |
| `ocde_regional_largo.csv.gz` | dato (subdivisión + año + medida + desagregación) | ídem | 1990-2026 | OCDE |
| `temperatura_subdivision_anual.csv` | subdivisión + año | 17 (sin Haití, Nicaragua, Panamá) | 1950-2024 | Banco Mundial (CCKP); México de la OCDE |
| `gobernantes_subdivision.csv` | mandato | 12 (incompleto) | 1900-2026 | Wikidata |
| `gobierno_subdivision_anual.csv` | subdivisión + año | 11 (incompleto) | 1980-2026 | Wikidata |
| `brasil_pib_poblacion_estado_anual.csv` | estado + año | BRA | 2001-2026 | IBGE |
| `agricultura_subdivision_anual.csv` | subdivisión + año + cultivo | ARG, BRA, COL | 1970-2026 | MAGyP, IBGE, MADR/UPRA |
| `ganaderia_subdivision_anual.csv` | subdivisión + año + especie | ARG, BRA, COL | 1974-2026 | MAGyP/SENASA, IBGE, ICA |
| `petroleo_gas_subdivision_anual.csv` | subdivisión + año | ARG, BRA, COL | 1997-2026 | Secretaría de Energía, ANP, ANH |

### 1. Indicadores regionales de la OCDE

La OCDE junta los datos de las oficinas de estadística de cada país con un mismo método, a nivel "TL2" (que en estos países son los estados, departamentos o regiones). Es la fuente que permite comparar Nuevo León con Antioquia o con Antofagasta. Columnas:

| Columna | Qué es |
|---|---|
| `poblacion`, `superficie_km2` | Habitantes y superficie |
| `pib_millones_moneda_nacional_corriente` | PIB en millones de moneda local, precios de cada año |
| `pib_pc_usd_ppa_corriente` / `_constante` | PIB por habitante en dólares PPA (paridad de poder adquisitivo): sirve para comparar entre países |
| `pct_vab_<sector>` | % del valor agregado bruto que genera cada sector (agro y pesca, industria con minería y energía, manufactura, construcción, comercio-transporte-turismo, información, finanzas, inmobiliarias, servicios profesionales, Estado-educación-salud, otros) |
| `esperanza_vida_anios`, `mortalidad_infantil_x1000`, `tasa_fecundidad` | Salud y demografía |
| `tasa_desempleo_pct`, `tasa_participacion_laboral_pct` | Mercado de trabajo, personas de 15 años o más |
| `homicidios_x100mil`, `vehiculos_x1000`, `participacion_electoral_pct` | Sociedad |
| `medicos_x1000`, `camas_hospital_x1000` | Sistema de salud |
| `pct_25_64_con_terciaria` | % de las personas de 25 a 64 años con estudios terciarios o universitarios |
| `temperatura_media_c_ocde` | Temperatura media (ERA5, método OCDE) |

El PIB y el valor agregado por sector existen para Chile (2008-2024), Colombia (2005-2024), México (2003-2024) y Perú (2007-2024); Brasil está en su propia tabla (abajo). **`industria_mineria_energia` incluye a la manufactura**: no sumes las dos. Ejemplo 2022: Antofagasta tiene un PIB por habitante de 114.000 dólares PPA (el 77 % de su valor agregado es industria, sobre todo minería del cobre); Vichada, en la Orinoquía colombiana, 5.500.

El archivo largo (`ocde_regional_largo.csv.gz`) tiene todo lo que trae la OCDE (por sexo, grupos de edad amplios, nivel educativo, exportaciones, ingreso de los hogares...). Está comprimido porque son 720.000 filas; pandas lo lee igual: `pd.read_csv("ocde_regional_largo.csv.gz")`. La columna `desagregacion` dice qué recorte es cada fila (vacía = total); `multiplicador` dice por cuánto hay que multiplicar `valor` (10⁶ = millones).

### 2. Temperatura

Igual que para las provincias argentinas: el promedio de **toda la superficie** de la subdivisión (reanálisis ERA5, grilla de 0,25°), del Climate Change Knowledge Portal del Banco Mundial. Por eso un departamento con cordillera da más frío que su capital.

Detalles técnicos que conviene conocer:

- El portal identifica cada subdivisión con un código GAUL (la capa de límites de la FAO). Los códigos salen de la base "Subnational Population" del Banco Mundial; tres venían cruzados o mal (San José de Costa Rica y de Uruguay, Santiago de R. Dominicana) y se corrigieron a mano. Paraguay no está en esa base: sus códigos siguen el orden alfabético, y se comprobó con la temperatura (el Chaco da más calor, Itapúa menos).
- **México, Nicaragua, Panamá y Haití** usan en el portal otra numeración (1, 2, 3...) sin nombres. No se adivina: México se completa con la temperatura de la OCDE (`fuente = OCDE`), que usa otro método y da entre 0,1 y 0,7 °C menos en promedio (hasta 2 °C) que el portal para los mismos estados. Compará México consigo mismo, no con los demás. Nicaragua, Panamá y Haití quedan sin dato.
- Subdivisiones creadas después de 2015 reciben la temperatura de la unidad de la que se separaron, marcado en `fuente_unidad`: Ñuble (de Biobío), Artemisa y Mayabeque (de la antigua provincia La Habana), Asunción (de Central). República Dominicana: cada región es el promedio de sus provincias, ponderado por superficie. **Lima Metropolitana no se aproxima**: el departamento de Lima incluye la sierra y da 6 °C menos que la ciudad.

### 3. Gobernadores (Wikidata, incompleto)

No hay una base oficial común de elecciones subnacionales en la región. Wikidata (la base de datos detrás de Wikipedia) registra para muchos estados el cargo "gobernador de X" y quién lo ocupó, con fechas. Cobertura de los años 2000-2026 con un gobernante cargado: Perú 85 %, Argentina 81 %, Brasil 75 %, Colombia 56 %, México 44 %, Chile 18 % y casi nada en el resto.

- `gobernantes_subdivision.csv`: un mandato por fila (`persona`, `cargo`, `inicio`, `fin`, `persona_wikidata` para buscarla en wikidata.org).
- `gobierno_subdivision_anual.csv`: quién estaba en el cargo el 1 de julio de cada año. Un mandato sin fecha de fin solo se extiende 8 años.
- **No trae el partido**: Wikidata da los partidos de toda la vida de la persona, no el del mandato, y tiene errores graves (un exgobernador de Antioquia figura en las FARC). Para Argentina sigue valiendo `argentina_provincias/gobernadores_elecciones.csv`, que sí tiene partido y familia política.

### 4. Brasil por estado (IBGE)

`brasil_pib_poblacion_estado_anual.csv`, del Sistema IBGE de Recuperação Automática (SIDRA, una API pública):

- PIB, impuestos y valor agregado por gran sector (agropecuaria, industria, servicios privados, administración pública), en **miles de reales corrientes**, 2002-2023, y su `pct_vab_*`.
- `poblacion` al 1 de julio con `poblacion_fuente`: estimación del IBGE, o el conteo 2007 y los censos 2010 y 2022 en esos años. 2023 no tiene ni estimación ni censo: es el punto medio entre el censo 2022 y la estimación 2024 (marcado). Ojo: el censo 2022 contó 10 millones menos que lo que se venía estimando (203 contra 213 millones), así que hay un salto entre 2021 y 2022.
- `pib_per_capita_reales`: el Distrito Federal (Brasilia) es el más alto (126.000 reales en 2023) y Maranhão el más bajo (21.600).

### 5. Agricultura, ganadería, petróleo y gas (Argentina, Brasil y Colombia juntos)

Estas tres tablas ponen en el mismo formato las fuentes de cada país, incluida Argentina (sale de `argentina_provincias/`), para poder comparar.

**Agricultura** (`agricultura_subdivision_anual.csv`): `area_sembrada_ha`, `area_cosechada_ha`, `produccion` (toneladas, ver `unidad_produccion`) y, para Brasil desde 1994, `valor_produccion_miles_moneda_local` (miles de reales; antes había otras monedas y se deja vacío).

- `cultivo_original` es el nombre como lo publica cada país ("Milho (em grão)", "Maiz", "Maíz"). `cultivo` es un nombre común para los 28 principales (Soja, Maíz, Trigo, Café, Caña de azúcar...), así se puede comparar la soja de Mato Grosso con la de Córdoba.
- **No sumar dos veces**: solo los totales reciben nombre común. "Soja total" = soja de primera + segunda (Argentina) y "Café (em grão) Total" = arábica + canephora (Brasil).
- Argentina usa el año de cosecha de la campaña (2023/24 = 2024). Colombia suma los dos semestres de los cultivos transitorios.
- Colombia tiene **dos bases con metodología distinta**: 2006-2018 y 2019 en adelante (ver `fuente`). La caña panelera, por ejemplo, salta de 1,4 a 11,7 millones de toneladas en 2019 porque cambió la forma de medirla. Compará años dentro de cada base.
- Ejemplo 2023: Brasil cosechó 152 millones de toneladas de soja (Mato Grosso es el primero), Argentina 25 millones (año de sequía) y Colombia 0,2.

**Ganadería** (`ganaderia_subdivision_anual.csv`): cabezas por especie. Argentina: stock bovino al 31-12 (SENASA). Brasil: todas las especies (bovinos, porcinos, aves, ovinos...) al 31-12 de la Pesquisa da Pecuária Municipal, desde 1974. Colombia: bovinos y búfalos del censo de vacunación contra la aftosa del ICA (primer ciclo de cada año), desde 2019. En 2024: Brasil 238 millones de bovinos, Argentina 52, Colombia 30.

**Petróleo y gas** (`petroleo_gas_subdivision_anual.csv`): `petroleo_m3` y `gas_miles_m3` por año, con `meses_con_dato` (el año en curso está incompleto).

- Brasil (ANP, desde 1997): la producción en el mar se asigna al estado que tiene enfrente; `pct_petroleo_en_el_mar` dice cuánto es costa afuera (Rio de Janeiro, casi todo el presal).
- Colombia (ANH, desde 2014): producción fiscalizada mensual por campo, convertida de barriles (× 0,159) y miles de pies cúbicos (× 28,3) a m³.
- Argentina: la misma serie de `argentina_provincias/`, sin la producción costa afuera ("Estado Nacional").
- 2024: Rio de Janeiro 170 millones de m³ de petróleo, Meta (Colombia) 25, Neuquén 24.

## Qué falta y por qué

| Dimensión | Estado |
|---|---|
| Agricultura y ganadería de México | El servidor del SIAP (`nube.siap.gob.mx`) no responde desde la nube (error 502) |
| PIB, IDH, educación y esperanza de vida comparables para los 20 países | Global Data Lab pide iniciar sesión para descargar: la usuaria puede bajar el archivo y subirlo |
| Valor agregado por sector de 1960 a 2020 (base DOSE) | Zenodo bloquea las descargas desde la nube ("tráfico inusual") |
| Chile y Perú: agro, minería, pobreza | Pendientes: necesitan fuentes nacionales (INE, ODEPA, Cochilco, INEI, MINEM) |
| Pobreza por subdivisión | Cada país la mide distinto (CONEVAL, DANE, CASEN, INEI, IBGE); pendiente |
| Partido del gobernador | Wikidata no es confiable para eso; no hay base regional |
| Países chicos (Centroamérica, Caribe, Bolivia, Paraguay, Uruguay, Venezuela) | Solo temperatura y, a veces, gobernadores: la OCDE no los cubre |
| Religión, legislaturas provinciales, intendencias | Igual que en Argentina: no hay fuentes por subdivisión |

## Ideas clave

**Compiladas vs. nacionales.** La OCDE y el Banco Mundial usan un mismo método para todos: sirven para comparar entre países. Las fuentes nacionales (IBGE, ICA, ANH...) tienen más detalle y llegan más cerca del presente, pero cada país mide a su manera: sirven sobre todo para mirar adentro de un país.

**PIB per cápita en dólares PPA.** Un real brasileño y un peso colombiano no compran lo mismo. La PPA (paridad de poder adquisitivo) convierte cada moneda a "dólares que compran lo mismo que en EE. UU.", y así se pueden comparar estados de países distintos.

**Cuidado con las regiones mineras y petroleras.** Antofagasta, Campeche o Casanare tienen PIB por habitante altísimos porque el valor del cobre o del petróleo se cuenta donde se extrae, aunque las ganancias se vayan a otro lado. No es el ingreso de su gente.

**Límites que cambian.** Chile creó Ñuble en 2018, Cuba partió La Habana en 2011, Panamá creó Panamá Oeste en 2014. Las series viejas de esas regiones incluyen a la nueva. El maestro ISO tiene los límites actuales.
