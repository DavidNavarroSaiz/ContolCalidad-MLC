from picket_fence import *
import pandas as pd
import datetime
import os

# EVALUACION PRUEBA PICKET FENCE

# Creación de dataframe para almacenar la información
columns = {
    'Image':[],
    'Center value [mm]' :[],
    'Left edge distance [mm]':[],
    'Right edge distance [mm]':[],
    'Lamina':[],
    'Result':[]
            }
df = pd.DataFrame(columns)

# Definición de constantes
mmpx = 0.253
tolerance_mm = 2

# Se hace evaluación de todas las imagenes en una carpeta
directory = './Recursos/2_PruebaPicketFence/PF Modificado/'
for name_img in os.listdir(directory):
    path_img = os.path.join(directory, name_img)    
    # checking if it is a file
    if os.path.isfile(path_img) and path_img.endswith('.tif'):
        prueba = Picket(path_img, df, name_img)
        mensaje, df = prueba.evaluate_error(tolerance_mm=tolerance_mm, number_of_zones=20, mmpx=mmpx)
        prueba.generar_pdf("PicketFence",tolerance_mm) 

print("Finished.")
# Creación de csv con la información extraida por la prueba
df.to_csv(f"./csvs/picket_fence_Y2_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)