# Actualización mensual de la base

La base se renueva sola una vez por mes con `actualizar_mensual.py`. Esta guía explica
qué hace, cómo leer el resumen y cómo volver atrás si hiciera falta.

## Qué hace, en orden

1. **Copia `etl/` a una carpeta temporal** y trabaja ahí. Los datos publicados no se tocan
   hasta el final.
2. **Corre los scripts** con `ETL_REFRESCAR=1`, que les indica volver a bajar las fuentes:

   | Paso | Scripts |
   |---|---|
   | Panel de países | `paso1_extraer_banco_mundial.py` + `paso2_distribucion_precios_bienestar.py` |
   | Maestros | `maestros/crear_maestros.py --descargar` |
   | Alianzas | `alianzas/extraer_alianzas_internacionales.py` |
   | Argentina por provincia | `argentina_provincias/extraer_argentina_provincias.py` |
   | Latinoamérica por subdivisión | `latam_subnacional/extraer_latam_subnacional.py` |
   | Dimensiones nuevas | `fuentes_nuevas/extraer_dimensiones_nuevas.py` |
   | Dimensiones nuevas en el panel de países | `paso3_dimensiones_nuevas.py` |
   | Modelo unificado | `modelo_unificado/construir_master.py` |
   | Bases Argentina, Latam y mundial | `bases_regionales/construir_bases_regionales.py` |

3. **Si un paso falla** (fuente caída, dominio bloqueado, formato nuevo), ese paso vuelve a
   su versión anterior y los siguientes siguen con ella.
4. **Controla** cada archivo contra el anterior. Se rechaza el paso si un archivo desaparece,
   se pierden columnas con datos o tablas, o caen más de 5 % las filas (20 % en
   `gobernantes_subdivision.csv`, que sale de Wikidata y varía más).
5. **Publica solo lo que cambió**, guardando antes la versión vieja en `historial/<fecha>/`
   (quedan las últimas 3).
6. **Escribe el resumen** en `actualizaciones/<fecha>_resumen.md`, suma una fila por paso a
   `actualizaciones/historial.csv` y deja los logs en `actualizaciones/logs/<fecha>/`.

## Fuentes que se vuelven a bajar y fuentes fijas

- **Se renuevan:** Banco Mundial, ILOSTAT, WHR, CEPAL, Energía, MAGyP, Argendata, turismo (EOH),
  temperatura (CCKP), proyecciones INDEC, diputados y senadores, salud, OEDE, DNAP, canastas
  INDEC, EPH, Wikidata (maestros) y las regiones M49; para Latinoamérica, OCDE regional, IBGE SIDRA,
  ANP y datos.gov.co (EVA, ICA, ANH).
- **Fijas (no cambian):** censos 2010 y 2022, elecciones de electorAr 1983-2019, CEP XXI 2021-22,
  registro MiPyME (foto al 23-12-2024), COW/DESTA/ATOP (versión fija), CIA Factbook (cerrado).
- Si una descarga de Argentina o del modelo falla, ese archivo usa la copia anterior y el
  resumen lo lista en "Fuentes que no respondieron".

**Límite a tener en cuenta:** algunas fuentes publican cada edición con un nombre de archivo
nuevo (WHR 2025, stock bovino 2007-2025, alícuotas IIBB por año, el Excel de CEPAL). La rutina
vuelve a bajar la misma dirección; para sumar la edición nueva hay que cambiar la URL en el script.

## ¿Alguna fuente se dio de baja?

Al final de cada corrida, `chequear_fuentes.py` prueba las 39 fuentes que se renuevan (es
Python puro, no necesita a Claude; también se puede correr solo con `python chequear_fuentes.py`).
Cada fuente queda en uno de estos estados:

| Estado | Qué significa |
|---|---|
| `ok` | respondió con datos |
| `bloqueada_por_la_red` | el entorno no deja salir a ese dominio; la fuente puede estar bien |
| `no_existe_mas` | da 404/410 o una página web en vez del archivo: se movió o se dio de baja |
| `no_responde` | error del servidor o sin respuesta; puede ser temporal |

Se cuenta como **posiblemente discontinuada** si da `no_existe_mas`, o `no_responde` dos meses
seguidos. El resumen muestra el porcentaje y el historial queda en `actualizaciones/estado_fuentes.csv`.

Buscar una fuente alternativa sí necesita a Claude: hay que buscar en la web y comparar si la
serie nueva mide lo mismo, con la misma cobertura y años. Por eso la rutina mensual, que corre
con Claude, lo hace solo cuando el chequeo marca una fuente. Primero busca la misma serie en su
dirección nueva y, si ya no existe, propone alternativas en el hilo para que la usuaria elija.

## Cómo correrlo a mano

```bash
pip install -r requirements.txt
python actualizar_mensual.py            # actualiza y publica
python actualizar_mensual.py --prueba   # corre y compara, sin publicar
```

## Cómo volver atrás

Copiar los archivos de `historial/<fecha>/` encima de los de `etl/` (misma ruta relativa).
