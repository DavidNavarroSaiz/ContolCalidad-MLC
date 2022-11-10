from calibration import *

image_path = './IMAGENES FORMATO TIFF/Calibracion/14X14.tif'

calibration = Calibration(image_path)
relation_mmpx = calibration.relation_mmpx(140, 140)

print(relation_mmpx)

## Relación mm/px = 0.283