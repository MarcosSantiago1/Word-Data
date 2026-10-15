# Alianzas económicas e internacionales

Esta carpeta es una tabla **aparte** del panel principal: no toca `datos_procesados/paises_anual.csv`. Todas las tablas usan el mismo código de país (**iso3**) y, cuando son anuales, la columna **anio**, así que se pueden unir con el panel.

```bash
cd etl/alianzas
python extraer_alianzas_internacionales.py
```

Necesita `requests`, `pandas`, `pyreadr` (lee archivos de R) y `pycountry` (traduce códigos de país). Los crudos se descargan una sola vez a `crudos/`.

## Las cuatro tablas

| Archivo | Una fila es | Para qué sirve |
|---|---|---|
| `membresias_organizaciones.csv` | un período en que un país perteneció a una organización (ingreso, salida, estado) | ver la historia completa: cuándo entró Finlandia a la OTAN, cuándo salió Qatar de la OPEP |
| `alianzas_pais_anual.csv` | un país en un año (217 países × 2000-2025) | unir con el panel y comparar países: una columna 0/1 por organización y varios conteos |
| `tratados_comerciales_pais.csv` | un país en un acuerdo comercial (842 acuerdos, 1948-2020) | ver qué tratados de libre comercio firmó cada país y cuándo entraron en vigor |
| `alianzas_militares_diadas.csv` | un par de países con un pacto militar en un año (1945-2018) | ver quién tiene compromiso de defensa con quién |

### Organizaciones incluidas (48)

- **Comercio e integración:** OMC, OCDE, UE, eurozona, AELC (EFTA), Unión Económica Euroasiática, Mercosur, Comunidad Andina, ALADI, Alianza del Pacífico, CARICOM, SICA, TLCAN y T-MEC, APEC, CPTPP, RCEP, ASEAN, SAARC, Consejo de Cooperación del Golfo, CEDEAO, UEMOA, CEMAC, SADC, SACU, COMESA, Comunidad de África Oriental.
- **Energía:** OPEP y OPEP+.
- **Seguridad:** OTAN, OTSC, Organización de Cooperación de Shanghái, AUKUS, Quad, Alianza de Estados del Sahel y los "aliados principales extra-OTAN" de EE. UU. (Argentina desde 1998, Brasil desde 2019, Colombia desde 2022).
- **Foros:** G7, G8, G20, BRICS.
- **Políticas:** Unión Africana, OEA, ALBA, Liga Árabe, Organización de Cooperación Islámica, Consejo de Europa, Commonwealth, CEI.

## Cómo leer los años

Un país cuenta como miembro en un año si lo era **al 31 de diciembre**. El año de ingreso cuenta y el de salida no: el Reino Unido tiene `anio_ingreso = 1973` y `anio_salida = 2020` en la UE porque salió el 31 de enero de 2020. Si `anio_salida` está vacío, el país sigue adentro.

`estado` puede ser **pleno**, **asociado**, **observador** o **suspendido**. Las columnas `miembro_*` del panel solo marcan 1 a los miembros plenos. Ejemplo: Bolivia figura como asociada del Mercosur desde 1996 y como plena desde 2024; Venezuela figura como suspendida desde 2016.

## Columnas de conteo del panel

| Columna | Qué es | Años con dato |
|---|---|---|
| `n_organizaciones_clave` | en cuántas de las 48 organizaciones es miembro pleno | 2000-2025 |
| `n_org_economica_comercial`, `n_org_militar_seguridad`, etc. | lo mismo, separado por tipo | 2000-2025 |
| `n_igos_cow_total` | en cuántas organizaciones intergubernamentales del mundo es miembro pleno (unas 530, de cualquier tema) | 2000-2014 |
| `n_acuerdos_comerciales_en_vigor` | acuerdos comerciales con año de entrada en vigor conocido, sin descontar los que fueron reemplazados por otros | 2000-2020 |
| `n_aliados_defensa` | con cuántos países tiene un pacto que obliga a defenderlo si lo atacan | 2000-2018 |
| `n_aliados_cualquier_pacto` | con cuántos países tiene algún pacto (defensa, no agresión, consulta…) | 2000-2018 |

El año de referencia del proyecto (2021) tiene todas las columnas `miembro_*`, pero no los últimos tres conteos, que vienen de bases académicas que terminan antes.

## Fuentes y cuánto confiar

- **Correlates of War, organizaciones intergubernamentales v3** (Pevehouse y otros, 2020): membresía año a año hasta 2014. Antes de 1965 registra cada 5 años, así que los ingresos viejos pueden estar corridos. Revisamos las organizaciones contra la cantidad de miembros conocida y encontramos errores, que el script corrige: Argelia aparecía en la OMC (es solo observadora), faltaba Macedonia del Norte, Bolivia y Chile figuraban como miembros plenos del Mercosur, la Comunidad de África Oriental tenía países de otro bloque, faltaba Angola en la OPEP. La UE, la OPEP, el Mercosur, la Comunidad de África Oriental y la Unión Africana se cargan enteras a mano.
- **Control con Wikidata** (12-10-2026): comparamos cada año de ingreso y salida con las membresías con fecha que publica Wikidata (`crudos/wikidata_membresias_p463.csv`). Todo lo cargado a mano coincide (OTAN, UE, OPEP, BRICS, T-MEC, AUKUS, eurozona y los cambios 2015-2025). Las diferencias estaban en fechas viejas de Correlates of War y se corrigieron: el Commonwealth arrancaba en 1965 para todos los miembros fundadores, Finlandia figuraba en el Consejo de Europa desde 1965 (es 1989), Fiyi y Nigeria no tenían sus suspensiones. Wikidata también tiene errores (pone a Argelia en la OMC), así que no se usa como fuente principal.
- **Carga manual**: los cambios de 2015 a 2025 (por ejemplo, la OTAN pasa de 28 a 32 miembros, los BRICS suman a Egipto, Etiopía, Irán y Emiratos en 2024 e Indonesia en 2025) y las organizaciones que esa base no tiene. Cada fila dice su fuente en la columna `fuente` y tiene una `nota` cuando hace falta.
- **DESTA 2.0** (Dür, Baccini y Elsig; versión 2020): acuerdos comerciales firmados hasta 2020. Cuando un país pertenece a un bloque, figura en los acuerdos del bloque: cada país de la UE aparece en el acuerdo UE-México.
- **ATOP 5.1** (Leeds y otros): pactos militares formales hasta 2018. Un mismo par de países puede tener varios tipos de pacto a la vez.

**Lo que no está:** la UNASUR y la CELAC (fechas de salida y regreso poco claras), las suspensiones dentro de la Unión Africana, y Myanmar en el RCEP. Los acuerdos comerciales posteriores a 2020 (por ejemplo, el acuerdo Mercosur-UE) no están en DESTA.

## Ejemplo: unir con el panel

```python
import pandas as pd
panel = pd.read_csv("../datos_procesados/paises_anual.csv")
alianzas = pd.read_csv("alianzas_pais_anual.csv").drop(columns="pais")
df = panel.merge(alianzas, on=["iso3", "anio"], how="left")

# PIB per cápita promedio en 2021: miembros de la OCDE frente al resto
df[df.anio == 2021].groupby("miembro_ocde").pib_pc_ppp.mean()
```
