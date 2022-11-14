from repeatability import CompareImages
import matplotlib.pyplot as plt
import numpy as np
import cv2

class RectangleDimensions():   
    def __init__(self, path_img, name_img, dataframe):
        self.img_raw = cv2.imread(path_img)
        self.name_img = name_img
        self.dataframe = dataframe
        self.img = self.img_raw[:,:,0]
        self.imgRoi = self.img[480:542,480:542]

    def find_min_level(self):
        average = np.average(self.imgRoi, axis=0)
        self.average = np.average(average, axis=0)
        self.min = np.amin(self.imgRoi)
        self.graylevel = (255-self.min)*0.5 + self.min

    def find_contour(self):
        self.mask = cv2.inRange(self.img, 0, self.graylevel)
        contours, _ = cv2.findContours(image=self.mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        self.c = contours[1]
    
    def evaluate_dimensions(self, mm_px, w_size, h_size, tolerance_mm):
        self.find_min_level()
        self.find_contour()
        x,y,w,h = cv2.boundingRect(self.c)

        self.w_mm = w*mm_px
        self.h_mm = h*mm_px
        # print(f"width {self.w_mm} mm")
        # print(f"height {self.h_mm} mm")
        # cv2.rectangle(self.img_raw, (x, y), (x + w, y + h), (0,0,255), 1)
        # cv2.imshow("final difference",self.img_raw)
        # cv2.waitKey()
        # cv2.destroyAllWindows()

        error = 0
        diff_w, diff_h = h_size-self.h_mm, w_size-self.w_mm
        # Se crean las filas para el dataframe con informacion importante.
        new_row_w = {'Image':self.name_img, 'Diferencia real-teorico [mm]':(round(diff_w, 4)), "Tipo":"Ancho"}
        new_row_h = {'Image':self.name_img, 'Diferencia real-teorico [mm]':(round(diff_h, 4)), "Tipo":"Alto"}
        self.dataframe = self.dataframe.append(new_row_w, ignore_index=True)
        self.dataframe = self.dataframe.append(new_row_h, ignore_index=True)

        if (abs(diff_w) > tolerance_mm) or (abs(diff_h) > tolerance_mm):
            error = 1

        if error == 0:
            message = f"La prueba cumple los parámetros de evauación. W={self.w_mm}, H={self.h_mm}"
        else:
            message = "La prueba excede la tolerancia. \n Compruebe que el campo irradiado coincida con la referencia seleccionada, realice la prueba nuevamente; en caso de persistir el error, ejecute la prueba con el método de película radiocrómica."

        return self.dataframe, message
