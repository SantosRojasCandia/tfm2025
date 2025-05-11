# -*- coding: utf-8 -*-
"""
Script que t'extreu els valors d'un raster a partir d'una capa vectorial, per una serie temporal.
Et retorna la mitjana diaria, la suma diaia i l'acumulat anual de la suma diaria.

És necessari una llista d'arxius nc/tiff on cada arxiu representa un dia i un arxiu vectorial (shp/geojson) amb els polígons

Et retorna tres arxius csv per cada variable (pots triar quina vols):
 - 'mean' => mitjan diaria del poligon
 - 'sum_daily' => suma diaria de totes les cel·les que estan dins del polígon
 - 'sum' => acumulat anual de la suma diaria de totes les cel·les que estan dins del polígon

#TODO FER QUE ACUTOMÀTICAMENT GESTIONI EL TEMA DELS ESTADÍSTICS (CREAR ARXIU CSV EN FUNCIÓ DELS ESTADÍSTICS TRIATS)

author: magipamies
datetime:7/5/2025 8:44
"""

# Define libaries
import sys
import os
import glob
import os.path as pth
env_name = os.environ['CONDA_DEFAULT_ENV']
os.environ['PROJ_LIB'] = fr'D:\PROGRAMAS\anaconda3\envs\{env_name}\Library\share\proj'
# os.environ['PROJ_LIB'] = r'D:\PROGRAMAS\anaconda3\envs\irta_db_env\Library\share\proj' % os.environ['CONDA_DEFAULT_ENV']
from rasterstats import zonal_stats, point_query
import geopandas as gpd
import pandas as pd
import numpy as np
import re
import time
from datetime import datetime as dt, timedelta
# from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import multiprocessing
import logging
import gc


import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)  # no longer needed

def range_dates(d_ini="20210101", d_fin="20231231"):
    start_date = dt.strptime(d_ini, '%Y%m%d')
    end_date = dt.strptime(d_fin, '%Y%m%d')

    date = start_date
    list_d = []
    while date <= end_date:
        list_d.append(date.strftime('%Y%m%d'))

        date = date + timedelta(days=1)

    return list_d


def list_dates_txt(list_dates):
    """

    :param list_dates: direcció del arxiu txt a on hi ha guardades les dades.
    :type list_dates: str
    :return: llista amb les dates
    :rtype: list
    """

    f = open(list_dates, 'r')
    if f.readlines() == 0:
        sys.exit("No hi ha dates al fitxer")
    f.close()
    f = open(list_dates, 'r')
    dates = f.read().splitlines()

    f.close()
    print("El fitxer txt conté %d dates" % (len(dates)))
    return dates


def list_images(list_files, list_dates, all_dates=True, list_dates_file=None, sort=False):
    """
    Funció que retorna una llista amb totes les imatges que s'han de processar, a partir d'una llista
    de totes les imatges que hi ha a la carpeta.

    :param list[str] list_files: llista d'arxius
    :param list[str] list_dates: llista de les dates
    :param bool all_dates: si ha d'agafar totes les imatges de la carpeta o les ha de seleccionar per data.
    :param str list_dates_file: direcció del arxiu txt a on hi ha guardades les dades.
    :param bool sort: Si volem ordenar la llista
    :return: llista amb totes les imatges que s'han de processar.
    :rtype: list[str]

    """

    list_images = []

    # Li diem que ens faci una llista amb tots els arxius .nc que coincideixen amb les dates
    if all_dates is True:
        list_images = list_files
        print("S'analitzaràn totes les imatges. En total %d imatges" % (len(list_images)))
    # elif list_dates_file is None:
    #     print("No hi ha cap arxiu amb dates")
    #     sys.exit
    else:
        if list_dates_file is not None:
            list_dates = list_dates_txt(list_dates_file)
        if len(list_dates) == 0:
            print("No hi ha imatges per analitzar")
            sys.exit()
        else:
            for x in list_dates:
                for file in list_files:
                    if x in file:
                        list_images.append(file)
                        break
                    else:
                        continue

    # Ordenem les imatges
    if sort:
        list_images.sort()

    print("S'analitzaran %d imatges" % (len(list_images)))
    return list_images


def  extrac_date(image_p):
    # Data pel geojson
    date = ''.join(re.findall(r"(\d{4})(\d{2})(\d{2})", os.path.basename(image_p))[0])
    print(var_name, date)

    # Obtenim les estadístiques
    if s2_folder:
        stats_o = zonal_stats(input_shape, image_p, stats=stats, nodata=np.nan)
    else:
        stats_o = zonal_stats(input_shape, "NETCDF:" + image_p + ":" + var_name, stats=stats)

    # Separem les estadístiques
    stats_sum = [{k: v for k, v in x.items() if k in ['sum']} for x in stats_o]
    stats_mean = [{k: v for k, v in x.items() if k in ['mean']} for x in stats_o]

    # Pel SUM
    if 'sum' in stats:
        stats_sum = [{k: v for k, v in x.items() if k in ['sum']} for x in stats_o]
        # Introduim les dades  a un DataFrame
        df_img_sum = pd.DataFrame(stats_sum, index=geo_df.index)
        # Canviem el nom de la columna
        df_img_sum = df_img_sum.rename(columns={df_img_sum.columns[0]: date})

    # Pel MEAN
    # Introduim les dades  a un DataFrame
    df_img_mean = pd.DataFrame(stats_mean, index=geo_df.index)
    # Canviem el nom de la columna
    df_img_mean = df_img_mean.rename(columns={df_img_mean.columns[0]: date})

    if 'sum' in stats:
        return df_img_mean, df_img_sum
    else:
        return df_img_mean
    # return df_img_mean, df_img_sum


# Main section
if __name__ == "__main__":

    # Carpeta de treball
    work_f = r'/media/hdd2/Satelite_data/ET/Lleida/processed_lleida/processed_lleida_2022/'

    # Carpeta amb les imatges
    # inputs_folder = pth.join(work_f, r'procesament/output_S2')
    # inputs_folder_2 = r'/media/hdd2/Satelite_data/ET/Lleida/Processed_2020_Lleida/procesament/output_S2/'
    inputs_folder = pth.join(work_f, r'ETa_pond')
    inputs_folder_2 = r'/media/hdd2/Satelite_data/ET/Lleida/Processed_2020_Lleida/ETa_pond/'


    # Data is stored in a CSV file
    out_csv_folder = r'/media/hdd15/TEMP/producccions_cat/out_csv/'

    # Si ha de recorrer subcarpetes per trobar les imatges (si volem correr biofísics de S2)
    s2_folder = False

    # Llista variables
    #list_var = ['FVC_LAI']
    # list_var = ['FAPAR', 'LAI', 'FVC_LAI']
    list_var = ["ETa_daily_TSEB_SW"]

    # Nom de la capa
    # var_name = 'ETpot_daily_SW'
    # var_name = 'Kc_SW'

    # shapefile from which data will be extracted
    # input_shape =  r'/media/hdd6/RegAssist/Bellmunt/bellmunt_ae/ccrr_bellmunt_dun2023_vinya.geojson'


    i_s_folder = r'D:\TFM 2025\Lleida\Shp_final_lleida'
    list_i_s_name = ['prod_lleida_2022.shp', 'prod_lleida_2023.shp', 'prod_lleida_2024_2da_siembra.shp',
                     'prod_lleida_2024a.shp']

    name_file1 = 'lleida'

#    input_shape = [pth.join(i_s_folder, x) for x in list_i_s_name][0]

    # for input_shape in [pth.join(i_s_folder, x) for x in list_i_s_name]:
    for in_shape in list_i_s_name:
        input_shape = pth.join(i_s_folder, in_shape)
        # ID de les parce·les. Columna de la capa vectorial que identifica les parcel·les.
        id_shp = r'COD'

        # Nom de l'arxiu csv
        #if name_file1:
        #    name_file = name_file1
        #else:
        #    l_n = pth.basename(input_shape).split('_')
        #    zona = l_n[0] if l_n[0] != 'ccrr' else "_".join(l_n[:2])
        #    cultiu = l_n[-1].split('.')[0]
        #    name_file = "_".join([zona, cultiu])
        name_file = pth.basename(input_shape).split('.')[0]


        # DATES
        # Si volem agafar totes les imatges o unes de concretes.
        all_dates = False

        any_str = name_file.split('_')[2][:4]
        # Data d'inici o final. Si tenim False a "all_dates" i "list_dates_files"
        date_i = "20%s0101" % (str(int(any_str[-2:])-1))
        date_f = "20%s1231" % any_str[-2:]
        # Any per ficar al final del nom de l'arxiu
        any_n = date_i[:4]
        if all_dates: any_n = "ALL"

        # Si volem agar les dates des d'un arxiu txt. Si posem None les agafa del 'date_i' i 'date_f'
        list_dates_file = None
        # list_dates_file = r'/media/hdd2/TEMP/dates.txt'

        # point or poligon extraction
        # if True polygon data is extrated, False for point data (interpolate by bilinear)
        extrac_pol = True

        # Statistics to be used
        # stats=['min', 'max', 'mean', 'count', 'median', 'sum','std','nodata','majority']
        stats = ['sum', 'mean']
        # stats = ['mean']

        # Numero de processadors
        # num_p = 5
        num_p = 10

        # Si volem sobreescriure
        overwrite = False

        # ---------------------------------------------------------------------------------------------

        # Range de dates
        list_dates_r = range_dates(date_i, date_f)

        # Llista de tots els arxius
        # list_files = glob.glob(pth.join(inputs_folder, '*.nc'))
        # if inputs_folder_2: list_files.extend(glob.glob(pth.join(inputs_folder_2, '*.nc')))

        if s2_folder:
            dict_img = {}
            for var_name in list_var:
                list_files = [f for f in glob.glob(inputs_folder + "/**/*[0-9]_" + var_name + ".tif", recursive=True)]
                if inputs_folder_2:
                    list_files_2 = [f for f in glob.glob(inputs_folder_2 + "/**/*[0-9]_" + var_name + ".tif", recursive=True)]
                    list_files.extend(list_files_2)
                list_files.sort()
                dict_img[var_name] = list_images(list_files, list_dates_r, all_dates, list_dates_file, sort=True)
        else:
            # Seleccionem arxius .tiff o .tif del directori
            list_files = glob.glob(pth.join(inputs_folder, '*.nc'))
            if inputs_folder_2:
                list_files_2 = glob.glob(pth.join(inputs_folder_2, '*.nc'))
                list_files.extend(list_files_2)
            # Li diem que ens faci una llista amb tots els arxius que coincideixen amb les dates
            list_img = list_images(list_files, list_dates_r, all_dates, list_dates_file, sort=True)

        # Li diem que ens faci una llista amb tots els arxius que coincideixen amb les dates
        # list_img = list_images(list_files, list_dates_r, all_dates, list_dates_file, sort=True)

        # Itinerem per cada variable
        var_name = list_var[0]
        for var_name in list_var:
            if s2_folder:
                list_img = dict_img[var_name]
            print(var_name)

            # Obrim el fitxer vectorial com un GeoDataFrame (amb Geopandas)
            geo_df = gpd.read_file(input_shape, engine='pyogrio', ignore_geometry=True, columns=[id_shp])
            geo_df = geo_df.set_index(geo_df.columns[0])

            # GUARDEM LES DADES
            out_csv_mean = pth.join(out_csv_folder, var_name, '_'.join([name_file, var_name,'mean.csv']))
            if var_name == 'FVC_LAI':
                out_csv_mean = pth.join(out_csv_folder, 'FVC', '_'.join([name_file, 'FVC', 'mean.csv']))

            out_var_fold = pth.dirname(out_csv_mean)
            os.makedirs(out_var_fold, exist_ok=True)
            #
            # if 'mean' in stats:
            #    out_csv_mean = pth.join(out_csv_folder, name_file + '_' + var_name + '_mean.csv')
            if 'sum' in stats:
                out_csv_sum_daily = pth.join(out_csv_folder, var_name, '_'.join([name_file, var_name, 'sum_daily.csv']))
                # out_csv_sum = pth.join(out_csv_folder, var_name, '_'.join([name_file, var_name,'sum.csv']))
            if var_name == 'FVC_LAI':
                stats.pop('sum')

            # if pth.isfile(out_csv_mean) and pth.isfile(out_csv_sum) and pth.isfile(out_csv_sum_daily) and overwrite is False:
            #     print("NO NECESSARI--->%s ja estava creat" % pth.basename(out_csv_mean))
            #     continue
            if pth.isfile(out_csv_mean) and overwrite is False:
                print("NO NECESSARI--->%s ja estava creat" % pth.basename(out_csv_mean))
                continue

            # extract_val(var_name_list[0])
            start2 = time.time()

            # Activem peqruè ens informi dels multiprocessos
            multiprocessing.log_to_stderr()
            logger = multiprocessing.get_logger()
            logger.setLevel(logging.INFO)

            # Multiprocessing
            if (not num_p) or (num_p > (cpu_count() - 1)):
                num_p = cpu_count() - 1

            with Pool(num_p) as p:
                print(f'starting computations on {num_p} cores')
                # p = Pool(cpu_count()-1)
                list_df = p.map(extrac_date, list_img)
                # Netegem el pool
                p.close()
                p.join()

            # print(list_df)

            if 'sum' in stats:
                pd_mean_list = [x[0] for x in list_df]  # Llista dates ETpot
                pd_sum_list = [x[1] for x in list_df]  # Llista d'array ETpot
            else:
                pd_mean_list = list_df

            df_out_mean = pd.concat(pd_mean_list, axis=1)
            df_out_mean.sort_index(axis=1, inplace=True)

            if 'sum' in stats:
                df_out_sum = pd.concat(pd_sum_list, axis=1)
                df_out_sum.sort_index(axis=1, inplace=True)

                # GUARDEM LES DADES
                # Transposem el DataFrame (els index cap a columnes i els noms de les columnes cap a index)
                df_out_sum = df_out_sum.transpose()
                df_out_sum.sort_index(inplace=True)
                # Guardem el DataFrame a un arxiu CSV
                df_out_sum.to_csv(out_csv_sum_daily)
                # ACUMULAT DELS TOTALS DIARIS
                # Guardem el DataFrame a un arxiu CSV
                # df_out_sum = df_out_sum.cumsum()
                # df_out_sum.to_csv(out_csv_sum)

            # Transposem el DataFrame (els index cap a columnes i els noms de les columnes cap a index)
            df_out_mean = df_out_mean.transpose()
            df_out_mean.sort_index(inplace=True)
            # Guardem el DataFrame a un arxiu CSV
            df_out_mean.to_csv(out_csv_mean)

            print(u"--- TEMPS TOTAL %s ---" % timedelta(seconds=int(time.time() - start2)))
            print('final')
            gc.collect()
