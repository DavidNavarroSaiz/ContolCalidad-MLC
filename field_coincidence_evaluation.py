from field_coincidence import FieldCoincidence
import pandas as pd
import os
import datetime


mmpx = 0.283
tolerance = 1
distance = 100
columns = {
    'Image':[]
            }

            


df = pd.DataFrame(columns)
# print(columns)
directory = './IMAGENES FORMATO TIFF/Coincidencia_tam_campo/buenas'
for name_img in os.listdir(directory):
    path_img = os.path.join(directory, name_img)    
    if os.path.isfile(path_img):
        field = FieldCoincidence(path_img,df,name_img)
        field.find_white_circle()  
        df,mensaje = field.evaluate_square_dimensions(distance,tolerance,mmpx)                    
        print('resultado image',name_img,' :', mensaje)
df.to_csv(f"./csvs/field_coincidence_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)
