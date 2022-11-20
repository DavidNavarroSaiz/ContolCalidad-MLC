from sheet_position import SheetPosition
import pandas as pd
import os
import datetime



mmpx = 0.283
numer_of_sheets = 20
tolerance = 6
distance = 56
columns = {
    'Image':[]
            }

for i in range(numer_of_sheets):
    columns["dist_izq_"+str(i+1)]=  0
    columns["dist_der_"+str(i+1)]= 0

df = pd.DataFrame(columns)
# print(columns)
directory = './IMAGENES FORMATO TIFF/PrecisionPosicionHoja/good/'
for name_img in os.listdir(directory):
    path_img = os.path.join(directory, name_img)    
    if os.path.isfile(path_img):
        sheet = SheetPosition(path_img,df,name_img)
        sheet.find_white_circle()  
        df,mensaje = sheet.evaluate_sheets(mmpx,numer_of_sheets,distance,tolerance)                    
        print('resultado image',name_img,' :', mensaje)
df.to_csv(f"./csvs/sheet_position_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)
