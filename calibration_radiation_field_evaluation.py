from calibration_radiation_field import *

image_path = './IMAGENES FORMATO TIFF/Calibracion/15X15.tif'

calibration = CalibrationField(image_path)
relation_mmpx = calibration.relation_mmpx(200, 200)

print(relation_mmpx)

## Relación mm/px = 0.283