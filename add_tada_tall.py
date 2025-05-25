# -*- coding: utf-8 -*-
"""
- Afegir data de tall
- Afegir ETa i precipitació

author: magipamies
datetime:2/6/2025 18:02
"""
from pathlib import Path
import pandas as pd
import geopandas as gpd

# Carpeta de treball
w_f = Path(r'/media/hdd15/TEMP/producccions_cat')
# Arxius shp de les parcel·les
shp_fold = w_f / "altres1/shp_lleida"
# Arxius csv amb les dates de tall
date_fold = w_f / "fechas_de_corte"
# Arxius csv amb les dades et ETa
eta_fold = w_f / "out_csv/ETa_daily_TSEB_SW"
# Arxius csv amb les dades de precipitació
ppt_fold = w_f / "out_csv/PPT"

# Carpeta de sortida
out_fold = w_f / "altres1/DUN_ccrr_v"



# ----------------------------------------------------------------------------------------
dict_cut = {
    'Inicio_crecimiento':{
        "BLAT TOU": "03-15",
        "CIVADA": "03-15",
        "ORDI": "03-15",
        "BLAT DE MORO": "04-15",
        "TRITICALE": "03-15",
    },
    'Fin_decrecimiento':{
        "BLAT TOU": "07-15",
        "CIVADA": "07-15",
        "ORDI": "07-15",
        "BLAT DE MORO": "10-30",
        "TRITICALE": "07-15",
    }
}


# Funció per sumar ET en el rang de dates per cada parcel·la
def calcular_et_total(row, df2, col_par='COD', col_ini='Inicio_crecimiento', col_fi='Fin_decrecimiento'):
    """
    Calcula la suma d'Evapotranspiració (ET) per una parcel·la en un rang de dates específic.

    Args:
        row (pd.Series):
            Fila d'un DataFrame que conté les columnes amb el codi de parcel·la i dates.
        df2 (pd.DataFrame):
            DataFrame d'ET amb:
            - Index: Dates (en format datetime).
            - Columnes: Codis de parcel·la (han de coincidir amb els valors de `col_par`).
        col_par (str, opcional):
            Nom de la columna que conté els codis de parcel·la. Per defecte 'COD'.
        col_ini (str, opcional):
            Nom de la columna amb la data d'inici. Per defecte 'Inicio_crecimiento'.
        col_fi (str, opcional):
            Nom de la columna amb la data final. Per defecte 'Fin_decrecimiento'.

    Returns:
        float:
            Suma acumulada d'ET en el rang de dates. Retorna 0 si la parcel·la no existeix a df2.

    Exemple:
        >>> df1['ET_total'] = df1.apply(
        ...     calcular_et_total,
        ...     axis=1,
        ...     df2=df_et,
        ...     col_par='Parcela',
        ...     col_ini='Inicio',
        ...     col_fi='Fi'
        ... )
    """
    # Validació bàsica
    try:
        cod = row[col_par]
        inicio = row[col_ini]
        fin = row[col_fi]
    except KeyError as e:
        raise KeyError(f"Columna no trobada a la fila: {e}")

    # Verificar si la parcel·la existeix a df2
    if cod not in df2.columns:
        return pd.NA

    # Seleccionar i sumar ET (ignorant NaN)
    et_rang = df2.loc[inicio:fin, cod]
    return et_rang.sum(skipna=True)
# -------------------------------------------------------------------------------------------

# Llista dels arxius
l_shp = [x for x in shp_fold.glob('*.shp')]
l_date = [x for x in date_fold.glob('*.csv')]
# l_csv = [x for x in csv_fold.glob('*sum_daily.csv')]
l_eta = [x for x in eta_fold.glob('*mean.csv')]
l_ppt = [x for x in ppt_fold.glob('*mean.csv')]

shp_f = l_shp[0]
for shp_f in l_shp:
    name_f = '_'.join(shp_f.name.split('_')[2:]).split('.')[0]

    any_s = shp_f.name.split('_')[2][:4]

    print(name_f, any_s)
    # Any de les parcel·les (tinguen en compte que el 2024 en té 2)
    if name_f == "2024a":
        date_f = [x for x in l_date if "2024.csv" in x.name][0]
    elif name_f == "2024_2da_siembra":
        date_f = [x for x in l_date if "20242dasiembra" in x.name][0]
    else:
        date_f = [x for x in l_date if name_f in x.name][0]

    # Arxiu ETa i Precipitació
    eta_f = [x for x in l_eta if name_f in x.name][0]
    ppt_f = [x for x in l_ppt if name_f in x.name][0]

    # Obrim arxiu vectorial
    gdf = gpd.read_file(shp_f)
    # Posem els noms del cultius amb majúscules
    gdf["Cultivo"] = gdf["Cultivo"].str.upper()
    # Reemplaçar 'PANIS' per 'BLAT DE MORO'
    gdf['Cultivo'] = gdf['Cultivo'].replace('PANIS', 'BLAT DE MORO')
    gdf['Cultivo'] = gdf['Cultivo'].replace('BLAT', 'BLAT TOU')
    gdf['ccrr'] = gdf['ccrr'].replace('NOCCRR', 'SS')

    # Obrim csv de les dates de tall
    df_date = pd.read_csv(date_f)

    # Llista de les parcel·les
    l_par = gdf['COD'].tolist()
    # Afegim al gdf les columnes de les dates de tall
    gdf1 = gdf.merge(df_date[['Parcela', 'Inicio_crecimiento', 'Fin_decrecimiento']],
                     left_on="COD",
                     right_on="Parcela",
                     how="left")
    gdf1.drop('Parcela', axis=1, inplace=True)  # Eliminem la columna "Parcela"

    # PER SI HI HA ALGUNA PARCEL·LA QUE NO TÉ DATA DE TALL!!!
    # # Omplir NaN amb valors del diccionari
    # gdf1['Inicio_crecimiento'] = gdf1.apply(
    #     lambda row: f"{any_s}-" + dict_cut['Inicio_crecimiento'][row['Cultivo']]
    #     if pd.isna(row['Inicio_crecimiento'])
    #     else row['Inicio_crecimiento'],
    #     axis=1
    # )
    #
    # gdf1['Fin_decrecimiento'] = gdf1.apply(
    #     lambda row: f"{any_s}-" + dict_cut['Fin_decrecimiento'][row['Cultivo']]
    #     if pd.isna(row['Fin_decrecimiento'])
    #     else row['Fin_decrecimiento'],
    #     axis=1
    # )

    # Passem a datetime
    gdf1['Inicio_crecimiento'] = pd.to_datetime(gdf1['Inicio_crecimiento'], format="%Y-%m-%d")
    gdf1['Fin_decrecimiento'] = pd.to_datetime(gdf1['Fin_decrecimiento'], format="%Y-%m-%d")


    # PER SI VOLEM TALLAR LA DATA FINAL EN FUNCIÓ DEL DICCIONARI
    # gdf1['Fin_decrecimiento'] = gdf1.apply(
    #     lambda row: f"{any_s}-" + dict_cut['Fin_decrecimiento'][row['Cultivo']]
    #     if row['Fin_decrecimiento'] > pd.to_datetime(f"{any_s}-" + dict_cut['Fin_decrecimiento'][row['Cultivo']])
    #     else row['Fin_decrecimiento'],
    #     axis=1
    # )
    # gdf1['Fin_decrecimiento'] = pd.to_datetime(gdf1['Fin_decrecimiento'], format="%Y-%m-%d")

    # Comprovem si hi ha cap NAN
    # gdf1[gdf1['Inicio_crecimiento'].isna()]['Inicio_crecimiento'].count()
    # gdf1[gdf1['Fin_decrecimiento'].isna()]['Fin_decrecimiento'].count()

    # POSAR QUE SI LA DISTÀNCIA ENTRE LA DATA INICIAL I LA FINAL ÉS INFERIOR A X DIES, AGAFAR LES DE PER DEFECTE.
    # SI ÉS SUPERIOR IGUAL.


    # Afegim ETa
    df_eta = pd.read_csv(eta_f, index_col=0, parse_dates=True)
    df_eta.columns = df_eta.columns.astype(int)
    # [x for x in l_par if x not in [int(x) for x in df_eta.columns.tolist()]]

    df_eta = df_eta[l_par]

    # Aplicar la funció a cada fila de df1
    gdf1['ETa'] = gdf1.apply(calcular_et_total, axis=1, df2=df_eta)


    # Afegim PPT
    df_ppt = pd.read_csv(ppt_f, index_col=0, parse_dates=True)
    df_ppt.columns = df_ppt.columns.astype(int)
    # [x for x in l_par if x not in [int(x) for x in df_ppt.columns.tolist()]]
    df_ppt = df_ppt[l_par]

    # Aplicar la funció a cada fila de df1
    gdf1['Prec'] = gdf1.apply(calcular_et_total, axis=1, df2=df_ppt)

    # Dies que dura el periode del cultiu
    gdf1["days_dif"] =  gdf1["Fin_decrecimiento"]- gdf1["Inicio_crecimiento"]
    gdf1["days_dif"] = gdf1["days_dif"].dt.days.astype(int)

    gdf1['Inicio_crecimiento'] = gdf1['Inicio_crecimiento'].dt.strftime('%Y-%m-%d')
    gdf1['Fin_decrecimiento'] = gdf1['Fin_decrecimiento'].dt.strftime('%Y-%m-%d')

    # Afegim el tipus de Reg
    gdf1['T_Reg'] = "SPRINKLER"
    gdf1.loc[gdf1["ccrr"] == "CU", 'T_Reg'] = "FLOOD"

    # Eliminem les files que no tenen dades
    # gdf1[(gdf1['ETa'] != 0) & (gdf1['Prec'] != 0)]
    gdf1 = gdf1[
        (gdf1['ETa'].fillna(0) != 0)
        &
        (gdf1['Prec'].fillna(0) != 0)
        ]

    # Comprovar NaN
    print("Hi ha NaN a 'ETa' o 'Prec'?", gdf1[['ETa', 'Prec']].isna().any().any())
    # print("Quantitat de NaN per columna:\n", gdf1[['ETa', 'Prec']].isna().sum())
    # print("Files amb NaN:\n", gdf1[gdf1[['ETa', 'Prec']].isna().any(axis=1)])

    gdf1.to_file(out_fold / shp_f.name)
