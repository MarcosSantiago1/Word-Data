"""Corre los 5 KPIs de kpis_multidimensionales.sql sobre el modelo unificado.

Uso:
    python etl/kpis/calcular_kpis.py

Abre la base en solo lectura (no la modifica), ejecuta cada bloque
"-- name: <codigo>" en orden y guarda el resultado de su último SELECT en
etl/kpis/resultados/<codigo>.csv. Imprime filas y las 5 primeras de cada KPI.
"""
import csv
import re
import sqlite3
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BASE = AQUI.parent / "modelo_unificado" / "master_paises_provincias.sqlite"
SQL = AQUI / "kpis_multidimensionales.sql"
SALIDA = AQUI / "resultados"


def bloques(texto):
    """Devuelve [(codigo, [sentencias])] separando por '-- name:'."""
    partes = re.split(r"^-- name:\s*(\S+)\s*$", texto, flags=re.M)
    for codigo, cuerpo in zip(partes[1::2], partes[2::2]):
        sentencias, actual = [], ""
        for linea in cuerpo.splitlines(keepends=True):
            actual += linea
            if sqlite3.complete_statement(actual):
                if actual.strip():
                    sentencias.append(actual.strip())
                actual = ""
        yield codigo, sentencias


def main():
    SALIDA.mkdir(exist_ok=True)
    con = sqlite3.connect(f"file:{BASE}?mode=ro", uri=True)
    for codigo, sentencias in bloques(SQL.read_text(encoding="utf-8")):
        t0 = time.time()
        for s in sentencias[:-1]:
            con.execute(s)
        cur = con.execute(sentencias[-1])
        columnas = [d[0] for d in cur.description]
        filas = cur.fetchall()
        with open(SALIDA / f"{codigo}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(columnas)
            w.writerows(filas)
        print(f"\n{codigo}: {len(filas)} filas, {time.time() - t0:.2f} s")
        print("  " + " | ".join(columnas[:8]))
        for fila in filas[:5]:
            print("  " + " | ".join(str(v) for v in fila[:8]))
    con.close()


if __name__ == "__main__":
    main()
