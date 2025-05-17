import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os.path as pth

# Paths
w_f = r'D:\TFM 2025\Lleida\out_csv\FAPAR\clean'
csv_f = r'D:\TFM 2025\Lleida\out_csv\FAPAR\clean\prod_lleida_2022_FAPAR_mean.csv_clean.csv'
csv_f2 = r'D:\TFM 2025\Lleida\out_csv\FAPAR\prod_lleida_2022_FAPAR_mean.csv'
crop_f = r'D:\TFM 2025\Lleida\Shp_final_lleida\prod_lleida_2022.shp'
out_fold = pth.join(w_f, 'proves')

os.makedirs(out_fold, exist_ok=True)

# Cultivo por parcela
df_crop = gpd.read_file(crop_f, ignore_geometry=True)
df_crop.set_index('COD', inplace=True)
dict_crop = df_crop['Cultivo'].to_dict()

# Año
any_s = pth.basename(csv_f).split('_')[2]

# Cargar CSVs
df_i = pd.read_csv(csv_f, index_col=0, parse_dates=True)
df_i2 = pd.read_csv(csv_f2, index_col=0, parse_dates=True)
list_col = df_i.columns

registros = []

for cult in list_col:
    df_c = df_i[[cult]]

    try:
        type_c = dict_crop[int(cult)]
    except KeyError:
        print(f"Cultivo no encontrado para parcela {cult}")
        continue

    # Fecha de corte
    if type_c == "PANIS":
        date_cut = f"{any_s}0101"
    else:
        date_cut = f"{str(int(any_s)-1)}1101"

    df_a = df_c[pd.to_datetime("20220101", format="%Y%m%d"):]
    if df_a.empty:
        print(f"Parcela {cult} vacía tras cortar fechas.")
        continue

    print(f"Parcela {cult} ({type_c}): {df_a.index.min().date()} -> {df_a.index.max().date()}")

    serie = df_a[cult].copy()
    delta = serie.diff()
    umbral_crecimiento = 0.005
    duracion_min = 25
    umbral_decrecimiento = -0.001

    # Inicio del crecimiento
    inicio = None
    for i in range(len(delta) - duracion_min):
        if (delta.iloc[i:i+duracion_min] > umbral_crecimiento).all():
            inicio = delta.index[i]
            break
    if not inicio:
        print(f"No se detectó inicio claro en parcela {cult}")
        continue

    # Fin del crecimiento
    fin = None
    for i in range(delta.index.get_loc(inicio) + duracion_min, len(delta) - duracion_min):
        if (delta.iloc[i:i+duracion_min] < umbral_crecimiento / 2).all():
            fin = delta.index[i]
            break
    if not fin:
        fin = serie.index[-1]

    # Decrecimiento
    serie_post = serie[fin:]
    if serie_post.empty:
        print(f"No hay datos tras el crecimiento en parcela {cult}")
        continue

    # Inicio del decrecimiento (pico)
    inicio_decrecimiento = serie_post.idxmax()
    valor_max = serie_post.max()

    # Fin del decrecimiento
    serie_derivada = serie_post.diff()
    fin_decrecimiento = None
    for i in range(serie_post.index.get_loc(inicio_decrecimiento) + 1, len(serie_post) - duracion_min):
        ventana = serie_derivada.iloc[i:i+duracion_min]
        if (ventana > umbral_decrecimiento).all():
            fin_decrecimiento = serie_post.index[i]
            break
    if not fin_decrecimiento:
        fin_decrecimiento = serie_post.index[-1]

    # Gráfico
    df_c2 = df_i2[[cult]][pd.to_datetime("20220101", format="%Y%m%d"):]
    fig, ax = plt.subplots(figsize=(10, 4))
    df_a.plot(ax=ax, label='Serie limpia')
    df_c2.plot(ax=ax, label='Serie original', linestyle='--')
    ax.axvline(inicio, color='r', linestyle='--', label='Inicio crecimiento')
    ax.axvline(fin, color='orange', linestyle='--', label='Fin crecimiento')
    ax.axvline(inicio_decrecimiento, color='green', linestyle='--', label='Inicio decrecimiento')
    ax.axvline(fin_decrecimiento, color='purple', linestyle='--', label='Fin decrecimiento')
    ax.set_title(f"Ciclo FAPAR: parcela {cult} ({type_c})")
    ax.legend()
    plt.tight_layout()
    plt.savefig(pth.join(out_fold, f"parcela_{cult}_{any_s}.png"))
    plt.close()

    registros.append({
        'Parcela': cult,
        'Cultivo': type_c,
        'Inicio_crecimiento': inicio.date(),
        'Fin_crecimiento': fin.date(),
        'Duracion_crecimiento_dias': (fin - inicio).days,
        'Inicio_decrecimiento': inicio_decrecimiento.date(),
        'Fin_decrecimiento': fin_decrecimiento.date(),
        'Duracion_decrecimiento_dias': (fin_decrecimiento - inicio_decrecimiento).days,
        'Valor_max_LAI': round(valor_max, 2)
    })

# Guardar resultados
df_out = pd.DataFrame(registros)
output_csv = pth.join(out_fold, 'ciclo_FAPAR_completo_2022.csv')
df_out.to_csv(output_csv, index=False)
print(f"\nCSV guardado: {output_csv}")