from gantry import AlineacionYCuadratura


<<<<<<< HEAD
mm_px = 0.283
=======
mm_px = 0.2506
>>>>>>> 9dead0b2a6ba92a1ea1ef97e1a3fa9bc3ff8c2e2


path_img = './IMAGENES FORMATO TIFF/2Junio/1.Alineacion.tif'
gantry = AlineacionYCuadratura(path_img)
tolerance_mm = 2
<<<<<<< HEAD

=======
>>>>>>> 9dead0b2a6ba92a1ea1ef97e1a3fa9bc3ff8c2e2
gantry.alineacion(mm_px,tolerance_mm)
gantry.cuadratura(mm_px,tolerance_mm)