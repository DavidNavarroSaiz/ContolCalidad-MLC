import matplotlib.pyplot as plt
import cv2
import numpy as np
class Alineacion():

    def __init__(self,path):
        self.img_raw = cv2.imread(path)
        self.img = self.img_raw[:,:,0]

    def find_min_level(self,imgRoi):

        min = np.amin(imgRoi)
        graylevel = (255-min)*0.5 + min
        return graylevel

    def find_height(self,img,x,y,w,h):
        imgRoi = img[y:y+h, x:x+w]
        min_level = self.find_min_level(imgRoi)
        mask = cv2.inRange(imgRoi, 0, min_level)
        contours, _ = cv2.findContours(image=mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        c = contours[1]
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(mask, (x, y), (x + w, y + h), (0,0,255), 1)
        cv2.imshow("final difference",mask)
        cv2.waitKey()
        return h
    def find_alignment(self):
        self.height11 = self.find_height(self.img,150,150,20,130)
        self.height12 = self.find_height(self.img,520,150,20,130)
        self.height21 = self.find_height(self.img,485,750,20,130)
        self.height22 = self.find_height(self.img,836,750,20,130)


    def evaluate_error(self,mm_px,tolerance_mm):
        self.find_alignment()
        print( tolerance_mm) 
        if (abs(self.height11 - self.height12)*mm_px > tolerance_mm) or (abs(self.height21 - self.height22)*mm_px  > tolerance_mm):
            mensaje = "Fallo de alineación. Compruebe inclinacion del gantry y EPID."
        else:
            mensaje = "Alineacion correcta."

        return mensaje



