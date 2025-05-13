import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os.path as pth
from datetime import timedelta

# Paths
w_f = r'D:\TFM 2025\Lleida\out_csv\LAI\clean'
csv_f = r'D:\TFM 2025\Lleida\out_csv\LAI\clean\prod_lleida_2022_LAI_mean.csv_clean.csv'
csv_f2 = r'D:\TFM 2025\Lleida\out_csv\LAI\prod_lleida_2022_LAI_mean.csv'
crop_f = r'D:\TFM 2025\Lleida\Shp_final_lleida\prod_lleida_2022.shp'
out_fold = pth.join(w_f, 'proves')

# Crear carpeta de salida si no existe
os.makedirs(out_fold, exist_ok=True)

# Cargar cultivo por parcela
df_crop = gpd.read_file(crop_f, ignore_geometry=True)
df_crop.set_index('COD', inplace=True)
dict_crop = df_crop['Cultivo'].to_dict()

# Año del archivo
any_s = pth.basename(csv_f).split('_')[2]

# Cargar CSVs
df_i = pd.read_csv(csv_f, index_col=0, header=0, parse_dates=True)
df_i2 = pd.read_csv(csv_f2, index_col=0, header=0, parse_dates=True)
list_col = df_i.columns

# Diccionario de configuración para rolling con numba
window = 3
dict_numb = {'nopython': True, 'nogil': True, 'parallel': True}

# Guardar resultados
registros = []

# Bucle por parcela
for cult in list_col:
    df_c = df_i[[cult]]

    try:
        type_c = dict_crop[int(cult)]
    except KeyError:
        print(f"Cultivo no encontrado para parcela {cult}")
        continue

    # Definir fecha de corte
    if type_c == "PANIS":
        date_cut = f"{any_s}0101"
    else:
        date_cut = f"{str(int(any_s)-1)}1101"

    df_a = df_c[pd.to_datetime("20220101", format="%Y%m%d"):]
    if df_a.empty:
        print(f"Parcela {cult} vacía tras cortar fechas.")
        continue

    print(f"Rang temporal de la parcel·la {cult} de {type_c}: {df_a.index.min()}, {df_a.index.max()}")

    # Calcular diferencias (limpio)
    ndiff = (df_a - df_a.rolling(window, min_periods=1, center=True)
             .mean(engine='numba', engine_kwargs=dict_numb)).abs()
    ndiff.sort_values(by=ndiff.columns[0], ascending=False, inplace=True)
    ndiff['data'] = ndiff.index

    data1 = ndiff.iloc[0]['data']
    for i in range(1, len(ndiff)):
        data2 = ndiff.iloc[i]['data']
        if abs(data1 - data2) > timedelta(days=80):
            break

    # Calcular diferencias (original)
    df_c2 = df_i2[[cult]][pd.to_datetime("20220101", format="%Y%m%d"):]
    ndiff2 = (df_a - df_c2.rolling(window, min_periods=1, center=True)
              .mean(engine='numba', engine_kwargs=dict_numb)).abs()
    ndiff2.sort_values(by=ndiff2.columns[0], ascending=False, inplace=True)
    ndiff2['data'] = ndiff2.index

    data1_2 = ndiff2.iloc[0]['data']
    for i in range(1, len(ndiff2)):
        data2_2 = ndiff2.iloc[i]['data']
        if abs(data1_2 - data2_2) > timedelta(days=80):
            break

    # Guardar gráficas
    fig, ax = plt.subplots(figsize=(10, 4))
    df_a.plot(ax=ax, label='Serie limpia')
    df_c2.plot(ax=ax, label='Serie original', linestyle='--')
    ax.axvline(data1, color='r', linestyle='--', label='Pico limpio 1')
    ax.axvline(data2, color='orange', linestyle='--', label='Pico limpio 2')
    ax.axvline(data1_2, color='green', linestyle=':', label='Pico original 1')
    ax.axvline(data2_2, color='purple', linestyle=':', label='Pico original 2')
    ax.set_title(f"Diferències: parcel·la {cult} ({any_s})")
    ax.legend()
    plt.tight_layout()
    out_img = pth.join(out_fold, f"parcela_{cult}_{any_s}.png")
    plt.savefig(out_img)
    plt.close()

    # Añadir a la tabla final
    registros.append({
        'Parcela': cult,
        'Cultivo': type_c,
        'Fecha1_limpio': data1.date(),
        'Fecha2_limpio': data2.date(),
        'Fecha1_original': data1_2.date(),
        'Fecha2_original': data2_2.date()
    })

# Guardar CSV
df_out = pd.DataFrame(registros)
output_csv = pth.join(out_fold, 'rango_de_fechas_2022.csv')
df_out.to_csv(output_csv, index=False)
print(f"\nCSV guardado: {output_csv}")
