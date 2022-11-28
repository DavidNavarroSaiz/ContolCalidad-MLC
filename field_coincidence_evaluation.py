from field_coincidence import FieldCoincidence
import pandas as pd    
import os
import datetime
import cv2

mmpx = 0.253 
mmpx = 0.2536
tolerance_white_points = 5
distance_white_points = 100
tolerance_edge = 1
distance_edge = 10


columns = {
    'Image':[]
            } 

            
df = pd.DataFrame(columns)
directory = './IMAGENES FORMATO TIFF/coincidencia_campo/coincidencia_campo_radiacion/'
for name_img in os.listdir(directory):
    path_img = os.path.join(directory, name_img)    
    if os.path.isfile(path_img):
        print(path_img)
        
        field = FieldCoincidence(path_img,df,name_img)
        field.find_white_circle()  
        df,mensaje = field.evaluate_square_dimensions(distance_white_points,tolerance_white_points,distance_edge,tolerance_edge,mmpx)                    
        print('resultado image',name_img,' :', mensaje)
df.to_csv(f"./csvs/field_coincidence_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)
