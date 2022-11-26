from field_size import RectangleDimensions
import pandas as pd
import os
import datetime

columns = {'Image':[], 'Diferencia real-teorico [mm]' :[], 'Tipo':[], 'Tolerancia [mm]':[], 'Resultado':[]}
dataframe = pd.DataFrame(columns)

# mm_px = 0.283
# Para 10x10
# mm_px_h = 0.253
# mm_px_w = 0.253
# Para 20x20
# mm_px_h = 0.253
# mm_px_w = 0.253
# Para 24x24
mm_px_h = 0.253
mm_px_w = 0.253
tolerance_mm = 2

directory = './IMAGENES FORMATO TIFF/Copia_field_size/24X24/'
for name_img in os.listdir(directory):
    path_img = os.path.join(directory, name_img)
    # checking if it is a file
    if os.path.isfile(path_img) and path_img.endswith('.tif'):
        prueba = RectangleDimensions(path_img, name_img, dataframe)
        dataframe, message = prueba.evaluate_dimensions(mm_px_h, mm_px_w, 240, 240, tolerance_mm)

    # print(message)
print("Finished.")

dataframe.to_csv(f"./csvs/tamaño_de_campo_24x24_{datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')}.csv", mode='a', index=False, header=True)