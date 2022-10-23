from spoke import Spoke


image_path = './IMAGENES FORMATO TIFF/2Junio/14.SpokeShot.tif' # 
prueba = Spoke(image_path)
coordinates_list, angles, couples = prueba.find_regions(0.2, 0.8, 0.2, 0.8, 230, 255)
intersection_points = prueba.find_intersection(couples)
mensaje = prueba.evaluate_error(intersection_points, 3)
print(mensaje)
