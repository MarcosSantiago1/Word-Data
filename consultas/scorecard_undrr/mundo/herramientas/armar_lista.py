"""Arma datos/ciudades_mundo.csv: gobiernos locales de +2 millones (lista_ciudades.py + ciudades-prefectura de China).

China: ciudades de nivel de prefectura (Wikidata Q748149) con más de 2 millones en su último dato (casi todos
del censo 2020), más los 4 municipios bajo jurisdicción central (Pekín, Shanghái, Tianjín, Chongqing).
uso: python armar_lista.py <crudos/wikidata> <salida.csv>
"""
import sys, os, re, unicodedata
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lista_ciudades import L

wd, salida = sys.argv[1], sys.argv[2]

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '_', s).strip('_')

cols = ['id', 'nombre', 'nombre_local', 'iso3', 'tipo', 'autoridad', 'pob', 'anio_pob', 'fuente_pob', 'lat', 'lon']
filas = [dict(zip(cols, x)) for x in L]

MUNIC = [  # municipios bajo jurisdicción central, censo 2020
    ('chongqing', 'Chongqing', '重庆市', 32054159, 29.56, 106.55), ('shanghai', 'Shanghái', '上海市', 24870895, 31.23, 121.47),
    ('pekin', 'Pekín', '北京市', 21893095, 39.90, 116.40), ('tianjin', 'Tianjín', '天津市', 13866009, 39.13, 117.20)]
for i, n, z, p, la, lo in MUNIC + [('harbin', 'Harbin', '哈尔滨市', 10009854, 45.80, 126.53)]:
    filas.append(dict(id=i, nombre=n, nombre_local=z, iso3='CHN', tipo='Municipio bajo jurisdicción central' if i != 'harbin' else 'Ciudad subprovincial (capital de Heilongjiang)', autoridad='Alcalde/sa (y secretario/a del Partido)',
                      pob=p, anio_pob=2020, fuente_pob='Censo 2020, NBS', lat=la, lon=lo, provincia=n if i != 'harbin' else 'Heilongjiang'))

d = pd.read_csv(os.path.join(wd, 'wd_china.csv'))
d['f'] = pd.to_datetime(d.fecha, errors='coerce', utc=True)
d = d[~d.zh.fillna('').str.contains('省|自治区|自治區')]
d = d[d.tipo.str.endswith('Q748149')]
d = d.sort_values(['c', 'f', 'pop']).groupby('c').tail(1)
d = d[d['pop'] > 2e6]
usados = {f['id'] for f in filas}
for _, r in d.sort_values('pop', ascending=False).iterrows():
    en = re.sub(r'\s+(City|Prefecture)$', '', str(r.en))
    nombre = r.es if isinstance(r.es, str) and not r.es.startswith('Q') else en
    nombre = re.sub(r'^(Ciudad de |Prefectura de )', '', nombre)
    i = slug(en)
    if i in usados: i = i + '_' + slug(str(r.provEn))
    usados.add(i)
    la, lo = map(float, re.match(r'Point\(([-\d.]+) ([-\d.]+)\)', r.coord).groups()[::-1])
    filas.append(dict(id=i, nombre=nombre, nombre_local=r.zh, iso3='CHN', tipo='Ciudad de nivel de prefectura', autoridad='Alcalde/sa (y secretario/a del Partido)',
                      pob=int(r['pop']), anio_pob=int(r.f.year) if pd.notna(r.f) else None, fuente_pob='Wikidata (censo 2020 de la NBS salvo indicación)', lat=la, lon=lo,
                      provincia=r.provEn, wikidata=r.c.rsplit('/', 1)[1]))
out = pd.DataFrame(filas)
out['hecha_a_mano'] = out.id.isin(['sao_paulo', 'cdmx', 'lima', 'bogota', 'rio', 'brasilia', 'guayaquil', 'quito', 'medellin', 'fortaleza', 'salvador',
                                    'belo_horizonte', 'cali', 'caracas', 'manaus', 'caba'])
assert out.id.is_unique
out.to_csv(salida, index=False)
print(len(out), 'ciudades;', (out.iso3 == 'CHN').sum(), 'de China;', out.iso3.nunique(), 'países')
