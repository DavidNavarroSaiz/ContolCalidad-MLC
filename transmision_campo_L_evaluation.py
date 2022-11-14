from transmision_campo_L import *
import pandas as pd
import datetime
import os

columns = {
    'Image':[],
    'Valor intensidad':[],
    'Lamina':[],
    'Prueba':[]
            } 
df = pd.DataFrame(columns)

mmpx = 0.283
tolerance_mm = 2

directory = './IMAGENES FORMATO TIFF/Transmision_CampoL/'
for name_img in os.listdir(directory):
    path_img = os.path.join(directory, name_img)    
    # checking if it is a file
    if os.path.isfile(path_img):
        prueba = TransmisionL(path_img, df, name_img)
        df = prueba.sup_der_analysis(mmpx)
        df = prueba.bot_der_analysis(220, 230) 

df.to_csv(f"./csvs/transmision_L_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)
