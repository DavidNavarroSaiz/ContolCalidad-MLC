<<<<<<< HEAD
hacer
=======
from sheet_position import SheetPosition

sheet = SheetPosition('./IMAGENES FORMATO TIFF/PrecisionPosicionHoja/good/10x10.tif')
sheet.find_white_circle()  
izq,der = sheet.find_black_zones_distances(20)                    
print(izq)
print(der)
>>>>>>> 9dead0b2a6ba92a1ea1ef97e1a3fa9bc3ff8c2e2
