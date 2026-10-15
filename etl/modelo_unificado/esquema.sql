-- Generado por construir_master.py

CREATE TABLE dim_region_geografica (       -- jerarquía M49 de la ONU: continente > subregión > región intermedia
    region_geografica_id INTEGER PRIMARY KEY,   -- código M49 (19 = América, 419 = América Latina y el Caribe...)
    nombre_es            TEXT NOT NULL,
    nombre_en            TEXT NOT NULL,
    nivel                INTEGER NOT NULL CHECK (nivel IN (1, 2, 3)),
    region_padre_id      INTEGER REFERENCES dim_region_geografica(region_geografica_id)
);

CREATE TABLE dim_region_bm (               -- regiones del Banco Mundial
    region_bm_codigo TEXT PRIMARY KEY,     -- LCN, ECS, ...
    nombre_en        TEXT NOT NULL,
    nombre_es        TEXT NOT NULL
);

CREATE TABLE dim_nivel_ingreso (           -- clasificación vigente del Banco Mundial
    nivel_ingreso_codigo TEXT PRIMARY KEY, -- LIC, LMC, UMC, HIC
    nombre_en            TEXT NOT NULL,
    nombre_es            TEXT NOT NULL,
    orden                INTEGER NOT NULL UNIQUE
);

CREATE TABLE dim_pais (
    pais_id               INTEGER PRIMARY KEY,   -- = ISO 3166-1 numérico (901 Kosovo, 902 Islas del Canal)
    iso3                  TEXT NOT NULL UNIQUE CHECK (length(iso3) = 3),
    iso2                  TEXT NOT NULL UNIQUE CHECK (length(iso2) = 2),
    iso_numerico          TEXT UNIQUE,           -- '032'; NULL si no es ISO
    codigo_banco_mundial  TEXT UNIQUE,           -- NULL si el BM no publica datos del territorio
    nombre_es             TEXT NOT NULL,
    nombre_en             TEXT NOT NULL,
    nombre_oficial_en     TEXT NOT NULL,
    nombre_es_banco_mundial TEXT,
    region_geografica_id  INTEGER REFERENCES dim_region_geografica(region_geografica_id),
    region_bm_codigo      TEXT REFERENCES dim_region_bm(region_bm_codigo),
    nivel_ingreso_codigo  TEXT REFERENCES dim_nivel_ingreso(nivel_ingreso_codigo),
    capital               TEXT,
    latitud_capital       REAL,
    longitud_capital      REAL,
    tipo_entidad          TEXT NOT NULL,
    es_miembro_onu        INTEGER NOT NULL CHECK (es_miembro_onu IN (0, 1)),
    pais_soberano_id      INTEGER REFERENCES dim_pais(pais_id),
    en_panel_bm           INTEGER NOT NULL CHECK (en_panel_bm IN (0, 1))
);

CREATE TABLE dim_region_subnacional (      -- agrupaciones de provincias (regiones EPH del INDEC)
    region_subnacional_id INTEGER PRIMARY KEY,   -- código de región de la EPH
    pais_id               INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    sistema               TEXT NOT NULL,
    nombre                TEXT NOT NULL,
    UNIQUE (pais_id, sistema, nombre)
);

CREATE TABLE dim_subdivision (             -- provincias, estados, regiones... (ISO 3166-2)
    subdivision_id        INTEGER PRIMARY KEY,
    pais_id               INTEGER NOT NULL REFERENCES dim_pais(pais_id),     -- relación 1:N
    codigo                TEXT NOT NULL UNIQUE,  -- 'AR-B' (ISO 3166-2)
    nombre                TEXT NOT NULL,         -- nombre corto, el mismo que usan las tablas del proyecto
    nombre_iso            TEXT,                  -- nombre oficial ISO, en el idioma local
    nombre_es             TEXT,                  -- etiqueta de Wikidata en español
    nombre_en             TEXT,
    tipo_iso              TEXT,
    tipo_es               TEXT,
    nivel                 INTEGER NOT NULL CHECK (nivel >= 1),          -- hoy solo primer nivel
    subdivision_padre_id  INTEGER REFERENCES dim_subdivision(subdivision_id),
    region_subnacional_id INTEGER REFERENCES dim_region_subnacional(region_subnacional_id),
    latitud               REAL,
    longitud              REAL,
    wikidata_id           TEXT,
    es_iso_3166_2         INTEGER NOT NULL CHECK (es_iso_3166_2 IN (0, 1)),
    pais_equivalente_id   INTEGER REFERENCES dim_pais(pais_id)  -- US-PR -> PRI: no sumar dos veces
);

CREATE TABLE pais_equivalencia (           -- cómo llama cada fuente a cada país
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    sistema TEXT NOT NULL,
    tipo    TEXT NOT NULL CHECK (tipo IN ('codigo', 'nombre')),
    valor   TEXT NOT NULL,
    PRIMARY KEY (sistema, valor)
);

CREATE TABLE subdivision_equivalencia (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    sistema        TEXT NOT NULL,
    tipo           TEXT NOT NULL CHECK (tipo IN ('codigo', 'nombre')),
    valor          TEXT NOT NULL,
    PRIMARY KEY (sistema, valor)
);

CREATE TABLE rel_reclamo_territorial (
    pais_id                    INTEGER NOT NULL REFERENCES dim_pais(pais_id),      -- territorio
    pais_reclamante_id         INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    subdivision_reclamante_id  INTEGER REFERENCES dim_subdivision(subdivision_id),
    descripcion                TEXT NOT NULL,
    PRIMARY KEY (pais_id, pais_reclamante_id)
);

CREATE TABLE dim_organizacion (
    organizacion_codigo TEXT PRIMARY KEY,  -- 'MERCOSUR', 'OTAN', ...
    nombre              TEXT NOT NULL,
    tipo                TEXT NOT NULL
);

CREATE TABLE dim_acuerdo_comercial (
    acuerdo_id     INTEGER PRIMARY KEY,    -- número DESTA
    nombre         TEXT NOT NULL,
    tipo           TEXT,
    region_acuerdo TEXT,
    listado_omc    INTEGER
);

CREATE TABLE dim_rama_cepal (
    rama_nro     INTEGER PRIMARY KEY,
    rama         TEXT NOT NULL,
    grupo_sector TEXT NOT NULL
);

CREATE TABLE ref_catalogo_tabla (
    tabla        TEXT PRIMARY KEY,
    tipo         TEXT NOT NULL,
    grano        TEXT NOT NULL,
    fuente       TEXT,
    archivo_origen TEXT,
    filas        INTEGER,
    anio_min     INTEGER,
    anio_max     INTEGER
);

CREATE TABLE ref_diccionario_columna (
    tabla    TEXT NOT NULL REFERENCES ref_catalogo_tabla(tabla),
    columna  TEXT NOT NULL,
    tipo_sql TEXT NOT NULL,
    unidad   TEXT,
    pct_nulos REAL,
    PRIMARY KEY (tabla, columna)
);

CREATE TABLE hecho_pais_anual (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    poblacion INTEGER,
    pib_pc_ppp REAL,
    esperanza_vida REAL,
    mortalidad_infantil REAL,
    camas_hospital_x1000 REAL,
    medicos_x1000 REAL,
    suicidio_total_x100k REAL,
    suicidio_hombres_x100k REAL,
    suicidio_mujeres_x100k REAL,
    gasto_salud_pct_pib REAL,
    gasto_salud_pct_gasto_pub REAL,
    gasto_educacion_pct_pib REAL,
    tipo_cambio_lcu_por_usd REAL,
    ppa_lcu_por_usd_intl REAL,
    gini REAL,
    ingreso_decil1_pct REAL,
    ingreso_quintil1_pct REAL,
    ingreso_quintil2_pct REAL,
    ingreso_quintil3_pct REAL,
    ingreso_quintil4_pct REAL,
    ingreso_quintil5_pct REAL,
    ingreso_decil10_pct REAL,
    lorenz_acum_10 REAL,
    lorenz_acum_20 REAL,
    lorenz_acum_40 REAL,
    lorenz_acum_60 REAL,
    lorenz_acum_80 REAL,
    lorenz_acum_90 REAL,
    gini_aprox_desde_lorenz REAL,
    ratio_quintil5_quintil1 REAL,
    ratio_palma REAL,
    dieta_saludable_lcu_dia REAL,
    dieta_saludable_ppa_dia REAL,
    pct_no_puede_pagar_dieta_saludable REAL,
    dieta_saludable_usd_mes REAL,
    dieta_saludable_lcu_mes REAL,
    salario_promedio_mensual_lcu REAL,
    salario_promedio_mensual_usd REAL,
    salario_promedio_mensual_ppa REAL,
    felicidad REAL,
    felicidad_ranking REAL,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE rel_pais_organizacion (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    organizacion_codigo TEXT NOT NULL REFERENCES dim_organizacion(organizacion_codigo),
    estado TEXT,
    anio_ingreso INTEGER NOT NULL,
    anio_salida INTEGER,
    fuente TEXT,
    nota TEXT,
    PRIMARY KEY (pais_id, organizacion_codigo, anio_ingreso)
);

CREATE TABLE rel_pais_acuerdo_comercial (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    acuerdo_id INTEGER NOT NULL REFERENCES dim_acuerdo_comercial(acuerdo_id),
    via TEXT,
    anio_firma INTEGER,
    anio_entrada_vigor INTEGER,
    anio_salida INTEGER,
    PRIMARY KEY (pais_id, acuerdo_id)
);

CREATE TABLE rel_alianza_militar_anual (
    pais_a_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    pais_b_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    defensa INTEGER,
    ofensiva INTEGER,
    neutralidad INTEGER,
    no_agresion INTEGER,
    consulta INTEGER,
    PRIMARY KEY (pais_a_id, pais_b_id, anio),
    CHECK (pais_a_id <> pais_b_id)
);

CREATE TABLE hecho_pais_relaciones_anual (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    n_igos_cow_total INTEGER,
    n_acuerdos_comerciales_en_vigor INTEGER,
    n_aliados_defensa INTEGER,
    n_aliados_cualquier_pacto INTEGER,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_perfil_factbook (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    codigo_gec TEXT NOT NULL,
    fecha_snapshot TEXT,
    superficie_total_km2 REAL,
    superficie_tierra_km2 REAL,
    superficie_agua_km2 REAL,
    costa_km REAL,
    fronteras_terrestres_km REAL,
    n_paises_limitrofes INTEGER,
    punto_mas_alto TEXT,
    elevacion_maxima_m REAL,
    elevacion_minima_m REAL,
    elevacion_media_m REAL,
    clima TEXT,
    terreno TEXT,
    recursos_naturales TEXT,
    tipo_gobierno TEXT,
    sistema_legal TEXT,
    independencia TEXT,
    anio_independencia INTEGER,
    sufragio TEXT,
    edad_minima_voto INTEGER,
    es_voto_obligatorio INTEGER,
    servicio_militar TEXT,
    exportaciones_productos TEXT,
    importaciones_productos TEXT,
    PRIMARY KEY (pais_id, codigo_gec)
);

CREATE TABLE rel_pais_frontera (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    codigo_gec TEXT NOT NULL,
    vecino_pais_id INTEGER REFERENCES dim_pais(pais_id),
    vecino_codigo_gec TEXT,
    vecino_nombre_factbook TEXT NOT NULL,
    frontera_km REAL,
    nota TEXT,
    PRIMARY KEY (pais_id, codigo_gec, vecino_nombre_factbook)
);

CREATE TABLE rel_pais_composicion (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    codigo_gec TEXT NOT NULL,
    dimension TEXT NOT NULL,
    orden INTEGER NOT NULL,
    grupo TEXT,
    poblacion_pct REAL,
    es_cota_superior INTEGER,
    es_oficial INTEGER,
    detalle TEXT,
    anio_estimacion INTEGER,
    PRIMARY KEY (pais_id, codigo_gec, dimension, orden)
);

CREATE TABLE rel_pais_socio_comercial (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    codigo_gec TEXT NOT NULL,
    flujo TEXT NOT NULL,
    rango INTEGER NOT NULL,
    socio_nombre_factbook TEXT,
    socio_pais_id INTEGER REFERENCES dim_pais(pais_id),
    participacion_pct REAL,
    anio INTEGER,
    PRIMARY KEY (pais_id, codigo_gec, flujo, rango)
);

CREATE TABLE hecho_pais_migracion_anual (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    saldo_migratorio_neto INTEGER,
    stock_migrantes_pct_poblacion REAL,
    remesas_recibidas_usd REAL,
    remesas_recibidas_pct_pib REAL,
    remesas_enviadas_usd REAL,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_emisiones (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    emisiones_gei_per_capita_tco2e REAL,
    emisiones_gei_total_mtco2e REAL,
    emisiones_co2_per_capita_tco2e REAL,
    energia_renovable_pct_consumo_final REAL,
    electricidad_renovable_pct REAL,
    electricidad_hidro_pct REAL,
    electricidad_solar_eolica_pct REAL,
    personas_afectadas_desastres_climaticos INTEGER,
    muertes_desastres_climaticos INTEGER,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_capital_social (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    confianza_interpersonal_pct REAL,
    desconfianza_poder_judicial_pct REAL,
    desconfianza_partidos_congreso_pct REAL,
    confianza_policia_pct REAL,
    confianza_interpersonal_wvs_pct REAL,
    indice_sociedad_civil_0_1 REAL,
    sociedad_civil_participacion_vdem REAL,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_diversidad_cultural (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    es_proteccion_lenguas_constitucion INTEGER,
    es_derechos_indigenas_constitucion INTEGER,
    es_derechos_culturales_constitucion INTEGER,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_poblacion_indigena (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    decada_censal INTEGER NOT NULL,
    poblacion_indigena_pct REAL,
    PRIMARY KEY (pais_id, decada_censal)
);

CREATE TABLE hecho_pais_institucional_gobernanza (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    indice_control_corrupcion REAL,
    indice_control_corrupcion_0_100 REAL,
    indice_estado_derecho REAL,
    indice_estado_derecho_0_100 REAL,
    estabilidad_politica_ausencia_violencia REAL,
    efectividad_gobierno REAL,
    calidad_regulatoria REAL,
    voz_rendicion_cuentas REAL,
    veto_players_count INTEGER,
    indice_democracia_electoral_0_1 REAL,
    indice_democracia_liberal_0_1 REAL,
    indice_estado_derecho_vdem_0_1 REAL,
    indice_corrupcion_politica_vdem_0_1 REAL,
    restricciones_judiciales_ejecutivo_0_1 REAL,
    restricciones_legislativas_ejecutivo_0_1 REAL,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_financiero_deuda (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    pib_usd REAL,
    deuda_externa_ids_usd REAL,
    deuda_externa_pct_ingreso_nacional REAL,
    deuda_externa_corto_plazo_pct REAL,
    servicio_deuda_pct_exportaciones REAL,
    servicio_deuda_pct_ingreso_nacional REAL,
    deuda_gobierno_central_pct_pib REAL,
    intereses_pct_ingresos_fiscales REAL,
    reservas_internacionales_usd REAL,
    reservas_internacionales_meses_importacion REAL,
    deuda_externa_usd REAL,
    spread_embi_pb REAL,
    spread_embi_meses INTEGER,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_salud_cronica (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    diabetes_prevalencia_pct REAL,
    mortalidad_ent_30_70_pct REAL,
    muertes_ent_pct INTEGER,
    hipertension_prevalencia_pct REAL,
    obesidad_adultos_pct REAL,
    avad_total INTEGER,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_tecnologia (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    banda_ancha_fija_x100 REAL,
    usuarios_internet_pct REAL,
    gasto_en_i_d_pct_pib REAL,
    hogares_con_conectividad_pct REAL,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_educacion (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    alfabetizacion_adultos_pct REAL,
    alfabetizacion_adultos_mujeres_pct REAL,
    alfabetizacion_adultos_hombres_pct REAL,
    alfabetizacion_jovenes_15_24_pct REAL,
    nivel_alcanzado_primaria_pct REAL,
    nivel_alcanzado_secundaria_baja_pct REAL,
    nivel_alcanzado_secundaria_alta_pct REAL,
    nivel_alcanzado_postsecundaria_pct REAL,
    nivel_alcanzado_terciaria_ciclo_corto_pct REAL,
    nivel_alcanzado_licenciatura_pct REAL,
    nivel_alcanzado_maestria_pct REAL,
    nivel_alcanzado_doctorado_pct REAL,
    escolaridad_promedio_25mas_anios REAL,
    escolaridad_esperada_anios REAL,
    escolaridad_ajustada_aprendizaje_anios REAL,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_digital_ocio (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    usa_redes_sociales_16_74_pct REAL,
    usa_redes_sociales_16_24_pct REAL,
    compro_online_videojuegos_software_16_74_pct REAL,
    compro_online_videojuegos_software_16_24_pct REAL,
    compro_online_algo_16_74_pct REAL,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_empleo_sectorial (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    empleo_total_modelado_miles_personas REAL,
    empleo_construccion_modelado_miles_personas REAL,
    empleo_total_encuesta_miles_personas REAL,
    empleo_artes_espectaculos_miles_personas REAL,
    empleo_bibliotecas_museos_patrimonio_miles_personas REAL,
    empleo_juegos_azar_apuestas_miles_personas REAL,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_gasto_cultura (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    gasto_recreacion_cultura_religion_pct_pib REAL,
    gasto_recreacion_cultura_religion_pct_gasto_publico REAL,
    gasto_servicios_culturales_pct_pib REAL,
    gasto_servicios_culturales_pct_gasto_publico REAL,
    gasto_recreacion_cultura_religion_gob_central_pct_pib REAL,
    gasto_servicios_culturales_gob_central_pct_pib REAL,
    gasto_recreacion_cultura_religion_usd_ppa_millones REAL,
    fuente_gobierno_general TEXT,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_deporte_olimpico (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    juegos_olimpicos TEXT,
    atletas_participantes INTEGER,
    atletas_mujeres INTEGER,
    medallas_oro INTEGER,
    medallas_plata INTEGER,
    medallas_bronce INTEGER,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_pais_consolas_comercio (
    pais_id INTEGER NOT NULL REFERENCES dim_pais(pais_id),
    anio INTEGER NOT NULL,
    importaciones_consolas_usd REAL,
    exportaciones_consolas_usd REAL,
    PRIMARY KEY (pais_id, anio)
);

CREATE TABLE hecho_subdivision_poblacion (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    habitantes INTEGER,
    varones INTEGER,
    mujeres INTEGER,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_economia (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    estado_dato TEXT,
    vab_total_mill_pesos_2004 REAL,
    pct_vab_adm_publica REAL,
    pct_vab_ensenanza_publica REAL,
    pct_vab_salud_publica REAL,
    pct_vab_hoteles REAL,
    pct_vab_restaurantes REAL,
    pct_vab_sector_publico REAL,
    pct_vab_turismo REAL,
    pbg_per_capita_pesos_2004 REAL,
    poblacion_implicita_vab REAL,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_vab_rama (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    estado_dato TEXT,
    rama_nro INTEGER NOT NULL REFERENCES dim_rama_cepal(rama_nro),
    vab_mill_pesos_2004 REAL,
    participacion_en_provincia REAL,
    PRIMARY KEY (subdivision_id, anio, rama_nro)
);

CREATE TABLE hecho_subdivision_hidrocarburos (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    petroleo_m3_convencional REAL,
    petroleo_m3_no_convencional REAL,
    petroleo_m3_total REAL,
    gas_miles_m3_convencional REAL,
    gas_miles_m3_no_convencional REAL,
    gas_miles_m3_total REAL,
    meses_con_dato INTEGER,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_agricultura (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    campania TEXT,
    anio_cosecha INTEGER NOT NULL,
    cultivo TEXT NOT NULL,
    sup_sembrada_ha INTEGER,
    sup_cosechada_ha INTEGER,
    produccion_tn INTEGER,
    rendimiento_kg_ha REAL,
    PRIMARY KEY (subdivision_id, anio_cosecha, cultivo)
);

CREATE TABLE hecho_subdivision_ganaderia (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    vacas REAL,
    vaquillonas REAL,
    novillos REAL,
    novillitos REAL,
    terneros REAL,
    terneras REAL,
    toros REAL,
    toritos INTEGER,
    bueyes TEXT,
    total_cabezas REAL,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_censo (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio_censo INTEGER NOT NULL,
    hogares INTEGER,
    habitantes INTEGER,
    pct_hogares_inquilino REAL,
    pct_hogares_otra_tenencia REAL,
    pct_hogares_prestada_o_cedida REAL,
    pct_hogares_propietario REAL,
    pct_hogares_agua_de_red REAL,
    pct_hogares_cloaca REAL,
    pct_hogares_gas_de_red REAL,
    pct_hogares_con_nbi REAL,
    pct_personas_escuela_asiste REAL,
    pct_personas_escuela_asistio REAL,
    pct_personas_escuela_nunca_asistio REAL,
    pct_personas_max_nivel_primario REAL,
    pct_personas_max_nivel_secundario REAL,
    pct_personas_max_nivel_sin_primario REAL,
    pct_personas_max_nivel_superior REAL,
    pct_personas_salud_obra_social_o_prepaga REAL,
    pct_personas_salud_sin_cobertura REAL,
    pct_personas_salud_solo_plan_estatal REAL,
    PRIMARY KEY (subdivision_id, anio_censo)
);

CREATE TABLE hecho_subdivision_turismo (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    pernoctes_no_residentes REAL,
    pernoctes_residentes REAL,
    pernoctes_total REAL,
    meses_con_dato INTEGER,
    localidades_relevadas INTEGER,
    viajeros_no_residentes REAL,
    viajeros_residentes REAL,
    viajeros_total REAL,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_clima (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    temperatura_media_c REAL,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_salud (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    pct_vacuna_srp_1ra_dosis_12_meses REAL,
    pct_vacuna_srp_2da_dosis_ingreso_escolar REAL,
    medicos REAL,
    medicos_cada_10000_hab REAL,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_empresas (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    empresas_con_empleados INTEGER,
    empresas_cada_1000_hab REAL,
    empresas_grandes_ind_com_serv REAL,
    empresas_medianas_ind_com_serv REAL,
    empresas_pequenas_ind_com_serv REAL,
    empresas_micro_ind_com_serv REAL,
    cep_empresas_con_empleados REAL,
    cep_locales_1_a_9_empleados REAL,
    cep_locales_10_a_49_empleados REAL,
    cep_locales_50_a_199_empleados REAL,
    cep_locales_200_a_499_empleados REAL,
    cep_locales_500_o_mas_empleados REAL,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_pymes (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    fecha_corte TEXT,
    pymes_total INTEGER,
    pymes_micro INTEGER,
    pymes_pequenas INTEGER,
    pymes_medianas_tramo1 INTEGER,
    pymes_medianas_tramo2 INTEGER,
    pymes_cada_1000_hab REAL,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_fiscal (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    recaudacion_propia_mill_pesos REAL,
    recaudacion_automotores_mill_pesos REAL,
    recaudacion_ingresos_brutos_mill_pesos REAL,
    recaudacion_inmobiliario_mill_pesos REAL,
    recaudacion_otros_mill_pesos REAL,
    recaudacion_sellos_mill_pesos REAL,
    pct_ingresos_brutos_en_total REAL,
    presion_tributaria_pct_pbg_estimado REAL,
    recaudacion_por_habitante_pesos_2024 REAL,
    alicuota_iibb_comercio_pct REAL,
    alicuota_iibb_industria_pct REAL,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_alicuota_iibb (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    actividad TEXT NOT NULL,
    alicuota_pct REAL,
    alicuota_texto TEXT,
    PRIMARY KEY (subdivision_id, anio, actividad)
);

CREATE TABLE hecho_subdivision_salarios (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    salario_promedio_mensual_pesos REAL,
    salario_promedio_mensual_pesos_2024 REAL,
    puestos_asalariados_privados_registrados REAL,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_canastas (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    cba_adulto_equivalente_pesos_estimado_por_region REAL,
    cbt_adulto_equivalente_pesos_estimado_por_region REAL,
    meses_con_dato INTEGER,
    cbt_hogar_tipo_4_personas_pesos_estimado_por_region REAL,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_pobreza (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    trimestres_con_dato INTEGER,
    pct_personas_pobres_estimado REAL,
    pct_personas_indigentes_estimado REAL,
    gini_ingreso_per_capita_familiar_estimado_grandes_ciudades REAL,
    casos_encuestados INTEGER,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_gobierno (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    familia_politica_gobierno TEXT,
    ganador_ultima_eleccion TEXT,
    anio_ultima_eleccion INTEGER,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_eleccion_gobernador (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio_eleccion INTEGER NOT NULL,
    lista_ganadora TEXT,
    pct_votos_ganador REAL,
    segunda_vuelta INTEGER,
    fuente TEXT,
    familia_politica TEXT,
    aclaracion TEXT,
    PRIMARY KEY (subdivision_id, anio_eleccion)
);

CREATE TABLE hecho_subdivision_legisladores (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    camara TEXT NOT NULL,
    bancas INTEGER,
    bancas_la_libertad_avanza INTEGER,
    bancas_pro_juntos_por_el_cambio INTEGER,
    bancas_izquierda INTEGER,
    bancas_otros INTEGER,
    bancas_partido_provincial INTEGER,
    bancas_peronismo INTEGER,
    bancas_radicalismo INTEGER,
    familia_mayoritaria TEXT,
    bloque_o_partido_mayoritario TEXT,
    PRIMARY KEY (subdivision_id, anio, camara)
);

CREATE TABLE hecho_subdivision_financiero (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    deuda_stock_mill_pesos REAL,
    deuda_gobierno_nacional_mill_pesos REAL,
    deuda_fffir_mill_pesos REAL,
    deuda_ffdp_mill_pesos REAL,
    deuda_bancos_mill_pesos REAL,
    deuda_consolidada_mill_pesos REAL,
    deuda_bonos_mill_pesos REAL,
    deuda_organismos_internacionales_mill_pesos REAL,
    servicio_deuda_amortizacion_mill_pesos REAL,
    servicio_deuda_intereses_mill_pesos REAL,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_finanzas_publicas (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    ingresos_corrientes_mill_pesos REAL,
    tributarios_mill_pesos REAL,
    tributarios_origen_provincial_mill_pesos REAL,
    tributarios_origen_nacional_mill_pesos REAL,
    coparticipacion_neta_mill_pesos REAL,
    contribuciones_seguridad_social_mill_pesos REAL,
    regalias_mill_pesos REAL,
    transferencias_corrientes_recibidas_mill_pesos REAL,
    gasto_corriente_mill_pesos REAL,
    gasto_personal_mill_pesos REAL,
    intereses_deuda_mill_pesos REAL,
    transferencias_capital_recibidas_mill_pesos REAL,
    inversion_real_directa_mill_pesos REAL,
    ingresos_totales_mill_pesos REAL,
    gasto_total_mill_pesos REAL,
    resultado_financiero_mill_pesos REAL,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_ambiental (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    emisiones_gei_per_capita_tco2e REAL,
    emisiones_gei_total_tco2e REAL,
    emisiones_gei_electricidad_tco2e REAL,
    emisiones_gei_industria_tco2e REAL,
    emisiones_gei_transporte_tco2e REAL,
    emisiones_gei_edificios_tco2e REAL,
    emisiones_gei_agro_tco2e REAL,
    emisiones_gei_residuos_tco2e REAL,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE TABLE hecho_subdivision_tecnologia (
    subdivision_id INTEGER NOT NULL REFERENCES dim_subdivision(subdivision_id),
    anio INTEGER NOT NULL,
    internet_fijo_accesos_x100_hogares REAL,
    internet_fijo_accesos_x100_hab REAL,
    internet_fijo_trimestre INTEGER,
    PRIMARY KEY (subdivision_id, anio)
);

CREATE VIEW v_pais AS
SELECT p.pais_id, p.iso3, p.iso2, p.iso_numerico, p.nombre_es, p.nombre_en, p.nombre_oficial_en,
       COALESCE(r1.nombre_es, r2.nombre_es, r3.nombre_es) AS continente,
       CASE WHEN r3.nivel = 2 THEN r3.nombre_es WHEN r2.nivel = 2 THEN r2.nombre_es END AS subregion,
       CASE WHEN r3.nivel = 3 THEN r3.nombre_es END AS region_intermedia,
       b.nombre_es AS region_bm, i.nombre_es AS nivel_ingreso, p.capital, p.latitud_capital, p.longitud_capital,
       p.tipo_entidad, p.es_miembro_onu, s.iso3 AS soberano_iso3, p.en_panel_bm,
       (SELECT COUNT(*) FROM dim_subdivision d WHERE d.pais_id = p.pais_id AND d.nivel = 1 AND d.es_iso_3166_2 = 1) AS n_subdivisiones_nivel1
FROM dim_pais p
LEFT JOIN dim_region_geografica r3 ON r3.region_geografica_id = p.region_geografica_id
LEFT JOIN dim_region_geografica r2 ON r2.region_geografica_id = r3.region_padre_id
LEFT JOIN dim_region_geografica r1 ON r1.region_geografica_id = r2.region_padre_id
LEFT JOIN dim_region_bm b ON b.region_bm_codigo = p.region_bm_codigo
LEFT JOIN dim_nivel_ingreso i ON i.nivel_ingreso_codigo = p.nivel_ingreso_codigo
LEFT JOIN dim_pais s ON s.pais_id = p.pais_soberano_id;

CREATE VIEW v_subdivision AS
SELECT d.subdivision_id, p.iso3, p.nombre_es AS pais, d.codigo, d.nombre, d.nombre_es, d.tipo_es, d.nivel,
       padre.codigo AS codigo_padre, r.nombre AS region_subnacional, d.latitud, d.longitud,
       d.es_iso_3166_2, eq.iso3 AS tambien_es_pais_iso3
FROM dim_subdivision d
JOIN dim_pais p ON p.pais_id = d.pais_id
LEFT JOIN dim_subdivision padre ON padre.subdivision_id = d.subdivision_padre_id
LEFT JOIN dim_region_subnacional r ON r.region_subnacional_id = d.region_subnacional_id
LEFT JOIN dim_pais eq ON eq.pais_id = d.pais_equivalente_id;

CREATE VIEW v_pais_membresia_anual AS
WITH RECURSIVE anios(anio) AS (SELECT 1945 UNION ALL SELECT anio + 1 FROM anios WHERE anio < 2025)
SELECT m.pais_id, a.anio, m.organizacion_codigo, o.tipo, m.estado
FROM rel_pais_organizacion m
JOIN dim_organizacion o ON o.organizacion_codigo = m.organizacion_codigo
JOIN anios a ON a.anio >= m.anio_ingreso AND (m.anio_salida IS NULL OR a.anio < m.anio_salida);

CREATE VIEW v_vab_provincia_grupo AS
SELECT v.subdivision_id, v.anio, v.estado_dato, r.grupo_sector,
       SUM(v.vab_mill_pesos_2004) AS vab_mill_pesos_2004,
       ROUND(SUM(v.participacion_en_provincia), 4) AS participacion_en_provincia
FROM hecho_subdivision_vab_rama v JOIN dim_rama_cepal r ON r.rama_nro = v.rama_nro
GROUP BY v.subdivision_id, v.anio, v.estado_dato, r.grupo_sector;

CREATE VIEW v_control_poblacion_pais_vs_subdivisiones AS
SELECT p.iso3, h.anio, h.poblacion AS poblacion_banco_mundial, SUM(s.habitantes) AS suma_subdivisiones,
       ROUND(100.0 * SUM(s.habitantes) / h.poblacion - 100, 2) AS diferencia_pct
FROM hecho_subdivision_poblacion s
JOIN dim_subdivision d ON d.subdivision_id = s.subdivision_id
JOIN dim_pais p ON p.pais_id = d.pais_id
JOIN hecho_pais_anual h ON h.pais_id = p.pais_id AND h.anio = s.anio
GROUP BY p.iso3, h.anio, h.poblacion;

CREATE VIEW v_pais_migracion_anual AS
SELECT p.iso3, m.pais_id, m.anio, m.saldo_migratorio_neto, h.poblacion,
       ROUND(1000.0 * m.saldo_migratorio_neto / h.poblacion, 3) AS tasa_migracion_neta_x1000,
       m.stock_migrantes_pct_poblacion, m.remesas_recibidas_usd, m.remesas_recibidas_pct_pib,
       m.remesas_enviadas_usd, ROUND(100.0 * m.remesas_enviadas_usd / f.pib_usd, 4) AS remesas_enviadas_pct_pib,
       m.remesas_recibidas_usd - m.remesas_enviadas_usd AS remesas_netas_usd
FROM hecho_pais_migracion_anual m
JOIN dim_pais p ON p.pais_id = m.pais_id
LEFT JOIN hecho_pais_anual h ON h.pais_id = m.pais_id AND h.anio = m.anio
LEFT JOIN hecho_pais_financiero_deuda f ON f.pais_id = m.pais_id AND f.anio = m.anio;

CREATE VIEW v_pais_financiero_deuda AS
SELECT p.iso3, f.*,
       ROUND(100.0 * COALESCE(f.deuda_externa_usd, f.deuda_externa_ids_usd) / f.pib_usd, 2) AS deuda_externa_pct_pib,
       ROUND(100.0 * f.reservas_internacionales_usd / COALESCE(f.deuda_externa_usd, f.deuda_externa_ids_usd), 2)
           AS reservas_pct_deuda_externa
FROM hecho_pais_financiero_deuda f
JOIN dim_pais p ON p.pais_id = f.pais_id;

CREATE VIEW v_pais_capital_social AS
SELECT p.iso3, c.*,
       ROUND((c.desconfianza_poder_judicial_pct + c.desconfianza_partidos_congreso_pct) / 2.0, 1)
           AS desconfianza_instituciones_pct
FROM hecho_pais_capital_social c
JOIN dim_pais p ON p.pais_id = c.pais_id;

CREATE VIEW v_pais_diversidad_cultural AS
WITH grupos AS (
    SELECT pais_id, codigo_gec, dimension, SUM(poblacion_pct) AS pct_cubierta,
           1 - SUM(poblacion_pct * poblacion_pct) / 10000.0 AS fragmentacion
    FROM rel_pais_composicion
    WHERE poblacion_pct IS NOT NULL
    GROUP BY pais_id, codigo_gec, dimension
), indices AS (
    SELECT pais_id, codigo_gec,
           MAX(CASE WHEN dimension = 'etnia' AND pct_cubierta <= 101 THEN ROUND(fragmentacion, 4) END)
               AS indice_fragmentacion_etnica_0_1,
           MAX(CASE WHEN dimension = 'idioma' AND pct_cubierta <= 101 THEN ROUND(fragmentacion, 4) END)
               AS indice_fragmentacion_linguistica_0_1,
           MAX(CASE WHEN dimension = 'religion' AND pct_cubierta <= 101 THEN ROUND(fragmentacion, 4) END)
               AS indice_fragmentacion_religiosa_0_1,
           MAX(CASE WHEN dimension = 'etnia' THEN ROUND(pct_cubierta, 1) END) AS pct_composicion_etnica_cubierta,
           MAX(CASE WHEN dimension = 'idioma' THEN ROUND(pct_cubierta, 1) END) AS pct_composicion_linguistica_cubierta
    FROM grupos GROUP BY pais_id, codigo_gec
), constitucion AS (
    SELECT * FROM hecho_pais_diversidad_cultural c
    WHERE anio = (SELECT MAX(anio) FROM hecho_pais_diversidad_cultural x WHERE x.pais_id = c.pais_id)
), indigena AS (
    SELECT * FROM hecho_pais_poblacion_indigena i
    WHERE decada_censal = (SELECT MAX(decada_censal) FROM hecho_pais_poblacion_indigena x WHERE x.pais_id = i.pais_id)
)
SELECT p.iso3, p.pais_id, i.codigo_gec, i.indice_fragmentacion_etnica_0_1, i.indice_fragmentacion_linguistica_0_1,
       i.indice_fragmentacion_religiosa_0_1, i.pct_composicion_etnica_cubierta,
       i.pct_composicion_linguistica_cubierta, c.anio AS anio_constitucion_ccp,
       c.es_proteccion_lenguas_constitucion, c.es_derechos_indigenas_constitucion,
       c.es_derechos_culturales_constitucion, ind.decada_censal, ind.poblacion_indigena_pct
FROM dim_pais p
LEFT JOIN indices i ON i.pais_id = p.pais_id
LEFT JOIN constitucion c ON c.pais_id = p.pais_id
LEFT JOIN indigena ind ON ind.pais_id = p.pais_id
WHERE i.pais_id IS NOT NULL OR c.pais_id IS NOT NULL OR ind.pais_id IS NOT NULL;

CREATE VIEW v_pais_salud_cronica AS
SELECT p.iso3, s.*, ROUND(100000.0 * s.avad_total / h.poblacion, 0) AS avad_x100k
FROM hecho_pais_salud_cronica s
JOIN dim_pais p ON p.pais_id = s.pais_id
LEFT JOIN hecho_pais_anual h ON h.pais_id = s.pais_id AND h.anio = s.anio;

CREATE VIEW v_pais_indicadores_sociales AS
WITH claves AS (
    SELECT pais_id, anio FROM hecho_pais_educacion UNION SELECT pais_id, anio FROM hecho_pais_digital_ocio
    UNION SELECT pais_id, anio FROM hecho_pais_empleo_sectorial UNION SELECT pais_id, anio FROM hecho_pais_gasto_cultura
    UNION SELECT pais_id, anio FROM hecho_pais_deporte_olimpico UNION SELECT pais_id, anio FROM hecho_pais_consolas_comercio
)
SELECT p.iso3, p.nombre_es AS pais, k.anio,
       e.alfabetizacion_adultos_pct, e.alfabetizacion_jovenes_15_24_pct,
       ROUND(e.alfabetizacion_adultos_hombres_pct - e.alfabetizacion_adultos_mujeres_pct, 2)
           AS brecha_alfabetizacion_hombres_menos_mujeres_pp,
       e.nivel_alcanzado_secundaria_alta_pct, e.nivel_alcanzado_licenciatura_pct,
       e.escolaridad_promedio_25mas_anios, e.escolaridad_esperada_anios,
       d.usa_redes_sociales_16_74_pct, d.compro_online_videojuegos_software_16_74_pct,
       ROUND(100.0 * s.empleo_construccion_modelado_miles_personas / s.empleo_total_modelado_miles_personas, 3)
           AS empleo_construccion_pct,
       CASE WHEN COALESCE(s.empleo_artes_espectaculos_miles_personas,
                          s.empleo_bibliotecas_museos_patrimonio_miles_personas) IS NOT NULL
            THEN ROUND(100.0 * (COALESCE(s.empleo_artes_espectaculos_miles_personas, 0)
                                + COALESCE(s.empleo_bibliotecas_museos_patrimonio_miles_personas, 0))
                       / s.empleo_total_encuesta_miles_personas, 3) END AS empleo_cultura_pct,
       ROUND(100.0 * s.empleo_juegos_azar_apuestas_miles_personas / s.empleo_total_encuesta_miles_personas, 3)
           AS empleo_juegos_azar_apuestas_pct,
       g.gasto_recreacion_cultura_religion_pct_pib, g.gasto_servicios_culturales_pct_pib,
       g.gasto_servicios_culturales_gob_central_pct_pib, g.fuente_gobierno_general,
       o.juegos_olimpicos, o.atletas_participantes, o.medallas_oro + o.medallas_plata + o.medallas_bronce AS medallas_total,
       ROUND(1e6 * (o.medallas_oro + o.medallas_plata + o.medallas_bronce) / h.poblacion, 3) AS medallas_por_millon_hab,
       ROUND(100.0 * o.atletas_mujeres / o.atletas_participantes, 1) AS atletas_mujeres_pct,
       c.importaciones_consolas_usd, ROUND(c.importaciones_consolas_usd / h.poblacion, 3) AS importaciones_consolas_usd_por_hab,
       c.importaciones_consolas_usd - COALESCE(c.exportaciones_consolas_usd, 0) AS importaciones_netas_consolas_usd
FROM claves k
JOIN dim_pais p ON p.pais_id = k.pais_id
LEFT JOIN hecho_pais_educacion e ON e.pais_id = k.pais_id AND e.anio = k.anio
LEFT JOIN hecho_pais_digital_ocio d ON d.pais_id = k.pais_id AND d.anio = k.anio
LEFT JOIN hecho_pais_empleo_sectorial s ON s.pais_id = k.pais_id AND s.anio = k.anio
LEFT JOIN hecho_pais_gasto_cultura g ON g.pais_id = k.pais_id AND g.anio = k.anio
LEFT JOIN hecho_pais_deporte_olimpico o ON o.pais_id = k.pais_id AND o.anio = k.anio
LEFT JOIN hecho_pais_consolas_comercio c ON c.pais_id = k.pais_id AND c.anio = k.anio
LEFT JOIN hecho_pais_anual h ON h.pais_id = k.pais_id AND h.anio = k.anio;

CREATE VIEW v_subdivision_financiero AS
SELECT s.codigo, s.nombre, d.*,
       ROUND(100.0 * (d.servicio_deuda_amortizacion_mill_pesos + d.servicio_deuda_intereses_mill_pesos)
             / f.ingresos_corrientes_mill_pesos, 2) AS servicio_deuda_pct_ingresos_corrientes,
       ROUND(100.0 * f.intereses_deuda_mill_pesos / f.ingresos_corrientes_mill_pesos, 2)
           AS intereses_pct_ingresos_corrientes,
       ROUND(100.0 * d.deuda_stock_mill_pesos / f.ingresos_totales_mill_pesos, 1) AS deuda_pct_ingresos_totales
FROM hecho_subdivision_financiero d
JOIN dim_subdivision s ON s.subdivision_id = d.subdivision_id
LEFT JOIN hecho_subdivision_finanzas_publicas f ON f.subdivision_id = d.subdivision_id AND f.anio = d.anio;

CREATE VIEW v_subdivision_federalismo_fiscal AS
SELECT s.codigo, s.nombre, f.subdivision_id, f.anio,
       ROUND(100.0 * f.tributarios_origen_nacional_mill_pesos / f.ingresos_totales_mill_pesos, 1)
           AS pct_ingresos_por_transferencias_automaticas,
       ROUND(100.0 * f.tributarios_origen_provincial_mill_pesos / f.gasto_total_mill_pesos, 1)
           AS indice_autonomia_financiera_subnacional,
       ROUND(100.0 * (f.transferencias_corrientes_recibidas_mill_pesos + f.transferencias_capital_recibidas_mill_pesos)
             / f.gasto_total_mill_pesos, 1) AS transferencias_discrecionales_pct_gasto,
       ROUND(100.0 * f.regalias_mill_pesos / f.ingresos_totales_mill_pesos, 1) AS regalias_pct_ingresos,
       ROUND(100.0 * f.resultado_financiero_mill_pesos / f.ingresos_totales_mill_pesos, 1)
           AS resultado_financiero_pct_ingresos
FROM hecho_subdivision_finanzas_publicas f
JOIN dim_subdivision s ON s.subdivision_id = f.subdivision_id;

CREATE VIEW v_pais_anual AS
SELECT v.iso3, v.nombre_es AS pais, v.continente, v.region_bm, v.nivel_ingreso, h.anio, h.poblacion, h.pib_pc_ppp, h.esperanza_vida, h.mortalidad_infantil, h.camas_hospital_x1000, h.medicos_x1000, h.suicidio_total_x100k, h.suicidio_hombres_x100k, h.suicidio_mujeres_x100k, h.gasto_salud_pct_pib, h.gasto_salud_pct_gasto_pub, h.gasto_educacion_pct_pib, h.tipo_cambio_lcu_por_usd, h.ppa_lcu_por_usd_intl, h.gini, h.ingreso_decil1_pct, h.ingreso_quintil1_pct, h.ingreso_quintil2_pct, h.ingreso_quintil3_pct, h.ingreso_quintil4_pct, h.ingreso_quintil5_pct, h.ingreso_decil10_pct, h.lorenz_acum_10, h.lorenz_acum_20, h.lorenz_acum_40, h.lorenz_acum_60, h.lorenz_acum_80, h.lorenz_acum_90, h.gini_aprox_desde_lorenz, h.ratio_quintil5_quintil1, h.ratio_palma, h.dieta_saludable_lcu_dia, h.dieta_saludable_ppa_dia, h.pct_no_puede_pagar_dieta_saludable, h.dieta_saludable_usd_mes, h.dieta_saludable_lcu_mes, h.salario_promedio_mensual_lcu, h.salario_promedio_mensual_usd, h.salario_promedio_mensual_ppa, h.felicidad, h.felicidad_ranking, r.n_igos_cow_total, r.n_acuerdos_comerciales_en_vigor, r.n_aliados_defensa, r.n_aliados_cualquier_pacto, n0.saldo_migratorio_neto, n0.stock_migrantes_pct_poblacion, n0.remesas_recibidas_usd, n0.remesas_recibidas_pct_pib, n0.remesas_enviadas_usd, n1.emisiones_gei_per_capita_tco2e, n1.emisiones_gei_total_mtco2e, n1.emisiones_co2_per_capita_tco2e, n1.energia_renovable_pct_consumo_final, n1.electricidad_renovable_pct, n1.electricidad_hidro_pct, n1.electricidad_solar_eolica_pct, n1.personas_afectadas_desastres_climaticos, n1.muertes_desastres_climaticos, n2.confianza_interpersonal_pct, n2.desconfianza_poder_judicial_pct, n2.desconfianza_partidos_congreso_pct, n2.confianza_policia_pct, n2.confianza_interpersonal_wvs_pct, n2.indice_sociedad_civil_0_1, n2.sociedad_civil_participacion_vdem, n3.es_proteccion_lenguas_constitucion, n3.es_derechos_indigenas_constitucion, n3.es_derechos_culturales_constitucion, n4.indice_control_corrupcion, n4.indice_control_corrupcion_0_100, n4.indice_estado_derecho, n4.indice_estado_derecho_0_100, n4.estabilidad_politica_ausencia_violencia, n4.efectividad_gobierno, n4.calidad_regulatoria, n4.voz_rendicion_cuentas, n4.veto_players_count, n4.indice_democracia_electoral_0_1, n4.indice_democracia_liberal_0_1, n4.indice_estado_derecho_vdem_0_1, n4.indice_corrupcion_politica_vdem_0_1, n4.restricciones_judiciales_ejecutivo_0_1, n4.restricciones_legislativas_ejecutivo_0_1, n5.pib_usd, n5.deuda_externa_ids_usd, n5.deuda_externa_pct_ingreso_nacional, n5.deuda_externa_corto_plazo_pct, n5.servicio_deuda_pct_exportaciones, n5.servicio_deuda_pct_ingreso_nacional, n5.deuda_gobierno_central_pct_pib, n5.intereses_pct_ingresos_fiscales, n5.reservas_internacionales_usd, n5.reservas_internacionales_meses_importacion, n5.deuda_externa_usd, n5.spread_embi_pb, n5.spread_embi_meses, n6.diabetes_prevalencia_pct, n6.mortalidad_ent_30_70_pct, n6.muertes_ent_pct, n6.hipertension_prevalencia_pct, n6.obesidad_adultos_pct, n6.avad_total, n7.banda_ancha_fija_x100, n7.usuarios_internet_pct, n7.gasto_en_i_d_pct_pib, n7.hogares_con_conectividad_pct,
       (SELECT COUNT(*) FROM v_pais_membresia_anual m
         WHERE m.pais_id = h.pais_id AND m.anio = h.anio AND m.estado = 'pleno') AS n_organizaciones_clave
FROM hecho_pais_anual h
JOIN v_pais v ON v.pais_id = h.pais_id
LEFT JOIN hecho_pais_relaciones_anual r ON r.pais_id = h.pais_id AND r.anio = h.anio
LEFT JOIN hecho_pais_migracion_anual n0 ON n0.pais_id = h.pais_id AND n0.anio = h.anio
LEFT JOIN hecho_pais_emisiones n1 ON n1.pais_id = h.pais_id AND n1.anio = h.anio
LEFT JOIN hecho_pais_capital_social n2 ON n2.pais_id = h.pais_id AND n2.anio = h.anio
LEFT JOIN hecho_pais_diversidad_cultural n3 ON n3.pais_id = h.pais_id AND n3.anio = h.anio
LEFT JOIN hecho_pais_institucional_gobernanza n4 ON n4.pais_id = h.pais_id AND n4.anio = h.anio
LEFT JOIN hecho_pais_financiero_deuda n5 ON n5.pais_id = h.pais_id AND n5.anio = h.anio
LEFT JOIN hecho_pais_salud_cronica n6 ON n6.pais_id = h.pais_id AND n6.anio = h.anio
LEFT JOIN hecho_pais_tecnologia n7 ON n7.pais_id = h.pais_id AND n7.anio = h.anio;

CREATE VIEW v_subdivision_anual AS
WITH esqueleto AS (
    SELECT subdivision_id, anio FROM hecho_subdivision_poblacion
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_economia
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_hidrocarburos
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_ganaderia
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_turismo
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_clima
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_salud
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_empresas
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_pymes
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_fiscal
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_salarios
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_canastas
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_pobreza
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_gobierno
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_financiero
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_finanzas_publicas
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_ambiental
    UNION SELECT subdivision_id, anio FROM hecho_subdivision_tecnologia
)
SELECT s.iso3, s.codigo, s.nombre AS subdivision, s.region_subnacional, e.anio,
       t0.habitantes AS habitantes,
       t0.varones AS varones,
       t0.mujeres AS mujeres,
       t1.estado_dato AS estado_dato,
       t1.vab_total_mill_pesos_2004 AS vab_total_mill_pesos_2004,
       t1.pct_vab_adm_publica AS pct_vab_adm_publica,
       t1.pct_vab_ensenanza_publica AS pct_vab_ensenanza_publica,
       t1.pct_vab_salud_publica AS pct_vab_salud_publica,
       t1.pct_vab_hoteles AS pct_vab_hoteles,
       t1.pct_vab_restaurantes AS pct_vab_restaurantes,
       t1.pct_vab_sector_publico AS pct_vab_sector_publico,
       t1.pct_vab_turismo AS pct_vab_turismo,
       t1.pbg_per_capita_pesos_2004 AS pbg_per_capita_pesos_2004,
       t1.poblacion_implicita_vab AS poblacion_implicita_vab,
       t2.petroleo_m3_convencional AS petroleo_m3_convencional,
       t2.petroleo_m3_no_convencional AS petroleo_m3_no_convencional,
       t2.petroleo_m3_total AS petroleo_m3_total,
       t2.gas_miles_m3_convencional AS gas_miles_m3_convencional,
       t2.gas_miles_m3_no_convencional AS gas_miles_m3_no_convencional,
       t2.gas_miles_m3_total AS gas_miles_m3_total,
       t2.meses_con_dato AS hidrocarburos_meses_con_dato,
       t3.vacas AS vacas,
       t3.vaquillonas AS vaquillonas,
       t3.novillos AS novillos,
       t3.novillitos AS novillitos,
       t3.terneros AS terneros,
       t3.terneras AS terneras,
       t3.toros AS toros,
       t3.toritos AS toritos,
       t3.bueyes AS bueyes,
       t3.total_cabezas AS total_cabezas,
       t4.pernoctes_no_residentes AS pernoctes_no_residentes,
       t4.pernoctes_residentes AS pernoctes_residentes,
       t4.pernoctes_total AS pernoctes_total,
       t4.meses_con_dato AS turismo_meses_con_dato,
       t4.localidades_relevadas AS localidades_relevadas,
       t4.viajeros_no_residentes AS viajeros_no_residentes,
       t4.viajeros_residentes AS viajeros_residentes,
       t4.viajeros_total AS viajeros_total,
       t5.temperatura_media_c AS temperatura_media_c,
       t6.pct_vacuna_srp_1ra_dosis_12_meses AS pct_vacuna_srp_1ra_dosis_12_meses,
       t6.pct_vacuna_srp_2da_dosis_ingreso_escolar AS pct_vacuna_srp_2da_dosis_ingreso_escolar,
       t6.medicos AS medicos,
       t6.medicos_cada_10000_hab AS medicos_cada_10000_hab,
       t7.empresas_con_empleados AS empresas_con_empleados,
       t7.empresas_cada_1000_hab AS empresas_cada_1000_hab,
       t7.empresas_grandes_ind_com_serv AS empresas_grandes_ind_com_serv,
       t7.empresas_medianas_ind_com_serv AS empresas_medianas_ind_com_serv,
       t7.empresas_pequenas_ind_com_serv AS empresas_pequenas_ind_com_serv,
       t7.empresas_micro_ind_com_serv AS empresas_micro_ind_com_serv,
       t7.cep_empresas_con_empleados AS cep_empresas_con_empleados,
       t7.cep_locales_1_a_9_empleados AS cep_locales_1_a_9_empleados,
       t7.cep_locales_10_a_49_empleados AS cep_locales_10_a_49_empleados,
       t7.cep_locales_50_a_199_empleados AS cep_locales_50_a_199_empleados,
       t7.cep_locales_200_a_499_empleados AS cep_locales_200_a_499_empleados,
       t7.cep_locales_500_o_mas_empleados AS cep_locales_500_o_mas_empleados,
       t8.fecha_corte AS fecha_corte,
       t8.pymes_total AS pymes_total,
       t8.pymes_micro AS pymes_micro,
       t8.pymes_pequenas AS pymes_pequenas,
       t8.pymes_medianas_tramo1 AS pymes_medianas_tramo1,
       t8.pymes_medianas_tramo2 AS pymes_medianas_tramo2,
       t8.pymes_cada_1000_hab AS pymes_cada_1000_hab,
       t9.recaudacion_propia_mill_pesos AS recaudacion_propia_mill_pesos,
       t9.recaudacion_automotores_mill_pesos AS recaudacion_automotores_mill_pesos,
       t9.recaudacion_ingresos_brutos_mill_pesos AS recaudacion_ingresos_brutos_mill_pesos,
       t9.recaudacion_inmobiliario_mill_pesos AS recaudacion_inmobiliario_mill_pesos,
       t9.recaudacion_otros_mill_pesos AS recaudacion_otros_mill_pesos,
       t9.recaudacion_sellos_mill_pesos AS recaudacion_sellos_mill_pesos,
       t9.pct_ingresos_brutos_en_total AS pct_ingresos_brutos_en_total,
       t9.presion_tributaria_pct_pbg_estimado AS presion_tributaria_pct_pbg_estimado,
       t9.recaudacion_por_habitante_pesos_2024 AS recaudacion_por_habitante_pesos_2024,
       t9.alicuota_iibb_comercio_pct AS alicuota_iibb_comercio_pct,
       t9.alicuota_iibb_industria_pct AS alicuota_iibb_industria_pct,
       t10.salario_promedio_mensual_pesos AS salario_promedio_mensual_pesos,
       t10.salario_promedio_mensual_pesos_2024 AS salario_promedio_mensual_pesos_2024,
       t10.puestos_asalariados_privados_registrados AS puestos_asalariados_privados_registrados,
       t11.cba_adulto_equivalente_pesos_estimado_por_region AS cba_adulto_equivalente_pesos_estimado_por_region,
       t11.cbt_adulto_equivalente_pesos_estimado_por_region AS cbt_adulto_equivalente_pesos_estimado_por_region,
       t11.meses_con_dato AS canastas_meses_con_dato,
       t11.cbt_hogar_tipo_4_personas_pesos_estimado_por_region AS cbt_hogar_tipo_4_personas_pesos_estimado_por_region,
       t12.trimestres_con_dato AS trimestres_con_dato,
       t12.pct_personas_pobres_estimado AS pct_personas_pobres_estimado,
       t12.pct_personas_indigentes_estimado AS pct_personas_indigentes_estimado,
       t12.gini_ingreso_per_capita_familiar_estimado_grandes_ciudades AS gini_ingreso_per_capita_familiar_estimado_grandes_ciudades,
       t12.casos_encuestados AS casos_encuestados,
       t13.familia_politica_gobierno AS familia_politica_gobierno,
       t13.ganador_ultima_eleccion AS ganador_ultima_eleccion,
       t13.anio_ultima_eleccion AS anio_ultima_eleccion,
       t14.deuda_stock_mill_pesos AS deuda_stock_mill_pesos,
       t14.deuda_gobierno_nacional_mill_pesos AS deuda_gobierno_nacional_mill_pesos,
       t14.deuda_fffir_mill_pesos AS deuda_fffir_mill_pesos,
       t14.deuda_ffdp_mill_pesos AS deuda_ffdp_mill_pesos,
       t14.deuda_bancos_mill_pesos AS deuda_bancos_mill_pesos,
       t14.deuda_consolidada_mill_pesos AS deuda_consolidada_mill_pesos,
       t14.deuda_bonos_mill_pesos AS deuda_bonos_mill_pesos,
       t14.deuda_organismos_internacionales_mill_pesos AS deuda_organismos_internacionales_mill_pesos,
       t14.servicio_deuda_amortizacion_mill_pesos AS servicio_deuda_amortizacion_mill_pesos,
       t14.servicio_deuda_intereses_mill_pesos AS servicio_deuda_intereses_mill_pesos,
       t15.ingresos_corrientes_mill_pesos AS ingresos_corrientes_mill_pesos,
       t15.tributarios_mill_pesos AS tributarios_mill_pesos,
       t15.tributarios_origen_provincial_mill_pesos AS tributarios_origen_provincial_mill_pesos,
       t15.tributarios_origen_nacional_mill_pesos AS tributarios_origen_nacional_mill_pesos,
       t15.coparticipacion_neta_mill_pesos AS coparticipacion_neta_mill_pesos,
       t15.contribuciones_seguridad_social_mill_pesos AS contribuciones_seguridad_social_mill_pesos,
       t15.regalias_mill_pesos AS regalias_mill_pesos,
       t15.transferencias_corrientes_recibidas_mill_pesos AS transferencias_corrientes_recibidas_mill_pesos,
       t15.gasto_corriente_mill_pesos AS gasto_corriente_mill_pesos,
       t15.gasto_personal_mill_pesos AS gasto_personal_mill_pesos,
       t15.intereses_deuda_mill_pesos AS intereses_deuda_mill_pesos,
       t15.transferencias_capital_recibidas_mill_pesos AS transferencias_capital_recibidas_mill_pesos,
       t15.inversion_real_directa_mill_pesos AS inversion_real_directa_mill_pesos,
       t15.ingresos_totales_mill_pesos AS ingresos_totales_mill_pesos,
       t15.gasto_total_mill_pesos AS gasto_total_mill_pesos,
       t15.resultado_financiero_mill_pesos AS resultado_financiero_mill_pesos,
       t16.emisiones_gei_per_capita_tco2e AS emisiones_gei_per_capita_tco2e,
       t16.emisiones_gei_total_tco2e AS emisiones_gei_total_tco2e,
       t16.emisiones_gei_electricidad_tco2e AS emisiones_gei_electricidad_tco2e,
       t16.emisiones_gei_industria_tco2e AS emisiones_gei_industria_tco2e,
       t16.emisiones_gei_transporte_tco2e AS emisiones_gei_transporte_tco2e,
       t16.emisiones_gei_edificios_tco2e AS emisiones_gei_edificios_tco2e,
       t16.emisiones_gei_agro_tco2e AS emisiones_gei_agro_tco2e,
       t16.emisiones_gei_residuos_tco2e AS emisiones_gei_residuos_tco2e,
       t17.internet_fijo_accesos_x100_hogares AS internet_fijo_accesos_x100_hogares,
       t17.internet_fijo_accesos_x100_hab AS internet_fijo_accesos_x100_hab,
       t17.internet_fijo_trimestre AS internet_fijo_trimestre
FROM esqueleto e
JOIN v_subdivision s ON s.subdivision_id = e.subdivision_id
LEFT JOIN hecho_subdivision_poblacion t0 ON t0.subdivision_id = e.subdivision_id AND t0.anio = e.anio
LEFT JOIN hecho_subdivision_economia t1 ON t1.subdivision_id = e.subdivision_id AND t1.anio = e.anio
LEFT JOIN hecho_subdivision_hidrocarburos t2 ON t2.subdivision_id = e.subdivision_id AND t2.anio = e.anio
LEFT JOIN hecho_subdivision_ganaderia t3 ON t3.subdivision_id = e.subdivision_id AND t3.anio = e.anio
LEFT JOIN hecho_subdivision_turismo t4 ON t4.subdivision_id = e.subdivision_id AND t4.anio = e.anio
LEFT JOIN hecho_subdivision_clima t5 ON t5.subdivision_id = e.subdivision_id AND t5.anio = e.anio
LEFT JOIN hecho_subdivision_salud t6 ON t6.subdivision_id = e.subdivision_id AND t6.anio = e.anio
LEFT JOIN hecho_subdivision_empresas t7 ON t7.subdivision_id = e.subdivision_id AND t7.anio = e.anio
LEFT JOIN hecho_subdivision_pymes t8 ON t8.subdivision_id = e.subdivision_id AND t8.anio = e.anio
LEFT JOIN hecho_subdivision_fiscal t9 ON t9.subdivision_id = e.subdivision_id AND t9.anio = e.anio
LEFT JOIN hecho_subdivision_salarios t10 ON t10.subdivision_id = e.subdivision_id AND t10.anio = e.anio
LEFT JOIN hecho_subdivision_canastas t11 ON t11.subdivision_id = e.subdivision_id AND t11.anio = e.anio
LEFT JOIN hecho_subdivision_pobreza t12 ON t12.subdivision_id = e.subdivision_id AND t12.anio = e.anio
LEFT JOIN hecho_subdivision_gobierno t13 ON t13.subdivision_id = e.subdivision_id AND t13.anio = e.anio
LEFT JOIN hecho_subdivision_financiero t14 ON t14.subdivision_id = e.subdivision_id AND t14.anio = e.anio
LEFT JOIN hecho_subdivision_finanzas_publicas t15 ON t15.subdivision_id = e.subdivision_id AND t15.anio = e.anio
LEFT JOIN hecho_subdivision_ambiental t16 ON t16.subdivision_id = e.subdivision_id AND t16.anio = e.anio
LEFT JOIN hecho_subdivision_tecnologia t17 ON t17.subdivision_id = e.subdivision_id AND t17.anio = e.anio;