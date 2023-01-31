from repeatability import CompareImages
import matplotlib.pyplot as plt
import numpy as np
import cv2
from reporte import PDF2
import datetime
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
            self.resultado = "Pasa."
            self.mensaje = f"La prueba cumple los parámetros de evauación. W={self.w_mm}, H={self.h_mm}"
            message = f"La prueba cumple los parámetros de evauación. W={self.w_mm}, H={self.h_mm}"
        else:
            self.resultado = "No pasa."
            self.mensaje = "Compruebe que el campo irradiado coincida con la referencia seleccionada."
            message = "La prueba excede la tolerancia. \n Compruebe que el campo irradiado coincida con la referencia seleccionada, realice la prueba nuevamente; en caso de persistir el error, ejecute la prueba con el método de película radiocrómica."

        return self.dataframe, message
    
    def generar_pdf(self, nombre_prueba, tolerancia):
        pdf = PDF2()
        pdf.add_page()

        initial = 80
        n_line = 10
        pdf.set_font("Times", size=8)
        pdf.set_margins(10, 60, -1)
        pdf.set_auto_page_break(True, margin = 40)
        pdf.set_xy(160, initial)
        pdf.set_font('arial', '', 10)
        pdf.cell(60, 10, "Fecha: "+datetime.datetime.now().strftime('%m-%d-%y %Hh:%Mm'), 0, 0, 'L')

        pdf.set_font('arial', 'B', 14)
        pdf.set_xy(30, initial)
        pdf.cell(60, 10, "Responsable: ", 0, 0, 'L')

        pdf.set_font('arial', 'B', 16)
        pdf.set_xy(70, initial+n_line*2)
        pdf.cell(75, 10, "Reporte "+nombre_prueba, 0, 1, 'L')
        pdf.set_font('arial', 'B', 16)
        pdf.set_xy(10, initial+n_line*3)
        pdf.cell(40, 10, "Imagen: "+self.name_img, 0, 0, 'L')
        pdf.set_font('arial', '', 14)
        pdf.set_xy(10, initial+n_line*4)
        pdf.cell(40, 10, "Tolerancia: "+str(tolerancia)+ 'mm', 0, 0, 'L')

        pdf.set_xy(10, initial+n_line*5)
        pdf.cell(40, 10, "Resultado: "+self.resultado, 0, 0, 'L')
        pdf.set_xy(10, initial+n_line*6)
        pdf.cell(40, 10, "Mensaje: "+str(self.mensaje), 0, 0, 'L')

        nombre_prueba = './reportes/' + nombre_prueba+self.name_img + datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')+'.pdf'
        pdf.output(nombre_prueba)
