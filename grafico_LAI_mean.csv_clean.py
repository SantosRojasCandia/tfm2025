import pandas as pd
import matplotlib.pyplot as plt
import os
import os.path as pth

# Parámetros
var_n = "FAPAR"
any_s = "2024_2da_siembra"

csv_f = r'D:\TFM 2025\Lleida\out_csv\%s\clean\prod_lleida_%s_%s_mean.csv_clean.csv' % (var_n, any_s, var_n)
out_dir = pth.join(pth.dirname(csv_f), "graficas_parcelas")
os.makedirs(out_dir, exist_ok=True)

# Cargar datos
df = pd.read_csv(csv_f, index_col=0, parse_dates=True)

# Generar gráficos
for parcela in df.columns:
    serie = df[parcela]
    plt.figure(figsize=(10, 4))
    plt.plot(serie.index, serie.values, label=f'Parcela {parcela}', color='green')
    plt.title(f'Serie temporal de FAPAR - Parcela {parcela}')
    plt.xlabel('Fecha')
    plt.ylabel('FAPAR')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(pth.join(out_dir, f"FAPAR_{any_s}_parcela_{parcela}.png"))
    plt.close()

print(f"Gráficos guardados en: {out_dir}")
