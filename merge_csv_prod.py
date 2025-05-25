# -*- coding: utf-8 -*-
"""
Script per calcular la recta de regresió a partir de la ADP i la producció de les parcel·les de mostra.
Primer uneix

Ypot_cr ==> Yeld calculat per model (ADP_P/AD95 * Yr_tm/ha) (el valor màxim és el Yr_tm/ha, ja que si ADP_P/AD95>1 llavor és multiplica per 1)

author: magipamies
datetime:2/6/2025 23:20
"""
import os
import sys
import glob
from os import path as pth
import geopandas as gpd
import pandas as pd
from tqdm import tqdm
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

os.environ['PROJ_LIB'] = r'/home/irta/anaconda3/envs/irta_bd/share/proj'


work_folder = r'/media/hdd15/TEMP/producccions_cat/altres1'

in_folder = pth.join(work_folder, 'DUN_ccrr_p')

out_folder = pth.join(work_folder, 'agg_cult')

list_files_shp = glob.glob(pth.join(in_folder, "*.shp"))



# Obrim els arxius geojson i el unim en df
df = pd.concat([gpd.read_file(f, ignore_geometry=True) for f in list_files_shp], ignore_index=True)

# Calculem la Producció simulada (és la de la columna "Ypot_cr"
# df.rename(columns={'Ypot_cr':'Yeld_sim'}, inplace=True)
df['Yeld_sim'] = df['Ypot_cr']
df['Yeld_sim2'] = (df['ADP'] / df['ADPp95']) * df['Yr_tm/ha']
df['Yeld_sim'] = df['Yeld_sim2']
# Calculem el Yeld (passem els kg a tonelades)
df['yeld_real'] = df['Rend_KgHa'] * 0.001
# df['yeld_real'] = (df['Rend_KgHa'] / df["ADP"])

#
df['Y_dif'] = df['yeld_real'] / df['Yr_tm/ha']
df['ADP_dif'] = df['ADP'] / df['ADPp95cr']
# df.loc[df['Y_dif']>1, 'Y_dif'] = 1
# df.loc[df['ADP_dif']>1, 'ADP_dif'] = 1
# df['ADP_dif'] = df['ADP'] / df['ADPp95']

list_cult = df["Cultiu"].unique().tolist()


# GRÀFICA AMB SEABORNfor cult in list_cult:
#     df_c = df.loc[df["Cultiu"]==cult]
#     df_c.to_csv(pth.join(out_folder, f"agg_{cult}.csv"), index=False)
#     print(cult, df_c.shape)
#
#     # Calcular regressió
#     x = df_c['ADP_dif'].values
#     y = df_c['Y_dif'].values
#     pendent, ordenada, r_value, _, _ = stats.linregress(x, y)
#
#     # Coeficient de determinació (R²)
#     r_squared = r_value**2
#
#     print(f"Recta: Yeld_ratio = {pendent:.2f} * ADP_ratio + {ordenada:.2f}")
#     print(f"R² = {r_squared:.2f}")
#
#
#     # Gràfic
#     plt.figure(figsize=(10, 6))
#     plt.scatter(x, y, color='blue', alpha=0.4)
#     plt.plot(x, pendent * x + ordenada, 'r-',
#              label=f'Regressió: y = {pendent:.2f}x + {ordenada:.2f}\nR² = {r_value**2:.2f}')
#     plt.xlabel('ADP relatiu')
#     # plt.xlabel('ADP (mm)')
#     plt.ylabel('Yeld relatiu')
#     # plt.ylabel('Yeld (kg/ha / mm)')
#     plt.title(f'{cult}')
#     plt.legend()
#     plt.grid(linestyle='--', alpha=0.6)
#     plt.savefig(pth.join(out_folder, f"YeldADP_recta_regresio_{cult}.png"), dpi=300, bbox_inches='tight')
#     plt.show()
import seaborn as sns
from seaborn import regplot
# plt.figure(figsize=(10, 6))
# regplot(x='ADP', y='Rend_KgHa', data=df_c, ci=95)  # 95% d'interval de confiança
# plt.show()
#
# sns.lmplot(x="ADP", y="Rend_KgHa", col="Campanya", data=df_c)
# plt.show()


for cult in list_cult:
    df_c = df.loc[df["Cultiu"]==cult]
    df_c.to_csv(pth.join(out_folder, f"agg_{cult}.csv"), index=False)
    print(cult, df_c.shape)

    # Calcular regressió
    x = df_c['ADP_dif'].values
    y = df_c['Y_dif'].values
    pendent, ordenada, r_value, _, _ = stats.linregress(x, y)

    # Coeficient de determinació (R²)
    r_squared = r_value**2

    print(f"Recta: Yeld = {pendent:.2f} * ADP + {ordenada:.2f}")
    print(f"R² = {r_squared:.2f}")


    # Gràfic
    plt.figure(figsize=(10, 6))
    regplot(x='ADP_dif', y='Y_dif', data=df_c, ci=95, line_kws = {'label': '$y=%3.7s*x+%3.7s$ \nR² = %3.7s' % (pendent, ordenada,r_value**2)})  # 95% d'interval de confiança

    plt.xlabel('ADP relatiu')
    # plt.xlabel('ADP (mm)')
    plt.ylabel('Yeld relatiu')
    # plt.ylabel('Yeld (kg/ha / mm)')
    plt.title(f'{cult}')
    plt.legend()
    plt.grid(linestyle='--', alpha=0.6)
    plt.savefig(pth.join(out_folder, f"YeldADP_recta_regresio_{cult}_v2.png"), dpi=300, bbox_inches='tight')
    plt.show()

    plt.figure(figsize=(10, 6))

    sns.lmplot(x="ADP_dif", y="Y_dif", col="Campanya", data=df_c)
    plt.savefig(pth.join(out_folder, f"YeldADP_recta_regresio_{cult}_campanya.png"), dpi=300, bbox_inches='tight')

# #############################
# Nomes pel blat de moro
cult = 'BLAT DE MORO'
df_c = df.loc[df["Cultiu"]==cult]

plt.figure(figsize=(10, 6))

x = df_c.loc[df_c['Campanya']==2024.0, 'ADP_dif'].values
y = df_c.loc[df_c['Campanya']==2024.0, 'Y_dif'].values
pendent24, ordenada24, r_value24, _, _ = stats.linregress(x, y)
r_squared24 = r_value24**2

x = df_c.loc[df_c['Campanya']==2022.0, 'ADP_dif'].values
y = df_c.loc[df_c['Campanya']==2022.0, 'Y_dif'].values
pendent22, ordenada22, r_value22, _, _ = stats.linregress(x, y)
r_squared22 = r_value22**2
print(f"20224 Recta: Yeld = {pendent24:.2f} * ADP + {ordenada24:.2f}")
print(f"2024R² = {r_squared24:.2f}")
print(f"20222 Recta: Yeld = {pendent22:.2f} * ADP + {ordenada22:.2f}")
print(f"2022R² = {r_squared22:.2f}")


g = sns.lmplot(x="ADP_dif", y="Y_dif", col="Campanya", data=df_c)
# Afegim recta regresió i r
for ax in g.axes.flat:
    # Obtenir els coeficients de la recta (per a cada Campanya)
    x_data = ax.lines[0].get_xdata()
    y_data = ax.lines[0].get_ydata()
    # a, b = np.polyfit(x_data, y_data, 1)
    pendent, ordenada, r_value, _, _ = stats.linregress(x_data, y_data)

    r_squared = r_value ** 2
    eq = f"y = {pendent:.2f}x + {ordenada:.2f}\nR²:{r_squared:.2f}"

    # Afegir text al subgràfic
    ax.text(
        0.05, 0.95, eq,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.7)
    )

plt.savefig(pth.join(out_folder, f"YeldADP_recta_regresio_{cult}_campanya.png"), dpi=300, bbox_inches='tight')
plt.show()

#### PRODUCCIONS
for cult in list_cult:
    df_c = df.loc[df["Cultiu"]==cult]
    df_c.to_csv(pth.join(out_folder, f"agg_{cult}.csv"), index=False)
    print(cult, df_c.shape)

    # Calcular regressió
    x = df_c['Yeld_sim'].values
    y = df_c['yeld_real'].values
    pendent, ordenada, r_value, _, _ = stats.linregress(x, y)

    # Coeficient de determinació (R²)
    r_squared = r_value**2

    print(f"Recta: Yeld_real = {pendent:.2f} * Yeld_sim + {ordenada:.2f}")
    print(f"R² = {r_squared:.2f}")


    # Gràfic
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, color='blue', alpha=0.4)
    plt.plot(x, pendent * x + ordenada, 'r-',
             label=f'Regressió: y = {pendent:.2f}x + {ordenada:.2f}\nR² = {r_value**2:.2f}')
    plt.xlabel('Yel_sim(t/ha)')
    # plt.xlabel('ADP (mm)')
    plt.ylabel('Yeld real (t/ha)')
    # plt.ylabel('Yeld (kg/ha / mm)')
    plt.title(f'{cult}')
    plt.legend()
    plt.grid(linestyle='--', alpha=0.6)
    plt.savefig(pth.join(out_folder, f"Yeld_comparacio_{cult}.png"), dpi=300, bbox_inches='tight')
    plt.show()
