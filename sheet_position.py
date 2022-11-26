from cmath import sqrt
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
class SheetPosition():

    def __init__(self,path,dataframe,name_img,field_size):
        self.img_raw = cv2.imread(path)
        self.img = self.img_raw[:,:,0]
        self.img = self.img_raw[:,:,0]
        self.imgray = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
        self.gray_img = self.imgray
        self.h_imgray, self.w_imgray = self.imgray.shape
        self.df = dataframe
        self.name_img = name_img
        self.new_row = {'Image':self.name_img}
        self.field_size = field_size
        

    def find_rectangle_contour(self):
        self.imgRoi = self.img[480:542,480:542]
        average = np.average(self.imgRoi, axis=0)
        self.average = np.average(average, axis=0)
        self.min = np.amin(self.imgRoi)
        self.graylevel = (255-self.min)*0.5 + self.min
        self.mask = cv2.inRange(self.img, 0, self.graylevel)
        contours, _ = cv2.findContours(image=self.mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        self.c = contours[0]
        self.square_center = 1000
    def rectangle_roi(self):
        self.find_rectangle_contour()
        x,y,w,h = cv2.boundingRect(self.c)
        self.img_rectangle = self.imgray[y:(y+h),x:(x+w) ]
        self.img_rectangleRGB = self.img_raw[y:(y+h),x:(x+w) ]
        # cv2.imshow("thresh",self.img_rectangle)
        # cv2.waitKey()

    def find_white_circle(self):
        self.rectangle_roi()
        _, self.thresh = cv2.threshold(self.img_rectangle, 105, 255, cv2.THRESH_BINARY_INV)
        # cv2.imshow("img",self.thresh)
        # cv2.waitKey()
        contours, _ = cv2.findContours(self.thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        self.circle_list = []
        for c in contours:
            a = cv2.contourArea(c)
            if a != 0:
                p = cv2.arcLength(c,True)
                ci = p**2/(4*np.pi*a)
                font = cv2.FONT_HERSHEY_SIMPLEX
                if ci < 1.2:
                    M = cv2.moments(c)
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    self.circle_list.append((cX,cY))
        if self.circle_list != []:
            self.square_center = int((self.circle_list[0][0]+self.circle_list[1][0])/2)
    def find_gray_levels(self, img):
        min_value = np.amin(img)
        max_value = np.amax(img)
        prom_value = min_value + (max_value - min_value)/2
        return min_value, max_value, prom_value
    def evaluate_sheets(self, mm_px,number_of_zones,distance,tolerance):
        _, max_value, prom_value = self.find_gray_levels(self.gray_img)
        _, self.thresh = cv2.threshold(self.gray_img, prom_value, max_value, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(self.thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        mensaje  =''
        '''
        x_values será una lista la cual contiene listas con dos parametros [X, [Y,Z,...]]
        - X es el valor en x de la gaussiana en esta región 
        - Y,Z,... son listas que contienen los valores izquierdo y derecho correspondiente al 50% de opacidad en cada placa o subregión
        '''        
        x_values = []
        counter = 0
        for cnt in contours:  
            x,y,w,h = cv2.boundingRect(cnt)  # Las variables "x" y "y" son el punto sup izq de la imagen
            # cv2.rectangle(self.gray_img, (x,y), (x+w,y+h), (0,255,0),2)
            # cv2.imshow("self.gray_img",self.gray_img)
            # cv2.waitKey()
            h_cut = int(h / number_of_zones) # Tamaño de cada división
            w_cut = int(w*2)             # Se hace una pequeña separación para la imagen
            dist_izq_list = []                # Lista con el valor d ela gaussiana en cada subregión
            dist_der_list = []              # Lista de valores correspondientes a Y,Z,...
        # Se divide cada region en placas ó subregiones, para obtener mayor precisión en las medidas
        error = False
        if self.field_size == '10':
            lamina_init = 25
            
        elif self.field_size == 'Y1':
            lamina_init = 20
        elif self.field_size == 'Y2':
            lamina_init = 40
        if self.square_center != 0:
            for i in range(0,number_of_zones):
                # Sub regiones van de arriba a abajo
                sub_region = self.thresh[(y+h_cut*i):(y+h_cut*(i+1)), (x):(x+int(w))]
                contours_sub, _ = cv2.findContours(sub_region, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours_sub:            
                    x_sub,y_sub,w_sub,h_sub = cv2.boundingRect(cnt)  # Las variables "x" y "y" son el punto sup izq de la imagen        
                    dist_izq_sub = round(abs(self.square_center- x_sub)*mm_px,2)
                    dist_der_sub = round(abs(self.square_center - (x_sub+w_sub))*mm_px,2)
                    
                
                if  (abs(dist_izq_sub- distance)> tolerance or abs(dist_der_sub- distance)> tolerance):
                    mensaje = "  la lamina", lamina_init," excede la tolerancia, con una distancia izquierda: ",dist_izq_sub,"derecha:",dist_der_sub," \n Si la posición de las laminas esta perceptiblemente equivocada comuniquese con el servicio de mantenimiento.\n En caso contrario, compruebe el posicionamiento de las fiducias, realice la prueba nuevamente. " 
                    error = True
                else:
                    mensaje = "\n La posicion de la hoja es precisa, la prueba cumple los parámetros de evauación \n"
            
                self.new_row["distance_izq"]= distance- dist_izq_sub
                self.new_row["distance_der"]= distance-dist_der_sub
                self.new_row["lamina"]= lamina_init
                self.new_row["error"]= error
                df_new_row = pd.DataFrame([self.new_row])

                self.df = pd.concat([self.df, df_new_row])
                lamina_init -= 1
        else : 
            mensaje = "Fallo encontrando puntos blancos"
        
            self.new_row["distance_izq"]= "error"
            self.new_row["distance_der"]= "error"
            self.new_row["lamina"]= lamina_init
            self.new_row["error"]= "error encontrando puntos blancos"
            df_new_row = pd.DataFrame([self.new_row])

            self.df = pd.concat([self.df, df_new_row])
            lamina_init -= 1
        return self.df,mensaje
    def draw_line(self):
        # self.img_line = np.stack((self.imgRoi,)*3, axis=-1)
        img2 = np.zeros_like(self.img_rectangleRGB)
        img2[:,:,0] = self.img_rectangle 
        img2[:,:,1] = self.img_rectangle 
        img2[:,:,2] = self.img_rectangle 
        cv2.line(img2, (self.circle_list[0][0], self.circle_list[0][1]), (self.circle_list[1][0], self.circle_list[1][1]), (255,0 , 0), thickness=2)



    