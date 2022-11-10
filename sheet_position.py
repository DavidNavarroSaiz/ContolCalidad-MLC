from cmath import sqrt
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np

class SheetPosition():

    def __init__(self,path):
        self.img_raw = cv2.imread(path)
        self.img = self.img_raw[:,:,0]
        self.imgray = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
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
    def draw_line(self):
        # self.img_line = np.stack((self.imgRoi,)*3, axis=-1)
        img2 = np.zeros_like(self.img_rectangleRGB)
        img2[:,:,0] = self.img_rectangle 
        img2[:,:,1] = self.img_rectangle 
        img2[:,:,2] = self.img_rectangle 
        cv2.line(img2, (self.circle_list[0][0], self.circle_list[0][1]), (self.circle_list[1][0], self.circle_list[1][1]), (255,0 , 0), thickness=2)
        cv2.imshow("thresh",img2)
        cv2.waitKey()