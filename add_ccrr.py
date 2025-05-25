# -*- coding: utf-8 -*-
"""

author: magipamies
datetime:2/6/2025 9:21
"""
from pathlib import Path
import pandas as pd
import geopandas as gpd


w_f = Path(r'/media/hdd15/TEMP/producccions_cat')

# Carpeta amb els shp de les parcel·les
shp_f = w_f / "shp_fecha_de_corte"

# Carpeta de sortida
shp_out = w_f / "altres1/shp_lleida"

# Shp de les comunitats de regants
ccrr_f = w_f / r'altres1/shp_auxiliars/comunitat_regants_retall.geojson'


gdf_ccrr = gpd.read_file(ccrr_f)
crs_ccrr = gdf_ccrr.crs
gdf_ccrr.rename(columns={'codi': 'ccrr'}, inplace=True)

l_shp = [x for x in shp_f.glob("*.shp")]

# shp_f = l_shp[0]
for shp_f in l_shp:
    print(str(shp_f))
    gdf = gpd.read_file(shp_f)
    # crs_out = gdf.crs
    # gdf_ccrr = gdf_ccrr.to_crs(gdf.crs)

    gdf = gdf.to_crs(crs_ccrr)

    gdf2 = gdf.sjoin(gdf_ccrr[['ccrr', 'geometry']], how='left')
    # Opcional: eliminar la columna extra 'index_right' que s'afegeix per defecte
    gdf2 = gdf2.drop(columns=['index_right'])

    print(gdf2['ccrr'].isna().sum(), f"{(gdf2['ccrr'].isna().sum()/gdf2['ccrr'].size) * 100} %")
    # Convertir a string però mantenir NaN com a string buit
    gdf2['ccrr'] = gdf2['ccrr'].fillna("NOCCRR").astype(str)
    # df = gdf2[[x for x in gdf2.columns if x != 'geometry']]

    gdf2.to_file(shp_out / shp_f.name)

print('Final')


