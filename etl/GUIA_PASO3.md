# Paso 3: las seis dimensiones nuevas en el panel de países

El paso 3 agrega a `datos_procesados/paises_anual.csv` 62 columnas de las dimensiones nuevas (migración, clima, capital social, constituciones, gobernanza, deuda, salud crónica y tecnología), con la misma clave **iso3 + anio**. No descarga nada: une las tablas por país que deja `fuentes_nuevas/extraer_dimensiones_nuevas.py`.

```bash
python paso1_extraer_banco_mundial.py
python paso2_distribucion_precios_bienestar.py
python fuentes_nuevas/extraer_dimensiones_nuevas.py   # baja los datos (solo si hace falta actualizarlos)
python paso3_dimensiones_nuevas.py
```

Si vuelves a correr el paso 1, el archivo se regenera sin las columnas de los pasos 2 y 3: vuelve a correr los dos. Las filas no cambian (217 países, 2000-2024); los datos de 2025 de algunas fuentes quedan solo en las tablas de `fuentes_nuevas/`.

## Columnas nuevas, por grupo

| Grupo (tabla de origen en `fuentes_nuevas/`) | Columnas | Fuente |
|---|---|---|
| Migración y remesas (`pais_migracion_anual.csv`) | `saldo_migratorio_neto`, `stock_migrantes_pct_poblacion` (cada 5 años), `remesas_recibidas_usd`, `remesas_recibidas_pct_pib`, `remesas_enviadas_usd` | Banco Mundial (ONU WPP, FMI) |
| Emisiones y energía (`pais_emisiones_energia_anual.csv`) | `emisiones_gei_per_capita_tco2e`, `emisiones_gei_total_mtco2e`, `emisiones_co2_per_capita_tco2e`, `energia_renovable_pct_consumo_final`, `electricidad_renovable_pct`, `electricidad_hidro_pct`, `electricidad_solar_eolica_pct`, `personas_afectadas_desastres_climaticos`, `muertes_desastres_climaticos` | Banco Mundial (EDGAR), OWID (Ember, EM-DAT) |
| Capital social (`pais_capital_social_anual.csv`) | `confianza_interpersonal_pct`, `desconfianza_poder_judicial_pct`, `desconfianza_partidos_congreso_pct`, `confianza_policia_pct` (Latinobarómetro, 18 países de AL), `confianza_interpersonal_wvs_pct` (por ola), `indice_sociedad_civil_0_1`, `sociedad_civil_participacion_vdem` | CEPALSTAT, OWID (WVS), V-Dem |
| Constituciones (`pais_diversidad_cultural_anual.csv`) | `es_proteccion_lenguas_constitucion`, `es_derechos_indigenas_constitucion`, `es_derechos_culturales_constitucion` (0/1, hasta 2023) | Comparative Constitutions Project |
| Gobernanza (`pais_gobernanza_anual.csv`) | `indice_control_corrupcion`, `indice_estado_derecho` (−2,5 a 2,5) y sus `_0_100`, `estabilidad_politica_ausencia_violencia`, `efectividad_gobierno`, `calidad_regulatoria`, `voz_rendicion_cuentas`, `veto_players_count` (hasta 2020), 6 índices V-Dem `_0_1` | Banco Mundial WGI, BID DPI, V-Dem |
| Deuda y riesgo (`pais_financiero_deuda_anual.csv`) | `pib_usd`, `deuda_externa_usd` (QEDS), `deuda_externa_ids_usd`, `deuda_externa_pct_ingreso_nacional`, `deuda_externa_corto_plazo_pct`, `servicio_deuda_pct_exportaciones`, `servicio_deuda_pct_ingreso_nacional`, `deuda_gobierno_central_pct_pib`, `intereses_pct_ingresos_fiscales`, `reservas_internacionales_usd`, `reservas_internacionales_meses_importacion`, `spread_embi_pb` y `spread_embi_meses` (8 países de AL) | Banco Mundial (IDS, QEDS), BCRP |
| Salud crónica (`pais_salud_cronica_anual.csv`) | `diabetes_prevalencia_pct`, `mortalidad_ent_30_70_pct`, `muertes_ent_pct`, `hipertension_prevalencia_pct` (hasta 2019), `obesidad_adultos_pct`, `avad_total` | Banco Mundial, OMS |
| Tecnología (`pais_tecnologia_anual.csv`) | `banda_ancha_fija_x100`, `usuarios_internet_pct`, `gasto_en_i_d_pct_pib`, `hogares_con_conectividad_pct` (países OCDE) | Banco Mundial, OCDE |

El detalle de cada fuente está en `fuentes_nuevas/FUENTES_DIMENSIONES_NUEVAS.md`.

## En la base unificada

`modelo_unificado/construir_master.py` no guarda estas columnas dos veces: comprueba que coincidan con sus tablas (`hecho_pais_migracion_anual`, `hecho_pais_emisiones`...), las saca de `hecho_pais_anual` y las vuelve a juntar en la vista `v_pais_anual`, que tiene las mismas columnas que el CSV.
