# Códigos de Python del proyecto

Esta carpeta junta los 14 scripts de Python del proyecto, con las mismas subcarpetas que en `etl/`.

**Es una copia.** Los originales siguen en `etl/` porque la actualización mensual (día 16) los
corre desde ahí y porque los scripts se importan entre sí y buscan sus datos en su propia carpeta.
Por eso:

- Para **leer o compartir** el código, usá esta carpeta.
- Para **correr o editar** un script, hacelo en `etl/`. Si corrés una copia de acá, va a buscar
  (y escribir) los datos dentro de `codigo_python/` y no los va a encontrar.
- Si se edita un script en `etl/`, esta copia queda vieja. Para rehacerla, desde `/mnt/project-files`:

  ```bash
  python codigo_python/actualizar_copia.py
  ```

  Borra las copias anteriores, vuelve a copiar cada `.py` y `requirements.txt`, y no toca este README.

Librerías necesarias: `pip install -r requirements.txt` (requests, pandas, openpyxl, xlrd, pyreadr, pycountry, lxml; statsmodels y scikit-learn solo para las regresiones).

## Orden de ejecución

Cada paso usa lo que dejaron los anteriores. Es el mismo orden que sigue `actualizar_mensual.py`.

| # | Script | Qué hace | Lee de pasos anteriores |
|---|---|---|---|
| 1 | `paso1_extraer_banco_mundial.py` | Baja 12 indicadores del Banco Mundial y arma el panel país-año `datos_procesados/paises_anual.csv` (217 países, 2000-2024). | — |
| 2 | `paso2_distribucion_precios_bienestar.py` | Suma al panel tipo de cambio, PPA, Gini, curva de Lorenz, costo de la dieta saludable, salario (ILOSTAT) y felicidad (WHR 2025). | 1 |
| 3 | `maestros/crear_maestros.py --descargar` | Tablas maestras de países (códigos ISO, nombres, región, ingreso) y de subdivisiones de primer nivel (ISO 3166-2). | 1 |
| 4 | `alianzas/extraer_alianzas_internacionales.py` | Membresías en organizaciones, tratados comerciales (DESTA) y pactos militares (ATOP) por país y año. | — |
| 5 | `argentina_provincias/extraer_argentina_provincias.py` | Argentina por provincia: VAB por rama (CEPAL), petróleo y gas, agricultura, ganado, censos, impuestos, gobernadores y más. | — |
| 6 | `latam_subnacional/extraer_latam_subnacional.py` | Estados, departamentos y regiones de 20 países de Latinoamérica (OCDE, temperatura, gobernadores, fuentes de Brasil y Colombia). | 3, 5 |
| 7 | `fuentes_nuevas/extraer_dimensiones_nuevas.py` | Seis dimensiones nuevas: migración, clima y energía, capital social, gobernanza, deuda y federalismo fiscal provincial. | 3, 4, 5, 6 |
| 8 | `indicadores_sociales_digitales/extraer_indicadores_sociales.py` | Alfabetización, nivel de estudios alcanzado, redes sociales, compra de videojuegos (OCDE y consolas de UN Comtrade), empleo en construcción, cultura y apuestas, gasto público en cultura (FMI), medallero olímpico (Olympedia). | 3 |
| 9 | `factbook/extraer_factbook.py` | CIA World Factbook (foto del 22-01-2026): perfil, fronteras, religiones, etnias, idiomas y socios comerciales. Se corre una sola vez: ya no se publica. | — |
| 10 | `modelo_unificado/construir_master.py` | Junta todo en una base SQLite normalizada (`master_paises_provincias.sqlite`). Va siempre al final de la extracción. | 1 a 9 |
| 11 | `kpis/calcular_kpis.py` | Corre los 5 KPIs multidimensionales del SQL sobre la base y guarda `kpis/resultados/*.csv`. | 10 |
| 12 | `graficos_progreso/preparar_datos_progreso.py` | Prepara los datos y la página del gráfico "Progreso en el tiempo". | 1, 2, 3, 5, 6 |
| 13 | `bases_regionales/construir_bases_regionales.py` | Separa todo en tres bases SQLite: Argentina (país + provincias), Latinoamérica (países + subdivisiones) y mundial. No baja nada: filtra el master y suma las tablas de Latam, festivales y KPIs. | 6, 10, 11 |

## Scripts de mantenimiento

| Script | Qué hace |
|---|---|
| `actualizar_mensual.py` | Corre los pasos 1 a 8, el 10 y el 13 con datos frescos en una carpeta temporal, compara con la versión anterior y publica solo lo que salió bien (guarda la versión vieja en `etl/historial/`). `--prueba` corre sin publicar. |
| `chequear_fuentes.py` | Prueba si cada una de las 39 fuentes que se renuevan sigue respondiendo y avisa cuáles podrían estar discontinuadas. Lo llama la actualización mensual; también se corre solo. |
| `actualizar_copia.py` | Rehace esta carpeta (solo existe acá, no en `etl/`). |

Cada script tiene al principio una explicación más larga de qué baja, de dónde y qué archivos deja.
Las guías paso a paso (`GUIA_*.md`) siguen en `etl/` y sus subcarpetas.
