from itertools import count
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

    def find_white_zones(self):
        imgray = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
        w_img, h_img = imgray.shape
        imgray = imgray[int(h_img*0.12) : int(h_img*0.88), int(w_img*0.12) : int(w_img*0.88)]
        _, thresh = cv2.threshold(imgray, 200, 255, 0)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        white_zones = []
        for cnt in contours:
            # Las variables "x" y "y" son el centro del contorno
            x,y,w,h = cv2.boundingRect(cnt)
            coordinates = [[int((w*0.2)+x+int(w_img*0.12)), int(y+(h/2)+int(h_img*0.12))], [int((w*0.8)+x+int(w_img*0.12)), int(y+(h/2)+int(h_img*0.12))]]
            white_zones.append(coordinates)        
            # cv2.rectangle(self.img_raw, coordinates[0], coordinates[1], (255, 0, 0), 4)

        # cv2.drawContours(thresh, contours, -1, (0,255,0), 3)
        # cv2.imshow("final difference",self.img_raw)
        # cv2.imshow("final Thresh",thresh)
        # cv2.waitKey()

        return white_zones

    def find_height(self,img,x,y,w,h):
        # Las variables "x" y "y" son el punto superior izquierdo
        imgRoi = img[y:y+h, x:x+w]
        min_level = self.find_min_level(imgRoi)
        mask = cv2.inRange(imgRoi, 0, min_level)
        contours, _ = cv2.findContours(image=mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        c = contours[1]
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(mask, (x, y), (x + w, y + h), (0,0,255), 1)
        # cv2.imshow("final difference",mask)
        # cv2.waitKey()
        return h

    def find_alignment(self):
        white_zones = self.find_white_zones()
        w, h = 20, 130

        diff_heights = []
        for zone in white_zones:
            x1, y1, x2, y2 = int(zone[0][0]-w/2), int(zone[0][1]-h/2), int(zone[1][0]-w/2), int(zone[1][1]-h/2)
            height_1 = self.find_height(self.img,x1,y1,w,h)
            height_2 = self.find_height(self.img,x2,y2,w,h)
            diff = abs(height_1 - height_2)
            diff_heights.append(diff)

        return diff_heights


    def evaluate_error(self,mm_px, tolerance_mm):
        diff_heights = self.find_alignment()
        print("Tolerance [mm] =", tolerance_mm) 

        error = 0
        for i in diff_heights:
            if i*mm_px > tolerance_mm:
                error = 1

        if error == 1:
            mensaje = "Fallo de alineación. Compruebe inclinacion del gantry y EPID."
        else:
            mensaje = "Alineacion correcta."

        return mensaje



