# Indicadores sociales y digitales: qué se consiguió y qué no

Fecha: 15-10-2026. Pedido: datos para todos los países sobre apuestas virtuales, uso de redes sociales, compra de videojuegos, rendimiento deportivo, tasa de construcción, alfabetización, nivel de estudios alcanzado e inversión en cultura.

`extraer_indicadores_sociales.py` baja lo que tiene una fuente pública y comparable entre países y deja 6 CSV en esta carpeta (clave `iso3 + anio`, 2000 en adelante). `modelo_unificado/construir_master.py` los carga como `hecho_pais_educacion`, `hecho_pais_digital_ocio`, `hecho_pais_empleo_sectorial`, `hecho_pais_gasto_cultura`, `hecho_pais_deporte_olimpico` y `hecho_pais_consolas_comercio`, más la vista `v_pais_indicadores_sociales` con las participaciones (que no se guardan, como en el resto del modelo). La actualización mensual lo corre como paso `indicadores_sociales`.

## Resumen por tema

| Tema | Qué quedó | Fuente | Cobertura | Estado |
|---|---|---|---|---|
| Alfabetización | % de adultos (15+) que sabe leer y escribir, total, mujeres y hombres; % de jóvenes (15-24) | Banco Mundial (UNESCO-UIS) | 155-160 países, 2000-2024 | completo |
| Nivel de estudios alcanzado | % de 25+ que completó al menos primaria, secundaria baja, secundaria alta, postsecundaria, terciaria corta, licenciatura, maestría, doctorado; años promedio de escolaridad; años esperados y ajustados por aprendizaje | Banco Mundial (UNESCO-UIS, Índice de Capital Humano) | 144-197 países según el nivel | completo |
| Uso de redes sociales | % de personas que usó redes sociales en los últimos 3 meses (16-74 y 16-24 años) | OCDE, encuesta TIC a personas | 43 países (OCDE, UE, Brasil, Colombia, Costa Rica, Egipto) | parcial |
| Compra de videojuegos | % que compró videojuegos o software por internet en los últimos 12 meses (16-74 y 16-24) | OCDE, encuesta TIC a personas | 38 países | parcial |
| Compra de videojuegos (todo el mundo) | importaciones y exportaciones de consolas en US$ | UN Comtrade (HS 950450; 950410 hasta 2011) | 198 países, 2000-2025 | aproximación |
| Tasa de construcción | empleo en construcción (y empleo total, para el % en la vista) | OIT, estimaciones modeladas | 188 países, 2000-2025 | completo (como empleo) |
| Inversión en cultura | gasto público en recreación, cultura y religión y en servicios culturales (% PIB y % del gasto público), del gobierno general y del central; US$ PPA | FMI (GFS COFOG) y OCDE | 89 países gobierno general, 93 gobierno central | completo donde el país lo informa |
| Inversión en cultura (complemento) | empleo en artes y espectáculos y en bibliotecas, museos y patrimonio | OIT, encuestas de hogares (CIIU rev. 4 a 2 dígitos) | 125-139 países | parcial |
| Apuestas virtuales | **no hay fuente pública**; se guardó empleo en juegos de azar y apuestas como aproximación | OIT, encuestas de hogares (CIIU 92) | 117 países | aproximación |
| Rendimiento deportivo | medallas de oro, plata y bronce y atletas (total y mujeres) en cada edición de los Juegos Olímpicos | Olympedia | 206 países, verano 2000-2024 e invierno 2002-2026 | completo |

## Lo que hay que saber de cada tabla

**Alfabetización.** Los países de ingreso alto casi no la miden porque la dan por universal: España o Argentina tienen pocos años con dato (último: España 2021, 99,7 %; Argentina 2020, 99,1 %). Vacío no significa analfabetismo.

**Nivel alcanzado.** Cada nivel es "al menos ese": el % de secundaria alta incluye a quienes terminaron la universidad. Para la distribución exacta se restan niveles consecutivos. Los años promedio de escolaridad (UIS) llegan hasta 2019; los del Índice de Capital Humano son de 2010, 2017, 2018 y 2020.

**Redes sociales y videojuegos.** Es la única encuesta oficial comparable entre países, y la hacen solo la OCDE y Eurostat. La compra de videojuegos se pregunta junto con software ("computer games or software"). Para el resto del mundo, `hecho_pais_tecnologia` ya trae el % de usuarios de internet (UIT vía Banco Mundial, ~200 países), que es el techo de quién puede usar redes.

**Construcción.** No existe una serie mundial abierta de obras iniciadas, permisos ni viviendas terminadas: la OCDE la tiene solo para sus miembros y la ONU publica el valor agregado de la construcción en `unstats.un.org` (bloqueado en este entorno). El empleo en construcción de la OIT cubre a todos los países con el mismo método; en la vista sale como `empleo_construccion_pct` (2022: Argentina 8,5 %, España 6,9 %, Qatar 31 %).

**Gasto en cultura.** COFOG 08 junta recreación y deporte, cultura, medios y religión; el 08.2 "servicios culturales" (museos, bibliotecas, teatros, patrimonio) es lo más parecido a inversión en cultura. La fuente principal es el FMI; la OCDE solo completa Chile y Colombia y aporta el monto en US$ PPA (columna `fuente_gobierno_general`). Donde están las dos, la diferencia mediana es 0,000 puntos. Argentina, México y algunos más solo informan el gobierno central (columnas `_gob_central_`), que deja afuera a provincias y municipios: no se compara con el gobierno general de otros países. España 2022: 1,24 % del PIB en la función completa y 0,49 % en servicios culturales.

**Medallero olímpico.** Olympedia publica el medallero con las medallas reasignadas por dopaje (Estados Unidos figura con 9 oros en Pekín 2022, uno más que en la ceremonia). París 2024 coincide con el medallero oficial (EE. UU. 40-44-42, Argentina 1-1-1). `anio` es el año nominal de los Juegos: verano en años divisibles por 4, invierno en los pares restantes; Tokio 2020 se jugó en 2021. Los países que participaron sin ganar medallas figuran con 0. Quedan afuera los equipos sin país: atletas neutrales (AIN: 5 medallas en 2024 y 1 en 2026), refugiados (EOR), participantes independientes (IOA) y Serbia y Montenegro (2004-2006), que ya no existe en el maestro. Rusia compitió como ROC (2020, 2022) y OAR (2018): se asignan a RUS. El cruce NOC → ISO3 está en `noc_iso3.csv`. En la vista hay medallas por millón de habitantes (2024: Granada, Dominica y Santa Lucía arriba de 10).

**Consolas.** Mide el valor de las consolas importadas, no los juegos digitales ni las suscripciones, que no pasan por aduana. Hasta 2011 el código era "videojuegos para usar con televisor" (HS 950410); el empalme es razonable pero no perfecto (Japón salta en 2012). Entre 2012 y 2014 informan menos países (99-132) porque varios seguían usando la nomenclatura anterior. La vista trae importaciones por habitante e importaciones netas.

**Apuestas.** El tamaño del mercado de apuestas online por país lo publican consultoras privadas (H2 Gambling Capital, Statista) y no hay encuesta oficial comparable. Lo más cercano y abierto es el empleo en "actividades de juegos de azar y apuestas" (CIIU 92), que mezcla casinos, loterías y apuestas presenciales con las online. Aun así marca casos conocidos: Malta 4,0-4,5 % del empleo (sede de licencias de apuestas online para Europa) y Japón 4,0 % (pachinko). Ojo: el 22 % de los valores la OIT los marca como de baja confiabilidad (`U`, muestra chica); el CSV crudo `crudos/oit_empleo_ciiu2.csv` trae esa marca.

## Lo que todavía falta

- **Apuestas online:** sigue sin fuente pública; el mercado lo miden consultoras privadas.
- **Redes sociales fuera de la OCDE:** no hay encuesta oficial comparable (DataReportal y GWI son privadas).
- **Construcción como % del PIB:** el valor agregado por actividad de la ONU está en `unstats.un.org`, que sigue bloqueado; con ese dominio habilitado se suma.
