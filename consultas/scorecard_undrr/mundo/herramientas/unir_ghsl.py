"""Une cada ciudad con su centro urbano del GHSL UCDB R2024A y trae los indicadores de amenaza y capacidad.

El centro urbano es la mancha urbana continua (no el límite administrativo). Se toma el que contiene el punto si tiene
más de 1 millón de habitantes; si no, el centro urbano más
poblado del mismo país a menos de 25 km del punto de la ciudad; si no hay, el más cercano a menos de 50 km.
Varios gobiernos locales pueden compartir el mismo centro urbano (p. ej. Yokohama y Tokio).
uso: python unir_ghsl.py <crudos/ghsl> <datos/ciudades_mundo.csv> <datos/ghsl_ciudades.csv>
"""
import sys, os
import pandas as pd, numpy as np
from pyogrio.raw import read
import shapely
from pyproj import Transformer

g, lista, salida = sys.argv[1:4]
gp = os.path.join(g, 'gpkg', 'GHS_UCDB_THEME_GENERAL_CHARACTERISTICS_GLOBE_R2024A.gpkg')
meta, fids, geom, campos = read(gp, layer='GHSL_UCDB_THEME_GENERAL_CHARACTERISTICS_GLOBE_R2024A',
                                columns=['ID_UC_G0', 'GC_CNT_GAD_2025', 'GC_POP_TOT_2025'])
ids, paises, pobs = campos[0], campos[1], campos[2]
polys = shapely.from_wkb(geom)
arbol = shapely.STRtree(polys)
tr = Transformer.from_crs('EPSG:4326', 'ESRI:54009', always_xy=True)

c = pd.read_csv(lista)
x, y = tr.transform(c.lon.values, c.lat.values)
pts = shapely.points(x, y)
# país GHSL de cada iso3: el más frecuente entre los polígonos que contienen los puntos de ese país
dentro = [arbol.query(p, predicate='within') for p in pts]
pais_iso = pd.Series([paises[h[0]] if len(h) else None for h in dentro]).groupby(c.iso3.values).agg(lambda s: s.mode().iloc[0] if s.notna().any() else None)
uc_id, dist, modo = [], [], []
for p, iso, h in zip(pts, c.iso3, dentro):
    if len(h) and pobs[h[0]] >= 1e6:  # el punto cae en un centro urbano grande: ese es
        uc_id.append(int(ids[h[0]])); dist.append(0.0); modo.append('contiene el punto'); continue
    # si no, el centro urbano más poblado del mismo país a menos de 25 km del punto (evita quedar en un satélite chico)
    cand = [j for j in arbol.query(shapely.buffer(p, 25000), predicate='intersects') if paises[j] == pais_iso.get(iso)]
    if cand:
        j = max(cand, key=lambda k: pobs[k])
        uc_id.append(int(ids[j])); dist.append(round(shapely.distance(p, polys[j]) / 1000, 1)); modo.append('mayor a <25 km'); continue
    j = arbol.nearest(p); d = shapely.distance(p, polys[j]) / 1000
    uc_id.append(int(ids[j]) if d < 50 else None); dist.append(round(d, 1)); modo.append('más cercano')
c['ID_UC_G0'] = uc_id; c['dist_uc_km'] = dist; c['modo_union'] = modo

V = {  # tema: columnas que se usan
 'GENERAL_CHARACTERISTICS': ['GC_UCN_MAI_2025', 'GC_POP_TOT_2025', 'GC_UCA_KM2_2025', 'GC_DEV_WIG_2025'],
 'HAZARD_RISK': ['HZ_CEV_TEV_2015', 'HZ_CEV_TEV_2010', 'HZ_CEV_TEV_2005', 'HZ_CEV_FLO_2015', 'HZ_CEV_FLO_2010', 'HZ_CEV_FLO_2005',
                 'HZ_CEV_EAR_2015', 'HZ_CEV_EAR_2010', 'HZ_CEV_EAR_2005', 'HZ_CEV_TCY_2015', 'HZ_CEV_TCY_2010', 'HZ_CEV_TCY_2005',
                 'HZ_CEV_HEW_2015', 'HZ_CEV_HEW_2010', 'HZ_CEV_HEW_2005', 'HZ_CEV_DRO_2015', 'HZ_CEV_DRO_2010', 'HZ_CEV_DRO_2005',
                 'HZ_CEV_LAN_2015', 'HZ_CEV_LAN_2010', 'HZ_CEV_LAN_2005', 'HZ_CEV_COW_2015', 'HZ_CEV_COW_2010', 'HZ_CEV_COW_2005',
                 'HZ_CEV_TSU_2015', 'HZ_CEV_TSU_2010', 'HZ_CEV_TSU_2005', 'HZ_CEV_VOL_2015', 'HZ_CEV_VOL_2010', 'HZ_CEV_VOL_2005',
                 'HZ_CEV_EWI_2015', 'HZ_CEV_EWI_2010', 'HZ_CEV_EWI_2005', 'HZ_CEV_WLF_2015', 'HZ_CEV_WLF_2010', 'HZ_CEV_WLF_2005',
                 'HZ_WLF_NUM_2024', 'HZ_WLF_BHA_2024', 'HZ_CON_TOT_2020', 'HZ_CON_FAT_2020'],
 'EXPOSURE': ['EX_100_POP_2025', 'EX_100_SHP_2025', 'EX_010_POP_2025', 'EX_010_SHP_2025', 'EX_SHA_POP_2025', 'EX_E07_POP_2025', 'EX_E08_POP_2025',
              'EX_E09_POP_2025', 'EX_E10_POP_2025', 'EX_LEC_SHP_2025', 'EX_L05_POP_2025', 'EX_CF1_POP_2025', 'EX_CF1_SHP_2025',
              'EX_100_S1P_2025', 'EX_400_S3P_2025'],
 'CLIMATE': ['CL_B01_CUR_2010', 'CL_B12_CUR_2010', 'CL_UTC_T32_2020', 'CL_UTC_T32_2000', 'CL_KOP_CUR_2025', 'CL_WDS_CUR_2010'],
 'INFRASTRUCTURES': ['IN_CIS_ALL_2020', 'IN_CIS_HEA_2020', 'IN_CIS_ENE_2020', 'IN_CIS_WAT_2020', 'IN_CIS_TRA_2020', 'IN_CIS_TEL_2020', 'IN_CIS_EDU_2020'],
 'SOCIOECONOMIC': ['SC_SEC_HDI_2020', 'SC_GDP_AVG_2020', 'SC_SEC_LET_2020', 'SC_SEC_SYT_2020'],
 'GEOGRAPHY': ['GE_ELV_AVG_2025', 'GE_MRB_MAI_2025'],
}
for t, cols in V.items():
    f = os.path.join(g, 'csv', f'GHS_UCDB_THEME_{t}_GLOBE_R2024A.csv')
    try: d = pd.read_csv(f, encoding='utf-8-sig', low_memory=False)
    except UnicodeDecodeError: d = pd.read_csv(f, encoding='latin1', low_memory=False)
    d.columns = [k.replace('ï»¿', '').replace('\ufeff', '') for k in d.columns]
    d = d.loc[:, ~d.columns.duplicated()]
    falt = [k for k in cols if k not in d.columns]
    if falt: print('AVISO faltan', t, falt)
    d = d[['ID_UC_G0'] + [k for k in cols if k in d.columns]]
    for k in d.columns[1:]:
        if k not in ('GC_UCN_MAI_2025', 'GE_MRB_MAI_2025', 'CL_KOP_CUR_2025'):
            d[k] = pd.to_numeric(d[k].replace('-', None), errors='coerce')  # el GHSL marca con '-' los ceros/sin dato
    c = c.merge(d, on='ID_UC_G0', how='left')
c.to_csv(salida, index=False)
print(len(c), 'ciudades;', c.ID_UC_G0.isna().sum(), 'sin centro urbano;', (c.dist_uc_km > 0).sum(), 'por cercanía')

