# Fuentes y variables para las 6 dimensiones nuevas

Fecha: 15-10-2026. Este documento es el plan de adquisición: qué fuente usar, cómo pedirle los datos y en qué columna del modelo cae cada variable.

> **Integrado el 15-10-2026.** `extraer_dimensiones_nuevas.py` baja todo lo marcado como verificado o habilitar dominio y deja 13 CSV en esta carpeta; `modelo_unificado/construir_master.py` los carga como tablas `hecho_*` con 7 vistas (lista en `GUIA_MODELO_UNIFICADO.md`). Diferencias con el plan de abajo:
> - La tabla de clima se llama `hecho_pais_emisiones`; la de deuda provincial, `hecho_subdivision_financiero`; la de emisiones regionales, `hecho_subdivision_ambiental` (6 países, no solo Argentina).
> - CEPAL publica *desconfianza* en el poder judicial y en partidos/congreso y *confianza* en la policía: las columnas se llaman así (`desconfianza_poder_judicial_pct`...). No hay serie de confianza en el gobierno; `fuente_encuesta` no hace falta porque Latinobarómetro y WVS quedaron en columnas distintas.
> - En vez de `eventos_climaticos_extremos` (EM-DAT pide registro) se guardan `personas_afectadas_desastres_climaticos` y `muertes_desastres_climaticos` (sequía, inundación, deslizamiento, tormenta, incendio, temperatura extrema; sin sismos ni volcanes). OWID solo trae años con algún evento: vacío no significa cero.
> - El reconocimiento constitucional quedó en tres columnas 0/1 (lenguas, derechos indígenas, derechos culturales) y el % indígena en su propia tabla por década censal.
> - `deuda_pct_pbg` provincial no se calculó: el PBG provincial está en pesos de 2004. En su lugar, `deuda_pct_ingresos_totales`.
> - Quedan pendientes, por ser manuales: calificaciones S&P/Moody's (`rel_pais_calificacion_crediticia`), afiliación a organizaciones civiles (WVS) y deuda provincial en moneda extranjera.

Se respetan las convenciones de `etl/modelo_unificado/GUIA_MODELO_UNIFICADO.md`: prefijos `dim_`/`hecho_`/`rel_`/`v_`, `snake_case` en español, unidad al final del nombre, clave `pais_id` o `subdivision_id` + `anio`, y **nada que se pueda calcular se guarda dos veces** (los cocientes van en vistas `v_`).

## Cómo leer la columna "Estado"

| Estado | Significado |
|---|---|
| **verificado** | El endpoint respondió hoy desde la nube con datos reales (se muestra el valor de prueba cuando ayuda) |
| **ya existe** | La variable o su insumo ya está en `master_paises_provincias.sqlite` |
| **vista** | No se guarda: se calcula en una vista a partir de columnas guardadas |
| **habilitar dominio** | La fuente existe pero el proxy de la nube devuelve 403; hace falta sumar el dominio al entorno |
| **manual** | La fuente pide registro o login: hay que bajar el archivo a mano y subirlo al proyecto |

## Dominios a habilitar (solo los que faltan)

Necesarios:

```
ourworldindata.org api-cepalstat.cepal.org data.iadb.org indicadores.enacom.gob.ar datahub.itu.int comparativeconstitutionsproject.org
```

Opcionales (mejoran o permiten controlar, pero hay alternativa ya habilitada):

```
dgsiaf-repo.mecon.gob.ar www.who.int cdn.who.int worldjusticeproject.org
```

Tercera prueba, 15-10-2026 00:45 UTC: Box funciona (`utexas.box.com` → `public.boxcloud.com`). El CCP "Characteristics of National Constitutions" v5 está en `https://utexas.box.com/shared/static/cpgysqaogi1590ucv5x0wn59urqm00x3.zip` (zip de 118 MB; `ccpcnc_v5.csv` con 21.735 filas país-año × 2.030 columnas, entre ellas `langprot` e `indpolgr_1` a `indpolgr_7`). El enlace `qzs6irrp...` es la cronología de eventos constitucionales, no el contenido.

Segunda prueba, 15-10-2026 00:40 UTC: `api-cepalstat.cepal.org` responde (confianza interpersonal = indicador 1831, ARG 24 %; % población indígena = 4992; desconfianza en el poder judicial = 5528; en partidos y congreso = 995; confianza en la policía = 3257). `data.iadb.org` responde: la DPI 2020 está en `https://data.iadb.org/files/download/5e9bae0b-2d7d-4537-8f9a-b52fa845fd62` (CSV 8.200 filas × 129 columnas, `checks` ARG 2020 = 5); el enlace `300507a6...` de arriba es el PDF de definiciones. `utexas.box.com` responde pero redirige a `utexas.app.box.com` (bloqueado). Opcionales sin habilitar.

Primera prueba, 15-10-2026 00:35 UTC, tras habilitarlos: `ourworldindata.org` y `comparativeconstitutionsproject.org` responden; `indicadores.enacom.gob.ar` responde si se agrega el intermedio Sectigo DV R36 (`argentina_provincias/crudos/sectigo_dv_r36.pem`) al bundle de certificados; los archivos del CCP están en `utexas.box.com` (bloqueado); `api-cepalstat.cepal.org`, `data.iadb.org` y los opcionales siguen en 403 del proxy; `datahub.itu.int` llega pero CloudFront rechaza la conexión desde la nube.

Ya habilitados y suficientes para todo lo demás: `api.worldbank.org`, `ghoapi.azureedge.net`, `sdmx.oecd.org`, `raw.githubusercontent.com`, `estadisticas.bcrp.gob.pe`, `www.argentina.gob.ar`, `datos.gob.ar`, `www.indec.gob.ar`. Probados hoy y bloqueados (no hace falta pedirlos porque hay alternativa): `population.un.org`, `www.imf.org`, `data.imf.org`, `api.uis.unesco.org`, `www.economia.gob.ar`, `www.presupuestoabierto.gob.ar`, `api.bcra.gob.ar`, `edgar.jrc.ec.europa.eu`, `api.ember-energy.org`.

---

## 1. Migración y remesas

**Fuente oficial sugerida:** Banco Mundial WDI, que republica las estimaciones de la División de Población de la ONU (World Population Prospects 2024) para migración y la balanza de pagos del FMI/BM para remesas. Para Argentina por provincia, Censo 2022 del INDEC (población nacida en el extranjero).

**Endpoints y patrón:**

```
https://api.worldbank.org/v2/country/all/indicator/{CODIGO}?format=json&per_page=20000&date=2000:2025
```

Mismo patrón que `paso1_extraer_banco_mundial.py`: se recorre la paginación, se filtran los agregados regionales con la lista de países y se pasa a largo (`iso3, anio, valor`).

**Tabla nueva `hecho_pais_migracion_anual`** (PK `pais_id, anio`)

| Columna | Tipo | Unidad | Fuente / código | Estado |
|---|---|---|---|---|
| `saldo_migratorio_neto` | INTEGER | personas por año | BM `SM.POP.NETM` | verificado (ARG 2025: +2.859; MEX: −108.037) |
| `stock_migrantes_pct_poblacion` | REAL | % de la población | BM `SM.POP.TOTL.ZS` | verificado (ARG 2024: 4,3 %) |
| `remesas_recibidas_usd` | REAL | US$ corrientes | BM `BX.TRF.PWKR.CD.DT` | verificado |
| `remesas_recibidas_pct_pib` | REAL | % del PIB | BM `BX.TRF.PWKR.DT.GD.ZS` | verificado (MEX 2025: 3,55 %) |
| `remesas_enviadas_usd` | REAL | US$ corrientes | BM `BM.TRF.PWKR.CD.DT` | verificado |
| `pib_usd` | REAL | US$ corrientes | BM `NY.GDP.MKTP.CD` (insumo de los cocientes) | verificado |

En la vista `v_pais_migracion_anual`:

| Columna | Cálculo | Estado |
|---|---|---|
| `tasa_migracion_neta_x1000` | `saldo_migratorio_neto / poblacion * 1000` (`poblacion` ya está en `hecho_pais_anual`) | vista |
| `remesas_enviadas_pct_pib` | `remesas_enviadas_usd / pib_usd * 100` (el BM no publica este cociente) | vista |

Notas:
- La ONU publica la tasa por 1.000 directamente, pero su API (`population.un.org/dataportalapi`) está bloqueada y además pide token; calcularla da el mismo número porque el BM usa la misma fuente.
- Cobertura: unos 215 países, 2000-2025 en migración y remesas.
- Provincias argentinas (opcional): `% nacidos en el extranjero` sale del Censo 2022 en `www.indec.gob.ar` (ya habilitado). RENAPER publica extranjeros identificados por provincia en `datosabiertos.renaper.gob.ar` (bloqueado; no lo pido porque el censo alcanza).

---

## 2. Transición energética y cambio climático

**Fuente oficial sugerida:** Banco Mundial (emisiones de EDGAR/JRC y energía de SE4All/IEA/IRENA). Para subdivisiones, el OCDE Regional Database (emisiones por región de 51 países, incluida Argentina). Como respaldo, los archivos de Our World in Data en GitHub.

**Endpoints y patrón:**

```
# país
https://api.worldbank.org/v2/country/all/indicator/{CODIGO}?format=json&per_page=20000
# respaldo con más columnas (verificado, ya habilitado)
https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv      -> ghg_per_capita, total_ghg
https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv -> renewables_share_elec, renewables_share_energy
# subdivisiones (OCDE SDMX, 10 dimensiones; REF_AREA de Argentina = AR01..AR24)
https://sdmx.oecd.org/public/rest/data/OECD.CFE.EDS,DSD_REG_CLIM@DF_GHG,2.4/A.TL2..........?startPeriod=2000&format=csvfilewithlabels
```

**Tabla nueva `hecho_pais_emisiones_energia`** (PK `pais_id, anio`)

| Columna | Tipo | Unidad | Fuente / código | Estado |
|---|---|---|---|---|
| `emisiones_gei_per_capita_tco2e` | REAL | t CO2e por habitante (sin uso del suelo) | BM `EN.GHG.ALL.PC.CE.AR5` | verificado (ARG 2024: 8,19) |
| `emisiones_gei_total_mtco2e` | REAL | Mt CO2e | BM `EN.GHG.ALL.MT.CE.AR5` | verificado |
| `emisiones_co2_per_capita_tco2e` | REAL | t CO2e por habitante | BM `EN.GHG.CO2.PC.CE.AR5` | verificado |
| `energia_renovable_pct_consumo_final` | REAL | % del consumo final de energía | BM `EG.FEC.RNEW.ZS` (hasta 2022) | verificado (ARG 2021: 9,2 %) |
| `electricidad_renovable_pct` | REAL | % de la generación eléctrica | BM `EG.ELC.RNEW.ZS` (hasta 2021) o OWID `renewables_share_elec` (más reciente) | verificado (ARG 2021: 25,5 %) |
| `electricidad_renovable_sin_hidro_pct` | REAL | % de la generación eléctrica | BM `EG.ELC.RNWX.ZS` | verificado |
| `eventos_climaticos_extremos` | INTEGER | eventos por año | EM-DAT (sequías, inundaciones, tormentas, temperatura extrema, incendios) vía el dataset de desastres naturales de OWID | habilitar dominio (`ourworldindata.org`) o manual (`public.emdat.be` pide registro) |
| `personas_afectadas_eventos_extremos` | INTEGER | personas | EM-DAT, misma ruta | habilitar dominio o manual |

`matriz_energetica_renovable_pct` del pedido se separa en dos columnas porque mezcla dos cosas distintas: la porción renovable del **consumo de energía** (incluye transporte y calor, Argentina ~9 %) y la de la **generación eléctrica** (Argentina ~25 %).

**Tabla nueva `hecho_subdivision_ambiental`** (PK `subdivision_id, anio`)

| Columna | Tipo | Unidad | Fuente / código | Estado |
|---|---|---|---|---|
| `emisiones_gei_per_capita_tco2e` | REAL | t CO2e por habitante | OCDE `DF_GHG`, medida `GHG_REG_TOTAL`, unidad `T_CO2E_PS` | verificado (51 países, Argentina incluida, 2021-2023 en la prueba) |
| `emisiones_gei_<sector>_tco2e` | REAL | t CO2e | OCDE `DF_GHG`: `GHG_POWER`, `GHG_AGRICULTURE`, `GHG_TRANSPORT`, `GHG_INDUSTRY`, `GHG_BUILDINGS`, `GHG_WASTE` | verificado |
| `temperatura_media_c` | REAL | °C | ya está en `hecho_subdivision_clima` | ya existe |

Notas:
- `EN.ATM.CO2E.PC` (el código viejo de CO2 per cápita) fue archivado por el BM: devuelve "indicator not found". Usar los `EN.GHG.*.AR5`.
- `EN.CLC.MDAT.ZS` (población afectada por sequías e inundaciones) es un promedio fijo 1990-2009; no sirve como serie anual.
- Inventario oficial argentino: `ciam.ambiente.gob.ar` (bloqueado) e `inventariogei.ambiente.gob.ar` publican el total país por sector. No hace falta habilitarlos porque el BM usa la misma metodología IPCC y la OCDE da la apertura provincial.

---

## 3. Capital social, confianza institucional y diversidad cultural

**Fuentes oficiales sugeridas:**
- Confianza interpersonal y en instituciones: Latinobarómetro (América Latina, 18 países desde 1996) a través de CEPALSTAT, que ya publica los indicadores agregados por país y año. Para el resto del mundo, World Values Survey / European Values Study.
- Participación en organizaciones: World Values Survey (preguntas de membresía activa) y el índice de sociedad civil de V-Dem.
- Diversidad étnica y lingüística: CIA World Factbook, **ya integrado** en `rel_pais_composicion` (etnia e idioma de 236 países).
- Población indígena: censos nacionales vía CEPALSTAT (América Latina) e INDEC Censo 2022 (provincias argentinas).
- Reconocimiento constitucional: Comparative Constitutions Project (CCP).

**Endpoints y patrón:**

```
# CEPALSTAT (habilitar api-cepalstat.cepal.org): primero el árbol temático para obtener el id del indicador,
# después los datos de ese id
https://api-cepalstat.cepal.org/cepalstat/api/v1/thematic-tree?lang=es&format=json
https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/{id}/data?lang=es&format=json
# OWID con datos de WVS/EVS (habilitar ourworldindata.org)
https://ourworldindata.org/grapher/self-reported-trust-attitudes.csv?useColumnShortNames=true
# V-Dem v16 (verificado, ya habilitado: 33,9 MB, se lee con pyreadr como los .rda de alianzas)
https://raw.githubusercontent.com/vdeminstitute/vdemdata/master/data/vdem.RData
# CCP (habilitar comparativeconstitutionsproject.org): archivo país-año de la sección "Download CCP Data"
```

**Tabla nueva `hecho_pais_capital_social`** (PK `pais_id, anio`)

| Columna | Tipo | Unidad | Fuente / código | Estado |
|---|---|---|---|---|
| `confianza_interpersonal_pct` | REAL | % que responde "se puede confiar en la mayoría" | Latinobarómetro vía CEPALSTAT (LatAm, anual); WVS vía OWID (resto, por ola) | habilitar dominio |
| `confianza_poder_judicial_pct` | REAL | % "mucha" + "algo" de confianza | Latinobarómetro vía CEPALSTAT | habilitar dominio |
| `confianza_congreso_pct` | REAL | % "mucha" + "algo" | Latinobarómetro vía CEPALSTAT | habilitar dominio |
| `confianza_gobierno_pct` | REAL | % "mucha" + "algo" | Latinobarómetro vía CEPALSTAT; OCDE Trust Survey (`DSD_GOV_INT@DF_GOV_TDG_2025`, países OCDE) | habilitar dominio / dataflow OCDE listado (sin bajar datos) |
| `fuente_encuesta` | TEXT | "Latinobarómetro", "WVS ola 7"... | (las dos encuestas no son comparables entre sí) | — |
| `tasa_afiliacion_organizaciones_civiles_pct` | REAL | % miembro activo de al menos una organización | WVS (microdatos, preguntas de membresía activa) | manual (`worldvaluessurvey.org` pide registro) |
| `indice_sociedad_civil_0_1` | REAL | índice 0 a 1 | V-Dem `v2xcs_ccsi` (núcleo de sociedad civil) | verificado (archivo accesible) |

En la vista `v_pais_capital_social`:

| Columna | Cálculo | Estado |
|---|---|---|
| `confianza_instituciones_publicas_pct` | promedio de judicial, congreso y gobierno | vista |

**Tablas de diversidad cultural.** El pedido propone `dim_grupo_etnico_linguistico` y `rel_pais_diversidad_cultural`. Los grupos ya están en `rel_pais_composicion` (columnas `dimension` = etnia/idioma/religión, `grupo`, `poblacion_pct`), así que no conviene duplicarlos: alcanza con una vista y una tabla chica.

| Columna | Tipo | Unidad | Fuente / cálculo | Estado |
|---|---|---|---|---|
| `indice_fragmentacion_etnica_0_1` | REAL | probabilidad 0 a 1 | `1 − Σ pᵢ²` sobre `rel_pais_composicion` con `dimension = 'etnia'` | vista (`v_pais_diversidad_cultural`) |
| `indice_fragmentacion_linguistica_0_1` | REAL | probabilidad 0 a 1 | igual, `dimension = 'idioma'` | vista |
| `pct_composicion_cubierta` | REAL | % | suma de `poblacion_pct` usada (control de calidad: si es baja, el índice está subestimado) | vista |
| `poblacion_indigena_pct` | REAL | % de la población | censos vía CEPALSTAT (LatAm); INDEC Censo 2022 para provincias | habilitar dominio (CEPALSTAT) / verificado el dominio INDEC |
| `es_reconocimiento_constitucional_derechos_culturales` | INTEGER | 0/1 | CCP: protección del uso de lenguas (`langprot`) y derechos de pueblos indígenas (`indpolgr`) | habilitar dominio |

`poblacion_indigena_pct` y el booleano constitucional van en una tabla nueva `hecho_pais_diversidad_cultural` (PK `pais_id, anio`), porque cambian con cada censo o reforma.

Notas:
- El Factbook lista los grupos con porcentajes redondeados y a veces "otros 5 %": el índice calculado así es una aproximación. Para comparar con la literatura existe el Historical Index of Ethnic Fractionalization (Harvard Dataverse), que no pido por ahora.
- Latinobarómetro y WVS miden en años y con muestras distintas; se guardan en filas separadas con `fuente_encuesta` y no se mezclan en el mismo gráfico sin aviso.

---

## 4. Estado de derecho y gobernanza

**Fuente oficial sugerida:** Worldwide Governance Indicators del Banco Mundial (fuente 3 de la API, actualizada el 25-09-2026, datos hasta 2025). Complementos: V-Dem (democracia y límites al Ejecutivo) y la Database of Political Institutions del BID (actores de veto).

**Endpoints y patrón:**

```
https://api.worldbank.org/v2/country/all/indicator/GOV_WGI_{XX}.{EST|SC}?source=3&format=json&per_page=20000
# XX = CC (corrupción), RL (estado de derecho), PV (estabilidad política), GE (efectividad), RQ (calidad regulatoria), VA (voz y rendición de cuentas)
https://raw.githubusercontent.com/vdeminstitute/vdemdata/master/data/vdem.RData
# DPI 2020 (habilitar data.iadb.org): CSV del dataset "The Database of Political Institutions (DPI) 2020"
https://data.iadb.org/file/download/300507a6-8295-48fa-988c-4bd279e4dea0
```

**Tabla nueva `hecho_pais_institucional_gobernanza`** (PK `pais_id, anio`)

| Columna | Tipo | Unidad | Fuente / código | Estado |
|---|---|---|---|---|
| `indice_control_corrupcion` | REAL | estimación, aprox. −2,5 a +2,5 | BM `GOV_WGI_CC.EST` | verificado (ARG 2025: −0,39) |
| `indice_control_corrupcion_0_100` | REAL | puntaje 0 a 100 | BM `GOV_WGI_CC.SC` | verificado |
| `indice_estado_derecho` | REAL | −2,5 a +2,5 | BM `GOV_WGI_RL.EST` | verificado (ARG 2025: −0,10) |
| `indice_estado_derecho_0_100` | REAL | 0 a 100 | BM `GOV_WGI_RL.SC` | verificado |
| `estabilidad_politica_ausencia_violencia` | REAL | −2,5 a +2,5 | BM `GOV_WGI_PV.EST` | verificado (ARG 2025: +0,16) |
| `efectividad_gobierno` | REAL | −2,5 a +2,5 | BM `GOV_WGI_GE.EST` | verificado |
| `calidad_regulatoria` | REAL | −2,5 a +2,5 | BM `GOV_WGI_RQ.EST` | verificado |
| `voz_rendicion_cuentas` | REAL | −2,5 a +2,5 | BM `GOV_WGI_VA.EST` | verificado |
| `veto_players_count` | INTEGER | cantidad de actores de veto | DPI 2020, variable `checks` (1975-2020) | habilitar dominio |
| `indice_democracia_electoral_0_1` | REAL | 0 a 1 | V-Dem `v2x_polyarchy` | verificado (archivo accesible) |
| `indice_estado_derecho_vdem_0_1` | REAL | 0 a 1 | V-Dem `v2x_rule` | verificado |
| `indice_corrupcion_politica_vdem_0_1` | REAL | 0 a 1 (más alto = más corrupción) | V-Dem `v2x_corr` | verificado |
| `restricciones_judiciales_ejecutivo_0_1` | REAL | 0 a 1 | V-Dem `v2x_jucon` | verificado |

Notas:
- Corrección al pedido: en los WGI, **−2,5 a +2,5 es la estimación**, no un percentil. La API ya no publica el rango percentil (`CC.PER.RNK` y los códigos sin prefijo `GOV_WGI_` dan "indicator not found"); en su lugar trae el puntaje 0-100 (`.SC`), que guardo aparte.
- La DPI termina en 2020. Para años posteriores se puede usar POLCON (Henisz, Wharton, bloqueado) o contar actores con V-Dem; lo dejo como pendiente.
- V-Dem resuelve también el "Índice de Democracia" que figura en las instrucciones del proyecto y que los KPIs marcaban como faltante.
- WJP Rule of Law Index (`worldjusticeproject.org`, opcional): datos anuales desde 2012, útil para validar `indice_estado_derecho`.

---

## 5. Análisis financiero y riesgo de crédito

**Fuentes oficiales sugeridas:**
- Deuda externa, servicio y reservas: International Debt Statistics del BM (fuente 6, países de ingreso bajo y medio) y Quarterly External Debt Statistics BM/FMI (fuente 22, todos los países).
- Spread soberano: el EMBI es de J.P. Morgan (propietario). El Banco Central de Reserva del Perú republica el EMBIG mensual de 8 países latinoamericanos más los agregados, con API abierta.
- Calificaciones: las agencias publican su historial completo en XBRL por obligación de la regla 17g-7(b) de la SEC; no hay una base pública consolidada.
- Deuda provincial argentina: Subsecretaría de Coordinación Fiscal Provincial (ex DNAP), Ministerio de Economía.

**Endpoints y patrón (país):**

```
https://api.worldbank.org/v2/country/all/indicator/{CODIGO}?format=json&per_page=20000
https://api.worldbank.org/v2/country/all/indicator/DT.DOD.DECT.CD.AR.US?source=22&format=json   # trimestral, "2026Q1"
# BCRP, serie mensual (promedio del mes, en puntos básicos); ir de a una serie con pausa: el servidor tiene Incapsula
https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{SERIE}/json/2000-1/2026-12
#   PN01129XM Perú, PN01130XM Argentina, PN01131XM Brasil, PN01132XM Chile, PN01133XM Colombia,
#   PN01134XM Ecuador, PN01135XM México, PN01136XM Venezuela, PN01137XM Latin EMBIG, PN01138XM EMBIG emergentes
```

**Tabla nueva `hecho_pais_financiero_deuda`** (PK `pais_id, anio`)

| Columna | Tipo | Unidad | Fuente / código | Estado |
|---|---|---|---|---|
| `deuda_externa_usd` | REAL | US$ corrientes | BM `DT.DOD.DECT.CD` (IDS, ~120 países) o `DT.DOD.DECT.CD.AR.US` fuente 22 (QEDS, todos; dato de fin de año = T4) | verificado (ARG 2024: 242.357 M; QEDS 2026T1: 321.783 M) |
| `deuda_externa_pct_ingreso_nacional` | REAL | % del INB | BM `DT.DOD.DECT.GN.ZS` | verificado (ARG 2024: 39,1 %) |
| `deuda_externa_corto_plazo_pct` | REAL | % de la deuda externa | BM `DT.DOD.DSTC.ZS` | verificado |
| `servicio_deuda_pct_exportaciones` | REAL | % de exportaciones de bienes, servicios e ingreso primario | BM `DT.TDS.DECT.EX.ZS` | verificado (ARG 2024: 38,3 %; MEX: 9,5 %) |
| `servicio_deuda_pct_ingreso_nacional` | REAL | % del INB | BM `DT.TDS.DECT.GN.ZS` | verificado |
| `deuda_gobierno_central_pct_pib` | REAL | % del PIB | BM `GC.DOD.TOTL.GD.ZS` (cobertura irregular: sin ARG) | verificado |
| `intereses_pct_ingresos_fiscales` | REAL | % de los ingresos del gobierno | BM `GC.XPN.INTP.RV.ZS` | verificado |
| `reservas_internacionales_usd` | REAL | US$ (incluye oro) | BM `FI.RES.TOTL.CD` | verificado |
| `reservas_internacionales_meses_importacion` | REAL | meses de importaciones | BM `FI.RES.TOTL.MO` | verificado (ARG 2025: 4,0) |
| `spread_embi_pb` | REAL | puntos básicos (promedio anual de los promedios mensuales) | BCRP, series de arriba | verificado (ARG sep-2026: 534; desde 2008 al menos) |

En la vista `v_pais_financiero_deuda`:

| Columna | Cálculo | Estado |
|---|---|---|
| `deuda_externa_pct_pib` | `deuda_externa_usd / pib_usd * 100` (el BM la publica sobre INB, no sobre PIB) | vista |

**Calificaciones: tabla nueva `rel_pais_calificacion_crediticia`** (PK `pais_id, agencia, fecha`), porque una calificación cambia en fechas puntuales y no una vez por año.

| Columna | Tipo | Unidad | Fuente | Estado |
|---|---|---|---|---|
| `agencia` | TEXT | "S&P", "Moody's", "Fitch" | — | — |
| `fecha` | TEXT | AAAA-MM-DD | archivos XBRL 17g-7(b) de cada agencia | manual (los portales de S&P y Moody's piden aceptar términos o registro; no verificado desde la nube) |
| `calificacion` | TEXT | escala de la agencia: "BBB", "Baa2", "CCC+" | idem | manual |
| `calificacion_escala_1_22` | INTEGER | 1 = AAA/Aaa ... 22 = D | tabla de equivalencias propia | — |
| `perspectiva` | TEXT | positiva / estable / negativa | idem | manual |

En `v_pais_financiero_deuda` se agregan `calificacion_crediticia_sp` y `calificacion_crediticia_moodys` (TEXT): la vigente al 31 de diciembre de cada año.

**Tabla nueva `hecho_subdivision_financiero`** (PK `subdivision_id, anio`; Argentina, 24 jurisdicciones)

| Columna | Tipo | Unidad | Fuente | Estado |
|---|---|---|---|---|
| `deuda_stock_mill_pesos` | REAL | millones de $ corrientes, al 31-12 | Coordinación Fiscal Provincial, "Evolución de stock" (columna "Total sin deuda flotante") | verificado (consolidado mar-2026: 32,6 billones; Buenos Aires 16,7) |
| `deuda_bonos_mill_pesos` | REAL | millones de $ | idem, columna "Bonos" (valor residual) | verificado |
| `deuda_organismos_internacionales_mill_pesos` | REAL | millones de $ | idem | verificado |
| `deuda_gobierno_nacional_mill_pesos` | REAL | millones de $ | idem (+ FFFIR) | verificado |
| `deuda_bancos_mill_pesos` | REAL | millones de $ | idem | verificado |
| `servicio_deuda_amortizacion_mill_pesos` | REAL | millones de $ devengados en el año | "Evolución de servicios" | verificado |
| `servicio_deuda_intereses_mill_pesos` | REAL | millones de $ | idem | verificado |
| `deuda_moneda_extranjera_pct` | REAL | % del stock | **sin dato por provincia** (ver nota) | pendiente |

En la vista `v_subdivision_financiero`:

| Columna | Cálculo | Estado |
|---|---|---|
| `deuda_subnacional_millones_moneda_local` | = `deuda_stock_mill_pesos` | vista |
| `servicio_deuda_sobre_ingresos_corrientes_pct` | `(amortización + intereses) / ingresos_corrientes_mill_pesos` (de la sección 6) `* 100` | vista |
| `deuda_pct_pbg` | `deuda_stock_mill_pesos` sobre el PBG nominal | vista (el PBG provincial está en pesos de 2004; hay que inflarlo con el deflactor que ya se bajó en `crudos/bm_arg_NY.GDP.DEFL.ZS.json`) |

Patrón de URL (en `www.argentina.gob.ar`, ya habilitado; los nombres no siguen una regla fija, así que se leen de la página):

```
https://www.argentina.gob.ar/economia/sechacienda/coordinacion-fiscal-provincial/deuda-publica-provincial/evolucion-de-stock
  -> /sites/default/files/stock_consolidado_{AAAA}_-_3112.xlsx (2009-2024; 2013 y antes en .xls), stock_iv_trim_2025_2.xlsx, stock_i_trim_2026.xlsx
https://www.argentina.gob.ar/economia/sechacienda/coordinacion-fiscal-provincial/deuda-publica-provincial/evolucion-de-servicios
```

Nota sobre moneda extranjera: los Excel por provincia abren la deuda por acreedor, no por moneda. La moneda solo aparece consolidada en el informe anual (`situacion_de_la_deuda_provincial_2024.pdf`: 89 % en moneda extranjera a fines de 2024). Propuesta: guardar `deuda_organismos_internacionales_mill_pesos` (toda en dólares) como **piso** del porcentaje en moneda extranjera, y completar el dato exacto desde los informes trimestrales de deuda de cada provincia si se necesita.

---

## 6. Institucional y federalismo fiscal subnacional

**Fuente oficial sugerida:** Coordinación Fiscal Provincial, serie "Esquema Ahorro-Inversión-Financiamiento" (AIF) de la Administración Pública No Financiera de cada provincia, 2005-2025, en una sola planilla con una hoja por provincia. Separa ingresos tributarios de **origen provincial** y de **origen nacional** (coparticipación y leyes especiales = transferencias automáticas), y las **transferencias corrientes y de capital** recibidas (no automáticas). Complementos: Recursos de Origen Nacional (RON, transferencias automáticas mensuales) y, para comparar países, la base SNG-WOFI de la OCDE.

**Endpoints y patrón:**

```
# AIF 2005-2025 (verificado, 496 KB, 25 hojas: Consolidado + 24 jurisdicciones; millones de $)
https://www.argentina.gob.ar/sites/default/files/serie_aif-apnf-2025.xlsx
# trimestrales sueltos 1983-2026 (mismo formato, para años previos o el año en curso)
https://www.argentina.gob.ar/economia/sechacienda/coordinacion-fiscal-provincial/ejecucion-presupuestaria-provincial/ejecuciones
# Transferencias automáticas (RON), consolidado anual por provincia y régimen (verificado)
https://www.argentina.gob.ar/sites/default/files/informacion_consolidada_2024.xlsx   (2007-2026 en la página /asuntosprovinciales/ron)
# Transferencias no automáticas con detalle de programa (opcional, habilitar dgsiaf-repo.mecon.gob.ar):
# presupuesto nacional ejecutado, filtrar inciso 5 (transferencias) con ubicación geográfica = provincia (columnas a confirmar al habilitar)
https://dgsiaf-repo.mecon.gob.ar/repository/pa/datasets/{AAAA}/credito-anual-{AAAA}.zip
# Países: OCDE SNG-WOFI (verificado; ARG con dato 2020)
https://sdmx.oecd.org/public/rest/data/OECD.CFE.RDG,DSD_SNG_WOFI@DF_FINANCE,1.0/{ISO3}........?format=csvfilewithlabels
```

**Tabla nueva `hecho_subdivision_finanzas_publicas`** (PK `subdivision_id, anio`): los montos del AIF, sin cocientes.

| Columna | Tipo | Unidad | Renglón del AIF | Estado |
|---|---|---|---|---|
| `ingresos_corrientes_mill_pesos` | REAL | millones de $ corrientes | I. Ingresos corrientes | verificado (Córdoba 2024: 7,89 billones) |
| `tributarios_origen_provincial_mill_pesos` | REAL | millones de $ | Tributarios de origen provincial | verificado |
| `tributarios_origen_nacional_mill_pesos` | REAL | millones de $ | Tributarios de origen nacional (coparticipación neta + financiamiento educativo + otros de origen nacional) | verificado |
| `coparticipacion_neta_mill_pesos` | REAL | millones de $ | Distribución secundaria neta Ley 23.548 | verificado |
| `regalias_mill_pesos` | REAL | millones de $ | Regalías | verificado |
| `transferencias_corrientes_recibidas_mill_pesos` | REAL | millones de $ | I. Transferencias corrientes | verificado |
| `transferencias_capital_recibidas_mill_pesos` | REAL | millones de $ | IV. Transferencias de capital | verificado |
| `ingresos_totales_mill_pesos` | REAL | millones de $ | VI. Ingresos totales | verificado |
| `gasto_total_mill_pesos` | REAL | millones de $ | VII. Gastos totales | verificado |
| `gasto_personal_mill_pesos` | REAL | millones de $ | Personal | verificado |
| `intereses_deuda_mill_pesos` | REAL | millones de $ | Rentas de la propiedad (gasto) | verificado |
| `resultado_financiero_mill_pesos` | REAL | millones de $ | VIII. Resultado financiero | verificado |

Vista `v_subdivision_federalismo_fiscal` con las tres variables del pedido:

| Columna | Cálculo | Estado |
|---|---|---|
| `pct_ingresos_por_transferencias_automaticas` | `tributarios_origen_nacional / ingresos_totales * 100` | vista |
| `indice_autonomia_financiera_subnacional` | `tributarios_origen_provincial / gasto_total * 100` | vista |
| `transferencias_discrecionales_pct_gasto` | `(transferencias_corrientes_recibidas + transferencias_capital_recibidas) / gasto_total * 100` | vista |
| `resultado_financiero_pct_ingresos` | `resultado_financiero / ingresos_totales * 100` | vista |

Notas:
- Ya existe `hecho_subdivision_fiscal` con la recaudación propia por impuesto (serie DNAP 1984-2025). Sirve de control: `recaudacion_propia_mill_pesos` debería acercarse a `tributarios_origen_provincial_mill_pesos` del AIF.
- Las transferencias corrientes y de capital del AIF son en su mayoría no automáticas de la Nación, pero pueden incluir transferencias de otros entes. El archivo de `dgsiaf-repo.mecon.gob.ar` permite confirmarlo desde el lado nacional (lo que la Nación devengó con destino a cada provincia), por eso queda como opcional.
- Para otros países de América Latina, SNG-WOFI de la OCDE da la composición de ingresos subnacionales (impuestos, transferencias, deuda) como % del total, pero un solo año por país en la mayoría de los casos.

---

## Complementos de los módulos (salud y tecnología)

### Salud pública: ampliación de `hecho_pais_anual` o tabla nueva `hecho_pais_salud_cronica`

**Fuente:** OMS Global Health Observatory (`ghoapi.azureedge.net`, ya habilitado) y Banco Mundial. Patrón OMS: `https://ghoapi.azureedge.net/api/{CODIGO}?$filter=Dim1 eq 'SEX_BTSX' and SpatialDimType eq 'COUNTRY'`.

| Columna | Tipo | Unidad | Fuente / código | Estado |
|---|---|---|---|---|
| `diabetes_prevalencia_pct` | REAL | % de 20 a 79 años | BM `SH.STA.DIAB.ZS` | verificado (ARG 2024: 14 %) |
| `hipertension_prevalencia_pct` | REAL | % de 30 a 79 años, estandarizado por edad | OMS `NCD_HYP_PREVALENCE_A` (194 países, 1990-2019) | verificado |
| `obesidad_adultos_pct` | REAL | % de 18+ años, estandarizado | OMS `NCD_BMI_30A` (199 países, 1980-2024) | verificado |
| `mortalidad_ent_30_70_pct` | REAL | probabilidad de morir entre 30 y 70 años por ECV, cáncer, diabetes o respiratoria crónica | BM `SH.DYN.NCOM.ZS` / OMS `NCDMORT3070` (185 países, 2000-2021) | verificado (ARG 2021: 13,4 %) |
| `muertes_ent_pct` | REAL | % de las muertes | BM `SH.DTH.NCOM.ZS` | verificado (ARG 2021: 60,5 %) |
| `anios_vida_ajustados_discapacidad_avad_x100k` | REAL | AVAD por 100.000 hab. | OMS Global Health Estimates 2021 (2000, 2010, 2015, 2019, 2020, 2021) o IHME GBD vía OWID (anual) | habilitar dominio (`ourworldindata.org`; o `www.who.int`/`cdn.who.int` para el archivo OMS) |

`prevalencia_enfermedades_no_transmisibles_pct` del pedido no existe como indicador oficial único (nadie suma diabéticos, hipertensos y oncológicos sin doble conteo). Propongo reemplazarla por las cuatro columnas de prevalencia y mortalidad de arriba. En la API de la OMS, los AVAD por país solo están para 2000 y 2012 (`GBD_DALYRTAGE`); `GHE_DALYRATE` trae regiones, no países.

### Tecnología: tabla nueva `hecho_pais_tecnologia`

| Columna | Tipo | Unidad | Fuente / código | Estado |
|---|---|---|---|---|
| `banda_ancha_fija_x100` | REAL | suscripciones por 100 hab. | BM `IT.NET.BBND.P2` | verificado (ARG 2024: 26,1) |
| `usuarios_internet_pct` | REAL | % de personas | BM `IT.NET.USER.ZS` | verificado (ARG 2024: 89,7 %) |
| `hogares_con_conectividad_pct` | REAL | % de hogares con internet en casa | UIT DataHub (indicador "Households with Internet access at home"); OCDE `DSD_ICT_HH_IND@DF_HH` para países OCDE | habilitar dominio (`datahub.itu.int`) / dataflow OCDE listado (sin bajar datos) |
| `gasto_en_i_d_pct_pib` | REAL | % del PIB | BM `GB.XPD.RSDV.GD.ZS` (fuente UNESCO) | verificado (ARG 2023: 0,60 %) |

Para provincias argentinas, `hecho_subdivision_tecnologia` con `internet_fijo_accesos_x100_hogares` (REAL) desde ENACOM: `https://indicadores.enacom.gob.ar/Files/DatosAbiertos/internet_accesos_penetracion_provincias.csv` (listado en el catálogo de datos.gob.ar; dominio a habilitar). Mismo sitio: accesos por tecnología y velocidad media de bajada por provincia.

---

## Resumen: qué ya está y qué es nuevo

| Ya está en el modelo | Dónde |
|---|---|
| Población, PIB pc PPA, gasto en salud y educación | `hecho_pais_anual` |
| Felicidad (puntaje y ranking WHR) | `hecho_pais_anual` |
| Grupos étnicos, idiomas y religiones con % | `rel_pais_composicion` (Factbook) |
| Tipo de gobierno, sistema legal, voto obligatorio (texto) | `hecho_pais_perfil_factbook` |
| Recaudación propia provincial por impuesto, presión tributaria | `hecho_subdivision_fiscal` |
| Temperatura por provincia | `hecho_subdivision_clima` |

Todo lo demás de este documento es nuevo: no hay WGI, emisiones, migración, remesas, deuda, EMBI, V-Dem ni finanzas provinciales en la base actual.

Orden sugerido para integrar, de menor a mayor esfuerzo: (1) los indicadores del Banco Mundial y la OMS, que siguen el patrón del paso 1; (2) AIF, stock y servicios de deuda provincial y EMBI del BCRP, ya accesibles; (3) V-Dem; (4) lo que depende de dominios nuevos; (5) lo manual (WVS, calificaciones).
