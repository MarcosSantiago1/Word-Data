"""Vivienda informal por municipio en América Latina, según la fuente oficial de cada país.

Cada país mide la vivienda informal a su manera, así que el valor NO es comparable entre países:
  Brasil     IBGE, Censo 2022: población que vive en favelas y comunidades urbanas (SIDRA 9884)
             sobre la población total (SIDRA 4709). Todos los municipios.
  Colombia   DANE, CNPV 2018 (metodología 2020, con ONU-Hábitat): hogares en déficit habitacional
             (cuantitativo + cualitativo) sobre el total de hogares. Todos los municipios.
  Argentina  RENABAP (registro de barrios populares, versión 2023-12-06): familias en barrios populares
             sobre los hogares del Censo 2022 (INDEC). Por ahora solo la Ciudad de Buenos Aires.

Escribe enfoques_urbanos/datos/vivienda_municipal.csv y guarda los archivos bajados en
enfoques_urbanos/crudos/municipal/ (si una fuente falla, usa esa copia).
construir_enfoques.py lo usa para reemplazar el dato de tugurios del país por el del municipio
en las ciudades del estudio que tienen dato (ver CIUDAD_MUNICIPIO).

uso (desde etl/): python enfoques_urbanos/vivienda_municipal.py
"""

import json
import os

import pandas as pd
import requests

AQUI = os.path.dirname(os.path.abspath(__file__))
CRUDOS = os.path.join(AQUI, 'crudos', 'municipal')
SALIDA = os.path.join(AQUI, 'datos', 'vivienda_municipal.csv')
REFRESCAR = os.environ.get('ETL_REFRESCAR') == '1'

URL = {
    'bra_favelas': 'https://apisidra.ibge.gov.br/values/t/9884/n6/all/v/9612/p/2022',
    'bra_poblacion': 'https://apisidra.ibge.gov.br/values/t/4709/n6/all/v/93/p/2022',
    'col_deficit': 'https://www.dane.gov.co/files/investigaciones/deficit-habitacional/deficit-hab-2020-anexo-nueva-metodologia.xlsx',
    'arg_renabap': 'https://www.argentina.gob.ar/sites/default/files/renabap-2023-12-06.geojson',
    'arg_caba_hogares': 'https://www.indec.gob.ar/ftp/cuadros/poblacion/c2022_caba_hogares_c1_1.xlsx',
}
ARCHIVO = {'bra_favelas': 'bra_favelas_2022.json', 'bra_poblacion': 'bra_poblacion_2022.json',
           'col_deficit': 'col_deficit_habitacional_cnpv2018.xlsx', 'arg_renabap': 'arg_renabap_2023-12-06.geojson',
           'arg_caba_hogares': 'arg_caba_hogares_censo2022.xlsx'}

# ciudad del estudio (id de riesgo_ciudades_mundo) -> (iso3, código de municipio en la fuente)
CIUDAD_MUNICIPIO = {
    'sao_paulo': ('BRA', '3550308'), 'rio': ('BRA', '3304557'), 'brasilia': ('BRA', '5300108'),
    'salvador': ('BRA', '2927408'), 'fortaleza': ('BRA', '2304400'), 'belo_horizonte': ('BRA', '3106200'),
    'manaus': ('BRA', '1302603'),
    'bogota': ('COL', '11001'), 'medellin': ('COL', '05001'), 'cali': ('COL', '76001'),
    'caba': ('ARG', '02'),
}


def bajar(clave):
    """Baja el archivo si falta o si se pide refrescar; si la fuente falla, usa la copia guardada."""
    f = os.path.join(CRUDOS, ARCHIVO[clave])
    if os.path.exists(f) and not REFRESCAR:
        return f
    try:
        r = requests.get(URL[clave], timeout=300)
        r.raise_for_status()
        if f.endswith('.json'):
            json.loads(r.content)   # SIDRA devuelve texto plano cuando el pedido es inválido
        os.makedirs(CRUDOS, exist_ok=True)
        with open(f, 'wb') as h:
            h.write(r.content)
    except Exception as e:
        if not os.path.exists(f):
            raise
        print(f'  aviso: no se pudo actualizar {clave} ({e}); uso la copia guardada')
    return f


def sidra(f):
    filas = json.load(open(f, encoding='utf-8'))[1:]   # la primera fila es el encabezado
    return {r['D1C']: (r['D1N'], pd.to_numeric(r['V'], errors='coerce')) for r in filas}


def brasil():
    fav = sidra(bajar('bra_favelas'))
    pob = sidra(bajar('bra_poblacion'))
    filas = []
    for cod, (nom, p) in pob.items():
        if not p or pd.isna(p):
            continue
        n = fav.get(cod, (nom, 0))[1]
        n = 0 if pd.isna(n) else n   # municipios que no figuran en la tabla de favelas no tienen favelas
        filas.append({'iso3': 'BRA', 'codigo': cod, 'municipio': nom, 'valor_pct': round(100 * n / p, 2),
                      'numerador': n, 'denominador': p, 'unidad': 'personas', 'anio': 2022,
                      'indicador': 'Población en favelas y comunidades urbanas',
                      'fuente': 'IBGE, Censo 2022 (SIDRA 9884 y 4709)'})
    return filas


def colombia():
    f = bajar('col_deficit')
    d = pd.read_excel(f, sheet_name='Total Municipios', header=None, dtype=str)
    filas = []
    for _, r in d.iterrows():
        cod = str(r[2]).strip()
        if not (cod.isdigit() and len(cod) == 5):
            continue
        tot, cuant, cual = (pd.to_numeric(r[k], errors='coerce') for k in (4, 5, 6))
        if not tot:
            continue
        filas.append({'iso3': 'COL', 'codigo': cod, 'municipio': str(r[3]).strip(), 'valor_pct': round(100 * (cuant + cual) / tot, 2),
                      'numerador': cuant + cual, 'denominador': tot, 'unidad': 'hogares', 'anio': 2018,
                      'indicador': 'Hogares en déficit habitacional (cuantitativo + cualitativo)',
                      'fuente': 'DANE, CNPV 2018, metodología 2020 del déficit habitacional'})
    return filas


def argentina_caba():
    g = json.load(open(bajar('arg_renabap'), encoding='utf-8'))
    fam = sum(int(x['properties'].get('familias_aproximadas') or 0) for x in g['features']
              if 'Ciudad' in str(x['properties'].get('provincia', '')))
    h = pd.read_excel(bajar('arg_caba_hogares'), sheet_name=2, header=None)
    tot = next(r[1] for _, r in h.iterrows() if str(r[0]).strip() == 'Total')
    return [{'iso3': 'ARG', 'codigo': '02', 'municipio': 'Ciudad Autónoma de Buenos Aires', 'valor_pct': round(100 * fam / tot, 2),
             'numerador': fam, 'denominador': tot, 'unidad': 'familias / hogares', 'anio': 2023,
             'indicador': 'Familias en barrios populares (RENABAP) sobre hogares del Censo 2022',
             'fuente': 'RENABAP 2023-12-06 (argentina.gob.ar) e INDEC, Censo 2022'}]


def main():
    filas = []
    for nombre, fn in [('Brasil', brasil), ('Colombia', colombia), ('Argentina (CABA)', argentina_caba)]:
        try:
            filas += fn()
        except Exception as e:   # un país caído no frena a los otros
            print(f'  aviso: {nombre} sin datos ({e})')
    d = pd.DataFrame(filas)
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    d.to_csv(SALIDA, index=False)
    print(f'{len(d)} municipios con vivienda informal ({", ".join(f"{k}: {v}" for k, v in d.iso3.value_counts().items())})')
    return d


def por_ciudad():
    """Valor municipal para cada ciudad del estudio que tiene dato: id, valor, indicador, fuente."""
    if REFRESCAR or not os.path.exists(SALIDA):   # en la actualización mensual se vuelve a bajar
        main()
    d = pd.read_csv(SALIDA, dtype={'codigo': str})
    filas = []
    for cid, (iso3, cod) in CIUDAD_MUNICIPIO.items():
        m = d[(d.iso3 == iso3) & (d.codigo == cod)]
        if len(m):
            r = m.iloc[0]
            filas.append({'id': cid, 'tugurios_municipal': r.valor_pct, 'tugurios_indicador': r.indicador,
                          'tugurios_fuente': r.fuente, 'tugurios_anio': r.anio})
    return pd.DataFrame(filas, columns=['id', 'tugurios_municipal', 'tugurios_indicador', 'tugurios_fuente', 'tugurios_anio'])


if __name__ == '__main__':
    main()
