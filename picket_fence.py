from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np
class Picket():
    def __init__(self,path):
        self.img_raw = cv2.imread(path)
        self.ROI_img = self.img_raw[50:950, 20:1000]
        self.gray_img = cv2.cvtColor(self.ROI_img, cv2.COLOR_BGR2GRAY)

    def find_gray_levels(self, img):
        min_value = np.amin(img)
        max_value = np.amax(img)
        prom_value = min_value + (max_value - min_value)/2
        return min_value, max_value, prom_value

    def find_black_zones_parameters(self):
        _, max_value, prom_value = self.find_gray_levels(self.gray_img)
        _, thresh = cv2.threshold(self.gray_img, prom_value, max_value, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # x_values será una lista la cual contiene listas con tres parametros
        # El primero es el valor de la gaussiana en cada region oscura
        # El segundo será el x a la izquierda con opacidad de 50%
        # El segundo será el x a la derecha con opacidad de 50%
        x_values = []

        for cnt in contours:
            # Las variables "x" y "y" son el punto sup izq de la imagen
            x,y,w,h = cv2.boundingRect(cnt)
            h_cut = int(h*0.02)
            w_cut = int(w*0.4)

            line_zone = self.gray_img[(y-h_cut):(y+h+h_cut), (x-w_cut):(x+w+w_cut)]
            
            min_value_line, max_value_line, prom_value_line = self.find_gray_levels(line_zone)
            # Punto mas oscuro de esta region
            _, thresh_min = cv2.threshold(line_zone, min_value_line, max_value_line, cv2.THRESH_BINARY_INV)
            contours_min, _ = cv2.findContours(thresh_min, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            x_list = []
            area = 0
            x_gauss = 0
            for c in contours_min:
                area_min = cv2.contourArea(cnt)
                if area_min > area:
                    x_min,_,w_min,_ = cv2.boundingRect(c)
                    x_gauss = x_min + (w_min/2)
            x_list.append(x_gauss)
            # Region que cumple con opacidad del 50%
            _, thresh_prom = cv2.threshold(line_zone, prom_value_line, max_value_line, cv2.THRESH_BINARY_INV)
            contours_prom, _ = cv2.findContours(thresh_prom, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            x_prom,_,w_prom,_ = cv2.boundingRect(contours_prom[0])
            x_prom_izq = x_prom
            x_prom_der = x_prom + w_prom
            x_list.append(x_prom_izq)    
            x_list.append(x_prom_der)   
            x_values.append(x_list)

            cv2.imshow("final difference",line_zone)
            cv2.imshow("final s",thresh_min)
            cv2.imshow("final ss",thresh_prom)
            cv2.waitKey()
            # contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)          
        return x_values
        

    def evaluate_error(self, tolerance_mm):
        print("Tolerance [mm] =", tolerance_mm) 

        x_values = self.find_black_zones_parameters()
        print(x_values)
        error = 0

        for x_list in x_values:
            value_1 = abs(x_list[0]-x_list[1])
            value_2 = abs(x_list[0]-x_list[2])           
            if (value_1 > tolerance_mm) or (value_2 > tolerance_mm):
                print(value_1, value_2)
                error = 1

        if error == 1:
            mensaje = "Fallo de posicionamiento de las laminas por Picket Fence."
        else:
            mensaje = "Posicionamiento correcto."

        return mensaje