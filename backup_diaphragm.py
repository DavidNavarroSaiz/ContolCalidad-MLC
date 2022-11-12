from cmath import sqrt
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np
import pandas as pd

class BackupDiaphragm():
    def __init__(self,path,df,name_img):
        self.img_raw = cv2.imread(path)
        self.img = self.img_raw[:,:,0]
        self.imgray = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
        self.gray_img = self.imgray
        self.h_imgray, self.w_imgray = self.imgray.shape
        self.name_img = name_img
        self.df = df
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

        
        _, self.thresh = cv2.threshold(self.img_rectangle, 103, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(self.thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # self.circle_list = []
        for c in contours:
            a = cv2.contourArea(c)
            p = cv2.arcLength(c,True)
            ci = p**2/(4*np.pi*a)
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            if ci < 1.2:
                M = cv2.moments(c)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                # self.circle_list.append((cX,cY))
                self.white_center = (cX,cY)
                # cv2.drawContours(self.img_rectangleRGB, c, -1, (0, 255, 0), 3)
                # cv2.imshow("image",self.img_rectangleRGB)
                # cv2.waitKey()
                # print("cX,cY",cX,cY)

    def calculate_distance(self,mm_px):
        # dist_izq_sub = round(abs(self.white_center[0]- self.x_rectangle)*mm_px,2)
        # dist_der_sub = round(abs(self.white_center[0] - (self.x_rectangle+self.w_rectangle))*mm_px,2)
        self.find_white_circle()

        contours_mask, _ = cv2.findContours(image=self.img_mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        x_rectangle_mask,y_rectangle_mask,w_rectangle_mask,h_rectangle_mask = cv2.boundingRect(contours_mask[0])

        dist_izq = round(abs(self.white_center[0]- x_rectangle_mask)*mm_px,2)
        dist_der = round(abs(self.white_center[0] - (x_rectangle_mask+w_rectangle_mask))*mm_px,2)
        new_row = {'Image':self.name_img, 'distancia izquierda[mm]':dist_izq, 'distancia derecha[mm]':dist_der, 'suma[mm]':(dist_izq+dist_der)}
        self.df = self.df.append(new_row, ignore_index=True)
        return self.df