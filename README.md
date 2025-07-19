# TFM - Estimación de la producción agrícola por evapotranspiración mediante teledetección

Este repositorio contiene los scripts desarrollados para el Trabajo de Fin de Máster (TFM) titulado:

**“Estimación de la producción agrícola de cultivos extensivos, a nivel de parcela, utilizando teledetección por evapotranspiración”**

El objetivo principal fue estimar el rendimiento agrícola a partir de la evapotranspiración acumulada (ETa), integrando datos satelitales, información climática y datos de producción real en parcelas de la provincia de Lleida.

---

## 📂 Estructura del repositorio

### 🔧 Scripts principales

- `estandarizar_datos_produccion.py`  
  Script para estandarizar los datos de producción (pasando a kg/ha si es necesario) y calcular estadísticas básicas como promedio, desviación estándar, y conteos por cultivo y año.

- `estadisticas_graficos_prod.py`  
  Genera estadísticas descriptivas y gráficos (histogramas, boxplots, etc.) a partir de los datos de producción reales obtenidos en campo.

- `union_shp_xlsx.py`  
  Une los datos tabulares (Excel o CSV) de producción y características de cultivo con archivos vectoriales (shapefiles), generando un archivo geoespacial con todos los atributos combinados.

- `grafico_LAI_mean.csv_clean.py`  
  Script para graficar la evolución temporal de variables biofísicas como LAI o FAPAR en diferentes campañas agrícolas, permitiendo comparar comportamientos anuales por cultivo o parcela.

- `fechas_de_corte_personalizadas_diccionario.py`  
  Detecta automáticamente fechas clave del ciclo de cultivo (inicio y fin del crecimiento vegetativo) usando umbrales personalizados sobre series de tiempo de LAI o FAPAR.

---

## 📊 Datos utilizados

Los scripts trabajan con:

- Datos satelitales (Copernicus: LAI, FAPAR, ETa)
- Archivos shapefile con geometría de parcelas agrícolas
- Archivos Excel/CSV con datos de producción real por parcela y campaña
- Información climática complementaria (precipitación, tipo de riego)

---

## 🧰 Requisitos

Todos los scripts están escritos en **Python 3.x** y utilizan las siguientes librerías:

- `pandas`, `numpy`, `matplotlib`, `seaborn`
- `geopandas`, `rasterstats`, `xarray`
- `shapely`, `datetime`, `scipy`

Podés instalar las dependencias con:

```bash
pip install -r requirements.txt
