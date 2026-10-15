# Modelo unificado de países y provincias

Una sola base de datos relacional que junta todo lo que construimos: el panel país-año (pasos 1 y 2), las alianzas y tratados, las 20 tablas de provincias argentinas y las tablas maestras de países y subdivisiones, y lo que suma el CIA World Factbook (fronteras, religiones, etnias, idiomas, socios comerciales).

```bash
cd etl/modelo_unificado
python construir_master.py
```

Orden de ejecución del proyecto: paso 1 → paso 2 → `alianzas/` → `argentina_provincias/` → `maestros/` → **este script**. No descarga datos nuevos de los pasos anteriores: lee sus CSV. Solo baja dos archivos chicos de referencia (lista de países del Banco Mundial y regiones M49 de la ONU) a `crudos/`.

| Archivo | Qué es |
|---|---|
| `master_paises_provincias.sqlite` | la base completa (11,5 MB): 43 tablas + 7 vistas |
| `esquema.sql` | el DDL (`CREATE TABLE` / `CREATE VIEW`), para llevarlo a PostgreSQL, MySQL u otro motor |
| `tablas/*.csv` | las dimensiones, tablas de equivalencias, catálogo y diccionario, en CSV |
| `tablas/ref_diccionario_columna.csv` | cada columna de cada tabla con su tipo, unidad y % de vacíos |

Para abrir la base: [DB Browser for SQLite](https://sqlitebrowser.org/), DBeaver, Power BI / Tableau (conector SQLite) o Python:

```python
import sqlite3, pandas as pd
con = sqlite3.connect("etl/modelo_unificado/master_paises_provincias.sqlite")
pd.read_sql("SELECT * FROM v_pais_anual WHERE anio = 2021", con)
```

---

## 1. Resumen de integración

Antes teníamos cuatro "islas" de datos que se unían a mano por código:

| Base previa | Clave que usaba | Qué pasó en el modelo |
|---|---|---|
| `datos_procesados/paises_anual.csv` (217 países, 2000-2024, 47 columnas) | `iso3` + `anio` | → `hecho_pais_anual`. Se sacaron `pais`, `region` y `nivel_ingreso` (ahora viven una sola vez en `dim_pais`) y `felicidad_fuente`, que estaba vacía |
| `alianzas/` (membresías, tratados, pactos militares) | `iso3` (+ `anio`) | → `rel_pais_organizacion`, `rel_pais_acuerdo_comercial`, `rel_alianza_militar_anual` y los catálogos `dim_organizacion` y `dim_acuerdo_comercial`. Las 48 columnas `miembro_*` ya no se guardan: se **recalculan** desde los episodios de membresía (vista `v_pais_membresia_anual`) |
| `argentina_provincias/` (20 tablas) | `provincia_iso` (+ `anio`) | → 20 tablas `hecho_subdivision_*`. El nombre de provincia y la región EPH ya no se repiten en cada fila |
| `maestros/` (251 países, 3.590 subdivisiones) | `iso3`, `subdivision_iso` | → base de `dim_pais` y `dim_subdivision` |

Cuatro decisiones explican todo el diseño:

1. **Un código para cada cosa.** Cada país tiene un `pais_id` (el código ISO numérico: Argentina = 32) y cada subdivisión un `subdivision_id`. Las tablas de hechos guardan solo esos números; los nombres y códigos de texto están una sola vez en las dimensiones. Así no puede pasar que "Argentina" esté escrita de dos maneras.
2. **El código ISO sigue siendo la puerta de entrada.** `iso3` (`ARG`) e `iso2` (`AR`) en `dim_pais`, y `codigo` (`AR-X`) en `dim_subdivision`, son únicos. Las vistas (`v_...`) los muestran para que nadie tenga que acordarse de los números.
3. **Las fuentes que llaman distinto a un país no se pierden.** La tabla `pais_equivalencia` guarda cómo lo nombra cada fuente (Banco Mundial, World Happiness Report, ILOSTAT, Correlates of War...). `subdivision_equivalencia` hace lo mismo con las provincias (código INDEC `14` = Córdoba, "Capital Federal" = `AR-C`).
4. **Nada que se pueda calcular se guarda dos veces.** El VAB por grupo de sectores se calcula sumando las 52 ramas; la membresía por año, desde los episodios. El script comprueba que el resultado sea idéntico a los CSV originales.

### Controles que corre el script

- Todas las claves foráneas se verifican (`PRAGMA foreign_key_check`): ninguna fila apunta a un país o provincia que no exista.
- Ninguna tabla tiene la clave primaria repetida.
- Membresías recalculadas: 20.462 país-año-organización, **0 diferencias** con `alianzas_pais_anual.csv`.
- VAB por grupo recalculado: **coincide** con `vab_provincia_grupos_largo.csv`.
- Los `subdivision_id` son estables: correr el script dos veces da los mismos números (se guardan en `tablas/dim_subdivision.csv`).
- Dimensiones nuevas, tres cruces entre fuentes independientes: la recaudación propia del esquema AIF coincide con la de la DNAP (`hecho_subdivision_fiscal`) en todos los años 2005-2025; los intereses de la planilla de deuda dan entre 97 % y 100 % de los del AIF; la suma de las regiones OCDE da entre 93 % y 104 % de la emisión nacional del Banco Mundial (2022).
- Suma de provincias contra el total país (vista `v_control_poblacion_pais_vs_subdivisiones`): la proyección INDEC da 1,8 % más que el Banco Mundial en 2022 y 3,0 % más en 2024. No es un error de la unión: las proyecciones provinciales del INDEC son base Censo 2010 y el Banco Mundial ya usa datos del Censo 2022.

---

## 2. Modelo de datos maestro

### Convenciones de nombres

- **Prefijos de tabla:** `dim_` (catálogos: quién o qué), `hecho_` (medidas por año), `rel_` (relaciones muchos a muchos), `*_equivalencia` (traducción de códigos), `ref_` (documentación), `v_` (vistas listas para el dashboard).
- **Columnas:** `snake_case`, en español, sin tildes ni espacios. Por eso `bancas_La Libertad Avanza` pasó a `bancas_la_libertad_avanza`.
- **Unidad al final:** `_pct`, `_x1000`, `_mill_pesos_2004`, `_usd`, `_ha`... (`ref_diccionario_columna` la deduce de ese sufijo).
- **Claves:** `<entidad>_id` para ids numéricos; año siempre `anio`; los años especiales conservan su nombre (`anio_censo`, `anio_cosecha`, `anio_eleccion`).
- **Booleanos:** `es_` o `en_` y valores 0/1.

### Diagrama (lo esencial)

```
dim_region_geografica (M49) ◄──┐ (se apunta a sí misma: continente > subregión > región intermedia)
dim_region_bm ◄────────────────┤
dim_nivel_ingreso ◄────────────┤
                               │
                         ┌─ dim_pais ─┐◄── pais_soberano_id (Puerto Rico → EE. UU.)
                         │  pais_id   │◄── pais_equivalencia (nombres y códigos de cada fuente)
                         └─────┬──────┘◄── rel_reclamo_territorial (Malvinas ← Argentina)
                 1             │ N
                               ▼
dim_region_subnacional ◄── dim_subdivision ◄── subdivision_equivalencia (INDEC, GAUL, alias)
     (regiones EPH)        subdivision_id
                               │ 1
                               ▼ N
                    hecho_subdivision_* (20 tablas: población, economía, pobreza, fiscal...)

dim_pais 1 ── N hecho_pais_anual, hecho_pais_relaciones_anual
dim_pais N ── N dim_organizacion       (vía rel_pais_organizacion)
dim_pais N ── N dim_acuerdo_comercial  (vía rel_pais_acuerdo_comercial)
dim_pais N ── N dim_pais               (vía rel_alianza_militar_anual: pares de países)
```

### Dimensiones geográficas

**`dim_pais`** — 251 filas: los 249 códigos ISO 3166-1 + Kosovo y las Islas del Canal (códigos del Banco Mundial).

| Columna | Tipo | Clave / regla | Ejemplo |
|---|---|---|---|
| `pais_id` | INTEGER | **PK**. ISO numérico; 901 Kosovo, 902 Islas del Canal | 32 |
| `iso3` | TEXT | UNIQUE, NOT NULL, largo 3 | ARG |
| `iso2` | TEXT | UNIQUE, NOT NULL, largo 2 | AR |
| `iso_numerico` | TEXT | UNIQUE (texto para no perder el cero) | 032 |
| `codigo_banco_mundial` | TEXT | UNIQUE; NULL si el BM no publica datos | ARG |
| `nombre_es`, `nombre_en`, `nombre_oficial_en` | TEXT | NOT NULL | Argentina / Argentine Republic |
| `nombre_es_banco_mundial` | TEXT | | Argentina |
| `region_geografica_id` | INTEGER | FK → `dim_region_geografica` (el nivel más fino) | 5 (América del Sur) |
| `region_bm_codigo` | TEXT | FK → `dim_region_bm` | LCN |
| `nivel_ingreso_codigo` | TEXT | FK → `dim_nivel_ingreso` (clasificación actual) | UMC |
| `capital`, `latitud_capital`, `longitud_capital` | TEXT, REAL, REAL | | Buenos Aires, −34,61, −58,42 |
| `tipo_entidad` | TEXT | ver "Casos especiales" | estado_miembro_onu |
| `es_miembro_onu` | INTEGER | 0/1 (suma 193) | 1 |
| `pais_soberano_id` | INTEGER | FK → `dim_pais` (a sí misma) | NULL |
| `en_panel_bm` | INTEGER | 0/1: está en el panel de 217 | 1 |

**`dim_subdivision`** — 3.591 filas: las subdivisiones de primer nivel ISO 3166-2 de 200 países (+ 1 caso especial argentino). Relación **1:N** con `dim_pais`.

| Columna | Tipo | Clave / regla | Ejemplo |
|---|---|---|---|
| `subdivision_id` | INTEGER | **PK**, estable entre corridas | 229 |
| `pais_id` | INTEGER | **FK → `dim_pais`**, NOT NULL | 32 |
| `codigo` | TEXT | UNIQUE (ISO 3166-2) | AR-X |
| `nombre` | TEXT | NOT NULL. Nombre corto, el mismo de `argentina_provincias/` | Córdoba |
| `nombre_iso`, `nombre_es`, `nombre_en` | TEXT | ISO en idioma local / Wikidata | Córdoba / Provincia de Córdoba |
| `tipo_iso`, `tipo_es` | TEXT | | Province / provincia |
| `nivel` | INTEGER | ≥ 1 (hoy todas son 1) | 1 |
| `subdivision_padre_id` | INTEGER | FK → `dim_subdivision`. Vacía hoy; queda lista para un 2.º nivel (provincias de España dentro de comunidades, departamentos argentinos) | NULL |
| `region_subnacional_id` | INTEGER | FK → `dim_region_subnacional` | 43 (Pampeana) |
| `latitud`, `longitud`, `wikidata_id` | REAL, REAL, TEXT | | −32,0, −64,0, Q44759 |
| `es_iso_3166_2` | INTEGER | 0/1 | 1 |
| `pais_equivalente_id` | INTEGER | FK → `dim_pais`: la subdivisión también es "país" | US-PR → PRI |

**`dim_region_geografica`** (29 filas) — jerarquía M49 de la ONU en una sola tabla que se apunta a sí misma: `region_geografica_id` (código M49, PK), `nombre_es`, `nombre_en`, `nivel` (1 continente, 2 subregión, 3 región intermedia), `region_padre_id` (FK a sí misma). Ejemplo: América del Sur (5) → América Latina y el Caribe (419) → América (19).

**`dim_region_bm`** (7) y **`dim_nivel_ingreso`** (4): catálogos del Banco Mundial con nombre en inglés y español; el nivel de ingreso trae `orden` (1 = bajo ... 4 = alto) para ordenar gráficos.

**`dim_region_subnacional`** (6): agrupaciones de provincias. Hoy, las regiones de la EPH del INDEC (GBA, Noroeste, Noreste, Cuyo, Pampeana, Patagonia), que son las que usan las canastas y la pobreza. Columnas: `region_subnacional_id` (código EPH), `pais_id`, `sistema`, `nombre`.

**`pais_equivalencia`** / **`subdivision_equivalencia`**: `(pais_id | subdivision_id, sistema, tipo, valor)`, con PK `(sistema, valor)` para que un mismo código no apunte a dos lugares. Sistemas cargados: nombres en español e inglés, nombre del Banco Mundial y del World Happiness Report, código ILOSTAT, código y abreviatura de Correlates of War, iso2 del Banco Mundial; en provincias, código INDEC, código GAUL del CCKP y alias ("CABA", "Capital Federal", "Estado Nacional").

**`rel_reclamo_territorial`**: `(pais_id, pais_reclamante_id, subdivision_reclamante_id, descripcion)`. Malvinas y Georgias del Sur (reclamadas por Argentina como parte de Tierra del Fuego, `AR-V`), los 7 reclamos antárticos, Sahara Occidental y Taiwán.

### Relaciones internacionales

| Tabla | Clave primaria | Qué guarda |
|---|---|---|
| `dim_organizacion` | `organizacion_codigo` | 48 organizaciones: nombre y tipo (económica, militar...) |
| `rel_pais_organizacion` | `pais_id, organizacion_codigo, anio_ingreso` | episodios de membresía: estado, ingreso, salida, fuente |
| `dim_acuerdo_comercial` | `acuerdo_id` (número DESTA) | 842 acuerdos: nombre, tipo, región, si está notificado a la OMC |
| `rel_pais_acuerdo_comercial` | `pais_id, acuerdo_id` | qué país está en qué acuerdo, fundador o adhesión, años de firma y vigor |
| `rel_alianza_militar_anual` | `pais_a_id, pais_b_id, anio` | pares de países con pacto (ATOP), 1945-2018 |
| `hecho_pais_relaciones_anual` | `pais_id, anio` | los 4 conteos que no se pueden recalcular (IGO de COW, acuerdos en vigor, aliados) |
| `rel_pais_frontera` | `pais_id, codigo_gec, vecino_nombre_factbook` → `vecino_pais_id` FK `dim_pais` | vecinos terrestres con km de frontera (CIA World Factbook, enero 2026) |
| `rel_pais_socio_comercial` | `pais_id, codigo_gec, flujo, rango` → `socio_pais_id` FK `dim_pais` | 5 principales destinos de exportación y orígenes de importación (Factbook, datos 2023) |

### CIA World Factbook (foto de enero 2026)

Ver `etl/factbook/GUIA_FACTBOOK.md`. Solo se tomó lo que no daban otras fuentes. Las tablas llevan `codigo_gec` (código de la CIA) en la clave porque Palestina son dos fichas: Cisjordania y Gaza.

| Tabla | Clave primaria | Qué guarda |
|---|---|---|
| `hecho_pais_perfil_factbook` | `pais_id, codigo_gec` | superficie, costa, elevación, clima, recursos, tipo de gobierno, sistema legal, independencia, edad de voto, servicio militar |
| `rel_pais_composicion` | `pais_id, codigo_gec, dimension, orden` | religiones, etnias e idiomas con su % (`dimension` = religion / etnia / idioma) |

### Hechos por país y por provincia

| Tabla | Clave primaria | Años |
|---|---|---|
| `hecho_pais_anual` | `pais_id, anio` | 2000-2024 (41 indicadores de los pasos 1 y 2) |
| `hecho_subdivision_poblacion` | `subdivision_id, anio` | 2010-2040 |
| `hecho_subdivision_economia` | `subdivision_id, anio` | 2004-2024 (`poblacion` pasó a llamarse `poblacion_implicita_vab` para no confundirla con la del INDEC) |
| `hecho_subdivision_vab_rama` | `subdivision_id, anio, rama_nro` → FK `dim_rama_cepal` | 2004-2024 |
| `hecho_subdivision_hidrocarburos` | `subdivision_id, anio` | 2009-2026 |
| `hecho_subdivision_agricultura` | `subdivision_id, anio_cosecha, cultivo` | 1970-2026 |
| `hecho_subdivision_ganaderia`, `_clima`, `_salud`, `_empresas`, `_pymes`, `_fiscal`, `_salarios`, `_canastas`, `_pobreza`, `_turismo`, `_gobierno` | `subdivision_id, anio` | según la fuente |
| `hecho_subdivision_censo` | `subdivision_id, anio_censo` | 2010 y 2022 |
| `hecho_subdivision_alicuota_iibb` | `subdivision_id, anio, actividad` | 2024-2025 |
| `hecho_subdivision_eleccion_gobernador` | `subdivision_id, anio_eleccion` | 1983-2025 |
| `hecho_subdivision_legisladores` | `subdivision_id, anio, camara` | 1984-2026 |

Fuente, grano, filas y años de cada tabla: `ref_catalogo_tabla`.

#### Seis dimensiones nuevas (octubre 2026)

Las baja `etl/fuentes_nuevas/extraer_dimensiones_nuevas.py`; el porqué de cada fuente está en `etl/fuentes_nuevas/FUENTES_DIMENSIONES_NUEVAS.md`.

| Tabla | Clave primaria | Años | Qué guarda (fuente) |
|---|---|---|---|
| `hecho_pais_migracion_anual` | `pais_id, anio` | 2000-2025 | saldo migratorio, stock de migrantes, remesas recibidas y enviadas (BM: ONU WPP, FMI) |
| `hecho_pais_emisiones` | `pais_id, anio` | 2000-2025 | GEI total y per cápita, CO2, % renovable en consumo final y en electricidad, afectados y muertos por desastres climáticos (BM, OWID: Ember, EM-DAT) |
| `hecho_pais_capital_social` | `pais_id, anio` | 2000-2025 | confianza interpersonal y en instituciones (Latinobarómetro vía CEPAL, 18 países), confianza WVS (por ola), sociedad civil (V-Dem) |
| `hecho_pais_diversidad_cultural` | `pais_id, anio` | 2000-2023 | la constitución protege lenguas / derechos indígenas / derechos culturales, 0/1 (Comparative Constitutions Project) |
| `hecho_pais_poblacion_indigena` | `pais_id, decada_censal` | censos 2000-2020 | % de población indígena, 17 países de América Latina (CELADE) |
| `hecho_pais_institucional_gobernanza` | `pais_id, anio` | 2000-2025 | 6 indicadores WGI (estimación de −2,5 a 2,5 y percentil 0-100), actores con veto (DPI, hasta 2020), democracia, estado de derecho y corrupción (V-Dem) |
| `hecho_pais_financiero_deuda` | `pais_id, anio` | 2000-2026 | PIB en US$, deuda externa (QEDS para todos; IDS para países en desarrollo), servicio de deuda, deuda del gobierno central, reservas, spread EMBIG promedio del año (8 países, BCRP) |
| `hecho_pais_salud_cronica` | `pais_id, anio` | 2000-2024 | diabetes, hipertensión, obesidad, mortalidad por enfermedades no transmisibles, AVAD totales (BM, OMS) |
| `hecho_pais_tecnologia` | `pais_id, anio` | 2000-2025 | banda ancha fija, usuarios de internet, I+D % PIB (BM), hogares con internet (OCDE) |
| `hecho_subdivision_financiero` | `subdivision_id, anio` | 2000-2025 | stock de deuda provincial al 31-12 por acreedor y servicios (amortización, intereses), millones de $ |
| `hecho_subdivision_finanzas_publicas` | `subdivision_id, anio` | 2005-2025 | esquema Ahorro-Inversión-Financiamiento: ingresos tributarios propios y nacionales, coparticipación, regalías, transferencias, gasto, resultado, millones de $ |
| `hecho_subdivision_ambiental` | `subdivision_id, anio` | 2000-2023 | GEI por sector en 155 regiones de ARG, BRA, CHL, COL, MEX y PER (OCDE) |
| `hecho_subdivision_tecnologia` | `subdivision_id, anio` | 2014-2026 | accesos a internet fijo cada 100 hogares y habitantes (ENACOM, último trimestre del año) |

Qué quedó afuera y por qué: calificaciones de S&P/Moody's (no hay una fuente abierta descargable: carga manual pendiente), deuda provincial en moneda extranjera (no se publica por provincia), membresía en organizaciones civiles (microdatos WVS con registro) y cantidad de eventos climáticos por país (EM-DAT pide registro; se usan afectados y muertos).

#### Indicadores sociales y digitales (octubre 2026)

Las baja `etl/indicadores_sociales_digitales/extraer_indicadores_sociales.py` (6 tablas); qué fuente se usó para cada tema y cuáles no tienen fuente pública comparable está en `etl/indicadores_sociales_digitales/FUENTES_INDICADORES_SOCIALES.md`.

| Tabla | Clave primaria | Años | Qué guarda (fuente) |
|---|---|---|---|
| `hecho_pais_educacion` | `pais_id, anio` | 2000-2025 | alfabetización de adultos (total, mujeres, hombres) y de jóvenes; % de 25+ que completó al menos primaria, secundaria baja/alta, postsecundaria, terciaria corta, licenciatura, maestría, doctorado; años promedio de escolaridad (UIS), años esperados y ajustados por aprendizaje (Índice de Capital Humano) (BM) |
| `hecho_pais_digital_ocio` | `pais_id, anio` | 2005-2025 | % que usa redes sociales y % que compró videojuegos o software por internet, 16-74 y 16-24 años; % que compró algo por internet (OCDE, 43 países) |
| `hecho_pais_empleo_sectorial` | `pais_id, anio` | 2000-2025 | empleo total y en construcción (OIT modelado, 188 países); empleo en artes y espectáculos, bibliotecas y museos, y juegos de azar y apuestas (encuestas de la OIT, 117-139 países) |
| `hecho_pais_gasto_cultura` | `pais_id, anio` | 2000-2025 | gasto público en recreación, cultura y religión y en servicios culturales, % PIB y % del gasto, gobierno general (89 países) y central (93); US$ PPA (FMI GFS COFOG; OCDE para Chile, Colombia y US$ PPA) |
| `hecho_pais_deporte_olimpico` | `pais_id, anio` | 2000-2026 | Juegos de verano o invierno, atletas (total y mujeres), medallas de oro, plata y bronce (Olympedia, 206 países) |
| `hecho_pais_consolas_comercio` | `pais_id, anio` | 2000-2025 | importaciones y exportaciones de consolas de videojuegos en US$ (UN Comtrade, 198 países) |

### Vistas para el dashboard

| Vista | Qué devuelve |
|---|---|
| `v_pais` | un país por fila con todo legible: continente, subregión, región BM, nivel de ingreso, soberano, cantidad de subdivisiones |
| `v_subdivision` | una subdivisión por fila con país, región EPH y si también es país |
| `v_pais_anual` | el panel país-año completo + conteos de alianzas (lo que antes era `paises_anual.csv` + `alianzas_pais_anual.csv`) |
| `v_subdivision_anual` | una fila por subdivisión y año con todas las tablas subdivisión-año juntas (desde octubre 2026 incluye las regiones de 5 países más por las emisiones OCDE) (columnas repetidas llevan el tema adelante: `turismo_meses_con_dato`) |
| `v_pais_membresia_anual` | país-año-organización en formato largo, calculado desde los episodios |
| `v_vab_provincia_grupo` | VAB por provincia, año y grupo de sectores |
| `v_control_poblacion_pais_vs_subdivisiones` | suma de provincias contra el total país |
| `v_pais_migracion_anual` | tasa de migración neta por 1.000 hab., remesas enviadas % del PIB, remesas netas |
| `v_pais_financiero_deuda` | deuda externa % del PIB y reservas % de la deuda externa |
| `v_pais_capital_social` | desconfianza promedio en jueces y partidos/congreso |
| `v_pais_diversidad_cultural` | fragmentación étnica, lingüística y religiosa (1 − Σp², desde `rel_pais_composicion`), última constitución y último censo indígena |
| `v_pais_salud_cronica` | AVAD por 100.000 hab. |
| `v_pais_indicadores_sociales` | resumen de los temas sociales: brecha de alfabetización hombres − mujeres, empleo en construcción, cultura y apuestas como % del empleo, gasto en servicios culturales % del PIB, medallas por millón de hab., % de atletas mujeres, importaciones de consolas por habitante y netas |
| `v_subdivision_financiero` | servicio de deuda e intereses % de ingresos corrientes, deuda % de ingresos totales |
| `v_subdivision_federalismo_fiscal` | % de ingresos por transferencias automáticas, autonomía financiera, transferencias discrecionales % del gasto, regalías y resultado % de ingresos |

### Casos especiales

- **Dependencias territoriales.** `tipo_entidad` distingue: `estado_miembro_onu` (193), `estado_observador_onu` (Vaticano, Palestina), `estado_reconocimiento_limitado` (Taiwán, Kosovo), `estado_libre_asociado` (Islas Cook, Niue), `territorio_dependiente` (32: Malvinas, Puerto Rico, Bermudas...), `departamento_de_ultramar` (Guadalupe, Martinica, Guayana Francesa, Reunión, Mayotte: son Francia), `pais_constituyente` (Aruba, Curazao, Groenlandia...), `region_administrativa_especial` (Hong Kong, Macao), `dependencia_de_la_corona` (Jersey, Guernsey, Man), `region_autonoma` (Åland), `municipio_especial` (Caribe Neerlandés), `territorio_en_disputa` (Sahara Occidental), `territorio_internacional` (Antártida) y `agrupacion_estadistica` (Islas del Canal, que el Banco Mundial publica juntas). `pais_soberano_id` dice de quién dependen.
- **No contar dos veces.** 30 subdivisiones también son países: Puerto Rico es `US-PR` dentro de EE. UU. y `PRI` en el panel. Para sumar subdivisiones sin duplicar: `WHERE pais_equivalente_id IS NULL`.
- **Producción en el mar.** Petróleo y gas offshore figuran como "Estado Nacional": quedó como subdivisión `AR-offshore` con `es_iso_3166_2 = 0`, así no se mezcla con las 24 jurisdicciones.
- **Códigos que no son ISO.** Kosovo (`XKX`) e Islas del Canal (`CHI`) usan ids 901 y 902 (ISO reserva 900-999 para uso propio). ILOSTAT llama `KOS` a Kosovo: está en `pais_equivalencia`.
- **Sin región M49.** La ONU no ubica a Taiwán, Kosovo ni Islas del Canal: se cargaron a mano en Asia Oriental, Europa del Sur y Europa del Norte.
- **Códigos de la CIA.** El Factbook usa códigos propios (`au` = Austria, `gm` = Alemania). Están en `pais_equivalencia` con `sistema = 'codigo_gec_cia_factbook'`.
- **Namibia se llama `NA`.** Al leer los CSV con pandas usar `keep_default_na=False, na_values=[""]`, o pandas lo convierte en vacío.

---

## 3. Ejemplo práctico: Argentina y tres de sus provincias

Datos reales sacados de la base (año 2022).

```json
{
  "pais": {
    "pais_id": 32, "iso3": "ARG", "iso2": "AR", "iso_numerico": "032",
    "nombre_es": "Argentina", "nombre_oficial_en": "Argentine Republic",
    "region_geografica_id": 5, "region_bm_codigo": "LCN", "nivel_ingreso_codigo": "UMC",
    "capital": "Buenos Aires", "tipo_entidad": "estado_miembro_onu", "es_miembro_onu": 1,
    "pais_soberano_id": null,
    "_vista_v_pais": {"continente": "América", "subregion": "América Latina y el Caribe",
                      "region_intermedia": "América del Sur", "nivel_ingreso": "Ingreso mediano alto",
                      "n_subdivisiones_nivel1": 24},
    "hecho_pais_anual_2022": {"poblacion": 45407904, "pib_pc_ppp": 27825.03, "esperanza_vida": 75.81,
                              "gini": 40.7, "felicidad": 6.024}
  },
  "subdivisiones": [
    {
      "subdivision_id": 210, "pais_id": 32, "codigo": "AR-C", "nombre": "Ciudad de Buenos Aires",
      "nombre_iso": "Ciudad Autónoma de Buenos Aires", "tipo_es": "ciudad", "nivel": 1,
      "region_subnacional_id": 1,
      "equivalencias": {"codigo_indec": "02", "codigo_gaul1_cckp": "ARG.1212430",
                        "nombre_en_fuentes": ["CABA", "Capital Federal", "Ciudad Autónoma de Buenos Aires"]},
      "v_subdivision_anual_2022": {"habitantes": 3081550, "pbg_per_capita_pesos_2004": 38642.0,
                                   "salario_promedio_mensual_pesos_2024": 1522733,
                                   "pct_personas_pobres_estimado": 16.2, "pct_hogares_cloaca": 98.79,
                                   "familia_politica_gobierno": "PRO / Juntos por el Cambio"}
    },
    {
      "subdivision_id": 229, "pais_id": 32, "codigo": "AR-X", "nombre": "Córdoba",
      "tipo_es": "provincia", "nivel": 1, "region_subnacional_id": 43,
      "equivalencias": {"codigo_indec": "14", "codigo_gaul1_cckp": "ARG.1212434"},
      "v_subdivision_anual_2022": {"habitantes": 3835738, "pbg_per_capita_pesos_2004": 13456.9,
                                   "salario_promedio_mensual_pesos_2024": 1072394,
                                   "pct_personas_pobres_estimado": 39.5, "pct_hogares_cloaca": 44.99,
                                   "familia_politica_gobierno": "peronismo"}
    },
    {
      "subdivision_id": 227, "pais_id": 32, "codigo": "AR-V", "nombre": "Tierra del Fuego",
      "tipo_es": "provincia", "nivel": 1, "region_subnacional_id": 44,
      "reclamos_asociados": ["FLK (Islas Malvinas)", "SGS (Georgias y Sandwich del Sur)", "ATA (Antártida Argentina)"],
      "v_subdivision_anual_2022": {"habitantes": 181983, "pbg_per_capita_pesos_2004": 32140.3,
                                   "salario_promedio_mensual_pesos_2024": 1680694,
                                   "pct_personas_pobres_estimado": 26.9, "pct_hogares_cloaca": 90.25,
                                   "familia_politica_gobierno": "peronismo"}
    }
  ],
  "dim_region_subnacional": [
    {"region_subnacional_id": 1, "nombre": "GBA"}, {"region_subnacional_id": 43, "nombre": "Pampeana"},
    {"region_subnacional_id": 44, "nombre": "Patagonia"}
  ]
}
```

Las claves que se ven repetidas (`pais_id: 32`, `region_subnacional_id: 43`) son justamente las uniones: cada provincia "sabe" a qué país pertenece por `pais_id`, y nada más se repite.

### Las mismas relaciones en SQL

**De país a provincias (1:N):** población y VAB de 2022 por región EPH.

```sql
SELECT r.nombre AS region_eph,
       SUM(p.habitantes) AS habitantes,
       ROUND(SUM(e.vab_total_mill_pesos_2004)) AS vab_mill_pesos_2004
FROM dim_pais pa
JOIN dim_subdivision d            ON d.pais_id = pa.pais_id
JOIN dim_region_subnacional r     ON r.region_subnacional_id = d.region_subnacional_id
JOIN hecho_subdivision_poblacion p ON p.subdivision_id = d.subdivision_id AND p.anio = 2022
LEFT JOIN hecho_subdivision_economia e ON e.subdivision_id = d.subdivision_id AND e.anio = 2022
WHERE pa.iso3 = 'ARG'
GROUP BY r.nombre
ORDER BY habitantes DESC;
```

| region_eph | habitantes | vab_mill_pesos_2004 |
|---|---|---|
| GBA | 20.957.293 | 315.514 |
| Pampeana | 9.200.967 | 123.253 |
| Noroeste | 5.805.228 | 47.794 |
| Noreste | 4.270.522 | 29.085 |
| Cuyo | 3.348.603 | 33.976 |
| Patagonia | 2.652.217 | 54.881 |

**De provincia a país (N:1):** poner el dato nacional al lado del provincial.

```sql
SELECT d.nombre AS provincia, s.salario_promedio_mensual_pesos_2024, h.pib_pc_ppp AS pib_pc_ppp_pais
FROM v_subdivision_anual s
JOIN dim_subdivision d ON d.codigo = s.codigo
JOIN hecho_pais_anual h ON h.pais_id = d.pais_id AND h.anio = s.anio
WHERE s.anio = 2022;
```

**Traducir un nombre de una fuente al código del proyecto:**

```sql
SELECT p.iso3 FROM pais_equivalencia e JOIN dim_pais p USING (pais_id)
WHERE e.sistema = 'nombre_world_happiness_report' AND e.valor = 'DR Congo';   -- COD
```

## Cómo sumar una fuente nueva

1. Si es por país: que el CSV tenga `iso3` (o un nombre que esté en `pais_equivalencia`). Si es por provincia: `provincia_iso` con el código ISO 3166-2.
2. Agregar el archivo a `TABLAS_PROVINCIA` (o una función como `leer_paises`) en `construir_master.py`, con su clave y su fuente.
3. Volver a correr el script: si algún código no existe en las dimensiones, el script se detiene y dice cuál.
4. Para sumar provincias de otro país no hace falta tocar `dim_subdivision`: las 3.590 subdivisiones del mundo ya están cargadas.
