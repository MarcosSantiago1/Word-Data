# Word-Data: análisis multidimensional de países

ETL (extracción, transformación y carga) en Python y SQL que junta datos abiertos del Banco Mundial,
la OMS, el World Happiness Report, ILOSTAT, V-Dem, el CIA World Factbook y fuentes oficiales
argentinas y latinoamericanas en una sola base, y calcula 5 KPIs que cruzan salud, economía,
desigualdad, geopolítica y federalismo fiscal.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MarcosSantiago1/Word-Data/blob/main/notebooks/explorar_proyecto.ipynb)

## Por dónde empezar

| Carpeta o archivo | Qué hay |
|---|---|
| `notebooks/explorar_proyecto.ipynb` | Recorrido guiado por los datos y los KPIs. Se abre en Colab con el botón de arriba. |
| `etl/datos_procesados/paises_anual.csv` | Panel país × año: 217 países, 2000-2024. |
| `etl/modelo_unificado/master_paises_provincias.sqlite` | La base unificada (SQLite), con su guía `GUIA_MODELO_UNIFICADO.md`. |
| `etl/kpis/` | Los 5 KPIs en SQL, su explicación (`KPIS_MULTIDIMENSIONALES.md`) y sus resultados. |
| `etl/GUIA_*.md` y las guías de cada subcarpeta | Explicación paso a paso de cada parte del ETL. |
| `codigo_python/` | Copia de los scripts con un README del orden en que se corren. |

## Correr el ETL

```bash
pip install -r etl/requirements.txt
python etl/actualizar_mensual.py --prueba   # corre todo sin publicar
```

El orden de los scripts está en `codigo_python/README.md`.

Por su tamaño quedan afuera del repositorio (ver `.gitignore`) un archivo original de más de 100 MB
(`etl/fuentes_nuevas/crudos/ccpcnc_v5.zip`, que el script vuelve a descargar) y las copias de
seguridad de `etl/historial/`.
