''' Se importan librerias necesarias '''
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
''' Creación clase para prueba Picket Fence '''
class Picket():
    '''
    Se cargan las imagenes:
    - img_raw -> imagen original
    - ROI_img -> imagen recortada con la región de interes a ser trabajada
    - gray_img -> imagen recortada pero de un solo canal (blanco o negro)
    Además valores establecidos de:
    - x1_ROI, x2_ROI, y1_ROI, y2_ROI -> Valores para recortar img_raw
    - name_img -> Necesario para creación de tabla con los datos necesarios
    - df -> Dataframe donde se almacena la información
    '''
    def __init__(self, path, dataframe, name_img):
        self.x1_ROI, self.x2_ROI, self.y1_ROI, self.y2_ROI = 20, 1000, 50, 950
        self.name_img = name_img
        self.img_raw = cv2.imread(path)
        self.ROI_img = self.img_raw[self.y1_ROI:self.y2_ROI, self.x1_ROI:self.x2_ROI]
        self.gray_img = cv2.cvtColor(self.ROI_img, cv2.COLOR_BGR2GRAY)  
        self.df = dataframe

    '''
    Se buscan los valores de interes de intensidad 
    para aplicar thresholds respectivos y extraer
    valor mínimo, máximo y promedio
    '''
    def find_gray_levels(self, img):
        min_value = np.amin(img)
        max_value = np.amax(img)
        prom_value = min_value + (max_value - min_value)/2
        return min_value, max_value, prom_value

    '''
    La función mode se encarga de extraer el valor de la 
    moda de una lista de datos
    '''
    def mode(self, dataset):
        frequency = {}
        for value in dataset:
            frequency[value] = frequency.get(value, 0) + 1

        most_frequent = max(frequency.values())
        modes = [key for key, value in frequency.items()
                        if value == most_frequent]
        return modes

    '''
    Se busca en la imagen cada región oscura, asociada a un segmento irradiado
    '''
    def find_black_zones_parameters(self, number_of_zones):
        _, max_value, prom_value = self.find_gray_levels(self.gray_img)
        _, thresh = cv2.threshold(self.gray_img, prom_value, max_value, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        '''
        x_values será una lista la cual contiene listas con dos parametros [X, [Y,Z,...]]
        - X es el valor en x del centro en esta región 
        - Y,Z,... son listas que contienen los valores izquierdo y derecho correspondiente al 50% de opacidad en cada placa o subregión
        '''        
        x_values = []

        for cnt in contours:            
            x,y,w,h = cv2.boundingRect(cnt)  # Las variables "x" y "y" son el punto sup izq de la imagen
            h_cut = int(h / number_of_zones) # Tamaño de cada división
            w_cut = int(w * 0.4)             # Se hace una pequeña separación para la imagen
            x_list_center = []               # Lista con el valor d ela gaussiana en cada subregión
            x_list_borders = []              # Lista de valores correspondientes a Y,Z,...

            # Se divide cada region en placas ó subregiones, para obtener mayor precisión en las medidas
            for i in range(number_of_zones):
                # Sub regiones van de arriba a abajo
                sub_region = self.gray_img[int(y+h_cut*i+h_cut*0.4):int(y+h_cut*(i+1)-h_cut*0.4), (x-w_cut):(x+w+w_cut)]
                sub_region_copy = sub_region.copy()
                _, max_value_line, prom_value_line = self.find_gray_levels(sub_region)

                # Puntos de interes
                x_borders = [] # Lista con los valores izquierda y derecha, donde la opacidad es del 50%
                x_center = 0   # Valor donde se encontrará el valor medio de x

                # Region que cumple con opacidad del 50% para encontrar valor izquierdo y derecho
                _, thresh_prom = cv2.threshold(sub_region, prom_value_line, max_value_line, cv2.THRESH_BINARY_INV)
                contours_prom, _ = cv2.findContours(thresh_prom, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                x_prom,_,w_prom,_ = cv2.boundingRect(contours_prom[0])
                x_prom_izq = x_prom + (x-w_cut) + self.x1_ROI           # Misma logica que para x_center
                x_prom_der = x_prom + w_prom + (x-w_cut) + self.x1_ROI  # Misma logica que para x_center
                x_center = x_prom + int(w_prom/2) + (x-w_cut) + self.x1_ROI  
                x_borders.append(x_prom_izq) 
                x_borders.append(x_prom_der) 
                x_list_borders.append(x_borders)
                x_list_center.append(x_center)

            x_center = 0
            x_center = self.mode(x_list_center)
            x_values.append([x_center[0], x_list_borders])            
        return x_values

    '''
    Se evalua la diferencia entre el valor de la gaussiana de cada región
    con el valor de distancia hacia la izquierda y derecha de cada segmento
    - tolerance_mm -> Tolerancia en milimetros
    - number_of_zones -> Cantidad de placas o subregiones en cada región 
    '''
    def evaluate_error(self, tolerance_mm, number_of_zones, mmpx):
        print("Tolerance [mm] =", tolerance_mm) 

        x_values = self.find_black_zones_parameters(number_of_zones)
        x_values = sorted(x_values, key=lambda val : val[0])
        error = 0

        cnt_region = 1
        for x_list in x_values:
            cnt_lamina = 1
            x_center = x_list[0]
            x_borders = x_list[1]
            for border in x_borders:
                distance_1 = abs(x_center-border[0])
                distance_2 = abs(x_center-border[1])
                ''' Lógica para evaluar distancias tanto izquierda como derechas, además de que
                debe cumplir con que la suma de las desviaciones de las distancias no debe ser
                mayor a la tolerancia '''
                if (abs(5-distance_1*mmpx) > tolerance_mm) or (abs(5-distance_2*mmpx) > tolerance_mm) or ((abs(5-distance_1*mmpx)+abs(5-distance_2*mmpx)) > tolerance_mm):
                    error = 1
                    # Para Y1 (de lámina 0 a 20)
                    new_row = {'Image':self.name_img, 'Center value [mm]':(round(x_center*mmpx, 4)), 'Left edge distance [mm]':(round(distance_1*mmpx, 3)), 'Right edge distance [mm]':(round(distance_2*mmpx, 3)), 'Lamina':str(number_of_zones-cnt_lamina+1)+"_0"+str(cnt_region), 'Result':'No pasa'}
                    # Para Y2 (de lámina 21 a 40)
                    # new_row = {'Image':self.name_img, 'Center value [mm]':(round(x_center*mmpx, 4)), 'Left edge distance [mm]':(round(distance_1*mmpx, 3)), 'Right edge distance [mm]':(round(distance_2*mmpx, 3)), 'Lamina':str(number_of_zones*2-cnt_lamina+1)+"_0"+str(cnt_region), 'Result':'No pasa'}
                else:
                    # Para Y1
                    new_row = {'Image':self.name_img, 'Center value [mm]':(round(x_center*mmpx, 4)), 'Left edge distance [mm]':(round(distance_1*mmpx, 3)), 'Right edge distance [mm]':(round(distance_2*mmpx, 3)), 'Lamina':str(number_of_zones-cnt_lamina+1)+"_0"+str(cnt_region), 'Result':'Pasa'}
                    # Para Y2
                    # new_row = {'Image':self.name_img, 'Center value [mm]':(round(x_center*mmpx, 4)), 'Left edge distance [mm]':(round(distance_1*mmpx, 3)), 'Right edge distance [mm]':(round(distance_2*mmpx, 3)), 'Lamina':str(number_of_zones*2-cnt_lamina+1)+"_0"+str(cnt_region), 'Result':'Pasa'}
                self.df = self.df.append(new_row, ignore_index=True)
                cnt_lamina += 1
            cnt_region += 1

        if error == 1:
            mensaje = "Fallo de posicionamiento de las laminas por Picket Fence."
        else:
            mensaje = "Posicionamiento correcto."

        return mensaje, self.df 

'''
CODIGOS PARA PRUEBAS

cv2.rectangle(self.gray_img, (x,y), (x+w,y+h), (0,255,0),2)
cv2.imshow("self.gray_img",self.gray_img)
cv2.waitKey()

# cv2.imshow("final difference",sub_region)
# cv2.imshow("thresh_min",thresh_min)
# cv2.imshow("thresh_prom",thresh_prom)
# cv2.waitKey()
'''