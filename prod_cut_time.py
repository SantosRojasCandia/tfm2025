# -*- coding: utf-8 -*-
"""

author: magipamies
datetime:7/5/2025 10:54
"""


import os
from os import path as pth
from os.path import basename as bn
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import glob
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import seaborn as sns
from pathlib import Path
import geopandas as gpd



w_f = r'D:\TFM 2025\Lleida\out_csv\FAPAR\clean'

# Arxiu csv
csv_f = pth.join(w_f, 'prod_lleida_2022_FAPAR_mean.csv_clean.csv')

# Arxiu per veure quin cultiu és
crop_f = r'D:\TFM 2025\Lleida\Shp_final_lleida\prod_lleida_2022.shp'

# Carpeta de sortida
out_fold = pth.join(w_f, 'proves')

# -----------------------------------------------
for fold in [out_fold]:
    if not pth.exists(fold):
        os.mkdir(fold)


# --------------------------------------------
# Per tenir el diccionari amb els tipus de cultius
df_crop = gpd.read_file(crop_f, ignore_geometry=True)
df_crop = gpd.read_file(crop_f, ignore_geometry=True)
df_crop.set_index('COD', inplace=True)
dict_crop = df_crop['Cultivo'].to_dict()

# Any de l'arxiu (per tallar després el df)
any_s = pth.basename(csv_f).split('_')[2]

# Obrim arxiu csv
df_i = pd.read_csv(csv_f, index_col=0, header=0, date_format="%Y-%m-%d")
list_col = df_i.columns

# Per cada parcel·la
# Seleccionem la parcel·la
cult = list_col[0]
df_c = df_i[[cult]]
# Tipus de cultiu que és
type_c = dict_crop[int(cult)]

# Tallar per data (si és PANIS any natural, sinó any anterior)
if type_c == "PANIS":
    date_cut = f"{any_s}0101"
else:
    date_cut = f"{str(int(any_s)-1)}1101"

# DF de la parcela
df_a = df_c[pd.to_datetime("20220101", format="%Y%m%d"):]
print(f"Rang temporal de la parcel·la {cult} de {type_c}: {df_a.index.min()}, {df_a.index.max()}")
# df_a.plot()
# plt.show()
# Per mirar les diferències
# Amplada del les dates a fer la mitjana
window=3
dict_numb = {'nopython':True, 'nogil':True, 'parallel':True}
# identify outliers
ndiff = (df_a - df_a.rolling(window, axis=0, min_periods=1, center=True).mean(engine='numba',
                                                                          engine_kwargs=dict_numb)).abs()
# Df amb les files ordenades de manjor diferencia a menor.
ndiff.sort_values(by=ndiff.columns.tolist()[0], ascending=False, inplace=True)

ndiff['data'] = ndiff.index
# Seleccionar data amb major diferencia
data1 = ndiff.iloc[0]['data']
for i in range(1, len(ndiff)):
    print(i)
    data2 = ndiff.iloc[i]['data']
    dif_data = abs(data1 - data2)
    if dif_data > timedelta(days=100):
        break
print(data1, data2)
# df[ndiff > threshold] = np.nan


#  Prova amb el csv sense CLEAN
csv_f2 = r'D:\TFM 2025\Lleida\out_csv\FAPAR\prod_lleida_2022_FAPAR_mean.csv'
df_i2 = pd.read_csv(csv_f2, index_col=0, header=0, date_format="%Y%m%d")
df_a2 = df_i2[[cult]][pd.to_datetime("20220101", format="%Y%m%d"):]
ndiff2 = (df_a - df_a2.rolling(window, axis=0, min_periods=1, center=True).mean(engine='numba',
                                                                          engine_kwargs=dict_numb)).abs()

ndiff2.sort_values(by=ndiff2.columns.tolist()[0], ascending=False, inplace=True)

ndiff2['data'] = ndiff2.index
# Seleccionar data amb major diferencia
data1_2 = ndiff2.iloc[0]['data']
for i in range(1, len(ndiff2)):
    print(i)
    data2_2 = ndiff2.iloc[i]['data']
    dif_data = abs(data1_2 - data2_2)
    if dif_data > timedelta(days=100):
        break
print(data1_2, data2_2)
