from picket_fence import *
import pandas as pd
import datetime
import os

columns = {
    'Image':[],
    'Gaussian value [mm]' :[],
    'Left edge distance [mm]':[],
    'Right edge distance [mm]':[],
    'Tolerance [mm]':[]
            }
df = pd.DataFrame(columns)

mmpx = 0.283
tolerance_mm = 6

directory = './IMAGENES FORMATO TIFF/Picket Fence/images/'
for name_img in os.listdir(directory):
    path_img = os.path.join(directory, name_img)    
    # checking if it is a file
    if os.path.isfile(path_img):
        prueba = Picket(path_img, df, name_img)
        mensaje, df = prueba.evaluate_error(tolerance_mm=tolerance_mm, number_of_zones=20, mmpx=mmpx)

df.to_csv(f"./csvs/datos_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)