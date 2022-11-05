''' Se importan librerias necesarias '''
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np

''' Creación clase para prueba Picket Fence '''
class TransmisionL():
    '''
    Se cargan las imagenes:
    - img_raw -> imagen original 
    - ROI_img -> imagen recortada con la región de interes a ser trabajada
    - gray_img -> imagen recortada pero de un solo canal (blanco y negro)
    '''
    def __init__(self, path):
        self.img_raw = cv2.imread(path)
        self.gray_img = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
        self.ROI_img = cv2.cvtColor(self.img_raw[110:840,180:840], cv2.COLOR_BGR2GRAY)
        

    '''
    Se 
    '''
    def interest_regions(self):
        self.sup_region = self.ROI_img[0:400, :]
        self.bot_region = self.ROI_img[400:700, :]

        self.sup_region_izq = self.sup_region[:, 0:340]
        self.sup_region_der = self.sup_region[:, 340:660]
        
        self.bot_region_izq = self.bot_region[:, 0:340]
        self.bot_region_der = self.bot_region[:, 340:660]

    '''
    Se buscan los valores de interes para aplicar thesholds
    '''
    def find_gray_levels(self, img):
        min_value = np.amin(img)
        max_value = np.amax(img)
        prom_value = min_value + (max_value - min_value)/2
        return min_value, max_value, prom_value

    '''
    Primer analisis para la prueba de transmisión, prueba región superior derecha, donde:
    - Se deben dibujar rectangulos los cuales se encuenbtran dentro de una región que cumple:
    -- 25mm de separación al borde superior e inferior
    -- 5mm de separación al borde derecho e izquierdo
    - Cada subregión debe medir 5mm de alto y todo el ancho de la región anteriormente mencionada
    Dentro de cada subregión se debe extraer:
    - Histograma
    - Maximo valor de intencidad de pixel
    - Mínimo valor de intencidad de pixel
    - Valor promedio de intencidad de pixeles (pico del histograma)
    '''
    def sup_der_analysis(self, mmpx):
        self.interest_regions()

        img = self.sup_region_der
        h_img, w_img = img.shape

        # Separaciones para posteriormente comenzar a dibujar las regiones de interes
        separation_to_vertical_border = 25 * mmpx
        separation_to_horizontal_border = 5 * mmpx
        separation_between_regions = 5 * mmpx

        # Número de regiones posibles que cumplen la condición de separación de 5mm 
        number_of_regions = int((h_img - 2*separation_to_vertical_border) / separation_between_regions)

        count = 1
        for i in range(number_of_regions): # Región inferior
            if (i == 0):
                y1 = h_img - separation_to_vertical_border - separation_between_regions
                y2 = h_img - separation_to_vertical_border
                x1 = separation_to_horizontal_border
                x2 = w_img - separation_to_horizontal_border
                region = img[y1:y2, x1:x2]
                # cv2.imshow("region", region)
                # cv2.waitKey()

                min_value, max_value, prom_value = self.find_gray_levels(region) # Extrae valores de interes de pixeles
                print("Region %s" % str(count))
                print(" -  MaxValue =", max_value)
                print(" -  MinValue =", min_value)
                print(" -  PromValue =", int(prom_value))
                count += 1

                hist = cv2.calcHist([region], [0], None, [256], [0, 256]) # Creación de histograma
                plt.plot(hist, color='gray' )
                plt.xlabel('Intensidad de pixel')
                plt.ylabel('Cantidad de pixeles')
                plt.show()
                cv2.destroyAllWindows()

                cv2.rectangle(img,(x1, y1), (x2, y2), (0,255,0), 1)

            elif (i%2 == 0): # Regiones intermedias, incrementando de abajo hacia arriba
                y1 = h_img - separation_to_vertical_border - (i+1)*separation_between_regions
                y2 = h_img - separation_to_vertical_border - (i)*separation_between_regions
                x1 = separation_to_horizontal_border
                x2 = w_img - separation_to_horizontal_border
                region = img[y1:y2, x1:x2]
                cv2.imshow("region", region)
                cv2.waitKey()

                min_value, max_value, prom_value = self.find_gray_levels(region)
                print("Region %s" % str(count))
                print(" -  MaxValue =", max_value)
                print(" -  MinValue =", min_value)
                print(" -  PromValue =", int(prom_value))
                count += 1

                hist = cv2.calcHist([region], [0], None, [256], [0, 256])
                plt.plot(hist, color='gray' )
                plt.xlabel('Intensidad de pixel')
                plt.ylabel('Cantidad de pixeles')
                plt.show()
                cv2.destroyAllWindows()

                cv2.rectangle(img,(x1, y1), (x2, y2), (0,255,0), 1)

            elif (i == number_of_regions-1) and ((i-1)%2 != 0): # Última region, esta se dibuja si es posible, quiere decir si la ultima reción esta a mas de 5mm de distancia
                y1 = separation_to_vertical_border
                y2 = separation_to_vertical_border + separation_between_regions
                x1 = separation_to_horizontal_border
                x2 = w_img - separation_to_horizontal_border
                region = img[y1:y2, x1:x2]
                cv2.imshow("region", region)
                cv2.waitKey()

                min_value, max_value, prom_value = self.find_gray_levels(region)
                print("Region %s" % str(count))
                print(" -  MaxValue =", max_value)
                print(" -  MinValue =", min_value)
                print(" -  PromValue =", int(prom_value))
                count += 1

                hist = cv2.calcHist([region], [0], None, [256], [0, 256])
                plt.plot(hist, color='gray' )
                plt.xlabel('Intensidad de pixel')
                plt.ylabel('Cantidad de pixeles')
                plt.show()
                cv2.destroyAllWindows()
                cv2.rectangle(img,(x1, y1), (x2, y2), (0,255,0), 1)
            
        cv2.imshow("Zona", img)
        cv2.waitKey()

    '''
    Segundo analisis para la prueba de transmisión, prueba región inferior derecha, donde:
    - Se deben encontrar las subregiones dentro de la región de interes, estas son:
    - Regiones mas claras dentro de esta misma
    Dentro de cada subregión se debe extraer:
    - Histograma
    - Maximo valor de intencidad de pixel
    - Mínimo valor de intencidad de pixel
    - Valor promedio de intencidad de pixeles (pico del histograma)
    '''
    def bot_der_analysis(self, min_thesh, max_thesh):
        self.interest_regions()
        img = self.bot_region_der
        h_img, w_img = img.shape

        img = img[int(h_img*0.1):h_img, 0:int(w_img*0.9)]
        h_img, w_img = img.shape

        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        plt.plot(hist, color='gray' )
        plt.xlabel('Intensidad de pixel')
        plt.ylabel('Cantidad de pixeles')
        plt.show()
        cv2.destroyAllWindows()

        min_value, max_value, prom_value = self.find_gray_levels(img)

        coordinate_list, _, thresh, contours = self.find_region(img, min_thesh, max_thesh)

        count = 1
        for coordinate in coordinate_list:
            cx, cy, w, h = coordinate[0], coordinate[1], coordinate[2], coordinate[3]
            x1, x2 = 0, w_img
            y1, y2 = cy-int(h/2), cy+int(h/2)
            # cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
            region = img[y1:y2, x1:x2]

            cv2.imshow("region", region)
            cv2.waitKey()

            min_value, max_value, prom_value = self.find_gray_levels(region)
            print("Region %s" % str(count))
            print(" -  MaxValue =", max_value)
            print(" -  MinValue =", min_value)
            print(" -  PromValue =", int(prom_value))
            count += 1

            hist = cv2.calcHist([region], [0], None, [256], [0, 256])
            plt.plot(hist, color='gray' )
            plt.xlabel('Intensidad de pixel')
            plt.ylabel('Cantidad de pixeles')
            plt.show()
            cv2.destroyAllWindows()

            # PARA FUTURAS IMPLEMENTACIONES
            # for i in range(divisions):
            #     separation = (w_img/divisions)/2 # Es la mitad del ancho de la imagen divido la cantidad de divisiones
            #     cv2.circle(img, (int(2*i*separation+separation), cy), h, (0,255,255), 2)

        cv2.imshow("img", img)
        cv2.imshow("thresh", thresh)
        cv2.waitKey()


    '''
    Se busca en la imagen cada región de interes correspondiente a cada distribución
    '''
    def find_region(self, img, min_thesh, max_thesh):
        _, thresh = cv2.threshold(img, min_thesh, max_thesh, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        area_list = []
        coordinate_list = [] # [cx, cy, w, h]
        for cnt in contours:
            area = cv2.contourArea(cnt)
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])        
            _,_,w,h = cv2.boundingRect(cnt)
            
            area_list.append(area)        
            try:
                coordinate_list.append([cx, cy, w, h])
            except NameError:
                print("No se encontraron regiones de interes")          

        return coordinate_list, area_list, thresh, contours
        


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