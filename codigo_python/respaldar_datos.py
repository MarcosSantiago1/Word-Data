"""
RESPALDO PROPIO DE TODOS LOS DATOS: una foto completa y fechada de lo descargado y lo procesado.

Por qué: las fuentes cambian, revisan años pasados o desaparecen (el CIA World Factbook se dio de
baja en 2026, la OMS reemplaza su API). La actualización mensual ya guarda la versión anterior de
lo que reemplaza, pero solo de las últimas 3 corridas. Este respaldo guarda TODO (crudos, tablas
procesadas y bases SQLite) en un solo .zip por fecha, fuera de la carpeta etl/, para poder
reconstruir el proyecto aunque una fuente ya no exista.

Qué hace:
  1. Recorre etl/ y junta todos los archivos de datos (no el código ni las guías, que están en
     GitHub; tampoco historial/, que ya son copias).
  2. Los comprime en respaldos/respaldo_<fecha>.zip (en la carpeta del proyecto, al lado de etl/).
  3. Escribe adentro del zip un inventario: ruta, tamaño, fecha de modificación y huella SHA-256 de
     cada archivo, para poder comprobar más adelante que nada cambió.
  4. Conserva los respaldos de los últimos 12 meses y, de los anteriores, el primero de cada año.

Uso (desde la carpeta etl/):
    python respaldar_datos.py
Lo llama también actualizar_mensual.py al terminar cada corrida publicada.

Para recuperar un archivo: abrir el zip y copiarlo a la misma ruta dentro de etl/.
"""

import csv
import hashlib
import io
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

ETL = Path(__file__).resolve().parent
RESPALDOS = ETL.parent / "respaldos"
MESES_A_CONSERVAR = 12
SIN_RESPALDO = {"historial", "__pycache__"}
EXTENSIONES_CODIGO = {".py", ".pyc", ".md", ".ipynb"}


def archivos_de_datos():
    for ruta in sorted(ETL.rglob("*")):
        rel = ruta.relative_to(ETL)
        if ruta.is_file() and ruta.suffix not in EXTENSIONES_CODIGO and not SIN_RESPALDO & set(rel.parts):
            yield ruta, rel


def huella(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def podar():
    """Deja los últimos 12 meses y el primer respaldo de cada año anterior."""
    zips = sorted(RESPALDOS.glob("respaldo_*.zip"))
    limite = datetime.now() - timedelta(days=31 * MESES_A_CONSERVAR)
    primeros_del_anio = {}
    for z in zips:
        primeros_del_anio.setdefault(z.stem[9:13], z)
    for z in zips:
        fecha = datetime.strptime(z.stem[9:19], "%Y-%m-%d")
        if fecha < limite and z not in primeros_del_anio.values():
            z.unlink()
            print(f"   se borró el respaldo viejo {z.name}")


def respaldar():
    RESPALDOS.mkdir(exist_ok=True)
    fecha = datetime.now().strftime("%Y-%m-%d")
    destino = RESPALDOS / f"respaldo_{fecha}.zip"
    temporal = destino.with_suffix(".zip.parcial")
    inventario = io.StringIO()
    escritor = csv.writer(inventario)
    escritor.writerow(["ruta", "bytes", "modificado", "sha256"])
    total = 0
    with zipfile.ZipFile(temporal, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for ruta, rel in archivos_de_datos():
            z.write(ruta, f"etl/{rel.as_posix()}")
            estado = ruta.stat()
            total += estado.st_size
            escritor.writerow([rel.as_posix(), estado.st_size,
                               datetime.fromtimestamp(estado.st_mtime).strftime("%Y-%m-%d %H:%M"), huella(ruta)])
        z.writestr("inventario.csv", inventario.getvalue())
    temporal.replace(destino)  # recién al final: un respaldo cortado nunca queda con el nombre bueno
    n = inventario.getvalue().count("\n") - 1
    print(f"Respaldo: {n:,} archivos ({total / 1e6:,.0f} MB sin comprimir) -> {destino} "
          f"({destino.stat().st_size / 1e6:,.0f} MB)")
    podar()
    return destino


if __name__ == "__main__":
    respaldar()
