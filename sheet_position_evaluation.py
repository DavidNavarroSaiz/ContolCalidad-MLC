from sheet_position import SheetPosition

sheet = SheetPosition('./IMAGENES FORMATO TIFF/PrecisionPosicionHoja/good/10x10.tif')
sheet.find_white_circle()  
izq,der = sheet.find_black_zones_distances(20)                    
print(izq)
print(der)
