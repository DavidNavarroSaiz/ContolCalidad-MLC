from gantry import AlineacionYCuadratura
import pandas as pd
import os
import datetime

columns_alineacion = {'Image':[], 'Diferencia ancho [mm]' :[], 'Lamina':[], 'Resultado':[]}
columns_diferencia_angulos = {'Image':[], 'Diferencia angulos [grados]' :[], 'Resultado':[]}
columns_cuadratura = {'Image':[], 'Diferencia angulos [grados]' :[], 'Lamina':[], 'Resultado':[]}
df_alineacion = pd.DataFrame(columns_alineacion)
df_diferencia_angulos = pd.DataFrame(columns_diferencia_angulos)
df_cuadratura = pd.DataFrame(columns_cuadratura)

mm_px = 0.283
tolerance_mm, tolerance_grados = 2, 5

directory = './Recursos/Alineacion/' 
for name_img in os.listdir(directory):
    path_img = os.path.join(directory, name_img)    
    # checking if it is a file
    if os.path.isfile(path_img) and path_img.endswith('.tif'):
        prueba = AlineacionYCuadratura(path_img, name_img, df_alineacion, df_diferencia_angulos, df_cuadratura)
        df_alineacion, msj_alineacion = prueba.alineacion(mm_px,tolerance_mm)
        df_diferencia_angulos, msj_diff_ang = prueba.comparacion_angulos(tolerance_grados)
        df_cuadratura, msj_cuadratura = prueba.cuadratura(tolerance_grados)

    print(msj_alineacion, '\n', msj_diff_ang, '\n', msj_cuadratura)

df_alineacion.to_csv(f"./csvs/gantry_alineacion_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)
df_diferencia_angulos.to_csv(f"./csvs/gantry_diferencia_angulos_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)
df_cuadratura.to_csv(f"./csvs/gantry_cuadratura_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)