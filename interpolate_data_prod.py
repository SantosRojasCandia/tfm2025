# -*- coding: utf-8 -*-
"""
script per interpolar i netejar les dades de Biofísics ( de Bellmunt.


author: magipamies
datetime:7/5/2025 10:08
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


# Carpeta de treball
w_f = r'D:\TFM 2025\Lleida\out_csv\FAPAR'
# Arxiu csv
csv_f = pth.join(w_f, 'prod_lleida_2024a_FAPAR_mean.csv')
# w_f = r'/media/hdd15/TEMP/producccions_cat/out_csv/LAI/'
# csv_f = pth.join(w_f, 'prod_lleida_2022_LAI_mean.csv')

# Arxiu per veure quin cultiu és
crop_f = r'D:\TFM 2025\Lleida\Shp_final_lleida/prod_lleida_2024a.shp'

# Carpeta de sortida
out_fold = pth.join(w_f, 'clean')
# Carpeta on guardar les imatges
plot_smooth_f = pth.join(out_fold, r'smooths')
# Número de gràfiques que es vol crear (si posem None farà un gràfic per cada parcel·la)
num_plots = None

# Paràmetres per filtrar les dades i fer el smoothing
# dict_filtering = {'threshold': 1.5, 'window': 3}
dict_filtering = {'threshold': 0.04, 'window': 3}  # FAPAR
dict_smoothing = {'window': 10}  # FAPAR


# ------------------------------------------------------------------------------------------
# Comprovem que les carpetes estan creades
for fold in [out_fold, plot_smooth_f]:
    if not pth.exists(fold):
        os.mkdir(fold)


def remove_outliers(df, threshold=3, window=3):
    """
    Function to remove outliers, Hampel filter.
    """
    dict_numb = {'nopython':True, 'nogil':True, 'parallel':True}

    #identify outliers
    ndiff = (df - df.rolling(window,min_periods=1, center = True).mean(engine='numba', engine_kwargs=dict_numb)).abs()
    #remove them
    df[ndiff>threshold] = np.nan
    return df


def df_clean(df, filtering=False, interpolate=False, smoothing=False, visualize=False, filtering_options=None,
             smoothing_options=None, out_folder_path=None, num_g=None, year_n="", d_crop=None):
    """
    Container for all the operations on timeseries: filtering, interpolation, smoothing and crop-naming. It also visualize the crops.

    INPUTS:
        df - pandas.DataFrame containing all timeseries (index = Datetime and columns = different timeseries)
        filtering       - flag to indicate if to perform filtering [default = False]
        interpolate     - flag to indicate if to perform interpolation [default = False]
        smoothing       - flag to indicate if to perform smoothing [default = False]
        visualize       - flag to indicate if to perform visualize [default = False]
        identify_crop   - flag to indicate if to perform crop identification [default = False]
        filtering_options - dictionary with option to filters (window size and threshold value) [default = {}]
        smoothing_options - dictionary with option to smooth (all options in pandas.rolling) [default = {}]
        out_folder_path   - folder path where to save all the images
        num_g             - nu
        d_crop            - diccionari {COD: Cultivo}

    OUTPUTS:
        df2: preprocessed pandas.DataFrame with timeseries

    """
    dict_numb = {'nopython':True, 'nogil':True, 'parallel':True}


    # reindex - Daily
    if smoothing_options is None:
        smoothing_options = {}
    if filtering_options is None:
        filtering_options = {}

    df2 = df.groupby(by=df.index.floor('D')).mean(engine='numba', engine_kwargs=dict_numb).copy()
    df2 = df2.reindex(pd.date_range(df2.index.min(), df2.index.max()))

    if filtering:
        dict_filt = {'threshold': 3, 'window': 3}
        if filtering_options:
            dict_filt.update(filtering_options)
        for col in df2.columns:
            sol = remove_outliers(df2.loc[:, col].dropna().copy(), **dict_filt)
            df2.loc[sol.index, col] = sol
        if visualize:  # save values to plot
            filt_df = df2.copy()

    if interpolate:
        if not ((df2.index.min() is pd.NaT) or (df2.index.max() is pd.NaT)):
            df2 = df2.groupby(by=df2.index.floor('D')).mean(engine='numba', engine_kwargs=dict_numb)
            df2 = df2.reindex(pd.date_range(df2.index.min(), df2.index.max()))
            df2 = df2.interpolate()
            if visualize:  # save values to plot
                int_df = df2.copy()

    if smoothing:
        dict_smoot = {'window': 7}
        if smoothing_options:
            dict_smoot.update(smoothing_options)
        df2 = df2.rolling(**dict_smoot, min_periods=1, center=True).mean(engine='numba', engine_kwargs=dict_numb)
        if visualize:  # save values to plot
            smt_df = df2.copy()

    if visualize:
        if not num_g: num_g = df.shape[1]
        for num, el in df.sample(n=num_g, axis=1).items():
            fig, ax = plt.subplots()
            ax = el.plot(ax=ax, style='co', label='initial values', ms=6)
            ax.set_title(f'column {num}')
            if filtering:
                filt_df.loc[:, num].plot(ax=ax, style='bo', label='values after filtering', ms=4)
            if interpolate:
                int_df.loc[:, num].plot(ax=ax, style='y-', label='values interpolated')
            if smoothing:
                smt_df.loc[:, num].plot(ax=ax, style='g-', label='values smoothed')
            ax.legend()
            ax.set_ylim((0, 1))
            ax.set_ylabel('FAPAR [-]')
            if out_folder_path is not None:
                figfile = Path(out_folder_path) / f'{el.index[-2].strftime("%Y")}_{d_crop[int(num)]}_{num}.png'
                # print(figfile)
                fig.savefig(figfile, facecolor='w')
            plt.close(fig)
    return df2


# ------------------------------------------------------------------------------------------
import geopandas as gpd
df_crop = gpd.read_file(crop_f, ignore_geometry=True)
df_crop.set_index('COD', inplace=True)
dict_crop = df_crop['Cultivo'].to_dict()

df_i = pd.read_csv(csv_f, index_col=0, header=0, date_format="%Y%m%d")
list_col = df_i.columns
list_col_nan = df_i.columns[df_i.isna().all()]
df_i.dropna(axis=1, how='all', inplace=True)

# Tallar per data
# df_i22 = df_i[pd.to_datetime("20220101", format="%Y%m%d"):]
# print(df_i.index.min(), df_i.index.max())
# print(df_i22.index.min(), df_i22.index.max())

df_c = df_clean(df_i, filtering=True, interpolate=True, smoothing=True, visualize=True,
                  filtering_options=dict_filtering, smoothing_options=dict_smoothing,
                  out_folder_path= plot_smooth_f, num_g=num_plots, d_crop=dict_crop)

for c in list_col_nan:
    df_c[c] = np.nan
    df_i[c] = np.nan

df_i = df_i[list_col]
df_c = df_c[list_col]
df_c.to_csv(pth.join(out_fold, bn(csv_f) + '_clean.csv'))

# PROVA PER DETECAR HERBA
# aa = df_c.max() - df_c.min()
# bb = df_i.max() - df_i.min()
# df_c[['256310']].plot()
# plt.show()
# df_i[['256310']].plot()
# plt.show()
# cc = df_c.loc['2021/07/01':'2021/10/01'].mean() - df_c.loc['2021/04/01':].mean()



#####3 FILTRE SAVGOL (NO MOSTRA CAP MILLORA) ####################################
#
# db_out = pd.DataFrame(columns=list_col, index=df_c.index)
#
# for column in df_c:
#     db_out[column] = savgol_filter(df_c[column], 31, 3)
#
#
# dict_numb = {'nopython':True, 'nogil':True, 'parallel':True}
# df_i2 = df_i.groupby(by=df_i.index.floor('D'), axis=0).mean(engine='numba', engine_kwargs=dict_numb).copy()
# df_i2 = df_i2.reindex(pd.date_range(df_i2.index.min(), df_i2.index.max()))
# df_i2 = df_i2.groupby(by=df_i2.index.floor('D'), axis=0).mean(engine='numba', engine_kwargs=dict_numb)
# df_i2 = df_i2.reindex(pd.date_range(df_i2.index.min(), df_i2.index.max()))
# df_i2 = df_i2.interpolate()
#
#
# db_out2 = pd.DataFrame(columns=list_col, index=df_i2.index)
# for column in df_i2:
#     db_out2[column] = savgol_filter(df_i2[column], 15, 3)
#
# col_n = '344591'
# fig, ax = plt.subplots()
# ax = df_i[[col_n]].plot(ax=ax, style='co', label='initial values', ms=6)
# ax.set_title(f'column {col_n}')
# df_c[[col_n]].plot(ax=ax, style='y-', label='values cleaned')
# db_out[[col_n]].plot(ax=ax, style='g-', label='values SAVGOL')
# df_i2[[col_n]].plot(ax=ax, style='r-', label='values interpolate')
# db_out2[[col_n]].plot(ax=ax, style='b-', label='values SAVGOL2')
#
# ax.legend()
# ax.set_ylim((0, 1))
# ax.set_ylabel('FAPAR [-]')
# figfile = Path(plot_smooth_f) / f'SAVGOL_{col_n}_{df_c.index[0].strftime("%Y")}.png'
# # print(figfile)
# fig.savefig(figfile, facecolor='w')
# plt.close(fig)






