# Cuatro enfoques del riesgo urbano (375 ciudades de más de 2 millones)

Este paso suma profundidad académica al scorecard UNDRR. Mide cada ciudad con cuatro índices, uno por enfoque teórico. El documento con el marco teórico, los resultados y la bibliografía es "Cuatro enfoques del riesgo urbano" (Claude Docs).

| Índice | Enfoque | Pregunta | Indicadores |
| --- | --- | --- | --- |
| `indice_epu` Producción del riesgo | Ecología política urbana | ¿Cómo el poder y la transformación del ambiente producen riesgo? | 7 |
| `indice_vse` Vulnerabilidad socio-espacial | Vulnerabilidad socio-espacial | ¿Cómo las desigualdades condicionan exposición y recuperación? | 11 |
| `indice_viv` Precariedad habitacional (subíndice) | Vulnerabilidad socio-espacial | ¿Cuánta vivienda informal o precaria hay? | 5 (también cuentan en `indice_vse`) |
| `indice_mu` Presión metabólica | Metabolismo urbano | ¿Cómo los flujos de agua, energía, materiales y residuos condicionan la resiliencia? | 7 |
| `indice_pg` Déficit de gobernanza | Planificación y gobernanza | ¿Cómo instituciones y normas condicionan el espacio y la gestión del riesgo? | 8 |

Todos van de 0 a 100 (percentil entre las 375 ciudades). Más alto siempre es más crítico.

El subíndice de precariedad habitacional sigue los criterios de tugurio de ONU-Hábitat (ODS 11.1.1). Usa cinco indicadores: tugurios (dato del municipio en 12 ciudades latinoamericanas; si no, país, Banco Mundial EN.POP.SLUM.UR.ZS), sin saneamiento básico urbano (país, SH.STA.BASS.UR.ZS), hacinamiento (volumen residencial por habitante, GHSL, por ciudad), vivienda de 1-2 pisos y vivienda baja en zona costera baja.

## Cómo se corre

```
cd etl
python riesgo_ciudades_mundo/bajar_ghsl.py        # solo si faltan los CSV de GHSL (lo hace actualizar_mundo.py)
python enfoques_urbanos/construir_enfoques.py
```

Va en `actualizar_mensual.py` como paso `enfoques_urbanos`, justo después de `riesgo_ciudades_mundo`.

## Qué lee

- `riesgo_ciudades_mundo/datos/ghsl_ciudades.csv`, `amenaza_capacidad_mundo.csv`, `indicadores_pais.csv`.
- `riesgo_ciudades_mundo/crudos/ghsl/csv/` los temas de GHSL UCDB R2024A: EXPOSURE, GHSL, SDG, GREENNESS, EMISSIONS, NATURAL_SYSTEMS, SOCIOECONOMIC, HEALTH, INFRASTRUCTURES. Se unen por `ID_UC_G0`.
- `riesgo_ciudades_mundo/crudos/cdp/reporting_2023.csv`: ciudades que reportaron a CDP-ICLEI en 2023 (unidas por distancia de hasta 20 km y población de al menos 300.000).
- `vivienda_municipal.py`: vivienda informal por municipio según la fuente oficial de cada país. Brasil: población en favelas, IBGE Censo 2022, SIDRA 9884 y 4709, los 5.570 municipios. Colombia: hogares en déficit habitacional, DANE CNPV 2018, los 1.122 municipios. Ciudad de Buenos Aires: familias en barrios populares del RENABAP sobre hogares del Censo 2022. México: población con carencia por calidad y espacios de la vivienda, CONEVAL 2020, los 2.466 municipios más la Ciudad de México (suma de sus 16 alcaldías). Escribe `datos/vivienda_municipal.csv`, guarda copias en `crudos/municipal/` y se vuelve a bajar con `ETL_REFRESCAR=1`. Las definiciones no son comparables entre países. Perú, Ecuador y Venezuela no tienen dato: gob.pe y el INEI rechazan la conexión, el Censo 2022 de Ecuador por cantón no se puede bajar (la ENEMDU del INEC solo da nacional, urbano y rural) y ine.gob.ve no responde.
- La API del Banco Mundial para tugurios y saneamiento. Guarda una copia en `crudos/vivienda_banco_mundial.csv`, que se usa si la API falla; se vuelve a bajar con `ETL_REFRESCAR=1`.
- La base de 90 ciudades con evidencia (`consultas/scorecard_undrr/alta_confianza/datos/resumen_ciudades.csv`). Si no está, usa la copia guardada en `entrada/resumen_ciudades_90.csv`.

## Qué escribe (`datos/`)

| Archivo | Contenido |
| --- | --- |
| `indicadores_enfoques.csv` | Los 30 indicadores crudos por ciudad |
| `indices_enfoques.csv` | Los cuatro índices y el subíndice de vivienda (0-100), sus z, cobertura, tipo, amenaza y puntaje del scorecard |
| `diccionario_indicadores.csv` | Nombre, sentido, unidad, fuente, fundamento y referencia de cada indicador |
| `consistencia_indices.csv` | Alfa de Cronbach, correlación ítem-resto y robustez al sacar cada indicador |
| `correlaciones.csv` | Spearman entre índices, amenaza y puntaje (375, 16 a mano y base de 90) |
| `regresiones.csv` | MCO con coeficientes estandarizados: puntaje y evidencia pública |
| `tipologias.csv` | Perfil mediano de cada tipo de ciudad (k-medias, k elegido por silueta) |
| `resumen_region.csv` | Mediana de cada índice y del subíndice de vivienda por región |
| `cdp_ciudades.csv` | Ciudades que reportan a CDP |
| `vivienda_municipal.csv` | Vivienda informal por municipio (Brasil, Colombia, México, CABA), con indicador y fuente |

## Método en breve

1. Cada indicador se recorta en los percentiles 2,5 y 97,5 (salvo los binarios), se pasa a z y se multiplica por su sentido.
2. El índice es el promedio de los z si la ciudad tiene al menos el 60% de los indicadores; luego, percentil 0-100.
3. Robustez: sacar cualquier indicador deja el orden casi igual (Spearman de 0,84 o más).
4. Tipología: k-medias sobre los cuatro z (sin el subíndice), de 3 a 6 grupos. Hoy salen 5 tipos (silueta 0,32).

## Cuidado al interpretar

- La gobernanza es casi toda de país (WGI y V-Dem). Dentro de un país solo cambian el reporte a CDP y la expansión del suelo.
- El puntaje de las 359 ciudades por modelo usa indicadores de país. Por eso la relación gobernanza-puntaje está inflada; la de las 16 hechas a mano es la más limpia.
- GHSL mide el centro urbano continuo, no el municipio. 44 ciudades comparten centro urbano con otra.
- Tugurios usa el dato municipal solo en 12 ciudades (columna `tugurios_origen` en `indicadores_enfoques.csv`); en el resto, y para el saneamiento, es dato de país.
- La base de 90 se eligió por prioridad: sus regresiones no se generalizan a las 375.
