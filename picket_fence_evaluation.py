from picket_fence import *

image_path_PF = './IMAGENES FORMATO TIFF/2Junio/9. PicketFence_Y1.tif' # 
prueba = Picket(image_path_PF)
mensaje = prueba.evaluate_error(tolerance_mm=27, number_of_zones=20)
print(mensaje)