"""Paso mensual del scorecard mundial: actualiza los datos y puntajes de las 375 ciudades (sin rehacer los .xlsm).

Escribe todo en etl/riesgo_ciudades_mundo/ (así lo controla y respalda actualizar_mensual.py):
  datos/ciudades_mundo.csv, ghsl_ciudades.csv, sismos_ciudades.csv, indicadores_pais.csv,
  datos/puntajes_mundo.csv, amenaza_capacidad_mundo.csv y Resumen_scorecards_UNDRR_mundo.xlsx
Corre en orden: bajar_ghsl, armar_lista (copia guardada de Wikidata), unir_ghsl, sismos_usgs, indicadores del país
(panel del proyecto), generar_mundo --sin-xlsm y resumen_mundo.
El código del modelo está en consultas/scorecard_undrr/ (al lado de etl/). Para rehacer también los 718 .xlsm:
  python ../consultas/scorecard_undrr/mundo/herramientas/generar_mundo.py ../consultas/scorecard_undrr/mundo --datos riesgo_ciudades_mundo/datos
Necesita pyogrio, shapely y pyproj (pip install pyogrio shapely pyproj).
uso (desde etl/): python riesgo_ciudades_mundo/actualizar_mundo.py
"""
import os, sys, subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ETL = AQUI.parent  # en la actualización mensual es la copia de trabajo de etl/
DAT = AQUI / 'datos'

def buscar_consultas():
    """actualizar_mensual.py corre los pasos en una copia de etl/ fuera del proyecto: se busca consultas/ en los lugares conocidos."""
    for c in (os.environ.get('PROYECTO_RAIZ'), ETL.parent, Path('/mnt/project-files'), Path.cwd().parent):
        if c and (Path(c) / 'consultas' / 'scorecard_undrr' / 'mundo' / 'herramientas' / 'generar_mundo.py').exists():
            return Path(c) / 'consultas' / 'scorecard_undrr'
    sys.exit('No se encontró consultas/scorecard_undrr/ (definir PROYECTO_RAIZ con la carpeta que tiene etl/ y consultas/)')

def correr(*args):
    print('>', ' '.join(Path(str(a)).name for a in args), flush=True)
    subprocess.run([sys.executable, *map(str, args)], check=True, cwd=ETL)

def main():
    HER = buscar_consultas() / 'mundo' / 'herramientas'
    DAT.mkdir(exist_ok=True)
    correr(AQUI / 'bajar_ghsl.py')
    correr(HER / 'armar_lista.py', AQUI / 'crudos' / 'wikidata', DAT / 'ciudades_mundo.csv')
    correr(HER / 'unir_ghsl.py', AQUI / 'crudos' / 'ghsl', DAT / 'ciudades_mundo.csv', DAT / 'ghsl_ciudades.csv')
    correr(AQUI / 'sismos_usgs.py', DAT / 'ciudades_mundo.csv', DAT / 'sismos_ciudades.csv')
    correr(HER / 'indicadores_pais.py', DAT, ETL / 'datos_procesados' / 'paises_anual.csv')
    correr(HER / 'generar_mundo.py', AQUI, '--sin-xlsm')
    correr(HER / 'resumen_mundo.py', AQUI)

if __name__ == '__main__':
    main()
