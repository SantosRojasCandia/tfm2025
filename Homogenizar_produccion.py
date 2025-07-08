import pandas as pd
import geopandas as gpd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
import numpy as np

df = r"D:\TFM 2025\Llerida\LLEIDA\Agraria Miralcamp\Rendiments finques Agrària de Miralcamp.xlsx"
df = pd.read_excel(df)
#print(df.head())
df['codsigpac'] = df['CODI '].astype(int).astype(str) + df['POL.'].astype(int).astype(str)  + df['PAR.'].astype(int).astype(str) + df['REC.'].astype(int).astype(str)
df_filtrado2024a = df[df['Rendiment Kg/jornal2024'] > 1].copy()
df_filtrado2024b = df[df['Producció 2nCULTIU2024'] > 1].copy()
df_filtrado2023 = df[df['Rendiment Kg/jornal2023'] > 1].copy()
df_filtrado2024a['Kg/ha'] = df_filtrado2024a['Rendiment Kg/jornal2024'] * 2.294471299319
df_filtrado2024b['Kg/ha'] = df_filtrado2024b['Producció 2nCULTIU2024'] * 2.294471299319
df_filtrado2023['Kg/ha'] = df_filtrado2023['Rendiment Kg/jornal2023'] * 2.294471299319
df_filtrado2024a['año'] = 2024
df_filtrado2024b['año'] = 20241
df_filtrado2023['año'] = 2023

#df_filtrado2024a.to_excel(r"D:\TFM 2025\Llerida\LLEIDA\Agraria Miralcamp\2024a.xlsx", index=False)
#df_filtrado2024b.to_excel(r"D:\TFM 2025\Llerida\LLEIDA\Agraria Miralcamp\2024b.xlsx", index=False)
#df_filtrado2023.to_excel(r"D:\TFM 2025\Llerida\LLEIDA\Agraria Miralcamp\2023.xlsx", index=False)
#print(df_filtrado2024a.head())

df_a = r"D:\TFM 2025\Llerida\LLEIDA\Agraria Miralcamp\2024a.xlsx"
df_b = r"D:\TFM 2025\TUTORES\Dades produccio per validacions\LLEIDA\Agraria Miralcamp MunMiralcampTorregrossa\2024aa.xlsx"
#codigos_comunes = df1['codisigpac'].isin(df_b['codisigpac'])
df_a = pd.read_excel(df_a)
df_b = pd.read_excel(df_b)

#duplicados = df_filtrado2024a[df_filtrado2024a['codsigpac'].duplicated(keep=False)]
#print(diferentes)
#print(duplicados[['codsigpac']].drop_duplicates())
#print(df_filtrado2024a.head())