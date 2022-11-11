from cmath import sqrt
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np

class SheetPosition():

    def __init__(self,path):
        self.img_raw = cv2.imread(path)
        self.img = self.img_raw[:,:,0]
        self.img = self.img_raw[:,:,0]
        self.imgray = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
        self.gray_img = self.imgray
        self.h_imgray, self.w_imgray = self.imgray.shape

    def find_rectangle_contour(self):
        self.imgRoi = self.img[480:542,480:542]
        average = np.average(self.imgRoi, axis=0)
        self.average = np.average(average, axis=0)
        self.min = np.amin(self.imgRoi)
        self.graylevel = (255-self.min)*0.5 + self.min
        self.mask = cv2.inRange(self.img, 0, self.graylevel)
        contours, _ = cv2.findContours(image=self.mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        self.c = contours[0]

    def rectangle_roi(self):
        self.find_rectangle_contour()
        x,y,w,h = cv2.boundingRect(self.c)
        self.img_rectangle = self.imgray[x:(x+w), y:(y+h)]
        self.img_rectangleRGB = self.img_raw[x:(x+w), y:(y+h)]
        # cv2.imshow("thresh",self.img_rectangle)
        # cv2.waitKey()

    def find_white_circle(self):
        self.rectangle_roi()
        _, self.thresh = cv2.threshold(self.img_rectangle, 105, 255, cv2.THRESH_BINARY_INV)
        
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
        self.square_center = int((self.circle_list[0][0]+self.circle_list[1][0])/2)
    def find_gray_levels(self, img):
        min_value = np.amin(img)
        max_value = np.amax(img)
        prom_value = min_value + (max_value - min_value)/2
        return min_value, max_value, prom_value
    def find_black_zones_distances(self, number_of_zones):
        _, max_value, prom_value = self.find_gray_levels(self.gray_img)
        _, self.thresh = cv2.threshold(self.gray_img, prom_value, max_value, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(self.thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
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
        for i in range(number_of_zones):
            # Sub regiones van de arriba a abajo
            sub_region = self.thresh[(y+h_cut*i):(y+h_cut*(i+1)), (x):(x+int(w))]
            contours_sub, _ = cv2.findContours(sub_region, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours_sub:            
                x_sub,y_sub,w_sub,h_sub = cv2.boundingRect(cnt)  # Las variables "x" y "y" son el punto sup izq de la imagen        
                dist_izq_sub = abs(self.square_center- x_sub)
                dist_der_sub = abs(self.square_center - (x_sub+w_sub))
                
            dist_izq_list.append(dist_izq_sub)  
            dist_der_list.append(dist_der_sub)  
            
        return dist_izq_list,dist_der_list
    def draw_line(self):
        # self.img_line = np.stack((self.imgRoi,)*3, axis=-1)
        img2 = np.zeros_like(self.img_rectangleRGB)
        img2[:,:,0] = self.img_rectangle 
        img2[:,:,1] = self.img_rectangle 
        img2[:,:,2] = self.img_rectangle 
        cv2.line(img2, (self.circle_list[0][0], self.circle_list[0][1]), (self.circle_list[1][0], self.circle_list[1][1]), (255,0 , 0), thickness=2)
        cv2.imshow("thresh",img2)
        cv2.waitKey()
        # Hallar distancia a bordes


    