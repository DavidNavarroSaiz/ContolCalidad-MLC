from repeatability import CompareImages
import matplotlib.pyplot as plt
import numpy as np
import cv2
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

class RectangleDimensions():   
    '''
    Se cargan las imagenes:
    - img_raw -> imagen original
    - img -> imagen de un solo canal (blanco y negro)
    Además valores establecidos de:
    - name_img -> Necesario para creación de tabla con los datos necesarios
    - df_x -> Dataframes donde se almacena la información
    '''
    def __init__(self, path_img, name_img, dataframe):
        self.name_img = name_img
        self.img_raw = cv2.imread(path_img)
        self.imgRoi = self.img_raw[20:1004,20:1004]
        self.img = cv2.cvtColor(self.imgRoi, cv2.COLOR_BGR2GRAY)  
        self.dataframe = dataframe

    def find_min_level(self):
        min_value = np.amin(self.img)
        max_value = np.amax(self.img)
        prom_value = min_value + (max_value - min_value)/2
        # print(min_value, prom_value, max_value)
        return min_value, prom_value, max_value

    def find_contour(self):
        min_value, prom_value, max_value = self.find_min_level()
        _, mask = cv2.threshold(self.img, prom_value-(max_value-prom_value)/3, max_value, cv2.THRESH_BINARY_INV)
        contour, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.imshow("final sadsa",mask)
        # cv2.waitKey()
        # cv2.destroyAllWindows()

        return contour
    
    def evaluate_dimensions(self, mm_px_h, mm_px_w, w_size, h_size, tolerance_mm):
        contour = self.find_contour()
        x,y,w,h = cv2.boundingRect(contour[0])
        # print(x,y,w,h)

        self.w_mm = w*mm_px_w
        self.h_mm = h*mm_px_h
        # print(f"width {self.w_mm} mm")
        # print(f"height {self.h_mm} mm")
        # print("w, h", w*mm_px, h*mm_px)
        # cv2.rectangle(self.img, (x, y), (x + w, y + h), (0,0,255), 1)
        # cv2.imshow("final difference",self.img)
        # cv2.waitKey()
        # cv2.destroyAllWindows()

        error = 0
        diff_w, diff_h = self.h_mm-h_size, self.w_mm-w_size

        if (abs(diff_w) > tolerance_mm):
            error = 1
            new_row_w = {'Image':self.name_img, 'Diferencia real-teorico [mm]':(round(diff_w, 4)), "Tipo":"Ancho", 'Tolerancia [mm]':tolerance_mm, 'Resultado':"No pasa"}
        elif (abs(diff_w) < tolerance_mm):
            new_row_w = {'Image':self.name_img, 'Diferencia real-teorico [mm]':(round(diff_w, 4)), "Tipo":"Ancho", 'Tolerancia [mm]':tolerance_mm, 'Resultado':"Pasa"}

        if (abs(diff_h) > tolerance_mm):
            error = 1
            new_row_h = {'Image':self.name_img, 'Diferencia real-teorico [mm]':(round(diff_h, 4)), "Tipo":"Alto", 'Tolerancia [mm]':tolerance_mm, 'Resultado':"No pasa"}
        elif (abs(diff_h) < tolerance_mm):
            new_row_h = {'Image':self.name_img, 'Diferencia real-teorico [mm]':(round(diff_h, 4)), "Tipo":"Alto", 'Tolerancia [mm]':tolerance_mm, 'Resultado':"Pasa"}

        # Se crean las filas para el dataframe con informacion importante.
        self.dataframe = self.dataframe.append(new_row_w, ignore_index=True)
        self.dataframe = self.dataframe.append(new_row_h, ignore_index=True)

        if error == 0:
            message = f"La prueba cumple los parámetros de evauación. W={self.w_mm}, H={self.h_mm}"
        else:
            message = "La prueba excede la tolerancia. \n Compruebe que el campo irradiado coincida con la referencia seleccionada, realice la prueba nuevamente; en caso de persistir el error, ejecute la prueba con el método de película radiocrómica."

        return self.dataframe, message
