from cmath import sqrt
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean

class FieldCoincidence():

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
        self.x_rectangle,self.y_rectangle,self.w_rectangle,self.h_rectange = cv2.boundingRect(self.c)
        self.img_rectangle = self.imgray[self.x_rectangle:(self.x_rectangle+self.w_rectangle), self.y_rectangle:(self.y_rectangle+self.h_rectange)]
        self.img_rectangleRGB = self.img_raw[self.x_rectangle:(self.x_rectangle+self.w_rectangle), self.y_rectangle:(self.y_rectangle+self.h_rectange)]
        self.img_mask = self.mask[self.x_rectangle:(self.x_rectangle+self.w_rectangle), self.y_rectangle:(self.y_rectangle+self.h_rectange)]
        

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
    def find_gray_levels(self, img):
        min_value = np.amin(img)
        max_value = np.amax(img)
        prom_value = min_value + (max_value - min_value)/2
        return min_value, max_value, prom_value
    def evaluate_square_dimensions(self,distance,tolerance,mm_px):
        # dist_izq_sub = round(abs(self.white_center[0]- self.x_rectangle)*mm_px,2)
        # dist_der_sub = round(abs(self.white_center[0] - (self.x_rectangle+self.w_rectangle))*mm_px,2)
        self.find_white_circle()

        contours_mask, _ = cv2.findContours(image=self.img_mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        x_rectangle_mask,y_rectangle_mask,w_rectangle_mask,h_rectangle_mask = cv2.boundingRect(contours_mask[0])

        min_sum = 10000
        max_sum = 0
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

           
        X1_distance = round(abs(euclidean(A[1],C[1]))*mm_px,2)
        X2_distance = round(abs(euclidean(B[1],D[1]))*mm_px,2)
        Y1_distance = round(abs(euclidean(A[0],B[0]))*mm_px,2)
        Y2_distance = round(abs(euclidean(C[0],D[0]))*mm_px,2)
        
        if ((X1_distance - distance)> tolerance or (X2_distance - distance)> tolerance or (Y1_distance - distance)> tolerance or (Y2_distance - distance)> tolerance):
            error = 1 

        if error == 1:
            mensaje = "\n  La dimensión del campo luminoso no es concordante, revise la posición de las fiducias y repita la prueba \n Si el error persiste, ejecute la prueba con el método de hoja milimetrada para verificar la dimensión del campo luminoso.  \n En caso de una apertura de campo luminoso equivocada, comuniquelo al servicio de mantenimiento para corregir la falla. \n " 
        else:
            mensaje = "\n La prueba cumple los parámetros de evaluación. \n"

        new_row = {'Image':self.name_img, 'A-C[mm]':X1_distance, 'B-D[mm]':X2_distance, 'A-B[mm]':Y1_distance,'C-D[mm]':Y2_distance}
        self.df = self.df.append(new_row, ignore_index=True)
        return self.df,mensaje

    