import pandas as pd
import os
import datetime
from backup_diaphragm import BackupDiaphragm


mmpx = 0.2536
tolerance = 1
distance = 51
ancho_teorico = 102
tolerancia_ancho = 2
columns = {
    'Image':[],
    'X1[mm]':[], 
    'X2[mm]':[],
    'ancho campo irradiado[mm]':[],            }
df = pd.DataFrame(columns)

directory = './IMAGENES FORMATO TIFF/BackupDiafragma/backup_2'
for name_img in os.listdir(directory): 
    path_img = os.path.join(directory, name_img)    
    if os.path.isfile(path_img):
        backup = BackupDiaphragm(path_img,df,name_img)
        df,mensaje = backup.calculate_distance(distance,tolerance,ancho_teorico,tolerancia_ancho,mmpx)
        backup.generar_pdf("backup_diaphragm",tolerance)
        print('resultado image',name_img,' :', mensaje)
df.to_csv(f"./csvs/backup_diaphragm_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)
