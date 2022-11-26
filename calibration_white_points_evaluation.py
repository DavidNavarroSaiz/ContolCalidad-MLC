from calibration_white_points import *

image_path = './IMAGENES FORMATO TIFF/Calibracion/15X15.tif'

calibration = Calibration(image_path)
relation_mmpx = calibration.relation_mmpx(150, 150)

print(relation_mmpx)

## Relación mm/px = 0.283