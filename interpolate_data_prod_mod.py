# -*- coding: utf-8 -*-
"""
Script per interpolar i netejar les dades de Biofísics (de Bellmunt).

author: magipamies
datetime: 7/5/2025 10:08
"""

import os
from os import path as pth
from os.path import basename as bn
import pandas as pd
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
from pathlib import Path
import geopandas as gpd
import seaborn as sns

# Carpeta de treball
w_f = r'D:\TFM 2025\Lleida\out_csv\LAI'
csv_f = pth.join(w_f, 'prod_lleida_2022_LAI_mean.csv')
crop_f = r'D:\TFM 2025\Lleida\Shp_final_lleida\prod_lleida_2022.shp'

out_fold = pth.join(w_f, 'clean')
plot_smooth_f = pth.join(out_fold, r'smooths')
num_plots = None

dict_filtering = {'threshold': 0.08, 'window': 3}  # FAPAR
dict_smoothing = {'window': 10}  # FAPAR

# Crear carpetes si no existeixen
for fold in [out_fold, plot_smooth_f]:
    os.makedirs(fold, exist_ok=True)

def remove_outliers(df, threshold=0.5, window=3):
    ndiff = (df - df.rolling(window, min_periods=1, center=True).mean()).abs()
    df[ndiff > threshold] = np.nan
    return df

def df_clean(df, filtering=False, interpolate=False, smoothing=False, visualize=False, filtering_options=None,
             smoothing_options=None, out_folder_path=None, num_g=None, d_crop=None):
    if filtering_options is None:
        filtering_options = {}
    if smoothing_options is None:
        smoothing_options = {}

    df2 = df.groupby(by=df.index.floor('D')).mean().copy()
    df2 = df2.reindex(pd.date_range(df2.index.min(), df2.index.max()))

    if filtering:
        dict_filt = {'threshold': 0.5, 'window': 3}
        dict_filt.update(filtering_options)
        for col in df2.columns:
            sol = remove_outliers(df2[col].dropna().copy(), **dict_filt)
            df2.loc[sol.index, col] = sol
        if visualize:
            filt_df = df2.copy()

    if interpolate:
        df2 = df2.interpolate()
        if visualize:
            int_df = df2.copy()

    if smoothing:
        dict_smoot = {'window': 7}
        dict_smoot.update(smoothing_options)
        df2 = df2.rolling(**dict_smoot, min_periods=1, center=True).mean()
        if visualize:
            smt_df = df2.copy()

    if visualize:
        if not num_g:
            num_g = min(5, df2.shape[1])
        for num, el in df2.sample(n=num_g, axis=1).items():
            fig, ax = plt.subplots()
            try:
                el.plot(ax=ax, style='co', label='initial values', ms=6)
                ax.set_title(f'column {num}')

                if filtering:
                    filt_df[num].plot(ax=ax, style='bo', label='filtered', ms=4)
                if interpolate:
                    int_df[num].plot(ax=ax, style='y-', label='interpolated')
                if smoothing:
                    smt_df[num].plot(ax=ax, style='g-', label='smoothed')

                ax.legend()
                ax.set_ylim((0, 5))
                ax.set_ylabel('LAI [-]')

                # Convertir la clave a float de forma segura
                try:
                    crop_key = float(num)
                except ValueError:
                    crop_key = str(num)
                crop_name = d_crop.get(crop_key, "Desconegut")

                figfile = Path(out_folder_path) / f'{el.index[-2].strftime("%Y")}_{crop_name}_{num}.png'
                fig.savefig(figfile, facecolor='w')
                plt.close(fig)
            except Exception as e:
                print(f"Error generant gràfic per columna {num}: {e}")

    return df2

# Llegim shapefile i convertim a diccionari
df_crop = gpd.read_file(crop_f, ignore_geometry=True)
df_crop.set_index('COD', inplace=True)
dict_crop = df_crop['Cultivo'].to_dict()

# Llegim arxiu de dades
df_i = pd.read_csv(csv_f, index_col=0, header=0, parse_dates=True, date_format="%Y%m%d")
list_col = df_i.columns
list_col_nan = df_i.columns[df_i.isna().all()]
df_i.dropna(axis=1, how='all', inplace=True)

# Netegem i processem dades
df_c = df_clean(df_i, filtering=True, interpolate=True, smoothing=True, visualize=True,
                filtering_options=dict_filtering, smoothing_options=dict_smoothing,
                out_folder_path=plot_smooth_f, num_g=num_plots, d_crop=dict_crop)

if df_c is not None:
    for c in list_col_nan:
        df_c[c] = np.nan
        df_i[c] = np.nan

    df_i = df_i[list_col]
    df_c = df_c[list_col]
    df_c.to_csv(pth.join(out_fold, bn(csv_f) + '_clean.csv'))
else:
    print("Error: df_clean ha retornat None.")
