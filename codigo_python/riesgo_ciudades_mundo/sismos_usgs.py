"""Historial sísmico de cada ciudad desde el catálogo del USGS (ComCat).

Para cada ciudad: sismos M>=6 a menos de 150 km desde 1900, sismos M>=5 a menos de 100 km desde 1975
y el sismo más fuerte a menos de 150 km desde 1900 (magnitud, fecha y lugar).
Cachea cada respuesta en crudos/usgs/<id>.json; con ETL_REFRESCAR=1 vuelve a consultar.
uso (desde etl/): python riesgo_ciudades_mundo/sismos_usgs.py <ciudades_mundo.csv> <salida.csv>
"""
import sys, os, json, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

CARPETA = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(CARPETA, 'crudos', 'usgs')
API = 'https://earthquake.usgs.gov/fdsnws/event/1/'
REFRESCAR = os.environ.get('ETL_REFRESCAR') == '1'

def pedir(metodo, **q):
    url = API + metodo + '?' + urllib.parse.urlencode(q)
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'word-data-etl/1.0'}), timeout=60) as r:
                return json.loads(r.read())
        except Exception as e:
            if i == 3: raise
            time.sleep(2 ** (i + 1))

def ciudad(r):
    f = os.path.join(CACHE, f'{r.id}.json')
    if os.path.exists(f) and not REFRESCAR:
        return json.load(open(f))
    base = dict(format='geojson', latitude=r.lat, longitude=r.lon)
    n6 = pedir('count', minmagnitude=6, maxradiuskm=150, starttime='1900-01-01', **base)['count']
    n5 = pedir('count', minmagnitude=5, maxradiuskm=100, starttime='1975-01-01', **base)['count']
    top = pedir('query', minmagnitude=5, maxradiuskm=150, starttime='1900-01-01', orderby='magnitude', limit=1, **base)['features']
    d = dict(id=r.id, sismos_m6_150km_desde1900=n6, sismos_m5_100km_desde1975=n5)
    if top:
        p = top[0]['properties']
        d.update(sismo_max_mag=p['mag'], sismo_max_fecha=time.strftime('%Y-%m-%d', time.gmtime(p['time'] / 1000)), sismo_max_lugar=p['place'])
    json.dump(d, open(f, 'w'), ensure_ascii=False)
    return d

def main():
    lista, salida = sys.argv[1], sys.argv[2]
    os.makedirs(CACHE, exist_ok=True)
    c = pd.read_csv(lista)
    with ThreadPoolExecutor(4) as ex:
        filas = list(ex.map(ciudad, [r for r in c.itertuples()]))
    pd.DataFrame(filas).to_csv(salida, index=False)
    print(len(filas), 'ciudades con historial sísmico')

if __name__ == '__main__':
    main()
