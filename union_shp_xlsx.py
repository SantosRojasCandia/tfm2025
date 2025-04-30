import pandas as pd
import geopandas as gpd
import os

f = r'D:\TFM 2025\Lleida\shp\mun_lleida.shp'
f2 = r"D:\TFM 2025\Lleida\2024a.xlsx"
f3 = r"D:\TFM 2025\Lleida\2024_2da_siembra.xlsx"
f4 = r"D:\TFM 2025\Lleida\2023.xlsx"
#os.path.isfile(f2)
#gdf = gpd.read_file(f)
#gdf.columns
#gdf.shape
#gdf["coef_regad"].unique()
#list_col = gdf.columns.tolist()[:3]
#list_col.append('geometry')
#gdf2 = gdf[list_col]
#gdf2 = gdf2.drop(columns=['dn_oid'])
#gdf2.to_file("prueba1.geojson", driver="GeoJSON")
#gdf2.to_file(r"D:\TFM 2025\Lleida\shp\prueba1.shp")

#df = pd.read_excel(f2)
#df.drop(df.index[df['COD'].isna()], inplace=True)
#df_g = df.groupby('CULTIU 2024').count()
#df.head()
#df.columns
#df.dtypes
#gdf.dtypes
#df.loc[df['COD'].isna()]
#df['COD'] = df['COD'].astype(int)
#df['COD'].dtype
#gdf['COD'].dtype

#gdf1 = gdf.merge(df, on="COD", how="left")
#gdf1.to_file("Mun25170Parc_adp.shp")
#gdf1.to_file("Mun25170Parc_adp.geojson", driver="GeoJSON")

#df['sigpac'] = df['CODI '].astype(int).astype(str) + df['POL.'].astype(int).astype(str)  + df['REC.'].astype(int).astype(str)

#gdf['sigpac'] = gdf['provincia'].astype(int).astype(str) + gdf['municipio'].astype(int).astype(str) + gdf['poligono'].astype(int).astype(str) + gdf['parcela'].astype(int).astype(str) + gdf['recinto'].astype(int).astype(str)
#df2 = gdf.merge(df, on="sigpac", how="left")
#df2.to_file("Mun25170Parc_adp_v2.shp")
#df2.to_file("Mun25170Parc_adp_v2.geojson", driver="GeoJSON")

#############################################################
#unir shp con produccion 2024 en Lleida
f = gpd.read_file(f)
f2 = pd.read_excel(f2)
f["COD"] = f["COD"].astype(int)
f2["COD"] = f2["COD"].astype(int)
gdf_merged = f.merge(f2, on="COD", how="left")
gdf_merged = gdf_merged.rename(columns={'Rendimiento  (Kg/Ha.)': 'Rend_KgHa'})
gdf_merged.columns = [col.replace(" ", "_").replace("(", "").replace(")", "")[:10] for col in gdf_merged.columns]
#gdf_merged['codsigpac'] = gdf['codsigpac'].astype(str)
if 'dn_oid' in gdf_merged.columns:
    gdf_merged = gdf_merged.drop(columns=['dn_oid'])
gdf_merged.to_file(r"D:\TFM 2025\Lleida\shp\prod_lleida_2024.shp")

###################################
#unir shp con segunda cosecha 2024 Lleida
f3 = pd.read_excel(f3)
f["COD"] = f["COD"].astype(int)
f3["COD"] = f3["COD"].astype(int)
gdf_merged = f.merge(f3, on="COD", how="left")
gdf_merged = gdf_merged.rename(columns={'Rendimiento  (Kg/Ha.)': 'Rend_KgHa'})
gdf_merged.columns = [col.replace(" ", "_").replace("(", "").replace(")", "")[:10] for col in gdf_merged.columns]
#gdf_merged['codsigpac'] = gdf['codsigpac'].astype(str)
if 'dn_oid' in gdf_merged.columns:
    gdf_merged = gdf_merged.drop(columns=['dn_oid'])
gdf_merged.to_file(r"D:\TFM 2025\Lleida\shp\prod_lleida_2024_2da_cosecha.shp")

#########################################
#unir shp con segunda cosecha 2023 Lleida
f4 = pd.read_excel(f4)
f["COD"] = f["COD"].astype(int)
f4["COD"] = f4["COD"].astype(int)
gdf_merged = f.merge(f4, on="COD", how="left")
gdf_merged = gdf_merged.rename(columns={'Rendimiento  (Kg/Ha.)': 'Rend_KgHa'})
gdf_merged.columns = [col.replace(" ", "_").replace("(", "").replace(")", "")[:10] for col in gdf_merged.columns]
#gdf_merged['codsigpac'] = gdf['codsigpac'].astype(str)
if 'dn_oid' in gdf_merged.columns:
    gdf_merged = gdf_merged.drop(columns=['dn_oid'])
gdf_merged.to_file(r"D:\TFM 2025\Lleida\shp\prod_lleida_2023.shp")
