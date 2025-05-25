# -*- coding: utf-8 -*-
"""
Script que calcula la adp


author: magipamies
datetime:6/3/2023 11:55
"""

import os
import sys
import glob
from os import path as pth
import geopandas as gpd
import pandas as pd

os.environ['PROJ_LIB'] = r'/home/irta/anaconda3/envs/irta_bd_311/share/proj'

# Carpeta de treball
work_folder = r'/media/hdd15/TEMP/producccions_cat/altres1'

# Carpeta amb els geojson d'entrada
in_folder = pth.join(work_folder, 'DUN_ccrr_v')
# Carpeta amb els geojson de sortida
out_folder = pth.join(work_folder, 'DUN_ccrr_p')

# Arxiu csv amb la producció i la funció de producció per tipus de cultiu
cultius_f = pth.join(work_folder, 't_cultiu_f_prod.csv')

# Dotacions de reg
dot_reg = {'AB': 600, 'C': 700, 'CAYC': 800, 'CP': 1000, 'CU': 900, 'GS': 130, 'SG': 450, 'SS': 200, 'NOCCRR': 200}

# Limit excès
lim_ex = 700
# Valors excès
dict_ex = {'DRIP': 100, 'SPRINKLER': 50, 'FLOOD': 0}

# Eficiencia pluja
ef_p = 0.65

# Diccionari amb l'eficiència de reg
dict_ef_r = {'DRIP': 0.9, 'SPRINKLER': 0.75, 'FLOOD': 0.60}

# Llista de les columnes finals
# list_c = ['OBJECTID', 'Campanya', 'id_ccrr', 'codi', 'HA', 'HA_r', 'Cultiu', 'T_Reg', 'ETa', 'Prec', 'geometry']
list_c = ['OBJECTID', 'Campanya', 'codi', 'HA', 'HA_r', 'Cultiu', 'T_Reg', 'ETa', 'Prec', 'Rend_KgHa', 'geometry']

dic_rename = {"COD": "OBJECTID", "Año": "Campanya", "ccrr": 'codi', "Has": "HA", "Cultivo": "Cultiu"}
# --------------------------------------------------------------------------------------

def calc_adp(pl, efp, d_r, ex, ef_r):
    """
    Funció per calcular al adp

    Args:
        pl (float): Precipitació
        efp (float): Eficiència de Precipitació
        d_r (float): Dotació de Reg
        ex (float): Exedent de Reg
        ef_r (float): Eficiència de Reg

    Returns:
         (float): ADP

    """
    # Calculem la ADP
    adp = pl * efp + (d_r - ex) * ef_r
    return adp

# ------------------------------------------------------------------------------------------

# Obrim les produccions i les convertim en diccionari
bd_p = pd.read_csv(cultius_f, index_col=0)

# Seleccionem tots els arxius geojson de la carpeta
list_files_shp = glob.glob(pth.join(in_folder, "*.shp"))

# shp_fil = list_files_shp[0]

# Itinerem per cada geojson (DUN de cada any)
for shp_fil in list_files_shp:
    print(pth.basename(shp_fil))
    # Obrim el geojson
    gdf = gpd.read_file(shp_fil)

    # Eliminem les que no es reguen
    # gdf.drop(gdf.loc[gdf['T_Reg'] == 'NOT_IRRIGATED'].index, inplace=True)

    # Calcular àrea en m² i convertir a hectàrees
    gdf['HA_r'] = gdf.geometry.area / 10_000  # 10,000 m² = 1 ha
    gdf.rename(columns=dic_rename, inplace=True)
    # Fem un subset
    gdf = gdf[list_c]

    # Creem columnes pels càlculs
    gdf.loc[:, 'Dot_Reg'] = gdf['codi'].map(dot_reg)

    # Creem la columna d'exccès de reg. En funció del tipus de reg i de la dotació (si és superior al límit d'excès)
    gdf['exces'] = 0
    for tg, e_v in dict_ex.items():
        print(tg, 'excès: ', e_v)
        gdf.loc[(gdf['Dot_Reg'] > lim_ex) & (gdf['T_Reg'] == tg), 'exces'] = e_v

    # Creem columnes de la Eficiència de Reg i la de Eficència de la precipitació
    gdf['ef_Reg'] = gdf['T_Reg'].map(dict_ef_r)
    gdf['ef_Pre'] = ef_p

    # Calculem la ADP
    gdf['ADP'] = gdf.apply(lambda x: calc_adp(x['Prec'], x['ef_Pre'], x['Dot_Reg'], x['exces'], x['ef_Reg']), axis=1)
    # Calculem el ratio
    gdf['Ratio'] = gdf['ADP'] / gdf['ETa']

    # Quan ADP < ETa ==> ADP = ETa (així el ratio és de 1)
    gdf.loc[gdf['Ratio'] < 1, 'ADP'] = gdf.loc[gdf['Ratio'] < 1, 'ETa']
    gdf['Ratio'] = gdf['ADP'] / gdf['ETa']

    # Imprimim el número de ratios superiors a 1, inferiors a 1 i igual a 1.
    print('R<1: ', gdf.loc[gdf['Ratio'] < 1, 'ADP'].count())
    print('R==1: ', gdf.loc[gdf['Ratio'] == 1, 'ADP'].count())
    print('R>1: ', gdf.loc[gdf['Ratio'] > 1, 'ADP'].count())

    # Quan ADP > ETa ==> Tornem a calcular la ADP però modificant l'exedencia de reg i després la eficiència de reg
    # Comencem modificant la exedència de reg.
    dic_exm = dict_ex.copy()  # Creem un diccionari nou que l'anirem modificant (si és 'FLOOD' sempre serà 0)
    i = 0
    m = 50  # Valor en que s'incrementarà l'exedencia en cada loop
    while i != 8:  # Fem 8 loops
        # Modifiquem el diccionari
        for k, v in dic_exm.items():
            if k != 'FLOOD':  # Si és FLOOD no es modifica
                dic_exm[k] = v + m  # Incrementem l'exedencia

        # Afegim els nous valors del diccionari a la columna 'exces' del df per les parcel·les que la Ratio sigui més gran que 1
        for tg, e_v in dic_exm.items():
            # print(tg, 'excès: ', e_v)
            gdf.loc[(gdf['Ratio'] > 1) & (gdf['Dot_Reg'] > lim_ex) & (gdf['T_Reg'] == tg), 'exces'] = e_v

        # Calculem la ADP amb els nous valors d'exedència per les parcel·les que la Ratio sigui més gran que 1
        gdf.loc[gdf['Ratio'] > 1, 'ADP'] = gdf.loc[gdf['Ratio'] > 1].apply(
            lambda x: calc_adp(x['Prec'], x['ef_Pre'], x['Dot_Reg'], x['exces'], x['ef_Reg']), axis=1)
        # Recalculem el ràtio
        gdf['Ratio'] = gdf['ADP'] / gdf['ETa']
        print('R>1: ', gdf.loc[gdf['Ratio'] > 1, 'ADP'].count())
        # m += 50
        i += 1

    # Modifiquem l'eficiència de reg (mateix procediment que amb l'exedència de reg)
    dic_efr_m = dict_ef_r.copy()
    i = 0
    m = 0.02
    while i != 20:
        for k, v in dic_efr_m.items():
            dic_efr_m[k] = v - m
            if dic_efr_m[k] < 0:
                dic_efr_m[k] = 0

        gdf.loc[gdf['Ratio'] > 1, 'ef_Reg'] = gdf.loc[gdf['Ratio'] > 1, 'T_Reg'].map(dic_efr_m)
        gdf.loc[gdf['Ratio'] > 1, 'ADP'] = gdf.loc[gdf['Ratio'] > 1].apply(
            lambda x: calc_adp(x['Prec'], x['ef_Pre'], x['Dot_Reg'], x['exces'], x['ef_Reg']), axis=1)
        gdf['Ratio'] = gdf['ADP'] / gdf['ETa']
        print('R>1: ', gdf.loc[gdf['Ratio'] > 1, 'ADP'].count())
        print(dic_efr_m)
        i += 1

    # Quan ADP < ETa ==> ADP = ETa (així el ratio és de 1) (igual que hem fet més amunt)
    gdf.loc[gdf['Ratio'] < 1, 'ADP'] = gdf.loc[gdf['Ratio'] < 1, 'ETa']
    gdf['Ratio'] = gdf['ADP'] / gdf['ETa']

    # Pels últims que queden de: ADP > ETa ==> ADP = ETa (així el ratio és de 1)
    # gdf.loc[gdf['Ratio'] > 1, 'ADP'] = gdf.loc[gdf['Ratio'] > 1, 'ETa']
    # gdf['Ratio'] = gdf['ADP'] / gdf['ETa']
    # SI VOLEM QUE TOTS ELS RATIOS SIGUIN 1. SINÓ HO FA A L'SCRIPT QUE CALCULA LES PRODUCCIONS.
    # gdf.loc[gdf['Ratio'] > 1, 'Ratio'] = gdf.loc[gdf['Ratio'] > 1, 'Ratio']

    # Imprimim el número de ratios superiors a 1, inferiors a 1 i igual a 1.
    print('R<1: ', gdf.loc[gdf['Ratio'] < 1, 'ADP'].count())
    print('R==1: ', gdf.loc[gdf['Ratio'] == 1, 'ADP'].count())
    print('R>1: ', gdf.loc[gdf['Ratio'] > 1, 'ADP'].count())

    # Calculem la ADP potencial (A partir de les variables hem modificat)
    # gdf['ADP_p'] = gdf.apply(lambda x: calc_adp(x['Prec'], x['ef_Pre'], x['Dot_Reg'], x['exces'], x['ef_Reg']), axis=1)
    gdf['ADP_p'] = gdf['ADP']

    # Eliminem si tenim algun valor de 'na' a la ratio (pel 2018
    print('Nans al ratio ----------------------\n', gdf.loc[gdf['Ratio'].isna()])
    gdf.drop(gdf.loc[gdf['Ratio'].isna()].index, inplace=True)

    # CALCULEM LA PRODUCCIÓ
    # Producció relativa (tm/ha)
    gdf['Yr_tm/ha'] = gdf['Cultiu'].map(bd_p['tm/ha'].to_dict())
    # Posem les columnes per la funció de producció
    for x in bd_p.columns.to_list()[1:]:
        gdf[x] = gdf['Cultiu'].map(bd_p[x].to_dict())

    # Producció Total per parcel·la (tm)
    gdf['Yt_tm'] = gdf['Yr_tm/ha'] * gdf['Ratio'] * gdf['HA']

    print(gdf['Yt_tm'].sum())

    # Guardem el geojson
    shp_out = pth.join(out_folder, pth.basename(shp_fil).replace('_v', '_prod'))
    gdf.to_file(shp_out)

    # Guardem els arxius en que R<1 (que la ADP és més gran que la ET)
    a = gdf.loc[gdf['Ratio'] > 1]
    a['dif'] = a['ADP_p'] - a['ETa']
    a['dif_p'] = (a['dif'] / a['ETa']) * 100
    a_out = pth.join(out_folder, 'r_mes_1', pth.basename(shp_fil).replace('_v', '_prod_r1'))
    a.to_file(a_out)

