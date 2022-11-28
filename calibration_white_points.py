from cmath import sqrt
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
class Calibration():
    def __init__(self,path):
        self.img_raw = cv2.imread(path)
        self.gray_img = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
        self.ROI_img = cv2.cvtColor(self.img_raw[150:950,150:950], cv2.COLOR_BGR2GRAY)

    def find_gray_levels(self):
        min_value = np.amin(self.ROI_img)
        max_value = np.amax(self.ROI_img)
        prom_value = min_value + (max_value - min_value)/2
        return min_value, max_value, prom_value

    def find_contour(self):
        min_value, max_value, prom_value = self.find_gray_levels()
        # print(min_value, max_value, prom_value)
        mask = cv2.inRange(self.ROI_img, int((max_value+prom_value)/2), int(max_value))
        cv2.imshow("img",mask)
        cv2.waitKey()
        contours, _ = cv2.findContours(image=mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

        coordinate_list = [] # [cx, cy, w, h]
        for cnt in contours:
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])        
            _,_,w,h = cv2.boundingRect(cnt)

            try:
                coordinate_list.append([cx, cy, w, h])
            except NameError:
                print("No se encontraron regiones de interes")          

        return coordinate_list

    def cal_distances(self):
        coordinate_list = self.find_contour()

        h_list, w_list = [], []
        for coordinate_1 in coordinate_list:
            for coordinate_2 in coordinate_list:
                x_diff = abs(coordinate_1[0] - coordinate_2[0])
                y_diff = abs(coordinate_1[1] - coordinate_2[1])
                if (coordinate_1 != coordinate_2) and (x_diff<10):
                    h_list.append(y_diff)
                elif (coordinate_1 != coordinate_2) and (y_diff < 10):
                    w_list.append(x_diff)

        h_prom = 0
        for h in h_list:
            h_prom += h
        h_prom = h_prom/len(h_list)

        w_prom = 0
        for w in w_list:
            w_prom += w
        w_prom = w_prom/len(w_list)

        return h_prom, w_prom

    def relation_mmpx(self, width_mm, height_mm):
        h_px, w_px = self.cal_distances()        
        relation_mmpx_h = height_mm / h_px
        relation_mmpx_w = width_mm / w_px

        mmpx = (relation_mmpx_h + relation_mmpx_w) / 2
        # print(f"Relation = h, w = {relation_mmpx_h, relation_mmpx_w} mm/px")
        # print(f"Relation = {mmpx} mm/px")

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
