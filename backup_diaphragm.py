from cmath import sqrt
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np
import pandas as pd
from reporte import PDF2
import datetime
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
class BackupDiaphragm():
    def __init__(self,path,df,name_img):
        self.img_raw = cv2.imread(path)
        self.img = self.img_raw[:,:,0]
        self.imgray = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
        self.gray_img = self.imgray
        self.h_imgray, self.w_imgray = self.imgray.shape
        self.name_img = name_img
        self.df = df
        self.white_center = (0,0)
    def find_rectangle_contour(self):
        """
        Definicion del rectangulo de campo de radiacion

        """
        self.imgRoi = self.img[480:542,480:542]
        
        average = np.average(self.imgRoi, axis=0)
        self.average = np.average(average, axis=0)
        self.min = np.amin(self.imgRoi)
        self.graylevel = (255-self.min)*0.4 + self.min
        self.mask = cv2.inRange(self.img, 0, self.graylevel)
        
        contours, _ = cv2.findContours(image=self.mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        self.c = contours[0]

    def rectangle_roi(self):
        """
        Segmentacion del rectangulo de campo de radiacion

        """
        self.find_rectangle_contour()
        self.x_rectangle,self.y_rectangle,self.w_rectangle,self.h_rectange = cv2.boundingRect(self.c)
        self.img_rectangle = self.imgray[self.y_rectangle:(self.y_rectangle+self.h_rectange),self.x_rectangle:(self.x_rectangle+self.w_rectangle)]
        self.img_rectangleRGB = self.img_raw[self.y_rectangle:(self.y_rectangle+self.h_rectange),self.x_rectangle:(self.x_rectangle+self.w_rectangle)]
        self.img_mask = self.mask[self.y_rectangle:(self.y_rectangle+self.h_rectange),self.x_rectangle:(self.x_rectangle+self.w_rectangle)]
        # cv2.imshow("img",self.img_mask)
        # cv2.waitKey()
    
    def find_white_circle(self):
        """
        Encuentra punto blanco central

        """
        self.rectangle_roi()
        
        
        _, self.thresh = cv2.threshold(self.img_rectangle, 105, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(self.thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # self.circle_list = []
        for c in contours:
            a = cv2.contourArea(c)
            if a != 0 and a > 20:
                p = cv2.arcLength(c,True)
                ci = p**2/(4*np.pi*a)
                
                font = cv2.FONT_HERSHEY_SIMPLEX
                if ci < 1.22:
                    M = cv2.moments(c)
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    self.white_center = (cX,cY)
                    # cv2.drawContours(self.img_rectangleRGB, c, -1, (0, 255, 0), 3)
                    # cv2.imshow("image",self.img_rectangleRGB)
                    # cv2.waitKey()
                # else :
                    # print("NO CIRCLE")
                    # print(ci)
                # cv2.drawContours(self.img_rectangleRGB, c, -1, (0, 255, 0), 3)
                # cv2.imshow("image",self.img_rectangleRGB)
                # cv2.waitKey()
                # cv2.imshow("img",self.thresh)
                # cv2.waitKey()
                
                # print("cX,cY",cX,cY)
    
        
    def calculate_distance(self,distance,tolerance,ancho_teorico,tolerancia_ancho,mm_px):

        """
        calcula distancia desde el centro hasta los bordes, teniendo en cuenta que el ancho coincida con 
        el ancho teorico

        """
        error = False
        self.find_white_circle()
        self.resultado = 'pasa'
        contours_mask, _ = cv2.findContours(image=self.img_mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        
        
        x_rectangle_mask,y_rectangle_mask,w_rectangle_mask,h_rectangle_mask = cv2.boundingRect(contours_mask[0])
        cv2.drawContours(self.img_rectangleRGB, contours_mask, -1, (0, 255, 0), 3)
        # cv2.imshow("list_white_distances",self.img_rectangleRGB)
        # cv2.waitKey()
        if self.white_center != (0,0):
            dist_izq = round(abs(self.white_center[0]- x_rectangle_mask)*mm_px,2)
            dist_der = round(abs(self.white_center[0] - (x_rectangle_mask+w_rectangle_mask))*mm_px,2)
            
            if ((dist_izq+dist_der)-ancho_teorico < tolerancia_ancho):
                if abs(dist_izq - dist_der)> tolerance :
                    self.mensaje = "El punto blanco no se encuentra centrado " 
                    error = True
                    self.resultado = ' no pasa'
                else:
                    self.mensaje = " Los diafragmas de respaldo estan en la posicion correcta"
                    mensaje = " Los diafragmas de respaldo estan en la posicion correcta.  La prueba cumple los parámetros de evauación.  \n La distancia del diafragma X1 es de:",dist_izq,"y La distancia del diafragma X2 es de :",dist_der
                
                new_row = {'Image':self.name_img, 'X1[mm]':distance - dist_izq, 'X2[mm]':distance - dist_der, 'ancho campo irradiado[mm]':ancho_teorico-(dist_izq+dist_der), 'error':error}
                df_new_row = pd.DataFrame([new_row])

                self.df = pd.concat([self.df, df_new_row])
            else:
                self.mensaje = "Compruebe que el campo irradiado coincida con la referencia seleccionada "
                mensaje = "Compruebe que el campo irradiado coincida con la referencia seleccionada, realice la prueba nuevamente; en caso de persistir el error, ejecute la prueba con el método de película radiocrómica. "
                new_row = {'Image':self.name_img, 'X1[mm]':distance - dist_izq, 'X2[mm]':distance - dist_der, 'ancho campo irradiado[mm]':ancho_teorico-(dist_izq+dist_der), 'error':"compruebe referencia"}
                df_new_row = pd.DataFrame([new_row])

                self.df = pd.concat([self.df, df_new_row])
                self.resultado = ' no pasa'
        else:
            self.mensaje = "Error encontrando el punto blanco"
            error = True
            new_row = {'Image':self.name_img, 'X1[mm]':"-", 'X2[mm]':"-", 'ancho campo irradiado[mm]':"-", 'error':"circulo no encontrado"}
            df_new_row = pd.DataFrame([new_row])

            self.df = pd.concat([self.df, df_new_row])
            self.resultado = ' no pasa'
        return self.df,self.mensaje

    def generar_pdf(self, nombre_prueba, tolerancia):

        initial = 80
        n_line = 10
        pdf = PDF2()
        pdf.add_page()

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
    