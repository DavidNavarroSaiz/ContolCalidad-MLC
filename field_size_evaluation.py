from alineacion import Alineacion


path_img = './IMAGENES FORMATO TIFF/2Junio/1.Alineacion.tif'
alineacion = Alineacion(path_img)
tolerance_degrees = 2
mensaje = alineacion.field_size(tolerance_degrees)
print(mensaje)