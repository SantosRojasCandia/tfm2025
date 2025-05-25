# -*- coding: utf-8 -*-
"""
Script per calcular les ADP potencials a partir de la mitjana o del percentil 95.

Crea tres columnes:
    - ADPp95 ==> ADP mitjana/Percentil 95 de cada cultiu (totes les ccrr juntes)
    - ADPp95cr ==> ADP mitjana/Percentil 95 de cada cultiu de cada ccrr
    - 'Ypot_cr' ==> Producció potencial(tm_ha) per cada cultiu i ccrr

S'utilitza l'script després d'executar el 'ccrr_calc_adp.py' i abans del 'ccrr_cacl_prod_agg.py'

IMPORTANT ==> NO S'UTILITZA EL PERCENTIL 95, S'UTILITZA LA MITJANA.
Enlloc del percentil 95 fem la mitjana per cada CCRR i agafem el valor més elevat.
El que fem:
 - Mitjana per CCRR i cultiu
 - Per cada cultiu agafem com a ADP_pot el valor més elevat
 - ADP_pot = El valor mitjà més elevat entre totes les CCRR


VERSIÓ 2  ==>  NO UTILIZA LA APD_pot_ccrr. LA ADP_pot ÉS LA DE LA PROPIA PARCEL·LA
Per calcular la producció màxima (Y_pot) de cada parcel·la ho fa a partir de la relació entre:
 - la ADP_pot de la parcel·la (ADP_p)
 - la mitjana de ADP per CCRR més elevada (ADPp95)

 Antigament s'utilitzava una producció potencial unica per cada ccrr/cultiu.
 Per això la variable "Ypot_cr" actualment fa referencia a la producció potencial de la parcel·la i no de tota la CCRR

author: magipamies
datetime:22/8/2023 14:56
"""

import os
import sys
import glob
from os import path as pth
import geopandas as gpd
import pandas as pd
from tqdm import tqdm

os.environ['PROJ_LIB'] = r'/home/irta/anaconda3/envs/irta_bd/share/proj'

#lleida_folder = r'/media/hdd2/Satelite_data/ET/Lleida/Series_temporals/Comunitat_Regants/Sequera/DUN_ccrr_p'

work_folder = r'/media/hdd15/TEMP/producccions_cat/altres1'

in_folder = pth.join(work_folder, 'DUN_ccrr_p')

# Si volem fer el percentil enlloc de la mitjana
do_per = False
# Percentil en que volem
n_per = 0.95

# Si volem guardar una copia dels fitxer originals
do_backup = True


# -------------------------------------------------------------
def calc_ypot(p_cr, p_all, y_max):
    """
    Funció per calcular la productivitat (tm_h) potencial. Adapatem el valor potencial a cada ccrr en funció de la ADP
    d'aquella CCRR en relació amb la de totes juntes (utilitzem el percentil 95).

    Args:
        p_cr (float): percentil 95 de adp de la CCRR
        p_all (float): percentil 95 de adp de totes les parcel·les
        y_max (float): Valor de la productivitat (tm_ha) màxim per tipus de cultiu.

    Returns:
        (float): Valor de la productivitat potencial per aquella ccrr i cultiu

    """
    if p_cr > p_all:
        return y_max
    else:
        return (p_cr / p_all) * y_max


# ------------------------------------------------
#
# # PER CALCULAR ELS POTENCIALS A PARTIR DE TOTS ELS SHP DE TOTES LES PARCEL·LES DE LLEIDA
# # Seleccionem tots els arxius geojson de la carpeta
# list_files_shp = glob.glob(pth.join(lleida_folder, "*.geojson"))
#
# # Obrim els arxius geojson i el unim en df
# df = pd.concat([gpd.read_file(f, ignore_geometry=True) for f in list_files_shp if '2017' not in pth.basename(f)],
#                ignore_index=True)
#
# if do_per:
#     # Creem el df percentil 95 per cada ccrr i cultiu (ho convertim en diccionari tmb)
#     df_p_cr = df.groupby(['codi', 'Cultiu'])['ADP_p'].quantile(n_per)
#     dic_p_cr = df.groupby(['codi', 'Cultiu'])['ADP_p'].quantile(n_per).to_dict()
#     # Creem el df del percentil 95 per cada cultiu
#     df_per = df.groupby('Cultiu')['ADP_p'].quantile(n_per)
# else:
#     # Creem el df de la mitjana per cada ccrr i cultiu (ho convertim en diccionari tmb)
#     df_p_cr = df.groupby(['codi', 'Cultiu'])['ADP_p'].mean()
#     dic_p_cr = df.groupby(['codi', 'Cultiu'])['ADP_p'].mean().to_dict()
#     # Creem el df de la mitjana per cada cultiu
#     df_per = df_p_cr.groupby(level=1).max()
#
# # Guardem els df dels percentils
# df_per.to_csv(pth.join(in_folder, 'ADP_p95_all.csv'))
# df_p_cr.reset_index().to_csv(pth.join(in_folder, 'ADP_p95_ccrr.csv'), index=False)
#
# # Eliminem el df ja que ja no ens serveix
# del df

# Obrim els arxius csv amb la info dels potencials
df_per = pd.read_csv(pth.join(in_folder, 'ADP_p95_all.csv'), index_col=0)['ADP_p']
df_p_cr = pd.read_csv(pth.join(in_folder, 'ADP_p95_ccrr.csv'), index_col=[0,1])['ADP_p']

# Afegim el triticale (mateix valor que l'ordi)
df_per['TRITICALE'] = df_per['ORDI']
# Afegim el tritical a l'altre df
nous_registres = df_p_cr[df_p_cr.index.get_level_values(1) == 'ORDI'].copy()
nous_registres.index = pd.MultiIndex.from_tuples(
    [(ccrr, 'TRITICALE') for ccrr in df_p_cr[df_p_cr.index.get_level_values(1) == 'ORDI'].copy().index.get_level_values(0)],
    names=['ccrr', 'cultiu']
)
df_p_cr = pd.concat([df_p_cr, nous_registres])
df_p_cr = df_p_cr.sort_index()

dic_p_cr = df_p_cr.to_dict()

# Seleccionem tots els arxius geojson de la carpeta
list_files_shp = glob.glob(pth.join(in_folder, "*.shp"))

# Itinerem per cada geojson (any)
for shp_fil in tqdm(list_files_shp):
    # Obrim l'arxiu
    gdf = gpd.read_file(shp_fil)
    # Guardem copia de seguretat
    if do_backup: gdf.to_file(pth.join(in_folder, 'bck', pth.basename(shp_fil)), driver='GeoJSON')
    # Creem la columna amb el percentil 95 per cada cultiu
    gdf['ADPp95'] = gdf['Cultiu'].map(df_per.to_dict())
    # Creem la columna amb el percintil 95 per cada cultiu i ccrr
    gdf['ADPp95cr'] = gdf.apply(lambda x: dic_p_cr[(x['codi'], x['Cultiu'])], axis=1)
    # Creem la columna amb la producció potencial (per cultiu i ccrr)
    gdf['Ypot_cr'] = gdf.apply(lambda x: calc_ypot(x['ADP_p'], x['ADPp95'], x['Yr_tm/ha']), axis=1)
    # Versió antiga on calculva la ADP_p en funció de la ADP mitjana de la ccrr i no de la propia parcel·la.
    # gdf['Ypot_cr'] = gdf.apply(lambda x: calc_ypot(x['ADPp95cr'], x['ADPp95'], x['Yr_tm/ha']), axis=1)


    # Guardem l'arxiu final
    gdf[[x for x in gdf.columns.tolist() if x != 'geometry'] + ['geometry']].to_file(shp_fil, driver='GeoJSON')

print('final')

# SI VOLEM GUARDAR UN RESUM DEL DF EN CSV (els percentils i la producció per ccrr i cultius)
df = pd.concat([gpd.read_file(f, ignore_geometry=True) for f in list_files_shp], ignore_index=True)
df_res = df.groupby(['codi', 'Cultiu'])[['ADPp95', 'ADPp95cr', 'Yr_tm/ha', 'Ypot_cr']].first()
df_res.reset_index().to_csv(pth.join(in_folder, 'ADP_resum.csv'), index=False)
print('final2')
