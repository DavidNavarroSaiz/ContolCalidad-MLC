from spoke import Spoke


image_path = './IMAGENES FORMATO TIFF/SpotShot/SpotShot.tif'
prueba = Spoke(image_path)

white_circle_coordinates = prueba.find_white_circle(97, 200)      # centro del circulo blanco

coordinates_list, angles, couples = prueba.find_regions(230, 255) # coordenadas de las lineas oscuras
intersection_points = prueba.find_intersection(couples)           # puntos de intersección de lineas oscuras

mensaje = prueba.evaluate_error(white_circle_coordinates, intersection_points, 3)
print(mensaje)

prueba.find_white_circle(97, 200)