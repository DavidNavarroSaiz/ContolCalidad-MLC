import pandas as pd
import os
import datetime
from backup_diaphragm import BackupDiaphragm


mmpx = 0.283
numer_of_sheets = 20 
tolerance = 6
distance = 55
columns = {
    'Image':[],
    'distancia izquierda[mm]':[],
    'distancia derecha[mm]':[],
    'suma[mm]':[],            }
df = pd.DataFrame(columns)

directory = './IMAGENES FORMATO TIFF/BackupDiafragma/Campo 10x10/good'
for name_img in os.listdir(directory): 
    path_img = os.path.join(directory, name_img)    
    if os.path.isfile(path_img):
        backup = BackupDiaphragm(path_img,df,name_img)
        df,mensaje = backup.calculate_distance(distance,tolerance,mmpx)
        print('resultado image',name_img,' :', mensaje)
df.to_csv(f"./csvs/backup_diaphragm_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)
