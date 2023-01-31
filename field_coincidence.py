from cmath import sqrt
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from reporte import PDF2
import datetime
class FieldCoincidence():
    """
    Esta clase se utiliza para tal cosa
    
    """
    def __init__(self,path,dataframe,name_img):
        self.img_raw = cv2.imread(path) 
        self.img = self.img_raw[:,:,0] 
        self.img = self.img_raw[:,:,0]
        self.imgray = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
        self.gray_img = self.imgray
        self.h_imgray, self.w_imgray = self.imgray.shape
        self.df = dataframe
        self.name_img = name_img
        self.new_row = {'Image':self.name_img}

    def find_rectangle_contour(self):

        """
        Definicion del rectangulo de capo de radiacion

        """
        self.imgRoi = self.img[480:542,480:542]
        average = np.average(self.imgRoi, axis=0)
        self.average = np.average(average, axis=0)
        self.min = np.amin(self.imgRoi)
        self.graylevel = (255-self.min)*0.5 + self.min
        self.mask = cv2.inRange(self.img, 0, self.graylevel)
        contours, _ = cv2.findContours(image=self.mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        self.c = contours[0]

    def rectangle_roi(self):
        """
        Segmentacion de campo de radiacion

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
        Encontrar los puntos blancos en la imagen

        """
        self.rectangle_roi() 
        _, self.thresh = cv2.threshold(self.img_rectangle, 103, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(self.thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        self.circle_list = []
        for c in contours:
            a = cv2.contourArea(c)
            p = cv2.arcLength(c,True)

            ci = p**2/(4*np.pi*a)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            if ci < 1.2:
                M = cv2.moments(c)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                self.circle_list.append((cX,cY))
        #         cv2.drawContours(self.img_rectangleRGB, c, -1, (0, 255, 0), 3) # dibujar punto blanco encontrado
        # cv2.imshow("img_rectangleRGB",self.img_rectangleRGB)        
        # cv2.waitKey()

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

    def evaluate_square_dimensions(self,distance_white_points,tolerance_white_points,distance_edge,tolerance_edge,mm_px):
        
        """
        Evalua distancia entre puntos blancos y evalua distancia de los puntos 
        blancos hasta los bordes mas cercanos.

        """
        self.resultado = "Pasa"
        self.find_white_circle()
        contours_mask, _ = cv2.findContours(image=self.img_mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        x_rectangle_mask,y_rectangle_mask,w_rectangle_mask,h_rectangle_mask = cv2.boundingRect(contours_mask[0])
        min_sum = 10000
        max_sum = 0
        A,B,C,D = 0,0,0,0
        for i in self.circle_list:  
            suma = i[0] + i[1]
            if suma > max_sum:
                max_sum = suma
            if suma < min_sum :
                min_sum = suma
        umbral_sup= max_sum*0.8
        umbral_inf= min_sum*1.2
        for item in self.circle_list:
            if item[0] + item[1] > umbral_sup:
                D = item
            elif item[0] + item[1] < umbral_inf:
                A = item
            else:
                if item[0] > item[1]:
                    B = item
                elif item[0] < item[1]:
                    C = item
        error_2 = 0
        error_1 = 0
        # print(A,B,C,D)
        if(A != 0 and B != 0 and C != 0 and D != 0):
            AC = round(abs(euclidean(A[1],C[1]))*mm_px,2)
            BD = round(abs(euclidean(B[1],D[1]))*mm_px,2)
            AB = round(abs(euclidean(A[0],B[0]))*mm_px,2)
            CD = round(abs(euclidean(C[0],D[0]))*mm_px,2)
            A_X1 = round(abs(euclidean(A[0],x_rectangle_mask))*mm_px,2)
            A_Y1 = round(abs(euclidean(A[1],y_rectangle_mask))*mm_px,2)
            B_X1 = round(abs(euclidean(B[0],w_rectangle_mask))*mm_px,2)
            B_Y1 = round(abs(euclidean(B[1],y_rectangle_mask))*mm_px,2)
            C_X1 = round(abs(euclidean(C[0],x_rectangle_mask))*mm_px,2)
            C_Y1 = round(abs(euclidean(C[1],h_rectangle_mask))*mm_px,2)
            D_X1 = round(abs(euclidean(D[0],w_rectangle_mask))*mm_px,2)
            D_Y1 = round(abs(euclidean(D[1],h_rectangle_mask))*mm_px,2)

            list_white_distances = [AC,BD,AB,CD]
            list_edge_distances= [A_X1,A_Y1,B_X1,B_Y1,C_X1,C_Y1,D_X1,D_Y1]
            # cv2.drawContours(self.img_rectangleRGB, contours_mask, -1, (0, 255, 0), 3)
            # cv2.imshow("list_white_distances",self.img_rectangleRGB)
            # cv2.waitKey()

            for dist_white in list_white_distances:
                if abs(dist_white - distance_white_points)> tolerance_white_points:
                    error_1 = 1
            for dist_edge in list_edge_distances:
                if abs(dist_edge - distance_edge)> tolerance_edge:
                    error_2 = 1 


            if error_2 == 1:
                mensaje = "\n  La dimensión del campo luminoso no es concordante, revise la posición de las fiducias y repita la prueba \n Si el error persiste, ejecute la prueba con el método de hoja milimetrada para verificar la dimensión del campo luminoso.  \n En caso de una apertura de campo luminoso equivocada, comuniquelo al servicio de mantenimiento para corregir la falla. \n " 
                self.mensaje = "La dimensión del campo luminoso no es concordante"
                self.resultado = "No pasa"
            elif error_1 == 1:
                mensaje = "El campo de radiación no coincide con el esperado. Revise que se halla seleccionado e iradiado el campo 12x12. Adquiera una nueva imagen con el campo 12x12."
                self.mensaje = "El campo de radiación no coincide con el esperado."
                self.resultado = "No pasa"
            else:
                mensaje = "\n La prueba cumple los parámetros de evaluación. \n"
                self.mensaje = "La prueba cumple los parámetros de evaluación. "

            new_row = {'Image':self.name_img, 'A-C[mm]':distance_white_points-AC, 'B-D[mm]':distance_white_points- BD,
            'A-B[mm]':distance_white_points-AB,'C-D[mm]':distance_white_points-CD,'A-X1[mm]':distance_edge-A_X1,
            'A-Y1[mm]':distance_edge-A_Y1, 'B-X1[mm]':distance_edge-B_X1,'B_Y1[mm]':distance_edge-B_Y1,'C-X1[mm]':distance_edge-C_X1,
            'C-Y1[mm]':distance_edge-C_Y1, 'D-X1[mm]':distance_edge-D_X1,'D_Y1[mm]':distance_edge-D_Y1,'Error campo de radiacion':error_1,'Error distacia bordes':error_2}
            self.df = self.df.append(new_row, ignore_index=True)
        else:
            mensaje = "Error encontrando los puntos blanco"
            self.mensaje = "Error encontrando los puntos blanco"
            error = True
            new_row = {'Image':self.name_img, 'A-C[mm]':"error", 'B-D[mm]':"error",
            'A-B[mm]':"error",'C-D[mm]':"error",'A-X1[mm]':"error",
            'A-Y1[mm]':"error", 'B-X1[mm]':"error",'B_Y1[mm]':"error",'C-X1[mm]':"error",
            'C-Y1[mm]':"error", 'D-X1[mm]':"error",'D_Y1[mm]':"error",'Error campo de radiacion':"error encontrando los puntos blancos",'Error distacia bordes':"error encontrando los puntos blancos"}
            self.df = self.df.append(new_row, ignore_index=True)
        print(self.resultado)
        return self.df,mensaje

    