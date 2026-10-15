# 5 KPIs multidimensionales

Cinco indicadores compuestos que cruzan al menos tres dimensiones (Demográfica, Salud Pública, Socio-Antropológica, Económica, Geopolítica y Constitucional/Fiscal). Están calculados de verdad sobre la base del proyecto, no sobre un esquema imaginario.

| Archivo | Qué es |
|---|---|
| `kpis_multidimensionales.sql` | las 5 consultas (más 2 de lectura complementaria), listas para correr |
| `calcular_kpis.py` | corre el SQL sobre la base y guarda cada resultado en `resultados/` |
| `resultados/*.csv` | la salida de cada KPI (corrida del 14-10-2026) |

## Cómo se corre

Las consultas usan la base `etl/modelo_unificado/master_paises_provincias.sqlite` y sus vistas **`v_pais_anual`** (país × año, 217 países, 2000-2024) y **`v_subdivision_anual`** (provincia × año, 24 provincias argentinas), más algunas tablas `rel_` y `hecho_` del mismo modelo. No hizo falta inventar ninguna vista: las dos ya existían.

```bash
python etl/kpis/calcular_kpis.py
```

También se puede abrir el `.sql` entero en DB Browser for SQLite o DBeaver y ejecutarlo: cada KPI crea una **vista temporal** (`kpi1_iese` … `kpi5_irfh`) que no toca la base y desaparece al cerrar la conexión. Requiere SQLite 3.35 o más nuevo (funciones de ventana, `ln`, `sqrt`); el de Python 3.13 trae la 3.45. Las 7 consultas tardan menos de medio segundo en total.

### Dos trucos de SQL que se repiten

- **Puntaje z sin `STDDEV`.** SQLite no tiene desvío estándar, así que se calcula como `sqrt(AVG(x*x) - AVG(x)*AVG(x))`. Un puntaje z dice a cuántos desvíos del promedio está cada país: 0 = promedio, +1 = un desvío arriba. Sirve para sumar cosas que tienen unidades distintas (años, %, puntos).
- **Regresión en una línea.** La pendiente de una recta de mínimos cuadrados es `(AVG(x*y) - AVG(x)*AVG(y)) / (AVG(x*x) - AVG(x)^2)`. Con eso se calcula el valor "esperado" de cada país y el **residuo** (lo observado menos lo esperado).
- **"Último dato disponible".** Gini y felicidad no se publican todos los años. `ROW_NUMBER() OVER (PARTITION BY iso3 ORDER BY anio DESC)` toma el último año con dato dentro de una ventana (por ejemplo, 2014-2021).

### Mapa de dimensiones

| KPI | Demográfica | Salud | Socio-antropológica | Económica | Geopolítica | Constitucional/Fiscal |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| 1. IESE eficiencia sanitaria | ● | ● | | ● | | ● |
| 2. IPFS paradoja felicidad-suicidio | ● | ● | ● | ● | | |
| 3. IEG exposición geoeconómica | ● | | | ● | ● | ● |
| 4. ITID tensión identitaria-distributiva | | | ● | ● | | ● |
| 5. IRFH rentismo fiscal provincial | | | ● | ● | | ● |

---

## KPI 1 · Índice de Eficiencia Sanitaria Estructural

**Código:** `KPI1_SAL_EFI_IESE` · **Grano:** país, año 2021 · **186 países**

### Fundamento teórico-interdisciplinario

- **Curva de Preston (demografía económica, 1975):** la esperanza de vida sube con el ingreso, pero con rendimientos decrecientes (por eso se usa el logaritmo del PIB per cápita). Lo interesante no es la esperanza de vida en sí, sino cuánto se aparta un país de lo que "le corresponde" por su riqueza.
- **Economía de la salud / eficiencia del gasto público:** dos países con el mismo resultado no son igual de eficientes si uno gasta el doble. El gasto del gobierno en salud (% del PIB, indicador `SH.XPD.GHED.GD.ZS`) entra como insumo que se descuenta.
- **Transición demográfica:** la mortalidad infantil es el indicador más sensible a la atención primaria y a la pobreza; se agrega para que el KPI no dependa solo de la longevidad de los adultos mayores.
- **Equidad:** el Gini clasifica a cada país en "desigualdad alta" (≥ 40) o no, porque un buen promedio puede esconder brechas.

**Fórmula**

```
residuo_EV    = esperanza de vida observada − esperada según ln(PIB pc PPA)
residuo_lnMI  = ln(mortalidad infantil) observada − esperada según ln(PIB pc PPA)
resultado     = (z(residuo_EV) − z(residuo_lnMI)) / 2
IESE          = resultado − 0,5 × z(gasto público en salud % PIB)
```

El gasto pesa la mitad porque una parte de su efecto ya está en el PIB per cápita y porque es insumo, no resultado.

### Consulta SQL

```sql
-- name: KPI1_SAL_EFI_IESE
-- Índice de Eficiencia Sanitaria Estructural (IESE), año 2021.
-- Salud pública × Económica × Fiscal × Demográfica (mortalidad infantil).
DROP VIEW IF EXISTS kpi1_iese;
CREATE TEMP VIEW kpi1_iese AS
WITH param AS (SELECT 2021 AS anio_ref),
base AS (
    SELECT p.iso3, p.pais, p.continente, p.nivel_ingreso,
           p.esperanza_vida          AS ev,
           ln(p.mortalidad_infantil) AS ln_mi,
           p.gasto_salud_pct_pib     AS gasto,
           ln(p.pib_pc_ppp)          AS x
    FROM v_pais_anual p CROSS JOIN param
    WHERE p.anio = param.anio_ref
      AND p.esperanza_vida IS NOT NULL
      AND p.mortalidad_infantil > 0
      AND p.pib_pc_ppp > 0
      AND p.gasto_salud_pct_pib IS NOT NULL
),
gini_ultimo AS (          -- último Gini publicado en los 7 años anteriores
    SELECT iso3, gini, anio AS anio_gini
    FROM (SELECT p.iso3, p.gini, p.anio,
                 ROW_NUMBER() OVER (PARTITION BY p.iso3 ORDER BY p.anio DESC) AS rn
          FROM v_pais_anual p CROSS JOIN param
          WHERE p.gini IS NOT NULL
            AND p.anio BETWEEN param.anio_ref - 7 AND param.anio_ref)
    WHERE rn = 1
),
curva_preston AS (        -- dos regresiones simples sobre ln(PIB pc)
    SELECT AVG(x) AS mx, AVG(ev) AS mev, AVG(ln_mi) AS mmi,
           (AVG(x*ev)    - AVG(x)*AVG(ev))    / (AVG(x*x) - AVG(x)*AVG(x)) AS b_ev,
           (AVG(x*ln_mi) - AVG(x)*AVG(ln_mi)) / (AVG(x*x) - AVG(x)*AVG(x)) AS b_mi,
           AVG(gasto) AS m_gasto,
           sqrt(AVG(gasto*gasto) - AVG(gasto)*AVG(gasto)) AS sd_gasto
    FROM base
),
residuos AS (
    SELECT b.*, c.m_gasto, c.sd_gasto,
           b.ev    - (c.mev + c.b_ev * (b.x - c.mx)) AS res_ev,    -- años de vida sobre/bajo la curva
           b.ln_mi - (c.mmi + c.b_mi * (b.x - c.mx)) AS res_ln_mi  -- >0 = más mortalidad que la esperada
    FROM base b CROSS JOIN curva_preston c
),
estandarizado AS (        -- los residuos de MCO tienen media 0: z = res / desvío
    SELECT r.*,
           res_ev    / sqrt(AVG(res_ev*res_ev)       OVER ()) AS z_res_ev,
           res_ln_mi / sqrt(AVG(res_ln_mi*res_ln_mi) OVER ()) AS z_res_mi,
           (gasto - m_gasto) / sd_gasto                       AS z_gasto
    FROM residuos r
)
SELECT e.iso3, e.pais, e.continente, e.nivel_ingreso,
       round(exp(e.x), 0)                   AS pib_pc_ppp,
       round(e.ev, 1)                       AS esperanza_vida,
       round(exp(e.ln_mi), 1)               AS mortalidad_infantil,
       round(e.gasto, 2)                    AS gasto_salud_publico_pct_pib,
       round(e.res_ev, 2)                   AS anios_sobre_curva_preston,
       round((e.z_res_ev - e.z_res_mi) / 2, 3)                       AS resultado_sanitario_z,
       round((e.z_res_ev - e.z_res_mi) / 2 - 0.5 * e.z_gasto, 3)     AS iese,
       g.gini, g.anio_gini,
       CASE WHEN (e.z_res_ev - e.z_res_mi) / 2 >= 0 AND e.z_gasto <  0 THEN 'eficiente (más salud, menos gasto)'
            WHEN (e.z_res_ev - e.z_res_mi) / 2 >= 0 AND e.z_gasto >= 0 THEN 'intensivo (más salud, más gasto)'
            WHEN (e.z_res_ev - e.z_res_mi) / 2 <  0 AND e.z_gasto <  0 THEN 'subinvertido (menos salud, menos gasto)'
            ELSE 'ineficiente (menos salud, más gasto)' END            AS cuadrante,
       CASE WHEN g.gini >= 40 THEN 'desigualdad alta' WHEN g.gini IS NULL THEN 'sin dato' ELSE 'desigualdad moderada/baja' END AS filtro_equidad
FROM estandarizado e
LEFT JOIN gini_ultimo g ON g.iso3 = e.iso3
;

SELECT * FROM kpi1_iese ORDER BY iese DESC;
```

### Criterio de interpretación

| Valor | Qué indica | Lectura de política pública |
|---|---|---|
| IESE > 0,5 | El país vive más (y pierde menos bebés) de lo que su ingreso predice, gastando poco | Modelo a estudiar: atención primaria, prevención, organización del sistema |
| IESE ≈ 0 | Resultado acorde a su riqueza y su gasto | Margen de mejora en gestión más que en presupuesto |
| IESE < −0,5 | Peor salud que la esperada **y/o** mucho gasto para lo que logra | Auditar el gasto (fragmentación, precios, hospitalocentrismo) y los determinantes sociales |

El **cuadrante** es más útil que el número para decidir: *subinvertido* pide más presupuesto; *ineficiente* pide reformar cómo se gasta; *intensivo* es un buen resultado caro; *eficiente* es el benchmark. Conviene comparar dentro del mismo nivel de ingreso (columna `nivel_ingreso`), porque los primeros puestos generales son países pobres con gasto muy bajo.

**Resultado 2021.** Entre los países de ingreso alto lideran Corea del Sur (0,92), San Marino, Grecia, Israel, Eslovenia, Portugal y España. Estados Unidos queda 181.º de 186: vive 3,9 años menos que lo que predice su PIB y gasta 9,6 % del PIB público en salud. **Argentina** es 147.ª (IESE −0,67): 0,6 años por debajo de la curva, 6,35 % del PIB de gasto público y Gini 42,4, cuadrante *ineficiente*. Chile y Costa Rica están por encima de la curva (+3,7 y +4,0 años) gastando menos que Argentina (5,2 y 5,4 % del PIB).

**Limitación:** 2021 incluye el exceso de mortalidad por COVID-19, que castiga a quien tuvo más muertes ese año.

---

## KPI 2 · Índice de Paradoja Felicidad-Suicidio

**Código:** `KPI2_PSI_PARADOJA_IPFS` · **Grano:** país, año 2021 · **142 países**

### Fundamento teórico-interdisciplinario

- **Sociología de Durkheim (*El suicidio*, 1897):** el suicidio es un hecho social, no solo individual; sube con la anomia (normas débiles) y con el exceso o falta de integración.
- **"Paradoja de los lugares felices" (Daly, Oswald, Wilson y Wu, 2011):** los países y estados con más satisfacción con la vida suelen tener tasas de suicidio *más altas*. Una explicación es la comparación social: ser infeliz rodeado de gente feliz pesa más.
- **Demografía de género:** los hombres se suicidan entre 2 y 4 veces más que las mujeres en casi todo el mundo (masculinidad, consumo de alcohol, menor consulta). La razón hombres/mujeres separa sociedades con un problema concentrado en varones.
- **Economía del bienestar:** la felicidad del World Happiness Report (promedio de tres años) mide bienestar subjetivo; el Gini permite ver si la paradoja convive con desigualdad.

**Fórmula**

```
IPFS = MIN( z(felicidad), z(suicidio por 100.000) )
```

Se usa el **mínimo** y no el promedio: el índice solo es alto si las dos cosas son altas a la vez. Un país muy feliz con poco suicidio, o uno con mucho suicidio pero infeliz, no es paradójico.

### Consulta SQL

```sql
-- name: KPI2_PSI_PARADOJA_IPFS
-- Índice de Paradoja Felicidad-Suicidio (IPFS), año 2021.
-- Salud mental × Socio-antropológica (bienestar subjetivo) × Demográfica (género) × Económica.
DROP VIEW IF EXISTS kpi2_ipfs;
CREATE TEMP VIEW kpi2_ipfs AS
WITH param AS (SELECT 2021 AS anio_ref),
base AS (
    SELECT p.iso3, p.pais, p.continente, p.nivel_ingreso, p.pib_pc_ppp,
           p.felicidad, p.suicidio_total_x100k AS suicidio,
           p.suicidio_hombres_x100k / NULLIF(p.suicidio_mujeres_x100k, 0) AS razon_h_m
    FROM v_pais_anual p CROSS JOIN param
    WHERE p.anio = param.anio_ref
      AND p.felicidad IS NOT NULL
      AND p.suicidio_total_x100k IS NOT NULL
),
gini_ultimo AS (
    SELECT iso3, gini
    FROM (SELECT p.iso3, p.gini,
                 ROW_NUMBER() OVER (PARTITION BY p.iso3 ORDER BY p.anio DESC) AS rn
          FROM v_pais_anual p CROSS JOIN param
          WHERE p.gini IS NOT NULL AND p.anio BETWEEN param.anio_ref - 7 AND param.anio_ref)
    WHERE rn = 1
),
momentos AS (
    SELECT AVG(felicidad) AS m_f, sqrt(AVG(felicidad*felicidad) - AVG(felicidad)*AVG(felicidad)) AS sd_f,
           AVG(suicidio)  AS m_s, sqrt(AVG(suicidio*suicidio)   - AVG(suicidio)*AVG(suicidio))   AS sd_s
    FROM base
),
z AS (
    SELECT b.*, (b.felicidad - m.m_f) / m.sd_f AS z_felicidad,
                (b.suicidio  - m.m_s) / m.sd_s AS z_suicidio
    FROM base b CROSS JOIN momentos m
)
SELECT z.iso3, z.pais, z.continente, z.nivel_ingreso,
       round(z.felicidad, 2)       AS felicidad_0a10,
       round(z.suicidio, 1)        AS suicidio_x100k,
       round(z.razon_h_m, 1)       AS razon_suicidio_hombres_mujeres,
       g.gini,
       round(z.z_felicidad, 2)     AS z_felicidad,
       round(z.z_suicidio, 2)      AS z_suicidio,
       round(min(z.z_felicidad, z.z_suicidio), 3) AS ipfs,   -- alto solo si AMBOS son altos
       CASE WHEN z.z_felicidad >= 0 AND z.z_suicidio >= 0 THEN 'paradoja (feliz y con suicidio alto)'
            WHEN z.z_felicidad >= 0 AND z.z_suicidio <  0 THEN 'bienestar consistente'
            WHEN z.z_felicidad <  0 AND z.z_suicidio >= 0 THEN 'malestar consistente'
            ELSE 'malestar con suicidio bajo (posible subregistro)' END AS cuadrante
FROM z
LEFT JOIN gini_ultimo g ON g.iso3 = z.iso3
;

SELECT * FROM kpi2_ipfs ORDER BY ipfs DESC;
```

### Criterio de interpretación

| Valor | Qué indica | Lectura de política pública |
|---|---|---|
| IPFS > 0,5 | Sociedad satisfecha en promedio pero con mucho suicidio | El bienestar promedio no protege a todos: buscar grupos rezagados (varones adultos, zonas rurales), acceso a salud mental, restricción de medios letales |
| IPFS entre 0 y 0,5 | Paradoja leve | Vigilancia epidemiológica y prevención focalizada |
| IPFS < 0 | No hay paradoja (ver el cuadrante) | *Malestar consistente*: crisis social amplia. *Malestar con suicidio bajo*: puede ser subregistro (estigma, mala certificación de causas de muerte) |

**Resultado 2021.** 41 de 142 países están en el cuadrante de paradoja. Encabezan Estados Unidos, Bélgica, Francia, Eslovenia, Finlandia, Austria, Suiza y Suecia. **Uruguay** es el caso latinoamericano más fuerte (9.º): felicidad 6,47 y 24,8 suicidios por 100.000, con 3,8 hombres por cada mujer. **Argentina** está en *bienestar consistente* (felicidad 5,97, suicidio 7,9). Corea del Sur tiene el suicidio más alto de los países ricos (27,5) pero felicidad apenas sobre el promedio, por eso su IPFS es 0,36.

**Limitación:** 57 países caen en "malestar con suicidio bajo", la mayoría de ingreso bajo, donde la OMS estima el suicidio con modelos por falta de registros vitales.

---

## KPI 3 · Índice de Exposición Geoeconómica

**Código:** `KPI3_GEO_EXPO_IEG` · **Grano:** país, comercio 2023 · **213 países**

### Fundamento teórico-interdisciplinario

- **Economía internacional:** el índice de Herfindahl-Hirschman (HHI = Σ participación², de 0 a 10.000) mide concentración. Un país que vende casi todo a un solo destino es vulnerable a un shock de ese mercado.
- **Interdependencia asimétrica (Keohane y Nye; Hirschman, 1945):** el comercio concentrado es poder para el comprador. Farrell y Newman (2019) lo llaman *interdependencia convertida en arma*.
- **Derecho internacional / constitucional:** un tratado de libre comercio o la pertenencia a un bloque (UE, Mercosur, ASEAN) da reglas y solución de controversias; en Argentina los tratados tienen jerarquía superior a las leyes (CN art. 75 inc. 22 y 24).
- **Geopolítica de alianzas (Gowa y Mansfield, 1993):** se comercia más y más seguro con aliados; un pacto de defensa (ATOP) baja el riesgo de que el comercio se use como presión.
- **Demografía:** los estados pequeños tienen mercados internos chicos y exportaciones naturalmente concentradas; la población se muestra para leerlo en contexto.

**Fórmula**

```
para cada uno de los 5 principales destinos de exportación (CIA World Factbook):
    respaldado = hay tratado comercial en vigor (DESTA, 2020)
              O ambos son miembros plenos del mismo bloque comercial preferencial (2024)
              O hay pacto de defensa (ATOP, 2018)
IEG = 10.000 × Σ (participación²) de los destinos NO respaldados
```

Es un HHI que solo cuenta la parte del comercio que queda "a la intemperie". Se excluyen OMC, APEC y OCDE porque no dan preferencias entre miembros.

### Consulta SQL

```sql
-- name: KPI3_GEO_EXPO_IEG
-- Índice de Exposición Geoeconómica (IEG): HHI de exportaciones hacia socios
-- SIN respaldo institucional (sin tratado comercial, bloque ni pacto de defensa).
-- Económica (comercio) × Geopolítica (alianzas) × Constitucional/jurídica (tratados) × Demográfica (tamaño).
DROP VIEW IF EXISTS kpi3_ieg;
CREATE TEMP VIEW kpi3_ieg AS
WITH param AS (SELECT 2020 AS anio_tratados,   -- DESTA llega a 2020
                      2018 AS anio_alianzas,   -- ATOP llega a 2018
                      2024 AS anio_bloques),
exportaciones AS (        -- top 5 destinos del CIA World Factbook (casi todo 2023)
    SELECT s.pais_id, s.socio_pais_id, s.anio, s.participacion_pct / 100.0 AS sh
    FROM rel_pais_socio_comercial s
    WHERE s.flujo = 'exportacion' AND s.socio_pais_id IS NOT NULL
),
cobertura AS (
    SELECT e.*,
           EXISTS (SELECT 1
                   FROM rel_pais_acuerdo_comercial a
                   JOIN rel_pais_acuerdo_comercial b ON b.acuerdo_id = a.acuerdo_id
                   CROSS JOIN param
                   WHERE a.pais_id = e.pais_id AND b.pais_id = e.socio_pais_id
                     AND a.anio_entrada_vigor <= param.anio_tratados
                     AND b.anio_entrada_vigor <= param.anio_tratados
                     AND (a.anio_salida IS NULL OR a.anio_salida > param.anio_tratados)
                     AND (b.anio_salida IS NULL OR b.anio_salida > param.anio_tratados)) AS con_tratado,
           EXISTS (SELECT 1
                   FROM rel_pais_organizacion a
                   JOIN rel_pais_organizacion b ON b.organizacion_codigo = a.organizacion_codigo
                   JOIN dim_organizacion o      ON o.organizacion_codigo = a.organizacion_codigo
                   CROSS JOIN param
                   WHERE a.pais_id = e.pais_id AND b.pais_id = e.socio_pais_id
                     AND o.tipo = 'económica-comercial'
                     AND o.organizacion_codigo NOT IN ('OMC', 'APEC', 'OCDE')   -- no son preferenciales
                     AND a.estado = 'pleno' AND b.estado = 'pleno'
                     AND a.anio_ingreso <= param.anio_bloques AND b.anio_ingreso <= param.anio_bloques
                     AND (a.anio_salida IS NULL OR a.anio_salida > param.anio_bloques)
                     AND (b.anio_salida IS NULL OR b.anio_salida > param.anio_bloques)) AS con_bloque,
           EXISTS (SELECT 1
                   FROM rel_alianza_militar_anual m CROSS JOIN param
                   WHERE m.anio = param.anio_alianzas AND m.defensa = 1
                     AND ((m.pais_a_id = e.pais_id AND m.pais_b_id = e.socio_pais_id)
                       OR (m.pais_b_id = e.pais_id AND m.pais_a_id = e.socio_pais_id))) AS con_defensa
    FROM exportaciones e
),
por_pais AS (
    SELECT pais_id, MAX(anio) AS anio_comercio,
           SUM(sh)                                             AS sh_top5,
           10000 * SUM(sh * sh)                                AS hhi_top5,
           SUM(CASE WHEN con_tratado OR con_bloque OR con_defensa THEN sh ELSE 0 END) AS sh_respaldado,
           10000 * SUM(CASE WHEN con_tratado OR con_bloque OR con_defensa THEN 0 ELSE sh * sh END) AS ieg,
           SUM(CASE WHEN con_defensa THEN sh ELSE 0 END)       AS sh_a_aliados_defensa
    FROM cobertura
    GROUP BY pais_id
)
SELECT v.iso3, v.nombre_es AS pais, v.continente, v.nivel_ingreso,
       pa.poblacion,
       x.anio_comercio,
       round(100 * x.sh_top5, 1)                           AS pct_export_top5,
       round(x.hhi_top5, 0)                                AS hhi_top5,
       round(100 * x.sh_respaldado / x.sh_top5, 1)         AS pct_top5_con_respaldo,
       round(100 * x.sh_a_aliados_defensa / x.sh_top5, 1)  AS pct_top5_a_aliados_defensa,
       round(x.ieg, 0)                                     AS ieg,
       CASE WHEN x.ieg >= 2500 THEN 'exposición alta'
            WHEN x.ieg >= 1000 THEN 'exposición media'
            ELSE 'exposición baja' END                     AS nivel,
       pr.n_acuerdos_comerciales_en_vigor, pr.n_aliados_defensa
FROM por_pais x
JOIN v_pais v ON v.pais_id = x.pais_id
LEFT JOIN hecho_pais_anual pa           ON pa.pais_id = x.pais_id AND pa.anio = 2023
LEFT JOIN hecho_pais_relaciones_anual pr ON pr.pais_id = x.pais_id AND pr.anio = 2018
WHERE x.sh_top5 > 0
  AND v.en_panel_bm = 1          -- solo los 217 países del panel (saca Tokelau, etc.)
;

SELECT * FROM kpi3_ieg ORDER BY ieg DESC;
```

### Criterio de interpretación

| Valor | Qué indica | Lectura de política pública |
|---|---|---|
| IEG ≥ 2.500 | Exposición alta (umbral del HHI de "mercado muy concentrado"): un destino grande sin reglas ni alianza | Prioridad para diversificar destinos y negociar acuerdos; riesgo de coerción económica |
| 1.000 a 2.500 | Exposición media | Diversificación gradual, seguros de crédito a la exportación |
| < 1.000 | Exposición baja: comercio diversificado o bien amparado | Mantener y profundizar acuerdos; vigilar dependencia de importaciones críticas |

`pct_top5_con_respaldo` y `hhi_top5` explican el porqué. México y Canadá tienen HHI altísimo (5.810 y 5.083, casi todo a EE. UU.) pero IEG casi 0, porque el T-MEC (y en Canadá también la OTAN) cubre ese comercio. Tuvalu, Kiribati, Nauru, Malí o Eritrea están concentrados y sin respaldo.

**Resultado.** 28 países con exposición alta, casi todos pequeños estados insulares y exportadores africanos de minerales. **Argentina** tiene exposición baja (IEG 64): sus 5 destinos suman el 47 % y el 83 % de eso está respaldado (Mercosur con Brasil, acuerdos con Chile e India; Brasil, EE. UU. y Chile también son aliados del TIAR en ATOP). Lo descubierto es China (8 %).

**Limitaciones:** el Factbook da solo los 5 primeros destinos (el HHI es un mínimo); tratados hasta 2020 y alianzas hasta 2018, así que no cuenta acuerdos más nuevos (por ejemplo Mercosur-UE). Algunos datos del Factbook son raros: Gambia figura con 92 % de exportaciones a Kazajistán.

---

## KPI 4 · Índice de Tensión Identitaria-Distributiva

**Código:** `KPI4_SOC_TENSION_ITID` · **Grano:** país (foto) · **130 países**

### Fundamento teórico-interdisciplinario

- **Antropología y sociología de la diversidad:** la fraccionalización de Alesina et al. (2003) es la probabilidad de que dos personas tomadas al azar pertenezcan a grupos distintos: `F = 1 − Σ sᵢ²`. Se calcula para etnia y religión con la composición del CIA World Factbook.
- **Economía política del conflicto (Easterly y Levine, 1997; Esteban y Ray, 1994; Stewart, "desigualdades horizontales"):** la diversidad por sí sola no genera conflicto; el riesgo aparece cuando las divisiones de identidad coinciden con divisiones de ingreso. Por eso el KPI multiplica diversidad por Gini.
- **Diseño constitucional (Lijphart, consociativismo; federalismo como acomodación de la diversidad):** la forma de Estado (federal o unitaria) y el tipo de régimen (constitucional o cerrado: monarquía absoluta, partido único, teocracia, militar) se cruzan para ver qué arreglos institucionales conviven mejor con sociedades diversas y desiguales.

**Fórmula**

```
F_etnica, F_religiosa = 1 − Σ (participación del grupo)²   (lo no listado cuenta como un grupo más)
ITID = 100 × ((F_etnica + F_religiosa) / 2) × (Gini / 100)
```

Va de 0 (sociedad homogénea o muy igualitaria) a unos 40 (muy diversa y muy desigual).

### Consulta SQL

```sql
-- name: KPI4_SOC_TENSION_ITID
-- Índice de Tensión Identitaria-Distributiva (ITID): fraccionalización étnica y
-- religiosa (Alesina) × desigualdad (Gini), cruzado con la forma de Estado.
-- Socio-antropológica × Económica × Constitucional × (Bienestar: felicidad).
DROP VIEW IF EXISTS kpi4_itid;
CREATE TEMP VIEW kpi4_itid AS
WITH grupos AS (
    SELECT pais_id, dimension, poblacion_pct AS pct
    FROM rel_pais_composicion
    WHERE dimension IN ('etnia', 'religion') AND poblacion_pct > 0
),
sumas AS (
    SELECT pais_id, dimension, SUM(pct) AS total, SUM(pct * pct) AS suma_cuadrados
    FROM grupos GROUP BY pais_id, dimension
),
fraccionalizacion AS (    -- F = 1 - Σ s²; lo no listado cuenta como un grupo más
    SELECT pais_id, dimension,
           CASE WHEN total >= 100 THEN 1 - suma_cuadrados / (total * total)          -- respuestas múltiples: normaliza
                ELSE 1 - (suma_cuadrados + (100 - total) * (100 - total)) / 10000.0 END AS f
    FROM sumas
    WHERE total >= 70     -- descarta fichas con menos del 70 % de la población cuantificada
),
f_pais AS (
    SELECT pais_id,
           MAX(CASE WHEN dimension = 'etnia'    THEN f END) AS f_etnica,
           MAX(CASE WHEN dimension = 'religion' THEN f END) AS f_religiosa
    FROM fraccionalizacion GROUP BY pais_id
),
ultimo AS (               -- último Gini (2014-2023) y última felicidad (2021-2024)
    SELECT h.pais_id,
           (SELECT h2.gini FROM hecho_pais_anual h2
             WHERE h2.pais_id = h.pais_id AND h2.gini IS NOT NULL AND h2.anio BETWEEN 2014 AND 2023
             ORDER BY h2.anio DESC LIMIT 1) AS gini,
           (SELECT h2.felicidad FROM hecho_pais_anual h2
             WHERE h2.pais_id = h.pais_id AND h2.felicidad IS NOT NULL AND h2.anio BETWEEN 2021 AND 2024
             ORDER BY h2.anio DESC LIMIT 1) AS felicidad
    FROM (SELECT DISTINCT pais_id FROM hecho_pais_anual) h
),
estado AS (
    SELECT pais_id, tipo_gobierno,
           CASE WHEN lower(tipo_gobierno) LIKE '%feder%' OR pais_id = 32   -- ARG: el Factbook omite "federal" (CN art. 1)
                THEN 'federal' ELSE 'unitario' END AS forma_estado,
           CASE WHEN lower(tipo_gobierno) LIKE '%absolute monarchy%' OR lower(tipo_gobierno) LIKE '%communist%'
                  OR lower(tipo_gobierno) LIKE '%theocra%' OR lower(tipo_gobierno) LIKE '%military%'
                THEN 'régimen cerrado' ELSE 'régimen constitucional' END AS tipo_regimen
    FROM hecho_pais_perfil_factbook
)
SELECT v.iso3, v.nombre_es AS pais, v.continente,
       round(f.f_etnica, 3)    AS fracc_etnica,
       round(f.f_religiosa, 3) AS fracc_religiosa,
       u.gini,
       round(100 * ((f.f_etnica + f.f_religiosa) / 2) * (u.gini / 100.0), 1) AS itid,
       round(u.felicidad, 2)   AS felicidad,
       e.forma_estado, e.tipo_regimen, e.tipo_gobierno
FROM f_pais f
JOIN v_pais v   ON v.pais_id = f.pais_id
JOIN ultimo u   ON u.pais_id = f.pais_id
LEFT JOIN estado e ON e.pais_id = f.pais_id
WHERE f.f_etnica IS NOT NULL AND f.f_religiosa IS NOT NULL AND u.gini IS NOT NULL
  AND v.en_panel_bm = 1
;

SELECT * FROM kpi4_itid ORDER BY itid DESC;
```

Lectura complementaria: felicidad promedio por cuartil de ITID y forma de Estado.

```sql
-- name: KPI4b_ITID_POR_CUARTIL_Y_FORMA_ESTADO
-- Lectura de política: ¿la forma federal acompaña mejor la diversidad?
-- Felicidad promedio por cuartil de ITID y forma de Estado.
WITH cuartiles AS (       -- usa la vista temporal kpi4_itid creada arriba
    SELECT *, NTILE(4) OVER (ORDER BY itid) AS cuartil_itid FROM kpi4_itid
)
SELECT cuartil_itid, forma_estado,
       COUNT(*)                   AS paises,
       round(AVG(itid), 1)        AS itid_promedio,
       round(AVG(felicidad), 2)   AS felicidad_promedio,
       group_concat(iso3, ' ')    AS paises_iso3
FROM cuartiles
GROUP BY cuartil_itid, forma_estado
ORDER BY cuartil_itid, forma_estado;
```

### Criterio de interpretación

| Valor | Qué indica | Lectura de política pública |
|---|---|---|
| ITID ≥ 25 (cuartil 4) | Diversidad alta que coincide con desigualdad alta | Riesgo de conflicto y de clientelismo étnico: políticas redistributivas con enfoque territorial, representación de minorías, descentralización |
| 13 a 25 | Tensión media | Vigilar si la desigualdad se alinea con grupos (datos desagregados por etnia/religión) |
| < 13 | Sociedad homogénea o igualitaria | Las políticas universales funcionan sin grandes fricciones identitarias |

**Resultado.** Encabezan Angola, República Centroafricana, Camerún, Zambia y Surinam; Brasil es 6.º (31,9) y Estados Unidos 16.º. **Argentina** está en el puesto 88 (12,7): diversidad religiosa media (0,55) pero étnica casi nula (0,06), porque el Factbook la registra como 97 % "europeo y mestizo" en un solo grupo. En el cuadro por cuartil, los países federales tienen más felicidad que los unitarios en los cuartiles 3 y 4 (6,49 contra 5,39 y 5,96 contra 5,17), pero el grupo federal es chico y más rico, así que es una correlación para explorar, no una prueba.

**Limitaciones:** las categorías del Factbook no son homogéneas entre países (Argentina en un solo grupo, India dividida en Indo-aria/Dravídica); el texto del Factbook no dice "federal" para Argentina, así que se corrige a mano en la consulta (CN art. 1).

---

## KPI 5 · Índice de Rentismo Fiscal y Hegemonía Provincial

**Código:** `KPI5_PROV_RENTISMO_IRFH` · **Grano:** provincia argentina, año 2023 · **24 jurisdicciones**

### Fundamento teórico-interdisciplinario

- **Federalismo fiscal (Oates, 1972; desequilibrio vertical):** en Argentina las provincias gastan mucho más de lo que recaudan y cubren la diferencia con la coparticipación y transferencias de la Nación. Una presión tributaria propia baja indica dependencia de recursos ajenos.
- **Teoría rentista del régimen subnacional (Gervasoni, 2010 y 2018):** las provincias que viven de transferencias federales funcionan como "estados rentistas": el gobierno no necesita cobrarle impuestos a la sociedad, puede financiar empleo público y redes de lealtad, y se vuelve más difícil la alternancia.
- **Economía regional:** el peso del sector público en el valor agregado (administración, enseñanza y salud públicas, ramas CEPAL 44, 45 y 47) mide cuánto de la economía provincial depende del Estado.
- **Sociología de la pobreza:** la pobreza (EPH, cálculo propio) se incluye porque la dependencia de ingresos estatales suele ir de la mano con economías privadas débiles.
- **Política y constitución provincial:** los años seguidos con la misma familia política en la gobernación (reelecciones indefinidas en algunas constituciones provinciales) aproximan la hegemonía.

**Fórmula**

```
rentismo_fiscal = (z(% VAB sector público) − z(presión tributaria propia % PBG)) / 2
IRFH            = (z(% VAB sector público) − z(presión tributaria) + z(% pobres) + z(años misma familia)) / 4
```

### Consulta SQL

```sql
-- name: KPI5_PROV_RENTISMO_IRFH
-- Índice de Rentismo Fiscal y Hegemonía Provincial (IRFH), Argentina 2023.
-- Fiscal (presión tributaria propia) × Económica (peso del sector público en el VAB)
-- × Social (pobreza) × Constitucional/política (continuidad de la familia gobernante).
DROP VIEW IF EXISTS kpi5_irfh;
CREATE TEMP VIEW kpi5_irfh AS
WITH param AS (SELECT 2023 AS anio_ref),
base AS (
    SELECT s.codigo, s.subdivision,
           s.pct_vab_sector_publico              AS pub,
           s.presion_tributaria_pct_pbg_estimado AS pres,
           s.pct_personas_pobres_estimado        AS pob,
           s.familia_politica_gobierno           AS familia,
           s.pbg_per_capita_pesos_2004           AS pbg_pc,
           s.petroleo_m3_total * 1.0 / s.habitantes AS petroleo_m3_por_hab
    FROM v_subdivision_anual s CROSS JOIN param
    WHERE s.iso3 = 'ARG' AND s.anio = param.anio_ref
      AND s.pct_vab_sector_publico IS NOT NULL
      AND s.presion_tributaria_pct_pbg_estimado IS NOT NULL
      AND s.pct_personas_pobres_estimado IS NOT NULL
),
continuidad AS (          -- años seguidos con la misma familia política hasta anio_ref
    SELECT b.codigo,
           param.anio_ref - COALESCE(
               (SELECT MAX(g.anio) FROM v_subdivision_anual g
                 WHERE g.codigo = b.codigo AND g.anio < param.anio_ref
                   AND g.familia_politica_gobierno IS NOT NULL
                   AND g.familia_politica_gobierno <> b.familia),
               (SELECT MIN(g.anio) - 1 FROM v_subdivision_anual g
                 WHERE g.codigo = b.codigo AND g.familia_politica_gobierno IS NOT NULL)) AS anios_misma_familia
    FROM base b CROSS JOIN param
),
momentos AS (
    SELECT AVG(pub) AS m_pub,  sqrt(AVG(pub*pub)   - AVG(pub)*AVG(pub))   AS sd_pub,
           AVG(pres) AS m_pres, sqrt(AVG(pres*pres) - AVG(pres)*AVG(pres)) AS sd_pres,
           AVG(pob) AS m_pob,  sqrt(AVG(pob*pob)   - AVG(pob)*AVG(pob))   AS sd_pob
    FROM base
),
cont_m AS (
    SELECT AVG(anios_misma_familia * 1.0) AS m_c,
           sqrt(AVG(anios_misma_familia * anios_misma_familia * 1.0)
                - AVG(anios_misma_familia * 1.0) * AVG(anios_misma_familia * 1.0)) AS sd_c
    FROM continuidad
),
z AS (
    SELECT b.*, c.anios_misma_familia,
           (b.pub  - m.m_pub)  / m.sd_pub  AS z_pub,
           (b.pres - m.m_pres) / m.sd_pres AS z_pres,
           (b.pob  - m.m_pob)  / m.sd_pob  AS z_pob,
           (c.anios_misma_familia - cm.m_c) / cm.sd_c AS z_cont
    FROM base b
    JOIN continuidad c ON c.codigo = b.codigo
    CROSS JOIN momentos m CROSS JOIN cont_m cm
)
SELECT codigo, subdivision AS provincia,
       round(pub, 1)  AS pct_vab_sector_publico,
       round(pres, 2) AS presion_tributaria_propia_pct_pbg,
       round(pob, 1)  AS pct_personas_pobres,
       familia        AS familia_gobierno,
       anios_misma_familia,
       round((z_pub - z_pres) / 2, 3)                   AS rentismo_fiscal_z,
       round((z_pub - z_pres + z_pob + z_cont) / 4, 3)  AS irfh,
       round(petroleo_m3_por_hab, 2)                    AS petroleo_m3_por_hab,
       round(pbg_pc, 0)                                 AS pbg_pc_pesos_2004
FROM z
;

SELECT * FROM kpi5_irfh ORDER BY irfh DESC;
```

Lectura complementaria: correlación de Pearson para probar la hipótesis rentista.

```sql
-- name: KPI5b_CORRELACION_RENTISMO_CONTINUIDAD
-- Prueba simple de la hipótesis rentista (Gervasoni): correlación de Pearson
-- entre rentismo fiscal y años de continuidad de la familia gobernante.
SELECT COUNT(*) AS provincias,
       round((AVG(rentismo_fiscal_z * anios_misma_familia) - AVG(rentismo_fiscal_z) * AVG(anios_misma_familia))
             / (sqrt(AVG(rentismo_fiscal_z * rentismo_fiscal_z) - AVG(rentismo_fiscal_z) * AVG(rentismo_fiscal_z))
                * sqrt(AVG(anios_misma_familia * anios_misma_familia * 1.0) - AVG(anios_misma_familia * 1.0) * AVG(anios_misma_familia * 1.0))), 3)
           AS pearson_rentismo_vs_continuidad,
       round((AVG(rentismo_fiscal_z * pct_personas_pobres) - AVG(rentismo_fiscal_z) * AVG(pct_personas_pobres))
             / (sqrt(AVG(rentismo_fiscal_z * rentismo_fiscal_z) - AVG(rentismo_fiscal_z) * AVG(rentismo_fiscal_z))
                * sqrt(AVG(pct_personas_pobres * pct_personas_pobres) - AVG(pct_personas_pobres) * AVG(pct_personas_pobres))), 3)
           AS pearson_rentismo_vs_pobreza
FROM kpi5_irfh;              -- vista temporal creada en KPI5
```

### Criterio de interpretación

| Valor | Qué indica | Lectura de política pública |
|---|---|---|
| IRFH > 0,5 | Economía muy dependiente del Estado, poca recaudación propia, más pobreza y poca alternancia | Condicionar transferencias a metas, fortalecer la administración tributaria, diversificar la economía privada; mirar la calidad institucional |
| IRFH entre −0,5 y 0,5 | Situación intermedia | Depende del componente que empuja (ver columnas) |
| IRFH < −0,5 | Economía privada fuerte, recauda lo suyo, alternancia | Más autonomía fiscal; riesgo de reclamar por la coparticipación (aportan más de lo que reciben) |

**Resultado 2023.** Encabezan **La Rioja** (1,10), **Formosa** (1,01), Chaco, Catamarca y San Luis: coincide con los casos que la literatura sobre regímenes provinciales señala como más hegemónicos (La Rioja, Formosa, San Luis, Santa Cruz, La Pampa y Neuquén llevan 40 años con la misma familia, desde 1983). Al otro extremo están la Ciudad de Buenos Aires (−1,40), Misiones, Tierra del Fuego, Santa Fe y Mendoza. La correlación entre rentismo fiscal y años de continuidad es **0,22** y con pobreza **0,38**: positivas, como predice la teoría, pero débiles con solo 24 casos.

**Limitaciones:** la presión tributaria es una estimación propia (recaudación sobre PIB nominal repartido por el peso de cada provincia en el VAB real); Misiones da 10,4 %, un valor alto que conviene revisar. Las regalías hidrocarburíferas no son tributos y no entran: Neuquén y Santa Cruz parecen menos rentistas de lo que son (la columna `petroleo_m3_por_hab` ayuda a verlo). La pobreza es de aglomerados urbanos EPH, no de la provincia entera.

---

## Datos que el pedido menciona y la base todavía no tiene

El pedido habla de "comercio exterior, alianzas militares y presupuestos fiscales". Esto es lo que se usó en su lugar y lo que falta:

| Pedido | Qué hay en la base | Qué falta |
|---|---|---|
| Comercio exterior | top 5 socios de exportación e importación (Factbook, foto 2023), tratados comerciales (DESTA, hasta 2020) | Comercio bilateral completo por año (UN Comtrade o WITS) |
| Alianzas militares | pactos país-país por año (ATOP, hasta 2018), membresías OTAN, OTSC, AUKUS, Quad hasta 2025 | Gasto militar (% PIB, SIPRI o Banco Mundial `MS.MIL.XPND.GD.ZS`) |
| Presupuestos fiscales | gasto público en salud y educación (% PIB) por país; recaudación propia por provincia | Presupuesto nacional completo, deuda pública, transferencias de coparticipación por provincia |
| Forma de gobierno / democracia | texto del Factbook (tipo de gobierno, voto obligatorio) | Índice de democracia continuo (V-Dem o EIU), que el proyecto lista como fuente pero no está descargado |
| Demografía | población total, mortalidad infantil, varones/mujeres por provincia | Estructura por edad (dependencia, envejecimiento) |

Sumar el gasto militar y V-Dem permitiría un sexto KPI de "seguridad vs. bienestar" (gasto militar contra gasto en salud y educación, ajustado por régimen).
