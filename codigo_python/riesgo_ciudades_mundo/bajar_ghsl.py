"""Baja los temas del GHSL Urban Centre Database R2024A (Comisión Europea, JRC) que usa el scorecard mundial.

Deja los .zip en crudos/ghsl/, los CSV y PDF de cada tema en crudos/ghsl/csv/ y el GeoPackage general en crudos/ghsl/gpkg/.
Si un archivo ya está, no lo vuelve a bajar (salvo ETL_REFRESCAR=1). Si la versión V1-2 deja de existir, busca la más nueva.
uso (desde etl/): python riesgo_ciudades_mundo/bajar_ghsl.py
"""
import os, re, time, zipfile, urllib.request

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crudos', 'ghsl')
BASE = 'https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_UCDB_GLOBE_R2024A/GHS_UCDB_THEME_GLOBE_R2024A'
TEMAS = ['GENERAL_CHARACTERISTICS', 'HAZARD_RISK', 'EXPOSURE', 'CLIMATE', 'INFRASTRUCTURES', 'SOCIOECONOMIC', 'GEOGRAPHY']
REFRESCAR = os.environ.get('ETL_REFRESCAR') == '1'

def leer(url):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'word-data-etl/1.0'}), timeout=300) as r:
                return r.read()
        except Exception:
            if i == 3: raise
            time.sleep(2 ** (i + 1))

def version(tema):
    html = leer(f'{BASE}/GHS_UCDB_THEME_{tema}_GLOBE_R2024A/').decode('utf8', 'ignore')
    vs = sorted(set(re.findall(r'href="(V\d+-\d+)/"', html)), key=lambda v: [int(x) for x in v[1:].split('-')])
    return vs[-1]

def main():
    os.makedirs(os.path.join(CARPETA, 'csv'), exist_ok=True); os.makedirs(os.path.join(CARPETA, 'gpkg'), exist_ok=True)
    for t in TEMAS:
        z = os.path.join(CARPETA, f'{t}.zip')
        if not os.path.exists(z) or REFRESCAR:
            try:
                v = version(t)
                datos = leer(f'{BASE}/GHS_UCDB_THEME_{t}_GLOBE_R2024A/{v}/GHS_UCDB_THEME_{t}_GLOBE_R2024A_{v.replace("-", "_")}.zip')
                open(z, 'wb').write(datos)
                print('bajado', t, v)
            except Exception as e:
                if os.path.exists(z): print('AVISO_FUENTE GHSL', t, 'no respondió; se usa la copia guardada:', e)
                else: raise
        with zipfile.ZipFile(z) as zz:
            for n in zz.namelist():
                if n.endswith('.csv') or (n.endswith('.pdf') and n.startswith('GHS_UCDB_THEME')):
                    open(os.path.join(CARPETA, 'csv', os.path.basename(n)), 'wb').write(zz.read(n))
                if t == 'GENERAL_CHARACTERISTICS' and n.endswith('.gpkg'):
                    open(os.path.join(CARPETA, 'gpkg', os.path.basename(n)), 'wb').write(zz.read(n))
    print('GHSL listo')

if __name__ == '__main__':
    main()
