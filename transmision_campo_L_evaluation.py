from transmision_campo_L import *

mmpx = 4
distance_5mm = 5 * mmpx

image_path = './IMAGENES FORMATO TIFF/Transmision_CampoL/CampoEnL.tif' # 
prueba = TransmisionL(image_path)
# prueba.sup_der_analysis(mmpx)
prueba.bot_der_analysis(220, 230)
