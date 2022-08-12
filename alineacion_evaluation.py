from alineacion import Alineacion


path_img = './IMAGENES FORMATO TIFF/2Junio/1.Alineacion.tif'
alineacion = Alineacion(path_img)
mm_px = 0.2506
tolerance_mm = 2
mensaje = alineacion.evaluate_error(mm_px,tolerance_mm)
print(mensaje)
  