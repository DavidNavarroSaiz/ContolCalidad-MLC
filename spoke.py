from cmath import sqrt
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np

class Spoke():

    def __init__(self,path):
        self.img_raw = cv2.imread(path)
        self.img = self.img_raw[:,:,0]

    def find_regions(self, y1_percentage, y2_percentage, x1_percentage, x2_percentage, min_thresh, max_thresh):
        imgray = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
        w_imgray, h_imgray = imgray.shape
        imgray = imgray[int(h_imgray*y1_percentage) : int(h_imgray*y2_percentage), int(w_imgray*x1_percentage) : int(w_imgray*x2_percentage)]
        w_imgray, h_imgray = imgray.shape
        cv2.circle(imgray, (int(w_imgray/2), int(h_imgray/2)), 100, (255, 255, 255), -1)

        _, thresh = cv2.threshold(imgray, min_thresh, max_thresh, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        coordinates_list = []
        angles = []
        couples = []
        for cnt in contours:
            # Se buscan los momentos par ahayar centros de masa en x y en y
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])            
            centers = [cx, cy]
            coordinates_list.append(centers)
            # Se buscan los angulos para comparar de manera adecuada las regiones
            _,_,angle = cv2.fitEllipse(cnt)            
            # Se crea una lista llamada couples que retorna las parejas pertenecientes a la misma linea
            for i in angles:
                if (abs(i-angle) < 3):
                    index_value = angles.index(i)
                    couples.append([[cx,cy],coordinates_list[index_value]])

            angles.append(angle)

        # print("Coordinates list", coordinates_list)
        # print("Len coordinates", len(coordinates_list))
        # print("Angles", angles)
        cv2.drawContours(imgray, contours, -1, (0,255,0), 3)
        for i in couples:
            cv2.line(imgray, i[0], i[1], (0,255,0), 1) 
        cv2.imshow("final difference",self.img_raw)
        cv2.imshow("final GRAY",imgray)
        # cv2.imshow("final Thresh",thresh)
        cv2.waitKey()

        return coordinates_list, angles, couples

    def det(self, a, b):
        return a[0] * b[1] - a[1] * b[0]

    def distance_between_points(self, point1, point2):
        distance = ((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)**(0.5)
        return distance

    def find_intersection(self, couples):
        intersection_points = []

        for line1 in couples:
            for line2 in couples:
                if line1 != line2:
                    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
                    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

                    div = self.det(xdiff, ydiff)
                    if div == 0:
                        raise Exception('lines do not intersect')

                    d = (self.det(*line1), self.det(*line2))
                    x = self.det(d, xdiff) / div
                    y = self.det(d, ydiff) / div
                    intersection_points.append([x,y])

        return intersection_points

    def evaluate_error(self, intersection_points, tolerance_mm):
        print("Tolerance [mm] =", tolerance_mm) 

        error = 0
        
        for point1 in intersection_points:
            for point2 in intersection_points:
                if point1 != point2:
                    distance = self.distance_between_points(point1, point2)                    
                    if distance > tolerance_mm:
                        error = 1

        if error == 1:
            mensaje = "Fallo de intersección de lineas centrales. Compruebe la alineación del MLC con respecto al isocentro de radiación y el eje mecánico de rotación del colimador."
        else:
            mensaje = "Alineacion del MLC correcta."

        return mensaje