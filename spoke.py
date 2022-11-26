'''Importe de librerias necesarias'''
from cmath import sqrt
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np

'''Creación de clase para analisis de Spoke Shot'''
class Spoke():
    '''
    Se cargan las imagenes:
    - img_raw -> imagen original
    - gray_img -> imagen de un solo canal (blanco y negro)
    Además valores establecidos de:
    - name_img -> Necesario para creación de tabla con los datos necesarios
    - df -> Dataframe donde se almacena la información
    - h_imgray, w_imgray ancho y alto de la imagen en px
    '''
    def __init__(self, path_img, dataframe, name_img):
        self.df = dataframe
        self.name_img = name_img
        self.img_raw = cv2.imread(path_img)
        self.imgray = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
        self.h_imgray, self.w_imgray = self.imgray.shape

    '''
    Encuentra el circulo blanco central y le encuentra
    el centro a este para ser comparado posteriormente
    '''
    def find_white_circle(self, min_thresh, max_thresh):
        imgray = self.imgray[int(self.h_imgray*0.4) : int(self.h_imgray*0.6), int(self.w_imgray*0.4) : int(self.w_imgray*0.6)]
        _, thresh = cv2.threshold(imgray, min_thresh, max_thresh, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        area_cte = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area_cte == 0 or area < area_cte:
                area_cte = area
                M = cv2.moments(cnt)
                if M['m00'] != 0:
                    cx = int(M['m10']/M['m00']) + int(self.w_imgray*0.4)
                    cy = int(M['m01']/M['m00']) + int(self.h_imgray*0.4)          
                white_circle_coordinates = [cx, cy]

        return white_circle_coordinates

    '''
    A partir de una mascara con forma circular sobre la imagen original 
    busca las regiones de interes y les calcula el centro y el angulo de
    cada una, posteriormente compara los angulos de cada una para ser 
    relacionadas y almacenadas en parejas en una lista nueva
    '''
    def find_regions(self, min_thresh, max_thresh):
        imgray = self.imgray[int(self.h_imgray*0.2) : int(self.h_imgray*0.8), int(self.w_imgray*0.2) : int(self.w_imgray*0.8)]
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
                if (abs(i-angle) < 1):
                    index_value = angles.index(i)
                    couples.append([[cx,cy],coordinates_list[index_value]])
            angles.append(angle)

        cv2.drawContours(imgray, contours, -1, (0,255,0), 3)

        for i in couples:
            cv2.line(imgray, i[0], i[1], (0,255,0), 1) 
        # cv2.imshow("Imagen original",self.img_raw)
        # cv2.imshow("Regiones láminas",imgray)
        # # cv2.imshow("final Thresh",thresh)
        # cv2.waitKey()
        return coordinates_list, angles, couples

    # Calcula el determinante de dos puntos
    def det(self, a, b):
        return a[0] * b[1] - a[1] * b[0]

    # Calcula la distancia entre dos puntos
    def distance_between_points(self, point1, point2):
        distance = ((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)**(0.5)
        return distance

    # Encuentra la interseccion entre dos lineas donde cada linea
    # esta compuesta por dos puntos
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
                    # Se le suma el valor int(self.w_imgray*0.2) para quitar el delay en la imagen original
                    x = (self.det(d, xdiff) / div) + int(self.w_imgray*0.2)
                    y = (self.det(d, ydiff) / div) + int(self.h_imgray*0.2)
                    intersection_points.append([x,y])

        return intersection_points

    '''
    Evalua el error para la prueba spoke shot en base a:
    - Distancia entre puntos generados por la intersección, esta debe ser menor a 1mm
    - Distancia entre cada punto de interseccion y el centro de la region circular
    blanca, esta debe ser de menos de 1mm
    '''
    def evaluate_error(self, white_circle_coordinates, intersection_points, tolerance_mm, relation_mmpx):
        print("Tolerance [mm] =", tolerance_mm) 
        mmpx = relation_mmpx

        error = 0
        punto = 1                
        for point1 in intersection_points:
            # Se busca que cada uno de los puntos de intersección se encuentren dentro de un circulo de [tolerance_mm] de diametro
            for point2 in intersection_points:
                if point1 != point2:
                    distance = self.distance_between_points(point1, point2)    
                    # Se añaden valores al dataframe
                    if distance*mmpx > tolerance_mm:
                        error = 1
                        new_row = {'Image':self.name_img, 'Distance [mm]':(round(distance*mmpx, 4)), 'Distance to:':f'Point {punto}-Others', 'Resultado':'No pasa'}
                    else:
                        new_row = {'Image':self.name_img, 'Distance [mm]':(round(distance*mmpx, 4)), 'Distance to:':f'Point {punto}-Others', 'Resultado':'Pasa'}
                    self.df = self.df.append(new_row, ignore_index=True)               

            # Se compara que cada punto se encuentre a por lo menos [tolerance_mm] de distancia del isocentro del circulo blanco
            distance_to_white_point = self.distance_between_points(point1, white_circle_coordinates)
            # Se añaden valores al dataframe
            if distance_to_white_point*mmpx > tolerance_mm:
                error = 1
                new_row = {'Image':self.name_img, 'Distance [mm]':(round(distance_to_white_point*mmpx, 4)), 'Distance to:':'White point', 'Resultado':'No pasa'}
            else:
                new_row = {'Image':self.name_img, 'Distance [mm]':(round(distance_to_white_point*mmpx, 4)), 'Distance to:':'White point', 'Resultado':'Pasa'}
            self.df = self.df.append(new_row, ignore_index=True)

            punto += 1        

        if error == 1:
            mensaje = "La prueba excede la tolerancia. Si alguno o varios de los campos esta perceptiblemente desalineado con el isocentro, comuniquese con el servicio de mantenimiento. En caso contrario, compruebe la ubicacón de la fiducia y realice la prueba nuevamente."
        else:
            mensaje = "El eje de rotación del colimador coincide con el isocentro. La prueba cumple los parámetros de evauación."

        return mensaje, self.df