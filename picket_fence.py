''' Se importan librerias necesarias '''
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np
import pandas as pd

''' Creación clase para prueba Picket Fence '''
class Picket():
    '''
    Se cargan las imagenes:
    - img_raw -> imagen original 
    - ROI_img -> imagen recortada con la región de interes a ser trabajada
    - gray_img -> imagen recortada pero de un solo canal (blanco y negro)
    '''
    def __init__(self, path, dataframe, name_img):
        self.name_img = name_img
        self.img_raw = cv2.imread(path)
        self.ROI_img = self.img_raw[50:950, 20:1000]
        self.gray_img = cv2.cvtColor(self.ROI_img, cv2.COLOR_BGR2GRAY)  
        self.df = dataframe

    '''
    Se buscan los valores de interes para aplicar thesholds
    '''
    def find_gray_levels(self, img):
        min_value = np.amin(img)
        max_value = np.amax(img)
        prom_value = min_value + (max_value - min_value)/2
        return min_value, max_value, prom_value

    '''
    Se busca en la imagen cada región de interes correspondiente a cada distribución
    '''
    def find_black_zones_parameters(self, number_of_zones):
        _, max_value, prom_value = self.find_gray_levels(self.gray_img)
        _, thresh = cv2.threshold(self.gray_img, prom_value, max_value, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        '''
        x_values será una lista la cual contiene listas con dos parametros [X, [Y,Z,...]]
        - X es el valor en x de la gaussiana en esta región 
        - Y,Z,... son listas que contienen los valores izquierdo y derecho correspondiente al 50% de opacidad en cada placa o subregión
        '''        
        x_values = []

        for cnt in contours:            
            x,y,w,h = cv2.boundingRect(cnt)  # Las variables "x" y "y" son el punto sup izq de la imagen
            # cv2.rectangle(self.gray_img, (x,y), (x+w,y+h), (0,255,0),2)
            # cv2.imshow("self.gray_img",self.gray_img)
            # cv2.waitKey()
            h_cut = int(h / number_of_zones) # Tamaño de cada división
            w_cut = int(w * 0.4)             # Se hace una pequeña separación para la imagen
            x_list_gauss = []                # Lista con el valor d ela gaussiana en cada subregión
            x_list_borders = []              # Lista de valores correspondientes a Y,Z,...

            # Se divide cada region en placas ó subregiones, para obtener mayor precisión en las medidas
            for i in range(number_of_zones):
                # Sub regiones van de arriba a abajo
                sub_region = self.gray_img[(y+h_cut*i):(y+h_cut*(i+1)), (x-w_cut):(x+w+w_cut)]
                min_value_line, max_value_line, prom_value_line = self.find_gray_levels(sub_region)
                
                # Punto mas oscuro de esta region (Gaussiana)
                _, thresh_min = cv2.threshold(sub_region, min_value_line, max_value_line, cv2.THRESH_BINARY_INV)
                contours_min, _ = cv2.findContours(thresh_min, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                x_borders = [] # Lista con los valores izquierda y derecha, donde la opacidad es del 50%
                x_gauss = 0    # Valor donde se encontrará la gaussiana de la subregión
                area = 0                 

                # Se busca que el contorno que se encuentre sea el mas significativo y que no es ruido
                for cnt in contours_min:
                    area_min = cv2.contourArea(cnt)
                    if area_min > area:
                        x_min,_,w_min,_ = cv2.boundingRect(cnt)
                        x_gauss = x_min + (w_min/2) + (x-w_cut) # Formado por x_min (valor sup izq dentro de subregion), (w_min/2) el ancho de la subregion y (x-w_cut) para englobar en img_raw
                x_list_gauss.append(x_gauss)

                # Region que cumple con opacidad del 50% para encontrar valor izquierdo y derecho
                _, thresh_prom = cv2.threshold(sub_region, prom_value_line, max_value_line, cv2.THRESH_BINARY_INV)
                contours_prom, _ = cv2.findContours(thresh_prom, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                x_prom,_,w_prom,_ = cv2.boundingRect(contours_prom[0])
                x_prom_izq = x_prom + (x-w_cut)           # Misma logica que para x_gauss
                x_prom_der = x_prom + w_prom + (x-w_cut)  # Misma logica que para x_gauss
                x_borders.append(x_prom_izq)    
                x_borders.append(x_prom_der)   
                x_list_borders.append(x_borders)

                # cv2.imshow("final difference",sub_region)
                # cv2.imshow("thresh_min",thresh_min)
                # cv2.imshow("thresh_prom",thresh_prom)
                # cv2.waitKey()
                # contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  

            # De la lista de gaussianas de cada región se saca el promedio de estas
            x_gauss = 0
            for x in x_list_gauss:
                x_gauss += x
            x_gauss = int(x_gauss/len(x_list_gauss))

            x_values.append([x_gauss, x_list_borders])            
        return x_values
        

    '''
    Se evalua la diferencia entre el valor de la gaussiana de cada región
    con el valor izquierdo y derecho de esta con opacidad del 50%
    - tolerance_mm -> Tolerancia en milimetros
    - number_of_zones -> Cantidad de placas o subregiones en cada región 
    '''
    def evaluate_error(self, tolerance_mm, number_of_zones, mmpx):
        print("Tolerance [mm] =", tolerance_mm) 

        x_values = self.find_black_zones_parameters(number_of_zones)
        error = 0

        for x_list in x_values:
            x_gauss = x_list[0]
            x_borders = x_list[1]
            # print(f"Gaussian val = {round(x_gauss*mmpx, 4)}")
            for border in x_borders:
                distance_1 = abs(x_gauss-border[0])
                distance_2 = abs(x_gauss-border[1])
                # print(f"Distancia izq = {round(distance_1*mmpx, 3)}, der = {round(distance_2*mmpx, 3)}")
                new_row = {'Image':self.name_img, 'Gaussian value [mm]':(round(x_gauss*mmpx, 4)), 'Left edge distance [mm]':(round(distance_1*mmpx, 3)), 'Right edge distance [mm]':(round(distance_2*mmpx, 3)), 'Tolerance [mm]':tolerance_mm}
                self.df = self.df.append(new_row, ignore_index=True)
                if (distance_1*mmpx > tolerance_mm) or (distance_2*mmpx > tolerance_mm):
                    error = 1

        if error == 1:
            mensaje = "Fallo de posicionamiento de las laminas por Picket Fence."
        else:
            mensaje = "Posicionamiento correcto."

        return mensaje, self.df
