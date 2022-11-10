from gantry import AlineacionYCuadratura


mm_px = 0.2506


path_img = './IMAGENES FORMATO TIFF/2Junio/1.Alineacion.tif'
gantry = AlineacionYCuadratura(path_img)
tolerance_mm = 2
gantry.alineacion(mm_px,tolerance_mm)
gantry.cuadratura(mm_px,tolerance_mm)