from compare_images import CompareImages
import matplotlib.pyplot as plt
import numpy as np
import cv2

class RectangleDimensions():   
    def __init__(self,path):
        self.img_raw = cv2.imread(path)
        self.img = self.img_raw[:,:,0]
        self.imgRoi = self.img[480:542,480:542]

    def find_min_level(self):
        average = np.average(self.imgRoi, axis=0)
        self.average = np.average(average, axis=0)
        self.min = np.amin(self.imgRoi)
        # graylevel = (250-average)*0.2 + average TODO: Preguntar si con average o min
        self.graylevel = (255-self.min)*0.5 + self.min


    def find_contour(self):
        self.mask = cv2.inRange(self.img, 0, self.graylevel)
        contours, _ = cv2.findContours(image=self.mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        self.c = contours[1]
    
    def evaluate_dimensions(self,mm_px):
        #  self.mm_px = 0.2631
        x,y,w,h = cv2.boundingRect(self.c)
        # print(w)
        cv2.rectangle(self.img_raw, (x, y), (x + w, y + h), (0,0,255), 1)
        
        self.w_mm = w*mm_px
        self.h_mm = h*mm_px
        # print(f"width {self.w_mm} mm")
        # print(f"height {self.h_mm} mm")
        cv2.imshow("final difference",self.img_raw)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def evaluate_relation(self, w_size):
        _,_,w,h = cv2.boundingRect(self.c)
        self.relation_mmpx = w_size/w
        # print(w)        
        # print(f"Relation = {self.relation_mmpx} mm/px")

    def evaluate_image(self,mmpx, w_size):
        self.find_min_level()
        self.find_contour()
        self.evaluate_dimensions(mmpx)
        self.evaluate_relation(w_size)

