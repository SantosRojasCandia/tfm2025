import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
import numpy as np


#estas lineas generan las estadisticas de datos 2023 y me reporta un excel con las estadisticas
df_a = r"D:\TFM 2025\Lleida\datos_scrips\2022.xlsx"
df_b = r"D:\TFM 2025\Lleida\datos_scrips\2023.xlsx"
df_c = r"D:\TFM 2025\Lleida\datos_scrips\2024_2da_siembra.xlsx"
df_d = r"D:\TFM 2025\Lleida\datos_scrips\2024a.xlsx"
df_a = pd.read_excel(df_a)
df_b = pd.read_excel(df_b)
df_c = pd.read_excel(df_c)
df_d = pd.read_excel(df_d)

# estadistica para rendimiento 2022
estadisticas = df_a.groupby('Cultivo')['Rendimiento  (Kg/Ha.)'].agg(['count', 'mean', 'min', 'max', 'std', 'sum'])
estadisticas = estadisticas.reset_index()
estadisticas.to_excel(r"D:\TFM 2025\Lleida\datos_scrips\estadisticalleida2022.xlsx", index=False)

#estadistica para rendimiento 2023
estadisticas = df_b.groupby('Cultivo')['Rendimiento  (Kg/Ha.)'].agg(['count', 'mean', 'min', 'max', 'std', 'sum'])
estadisticas = estadisticas.reset_index()
estadisticas.to_excel(r"D:\TFM 2025\Lleida\datos_scrips\estadisticalleida2023.xlsx", index=False)

# estadistica para rendimiento 2024_2da_siembra
estadisticas = df_c.groupby('Cultivo')['Rendimiento  (Kg/Ha.)'].agg(['count', 'mean', 'min', 'max', 'std', 'sum'])
estadisticas = estadisticas.reset_index()
estadisticas.to_excel(r"D:\TFM 2025\Lleida\datos_scrips\estadisticalleida2024_2da_siembra.xlsx", index=False)

# estadistica para rendimiento 2024a
estadisticas = df_d.groupby('Cultivo')['Rendimiento  (Kg/Ha.)'].agg(['count', 'mean', 'min', 'max', 'std', 'sum'])
estadisticas = estadisticas.reset_index()
estadisticas.to_excel(r"D:\TFM 2025\Lleida\datos_scrips\estadisticalleida2024a.xlsx", index=False)

#Graficos
# rendimiento_Blat = df_d[df_d['Cultivo'] == 'Blat']['Rendimiento  (Kg/Ha.)']
# media = rendimiento_Blat.mean()
# std = rendimiento_Blat.std()
# x = np.linspace(rendimiento_Blat.min(), rendimiento_Blat.max(), 100)
# plt.figure(figsize=(8, 5))
# sns.histplot(rendimiento_Blat, bins=15, kde=False, stat='density', color='skyblue', label='Datos')
# plt.plot(x, norm.pdf(x, media, std), 'r-', lw=2, label='Distribución normal')
# plt.title('Distribución de rendimiento - Blat')
# plt.xlabel('Rendimiento')
# plt.ylabel('Densidad')
# plt.legend()
# plt.grid(True)
# plt.savefig(r"D:\TFM 2025\Lleida\graficas\estadisticalleidaBlat2024a.jpg")
# # #plt.show()

# rendimiento_Ordi = df_a[df_a['Cultivo'] == 'Ordi']['Rendimiento  (Kg/Ha.)']
# media = rendimiento_Ordi.mean()
# std = rendimiento_Ordi.std()
# x = np.linspace(rendimiento_Ordi.min(), rendimiento_Ordi.max(), 100)
# plt.figure(figsize=(8, 5))
# sns.histplot(rendimiento_Ordi, bins=15, kde=False, stat='density', color='skyblue', label='Datos')
# plt.plot(x, norm.pdf(x, media, std), 'r-', lw=2, label='Distribución normal')
# plt.title('Distribución de rendimiento - Ordi')
# plt.xlabel('Rendimiento')
# plt.ylabel('Densidad')
# plt.legend()
# plt.grid(True)
# plt.savefig(r"D:\TFM 2025\estadistica_lleida\graficas\estadisticalleidaOrdi2023.jpg")
# #plt.show()

# rendimiento_Triticale   = df_a[df_a['Cultivo'] == 'Triticale  ']['Rendimiento  (Kg/Ha.)']
# media = rendimiento_Triticale  .mean()
# std = rendimiento_Triticale  .std()
# x = np.linspace(rendimiento_Triticale  .min(), rendimiento_Triticale  .max(), 100)
# plt.figure(figsize=(8, 5))
# sns.histplot(rendimiento_Triticale  , bins=15, kde=False, stat='density', color='skyblue', label='Datos')
# plt.plot(x, norm.pdf(x, media, std), 'r-', lw=2, label='Distribución normal')
# plt.title('Distribución de rendimiento - Triticale  ')
# plt.xlabel('Rendimiento')
# plt.ylabel('Densidad')
# plt.legend()
# plt.grid(True)
# plt.savefig(r"D:\TFM 2025\estadistica_lleida\graficas\estadisticalleidaTriticale2023.jpg")
# #plt.show()
######################################
# max_min = df_a.groupby('Cultivo')['Rendimiento  (Kg/Ha.)'].agg(['min', 'max'])
# print(max_min)
###############################
# grafico 2022
g = sns.displot(data=df_a, x='Rendimiento  (Kg/Ha.)', col='Cultivo', col_wrap=4, bins=20, kde=True)
g.set_axis_labels('Rendimiento  Kg/Ha.', 'Frecuencia')
g.fig.suptitle('Frecuencia de Rendimiento por Cultivo', y=1.5)
# plt.tight_layout()
#plt.show()
g.savefig(r"D:\TFM 2025\Lleida\graficas\estadisticageneral2022.jpg")

# grafico 2023
g = sns.displot(data=df_b, x='Rendimiento  (Kg/Ha.)', col='Cultivo', col_wrap=4, bins=20, kde=True)
g.set_axis_labels('Rendimiento  Kg/Ha.', 'Frecuencia')
g.fig.suptitle('Frecuencia de Rendimiento por Cultivo', y=1.5)
# plt.tight_layout()
#plt.show()
g.savefig(r"D:\TFM 2025\Lleida\graficas\estadisticageneral2023.jpg")

# grafico 2024_2da_siembra
g = sns.displot(data=df_c, x='Rendimiento  (Kg/Ha.)', col='Cultivo', col_wrap=4, bins=20, kde=True)
g.set_axis_labels('Rendimiento  Kg/Ha.', 'Frecuencia')
g.fig.suptitle('Frecuencia de Rendimiento por Cultivo', y=1.5)
# plt.tight_layout()
#plt.show()
g.savefig(r"D:\TFM 2025\Lleida\graficas\estadisticageneral2024_2da_siembra.jpg")

# grafico 2024a
g = sns.displot(data=df_d, x='Rendimiento  (Kg/Ha.)', col='Cultivo', col_wrap=4, bins=20, kde=True)
g.set_axis_labels('Rendimiento  Kg/Ha.', 'Frecuencia')
g.fig.suptitle('Frecuencia de Rendimiento por Cultivo', y=1.5)
# plt.tight_layout()
#plt.show()
g.savefig(r"D:\TFM 2025\Lleida\graficas\estadisticageneral2024a.jpg")