-- =====================================================================
-- 5 KPIs multidimensionales sobre master_paises_provincias.sqlite
-- Motor: SQLite >= 3.35 (usa funciones de ventana y ln/sqrt).
-- Se corre entero, en orden, en cualquier cliente SQLite (DB Browser,
-- DBeaver, sqlite3 CLI) o con calcular_kpis.py. Cada KPI crea una vista
-- TEMPORAL (kpi1_iese ... kpi5_irfh: no modifica la base, desaparece al
-- cerrar la conexión) y termina con un SELECT que la muestra ordenada.
-- Las líneas "-- name: <codigo>" separan los bloques para el script.
--
-- Truco que se repite: SQLite no trae STDDEV, así que el desvío se
-- calcula como sqrt(AVG(x*x) - AVG(x)^2) (desvío poblacional).
-- La pendiente de una regresión simple (MCO) sale de los mismos
-- promedios: b = (AVG(x*y) - AVG(x)*AVG(y)) / (AVG(x*x) - AVG(x)^2).
-- =====================================================================


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
