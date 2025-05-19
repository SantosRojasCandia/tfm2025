
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os.path as pth

var_n = "FAPAR"
any_s = "2024a"
#any_s = "2024_2da_siembra"

# Paths
w_f = r'D:\TFM 2025\Lleida\out_csv\%s\clean' % var_n
csv_f = r'D:\TFM 2025\Lleida\out_csv\%s\clean\prod_lleida_%s_%s_mean.csv_clean.csv'  % (var_n, any_s, var_n)
csv_f2 = r'D:\TFM 2025\Lleida\out_csv\%s\prod_lleida_%s_%s_mean.csv' % (var_n, any_s, var_n)
crop_f = r'D:\TFM 2025\Lleida\Shp_final_lleida\prod_lleida_%s.shp'  % any_s
out_fold = pth.join(w_f, 'proves')

os.makedirs(out_fold, exist_ok=True)

# Cultivo por parcela
df_crop = gpd.read_file(crop_f, ignore_geometry=True)
df_crop.set_index('COD', inplace=True)
dict_crop = df_crop['Cultivo'].str.capitalize().to_dict()

# Año
any_s = pth.basename(csv_f).split('_')[2][:4]
any_ant_s = str(int(any_s) - 1)

# Diccionario de fechas por cultivo
fechas_por_cultivo = {
    "Blat": (f"{any_ant_s}1101", f"{any_s}0925"),
    "Colza": (f"{any_ant_s}1201", f"{any_s}0925"),
    "Ordi": (f"{any_ant_s}1101", f"{any_s}0925"),
    "Triticale": (f"{any_ant_s}1201", f"{any_s}0925"),
    "Civada": (f"{any_ant_s}1201", f"{any_s}0925"),
    "Panis": (f"{any_s}0201", f"{any_s}1225")
}

if var_n == "FAPAR":
    dic_esta = {
        'Blat': {"umbral_crecimiento": 0.002, "duracion_s": 24, "duracion_b": 40, "umbral_decrecimiento": -0.006},
        'Colza': {"umbral_crecimiento": 0.004, "duracion_s": 20, "duracion_b": 40, "umbral_decrecimiento": -0.006},
        'Ordi': {"umbral_crecimiento": 0.001, "duracion_s": 20, "duracion_b": 40, "umbral_decrecimiento": -0.006},
        'Civada': {"umbral_crecimiento": 0.004, "duracion_s": 20, "duracion_b": 40, "umbral_decrecimiento": -0.006},
        'Triticale': {"umbral_crecimiento": 0.004, "duracion_s": 20, "duracion_b": 55, "umbral_decrecimiento": -0.001},
        'Panis': {"umbral_crecimiento": 0.004, "duracion_s": 20, "duracion_b": 30, "umbral_decrecimiento": -0.0005},
    }
elif var_n == "LAI":
    dic_esta = {
        'Blat': {"umbral_crecimiento": 0.01, "duracion_s": 20, "duracion_b": 50, "umbral_decrecimiento": -0.008},
        'Colza': {"umbral_crecimiento": 0.01, "duracion_s": 20, "duracion_b": 40, "umbral_decrecimiento": -0.06},
        'Ordi': {"umbral_crecimiento": 0.01, "duracion_s": 20, "duracion_b": 45, "umbral_decrecimiento": -0.02},
        'Civada': {"umbral_crecimiento": 0.01, "duracion_s": 20, "duracion_b": 40, "umbral_decrecimiento": -0.06},
        'Triticale': {"umbral_crecimiento": 0.01, "duracion_s": 20, "duracion_b": 40, "umbral_decrecimiento": -0.02},
        'Panis': {"umbral_crecimiento": 0.01, "duracion_s": 20, "duracion_b": 20, "umbral_decrecimiento": -0.01},
    }
else:
    print('La variable no té diccionari')

# Cargar CSVs
df_i = pd.read_csv(csv_f, index_col=0, parse_dates=True)
df_i2 = pd.read_csv(csv_f2, index_col=0, parse_dates=True)
list_col = df_i.columns

registros = []
fail_l = []
for cult in list_col:
    df_c = df_i[[cult]]

    try:
        type_c = dict_crop[int(cult)]
    except KeyError:
        print(f"Cultivo no encontrado para parcela {cult}")
        continue

    try:
        fecha_inicio_str, fecha_fin_str = fechas_por_cultivo[type_c]
    except KeyError:
        print(f"No se definió rango de fechas para cultivo {type_c}. Parcela {cult} omitida.")
        continue

    fecha_inicio = pd.to_datetime(fecha_inicio_str, format="%Y%m%d")
    fecha_fin = pd.to_datetime(fecha_fin_str, format="%Y%m%d")
    df_a = df_c[fecha_inicio:fecha_fin]

    if df_a.empty:
        print(f"Parcela {cult} ({type_c}) vacía tras cortar entre {fecha_inicio.date()} y {fecha_fin.date()}.")
        continue

    print(f"Parcela {cult} ({type_c}): {df_a.index.min().date()} -> {df_a.index.max().date()}")

    serie = df_a[cult].copy()
    delta = serie.diff()
    parametros = dic_esta[type_c]
    umbral_crecimiento = parametros["umbral_crecimiento"]
    duracion_s = parametros["duracion_s"]
    duracion_b = parametros["duracion_b"]
    umbral_decrecimiento = parametros["umbral_decrecimiento"]

    inicio = None
    for i in range(len(delta) - duracion_s):
        if (delta.iloc[i:i+duracion_s] > umbral_crecimiento).all():
            inicio = delta.index[i]
            break
    if not inicio:
        print(f"No se detectó inicio claro en parcela {cult}")
        fail_l.append(f"{type_c} - {cult}")
        continue

    fin = None
    for i in range(delta.index.get_loc(inicio) + duracion_s, len(delta) - duracion_s):
        if (delta.iloc[i:i+duracion_s] < umbral_crecimiento / 2).all():
            fin = delta.index[i]
            break
    if not fin:
        fin = serie.index[-1]

    serie_post = serie[fin:]
    if serie_post.empty:
        print(f"No hay datos tras el crecimiento en parcela {cult}")
        continue

    inicio_decrecimiento = serie_post[:30].idxmax()
    valor_max = serie_post[:30].max()

    max_dias_decrecimiento = 60
    fecha_limite = inicio_decrecimiento + pd.Timedelta(days=max_dias_decrecimiento)
    serie_post_limitada = serie_post[:fecha_limite]
    serie_derivada = serie_post_limitada.diff()

    fin_decrecimiento = None
    if not serie_post_limitada.empty and len(serie_post_limitada) > duracion_b:
        for i in range(serie_post_limitada.index.get_loc(inicio_decrecimiento) + 1, len(serie_post_limitada) - duracion_b):
            ventana = serie_derivada.iloc[i:i+duracion_b]
            if (ventana > umbral_decrecimiento).all():
                fin_decrecimiento = serie_post_limitada.index[i]
                break

    if not fin_decrecimiento:
        fin_decrecimiento = serie_post_limitada.index[-1]

    df_c2 = df_i2[[cult]][fecha_inicio:fecha_fin]
    fig, ax = plt.subplots(figsize=(10, 4))
    df_a.plot(ax=ax, label='Serie limpia')
    df_c2.plot(ax=ax, label='Serie original', linestyle='--')
    ax.axvline(inicio, color='r', linestyle='--', label='Inicio crecimiento')
    ax.axvline(fin, color='orange', linestyle='--', label='Fin crecimiento')
    ax.axvline(inicio_decrecimiento, color='green', linestyle='--', label='Inicio decrecimiento')
    ax.axvline(fin_decrecimiento, color='purple', linestyle='--', label='Fin decrecimiento')
    ax.set_title(f"Ciclo {var_n}: parcela {cult} ({type_c})")
    ax.legend()
    # plt.tight_layout()
    # if "2da_siembra" in pth.basename(csv_f):
    #     any_s += "2dasiembra"
    any_s_tag = any_s
    if "2da_siembra" in pth.basename(csv_f):
        any_s_tag += "2dasiembra"
    plt.savefig(pth.join(out_fold, f"parcela_{cult}_{any_s_tag}.png"))
    # plt.savefig(pth.join(out_fold, f"parcela_{cult}_{any_s}.png"))
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
        'Valor_max_FAPAR': round(valor_max, 2)
    })

# Guardar resultados
df_out = pd.DataFrame(registros)
if "2da_siembra" in pth.basename(csv_f):
    any_s += "2dasiembra"
# output_csv = pth.join(out_fold, 'ciclo_%s_completo_%s.csv' % (var_n, any_s))
# output_xlsx = pth.join(out_fold, 'ciclo_%s_completo_%s.xlsx' % (var_n, any_s))
output_csv = pth.join(out_fold, 'ciclo_%s_completo_%s.csv' % (var_n, any_s_tag))
output_xlsx = pth.join(out_fold, 'ciclo_%s_completo_%s.xlsx' % (var_n, any_s_tag))
df_out = df_out[['Parcela', 'Cultivo', 'Inicio_crecimiento', 'Fin_decrecimiento']]
df_out.to_csv(output_csv, index=False)
df_out.to_excel(output_xlsx, index=False)
df_fail_list = pd.DataFrame({'Parcela_no_calculada': fail_l})
# fail_list_csv = pth.join(out_fold, 'parcelas_no_calculadas_lista_%s.csv' % any_s)
# fail_list_excel = pth.join(out_fold, 'parcelas_no_calculadas_lista_%s.xlsx' % any_s)
fail_list_csv = pth.join(out_fold, 'parcelas_no_calculadas_lista_%s.csv' % any_s_tag)
fail_list_excel = pth.join(out_fold, 'parcelas_no_calculadas_lista_%s.xlsx' % any_s_tag)
df_fail_list.to_csv(fail_list_csv, index=False)
df_fail_list.to_excel(fail_list_excel, index=False)
print(f"\nCSV guardado: {output_csv}")
print(f"Parcelas no calculadas: {len(fail_l)}")
print("\n ".join(fail_l))
