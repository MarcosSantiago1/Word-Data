"""
Rehace esta carpeta con la versión actual de todos los scripts de Python de etl/.

Los originales viven en etl/ (ahí los usa la actualización mensual). Esta carpeta es una
COPIA para leerlos o compartirlos juntos. Si se edita un script en etl/, correr:

    python codigo_python/actualizar_copia.py      (desde /mnt/project-files)

Borra las copias viejas y vuelve a copiar cada .py (y requirements.txt) con la misma
estructura de subcarpetas. No toca este script ni el README.md.
"""
import shutil
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ETL = AQUI.parent / "etl"
PROPIOS = {"actualizar_copia.py", "README.md"}

# 1. Borrar lo copiado antes (todo menos los archivos propios de esta carpeta)
for ruta in sorted(AQUI.rglob("*"), reverse=True):
    if ruta.relative_to(AQUI).as_posix() in PROPIOS:
        continue
    if ruta.is_file():
        ruta.unlink()
    elif ruta.is_dir() and not any(ruta.iterdir()):
        ruta.rmdir()

# 2. Copiar cada script, salteando __pycache__ y el historial de versiones viejas
copiados = []
for origen in sorted(ETL.rglob("*.py")):
    rel = origen.relative_to(ETL)
    if "__pycache__" in rel.parts or "historial" in rel.parts:
        continue
    destino = AQUI / rel
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origen, destino)
    copiados.append(rel.as_posix())
shutil.copy2(ETL / "requirements.txt", AQUI / "requirements.txt")

print(f"{len(copiados)} scripts copiados desde {ETL}:")
for rel in copiados:
    print("  " + rel)
