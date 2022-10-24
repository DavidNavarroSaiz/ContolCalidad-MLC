from picket_fence import *


image_path = './IMAGENES FORMATO TIFF/2Junio/9. PicketFence_Y1.tif' # 
prueba = Picket(image_path)
# min_value, max_value, prom_value = prueba.find_gray_levels(prueba.gray_img)
# prueba.find_black_zones_parameters()
mensaje = prueba.evaluate_error(26)
print(mensaje)