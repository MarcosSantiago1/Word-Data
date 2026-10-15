# Paso 1: cómo recuperar los datos de los países

Esta guía explica, desde cero, cómo descargamos los datos de todos los países y los dejamos en una sola tabla lista para analizar.

## La idea en una frase

Pedimos los datos a la **API del Banco Mundial** (un servicio web que devuelve datos cuando le haces una pregunta por URL) y los juntamos en una tabla donde cada fila es **un país en un año**, identificado por su **código ISO Alpha-3** (ARG, CHL, ESP, USA...).

## ¿Por qué empezar por el Banco Mundial?

Porque con una sola fuente abierta, sin registro ni clave, cubrimos casi toda la matriz de variables del proyecto:

| Dimensión | Variable en nuestra tabla | Código del Banco Mundial |
|---|---|---|
| Demografía y economía | `poblacion` | SP.POP.TOTL |
| | `pib_pc_ppp` | NY.GDP.PCAP.PP.KD |
| Salud pública | `esperanza_vida` | SP.DYN.LE00.IN |
| | `mortalidad_infantil` (por 1.000 nacidos vivos) | SP.DYN.IMRT.IN |
| | `camas_hospital_x1000` | SH.MED.BEDS.ZS |
| | `medicos_x1000` | SH.MED.PHYS.ZS |
| Salud mental | `suicidio_total_x100k` | SH.STA.SUIC.P5 |
| | `suicidio_hombres_x100k` / `suicidio_mujeres_x100k` | SH.STA.SUIC.MA.P5 / FE.P5 |
| Inversión pública | `gasto_salud_pct_pib` | SH.XPD.GHED.GD.ZS |
| | `gasto_salud_pct_gasto_pub` | SH.XPD.GHED.GE.ZS |
| | `gasto_educacion_pct_pib` | SE.XPD.TOTL.GD.ZS |

Los datos de suicidio que publica el Banco Mundial vienen de la OMS, así que no hace falta conectarse a la OMS todavía. Puedes ver cualquier indicador en `https://data.worldbank.org/indicator/<CÓDIGO>`.

Quedan para los pasos siguientes la **felicidad** (World Happiness Report), el **índice de democracia** (V-Dem) y el desglose de suicidio por **edad** (OMS).

## Cómo ejecutarlo

1. Instala Python 3 (o abre un cuaderno en Google Colab).
2. Abre una terminal en la carpeta `etl/` y escribe:

```bash
pip install -r requirements.txt
python paso1_extraer_banco_mundial.py
```

Tarda uno o dos minutos. Al terminar verás cuántos países y filas se descargaron y qué porcentaje de datos hay para cada variable.

## Qué archivos genera

| Archivo | Qué contiene | Para qué sirve |
|---|---|---|
| `datos_crudos/paises.csv` | Los ~217 países con su ISO3, región y nivel de ingreso | Tabla "maestra" de países |
| `datos_crudos/banco_mundial_largo.csv` | Una fila por país + año + indicador, tal como llegó | Auditar y revisar el origen de un dato |
| `datos_procesados/paises_anual.csv` | Una fila por país + año, una columna por variable | Tabla base para el análisis y el dashboard |

## Qué hace el código por dentro (las 3 letras del ETL)

**E de Extraer.** La función `pedir_a_la_api` visita una URL como esta (puedes pegarla en el navegador):

```
https://api.worldbank.org/v2/country/all/indicator/SP.DYN.LE00.IN?format=json&date=2022
```

La respuesta es un JSON con dos partes: información de páginas y la lista de datos. Si los datos no caben en una página, el código pide las siguientes. Si falla la conexión, reintenta hasta 4 veces esperando cada vez un poco más.

**T de Transformar.** Hay tres transformaciones importantes:

- **Quitar agregados.** La API mezcla países con grupos como "World" o "High income". Los reconocemos porque su región es "Aggregates" y los quitamos, si no contaríamos el mundo como si fuera un país más.
- **Pasar de formato largo a ancho** (`pivot_table`). Llega una fila por cada dato; nosotros queremos una fila por país y año, con cada variable en su columna, que es como se analiza y se grafica.
- **Unir por la clave ISO3** (`merge`). Es el equivalente a un `JOIN` en SQL: pegamos el nombre del país, su región y su nivel de ingreso usando el código de tres letras.

**L de Cargar (Load).** Por ahora guardamos en CSV. Más adelante cargaremos la tabla en una base de datos SQL (SQLite) para hacer consultas.

## Cosas que vas a notar en los datos

- **Hay huecos.** No todos los países informan todos los años. Las camas de hospital y los médicos tienen muchos huecos; el PIB y la población casi ninguno. El resumen de cobertura al final del script te lo muestra.
- **Los últimos años están incompletos.** El Banco Mundial publica con uno o dos años de retraso, así que 2024 tendrá pocos datos.
- **Los años no coinciden entre variables.** Para comparar países lo habitual es tomar, para cada país, el último año disponible de cada variable. Ese será parte del paso 2.

## Para cambiar qué se descarga

Arriba del script están `ANIO_INICIO`, `ANIO_FIN` y el diccionario `INDICADORES`. Para añadir una variable, busca su código en data.worldbank.org y agrega una línea `"CÓDIGO": "nombre_columna",`.

## Siguiente paso

Paso 2: añadir el World Happiness Report. Ese archivo no trae el código ISO3, solo el nombre del país ("Czechia", "Türkiye", "Hong Kong SAR of China"...), así que habrá que construir una tabla de equivalencias entre nombres y códigos antes de poder unirlo. Es un buen ejemplo de un problema real de limpieza de datos.
