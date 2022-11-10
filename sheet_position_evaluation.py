from sheet_position import SheetPosition

sheet = SheetPosition('./IMAGENES FORMATO TIFF/PrecisionPosicionHoja/good/10x10.tif')
sheet.find_white_circle()
sheet.draw_line()