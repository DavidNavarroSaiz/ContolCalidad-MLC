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

    def find_white_zones_parameters(self, y1_percentage, y2_percentage, x1_percentage, x2_percentage):
        imgray = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
        w_img, h_img = imgray.shape
        imgray = imgray[int(h_img*y1_percentage) : int(h_img*y2_percentage), int(w_img*x1_percentage) : int(w_img*x2_percentage)]
        _, thresh = cv2.threshold(imgray, 200, 255, 0)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        coordinates_list = []
        angles = []
        for cnt in contours:
            # Las variables "x" y "y" son el centro del contorno
            x,y,w,h = cv2.boundingRect(cnt)
            _,_,angle = cv2.fitEllipse(cnt)
            # coordinates es una lista que contiene dos listas, con dos puntos claves dentro de la región
            # un punto x1,y1 a la izquierda de la region y un punto x2,y2 a la derecha
            # por tanto coordinates es [[x1,y1],[x2.y2]]
            coordinates = [[int((w*0.2)+x+int(w_img*0.12)), int(y+(h/2)+int(h_img*0.12))], [int((w*0.8)+x+int(w_img*0.12)), int(y+(h/2)+int(h_img*0.12))]]
            coordinates_list.append(coordinates)  
            angles.append(angle)
            # cv2.rectangle(self.img_raw, coordinates[0], coordinates[1], (255, 0, 0), 4)

        # print(coordinates_list, angles)
        # cv2.drawContours(thresh, contours, -1, (0,255,0), 3)
        # cv2.imshow("final difference",self.img_raw)
        # cv2.imshow("final Thresh",thresh)
        # cv2.waitKey()

        return coordinates_list, angles

    def find_height(self,img,x,y,w,h):
        # Las variables "x" y "y" son el punto superior izquierdo
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
        coordinates_list, _ = self.find_white_zones_parameters(0.12, 0.88, 0.12, 0.88)
        w, h = 20, 130

        diff_heights = []
        for zone in coordinates_list:
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

    def field_size(self, tolerance):
        # white_zones_angle son las regiones blancas correspondientes a las placas
        # reference_edge corresponde al borde inferior de la imagen para referencia
        _, white_zones_angle = self.find_white_zones_parameters(0.12, 0.88, 0.12, 0.88)
        _, reference_edge = self.find_white_zones_parameters(0.88, 1.0, 0.12, 0.88)
        error = 0

        # Verificar que se encuentra un solo borde en la imagen
        if len(reference_edge) == 1:
            reference_edge = reference_edge[0]
        else:
            error = 1

        # Verificar paralelismo entre zonas blanca y borde inferior
        for zone_angle in white_zones_angle:
            diff = abs(zone_angle - reference_edge)
            if diff >= tolerance:
                error = 1

        if error == 1:
            mensaje = "Fallo de paralelismo. Compruebe la alineacion del banco de multilaminas con el borde del campo."
        else:
            mensaje = "Paralelismo correcto."

        return mensaje
