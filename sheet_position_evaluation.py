from sheet_position import SheetPosition
import pandas as pd
import os
import datetime



columns = {
    'Image':[]
            }

df = pd.DataFrame(columns)
# print(columns) 
directory = './IMAGENES FORMATO TIFF/PrecisionPosicionHoja/10X10'
field_size = directory[-2::]
# mmpx = 0.253
mmpx = 0.1854 
tolerance = 1
if field_size == '10':
    numer_of_sheets = 10
    distance = 50
else:
    numer_of_sheets = 20
    distance = 100

for name_img in os.listdir(directory):
    path_img = os.path.join(directory, name_img)    
    if os.path.isfile(path_img):
        sheet = SheetPosition(path_img,df,name_img,field_size)
        sheet.find_white_circle()  
        df,mensaje = sheet.evaluate_sheets(mmpx,numer_of_sheets,distance,tolerance)                    
        print('resultado image',name_img,' :', mensaje)
df.to_csv(f"./csvs/sheet_position_{field_size}x{field_size}_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)
