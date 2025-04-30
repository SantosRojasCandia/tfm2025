import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
import numpy as np


#df = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\Rendiments finques Agrària de Miralcamp.xlsx"
#df = pd.read_excel(df)
#print(df.head())
#print(list(df.columns))
#print(df[['CODI ', 'POL.', 'PAR.', 'REC.']].isnull().sum())
#df['codsigpac'] = df['CODI '].astype(int).astype(str) + df['POL.'].astype(int).astype(str)  + df['PAR.'].astype(int).astype(str) + df['REC.'].astype(int).astype(str)
#df['codsigpac'] = df['CODI '].astype(int) + df['POL.'].astype(int)  + df['PAR.'].astype(int) + df['REC.'].astype(int)
#df.to_excel(r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\nuevo.xlsx", index=False)
#dfa = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\nuevo.xlsx"
#dfa = pd.read_excel(dfa)
#print(dfa.head())
#print(list(dfa.columns))
#print(dfa.dtypes)
#pg = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\Rendiments finques Agrària de Miralcamp proceso.xlsx"
#pg = pd.read_excel(pg)
#print(pg.head())
#print(list(pg.columns))
#print(pg[['CODI ', 'POL.', 'PAR.', 'REC.']].isnull().sum())
#pg['codsigpac'] = pg['CODI '].astype(int).astype(str) + pg['POL.'].astype(int).astype(str)  + pg['PAR.'].astype(int).astype(str) + pg['REC.'].astype(int).astype(str)
#pg['codsigpac'] = df['CODI '].astype(int) + df['POL.'].astype(int)  + df['PAR.'].astype(int) + df['REC.'].astype(int) esta linea convirte a entero un tipo de dato
#pg.to_excel(r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\pg.xlsx", index=False)
#df_a = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\a.xlsx"
#df_b = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\excel_para_programar.xlsx"
#df_a = pd.read_excel(df_a)
#df_b = pd.read_excel(df_b)
#df_filtrado = df_b[df_b['codsigpac'].isin(df_a['codsigpac'])]
#df_filtrado.to_excel(r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\df_bfiltrado.xlsx", index=False)
#df_a = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\df_bfiltrado.xlsx"
#df_b = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\a.xlsx"
#df_a = pd.read_excel(df_a)
#df_b = pd.read_excel(df_b)
#df_resultado = df_a.merge(df_b[['codsigpac', 'COD']], on='codsigpac', how='inner')
#df_resultado.to_excel(r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\resultado.xlsx", index=False)
#print(df_resultado['COD'].value_counts())
#####################################################################################
#filtra las filas que tengas dados mayor a uno en la columna de rendimiento
#a esta columna lo multipilca por una constante para convertir de Kg/jornal a Kr/ha.
#genera una columna con el año
df_c = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\resultado.xlsx"
df_c = pd.read_excel(df_c)
#print(list(df_c.columns))
df_filtrado2024a = df_c[df_c['Rendiment Kg/jornal 2024'] > 1].copy()
df_filtrado2024b = df_c[df_c['Producció 2nCULTIU2024'] > 1].copy()
df_filtrado2023 = df_c[df_c['Rendiment Kg/jornal 2023'] > 1].copy()
df_filtrado2024a['Kg/ha'] = df_filtrado2024a['Rendiment Kg/jornal 2024'] * 2.294471299319
df_filtrado2024b['Kg/ha'] = df_filtrado2024b['Rendiment Kg/jornal 2nCULTIU2024'] * 2.294471299319
df_filtrado2023['Kg/ha'] = df_filtrado2023['Rendiment Kg/jornal 2023'] * 2.294471299319
df_filtrado2024a['año'] = 2024
df_filtrado2024b['año'] = 20241
df_filtrado2023['año'] = 2023
df_filtrado2024a.to_excel(r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\2024a.xlsx", index=False)
df_filtrado2024b.to_excel(r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\2024b.xlsx", index=False)
#df_filtrado2023.to_excel(r"D:\TFM 2025\estadistica_lleida\2023.xlsx", index=False)
################################################################################
#estas lineas elimina los : de una columna que usa este caracter como separador
df_d = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Coop_Bellvis MunLleida\RENDIMENT BLAT 2024 - copia.xlsx"
df_e = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Coop_Bellvis MunLleida\RENDIMENT BLAT 2023 - copia.xlsx"
df_g = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Coop_Bellvis MunLleida\2024 RENDIMENTS PANÍS - copia.xlsx"
df_h = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Coop_Bellvis MunLleida\2022 RENDIMENTS PANÍS - copia.xlsx"
df_d = pd.read_excel(df_d)
df_e = pd.read_excel(df_e)
df_g = pd.read_excel(df_g)
df_h = pd.read_excel(df_h)
#print(df_d.columns)
df_d['codsigpac'] = df_d['codigo'].str.replace(":", "", regex=False)
df_e['codsigpac'] = df_e['codigo'].str.replace(":", "", regex=False)
df_g['codsigpac'] = df_g['codigo'].str.replace(":", "", regex=False)
df_h['codsigpac'] = df_h['codigo'].str.replace(":", "", regex=False)
df_d.to_excel(r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Coop_Bellvis MunLleida\blat2024.xlsx", index=False)
df_e.to_excel(r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Coop_Bellvis MunLleida\blat2023.xlsx", index=False)
df_g.to_excel(r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Coop_Bellvis MunLleida\panis2024.xlsx", index=False)
df_h.to_excel(r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Coop_Bellvis MunLleida\panis2022.xlsx", index=False)
#############################################################################

#esta linas concatenan varias columnas en una sola y guarda en un archivo nuevo de salida

# df_h = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\CoopGuissona MunMassoteres\dades_produccio.xlsx"
# df_h = pd.read_excel(df_h)
# df_h['codsigpac'] = (df_h['PROV'].astype(str) + df_h['MUNICIPI'].astype(str) + df_h['POLIGON'].astype(str) + df_h['PARCEL.LA'].astype(str) + df_h['RECINTE'].astype(str))
# df_h.to_excel(r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\CoopGuissona MunMassoteres\dades_produccio1.xlsx", index=False)

# df_i = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Jordi_Quilez_MunAlcarras\Dades de Producció de algunes Parcel.les. Fruits de Ponent d'Alcarràs i Secció de Crèdit. 2024.xlsx"
# df_i = pd.read_excel(df_i)
# df_i['codsigpac'] = (df_i['Codi. Municipio'].astype(str) + df_i['Zona Polígono'].astype(str) + df_i['Parcela '].astype(str) + df_i['Recintes'].astype(str))
# df_i.to_excel(r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Jordi_Quilez_MunAlcarras\codsigpac.xlsx", index=False)
# ###############################################################################
# df_j = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Llenes MunTorrefeta i Florejacs_Tarroja de Segarra\Rendiments 2024 per a Quim.xlsx"
# df_j = pd.read_excel(df_j)
# df_j['codsigpac'] = df_j['ID_REC'].str.replace(":", "", regex=False)
# df_j.to_excel(r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Llenes MunTorrefeta i Florejacs_Tarroja de Segarra\sigpac.xlsx", index=False)
# ##################################################################################
# #estas lineas, muestra en encabezado de un archivo excel, luego calcula las estadisticas de rendimiento por cultivo
# #generea un grafico del rendimiento comparado con una distribucion normal de tre tipos de cultivo
# df_k = r"D:\TFM 2025\estadistica_lleida\2024a.xlsx"
# df_k = pd.read_excel(df_k)
# print(df_k.head())
# estadisticas = df_k.groupby('Cultivo')['Rendimiento  (Kg/Ha.)'].agg(['count', 'mean', 'min', 'max', 'std', 'sum'])
# estadisticas = estadisticas.reset_index()
# print(estadisticas)
# estadisticas.to_excel(r"D:\TFM 2025\estadistica_lleida\estadistica.xlsx", index=False)
#
# #Graficos
# rendimiento_Blat = df_k[df_k['Cultivo'] == 'Blat']['Rendimiento  (Kg/Ha.)']
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
# plt.savefig(r"D:\TFM 2025\estadistica_lleida\graficas\estadisticaBlat.jpg")
# #plt.show()
#
# rendimiento_Ordi = df_k[df_k['Cultivo'] == 'Ordi']['Rendimiento  (Kg/Ha.)']
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
# plt.savefig(r"D:\TFM 2025\estadistica_lleida\graficas\estadisticaOrdi.jpg")
# #plt.show()
#
# rendimiento_PANIS = df_k[df_k['Cultivo'] == 'PANIS']['Rendimiento  (Kg/Ha.)']
# media = rendimiento_PANIS.mean()
# std = rendimiento_PANIS.std()
# x = np.linspace(rendimiento_PANIS.min(), rendimiento_PANIS.max(), 100)
# plt.figure(figsize=(8, 5))
# sns.histplot(rendimiento_PANIS, bins=15, kde=False, stat='density', color='skyblue', label='Datos')
# plt.plot(x, norm.pdf(x, media, std), 'r-', lw=2, label='Distribución normal')
# plt.title('Distribución de rendimiento - PANIS')
# plt.xlabel('Rendimiento')
# plt.ylabel('Densidad')
# plt.legend()
# plt.grid(True)
# plt.savefig(r"D:\TFM 2025\estadistica_lleida\graficas\estadisticaPANIS.jpg")
# #plt.show()
# ######################################
# max_min = df_k.groupby('Cultivo')['Rendimiento  (Kg/Ha.)'].agg(['min', 'max'])
# print(max_min)
# ###############################
# g = sns.displot(data=df_k, x='Rendimiento  (Kg/Ha.)', col='Cultivo', col_wrap=4, bins=20, kde=True)
# g.set_axis_labels('Rendimiento  (Kg/Ha.', 'Frecuencia')
# g.fig.suptitle('Frecuencia de Rendimiento por Cultivo', y=1.5)
# plt.tight_layout()
# #plt.show()
# g.savefig(r"D:\TFM 2025\estadistica_lleida\graficas\estadisticageneral.jpg")
