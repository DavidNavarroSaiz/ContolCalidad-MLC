from cmath import sqrt
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
class CalibrationField():
    def __init__(self,path):
        self.img_raw = cv2.imread(path)
        self.gray_img = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
        self.ROI_img = cv2.cvtColor(self.img_raw[150:950,150:950], cv2.COLOR_BGR2GRAY)
        self.imgRoi = self.gray_img[380:542,380:542]

    def find_min_level(self):
        average = np.average(self.imgRoi, axis=0)
        self.average = np.average(average, axis=0)
        self.min = np.amin(self.imgRoi)
        self.graylevel = (255-self.min)*0.5 + self.min
    def find_gray_levels(self, img):
        min_value = np.amin(img)
        max_value = np.amax(img)
        prom_value = min_value + (max_value - min_value)/2
        return min_value, max_value, prom_value
    def find_contour(self):
        _, max_value, prom_value = self.find_gray_levels(self.gray_img)
        _, self.mask = cv2.threshold(self.gray_img, prom_value, max_value, cv2.THRESH_BINARY_INV)
        # contours, _ = cv2.findContours(self.thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # self.mask = cv2.inRange( self.gray_img, self.graylevel, 255)
        # cv2.imshow("d",self.mask)
        # cv2.waitKey()
        contours, _ = cv2.findContours(image=self.mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        self.c = contours[0]



    def cal_distances(self):
        self.find_min_level()
        self.find_contour()
        x,y,w,h = cv2.boundingRect(self.c)
        cv2.drawContours(self.img_raw, self.c, -1, (0, 0, 255), 1) # dibujar punto blanco encontrado
        # cv2.imshow("self.img_raw",self.img_raw)
        # cv2.waitKey()
        return w, h

    def relation_mmpx(self, width_mm, height_mm):
        w_px,h_px,  = self.cal_distances()
        relation_mmpx_h = height_mm / h_px
        relation_mmpx_w = width_mm / w_px

        mmpx = (relation_mmpx_h + relation_mmpx_w) / 2


        return mmpx

'''
                        AYUDAS

cv2.circle(img, (px, py), thinkness, (255,255,255), -1)

cv2.imshow("name_window", img)
cv2.waitKey()

cv2.drawContours(img, contours, -1, (0,255,0), 3)

hist = cv2.calcHist([region], [0], None, [256], [0, 256])
plt.plot(hist, color='gray' )
plt.xlabel('Intensidad de pixel')
plt.ylabel('Cantidad de pixeles')
plt.show()

'''
