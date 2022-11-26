from spoke import Spoke
import pandas as pd
import datetime
import os

columns = {
    'Image':[],
    'Distance [mm]':[],
    'Distance to:':[],
    'Resultado':[],
    'Tolerancia':[]
            }
df = pd.DataFrame(columns)

mmpx = 0.283
tolerance_mm = 1

directory = './IMAGENES FORMATO TIFF/SpotShot/'
for name_img in os.listdir(directory):
    path_img = os.path.join(directory, name_img)    
    # checking if it is a file
    if os.path.isfile(path_img) and path_img.endswith('.tif'):
        prueba = Spoke(path_img, df, name_img)
        white_circle_coordinates = prueba.find_white_circle(97, 200)      # centro del circulo blanco
        coordinates_list, angles, couples = prueba.find_regions(230, 255) # coordenadas de las lineas oscuras
        intersection_points = prueba.find_intersection(couples)           # puntos de intersección de lineas oscuras
        
        mensaje, df = prueba.evaluate_error(white_circle_coordinates, intersection_points, tolerance_mm, mmpx)
        # print(mensaje)

df.to_csv(f"./csvs/spoke_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)