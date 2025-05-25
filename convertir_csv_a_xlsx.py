import pandas as pd
import os


def csv_to_xlsx(input_csv_path, output_xlsx_path):
    """
    Convierte un archivo CSV a XLSX (Excel) y guarda en la ruta especificada.

    Args:
        input_csv_path (str): Ruta completa del archivo CSV de entrada.
        output_xlsx_path (str): Ruta completa del archivo XLSX de salida.
    """
    try:
        # Leer el archivo CSV
        df = pd.read_csv(input_csv_path)

        # Crear directorio de salida si no existe
        os.makedirs(os.path.dirname(output_xlsx_path), exist_ok=True)

        # Guardar como XLSX
        df.to_excel(output_xlsx_path, index=False, engine='openpyxl')
        print(f"✅ Conversión exitosa:\n   CSV: {input_csv_path}\n   XLSX: {output_xlsx_path}")

        # Abrir el archivo automáticamente (opcional)
        if os.name == 'nt':  # Solo para Windows
            os.startfile(output_xlsx_path)

    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo CSV en:\n{input_csv_path}")
    except PermissionError:
        print(f"❌ Error de permisos: No se puede escribir en:\n{output_xlsx_path}")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")


# Configuración de rutas (¡ESTAS SON TUS RUTAS!)
input_csv = r"D:\TFM 2025\Lleida\Magi Final\Otros1\agg_cult\agg_BLAT DE MORO.csv"
output_xlsx = r"D:\TFM 2025\Lleida\Magi Final\Otros1\agg_cult\agg_BLAT DE MORO.xlsx"

# Ejecutar la conversión
if __name__ == "__main__":
    csv_to_xlsx(input_csv, output_xlsx)