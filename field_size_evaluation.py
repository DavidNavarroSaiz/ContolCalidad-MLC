from field_size import RectangleDimensions
import pandas as pd
import os
import datetime

columns = {'Image':[], 'Diferencia real-teorico [mm]' :[], 'Tipo':[]}
dataframe = pd.DataFrame(columns)

mm_px = 0.283
tolerance_mm = 1

directory = './IMAGENES FORMATO TIFF/FieldSize/10x10'
for name_img in os.listdir(directory):
    path_img = os.path.join(directory, name_img)    
    # checking if it is a file
    if os.path.isfile(path_img):
        prueba = RectangleDimensions(path_img, name_img, dataframe)
        dataframe, message = prueba.evaluate_dimensions(mm_px, 100, 100, tolerance_mm)

    print(message)

dataframe.to_csv(f"./csvs/tamaño_de_campo_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)