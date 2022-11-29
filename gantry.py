''' Se importan librerias necesarias '''
from itertools import count
import matplotlib.pyplot as plt
import cv2
import numpy as np
from reporte import PDF2
import datetime
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
''' Creación clase para prueba Picket Fence '''
class AlineacionYCuadratura():
    '''
    Se cargan las imagenes:
    - img_raw -> imagen original
    - img -> imagen de un solo canal (blanco y negro)
    Además valores establecidos de:
    - name_img -> Necesario para creación de tabla con los datos necesarios
    - df_x -> Dataframes donde se almacena la información
    '''
    def __init__(self,path, name_img, df_alineacion, df_diferencia_angulos, df_cuadratura):
        self.img_raw = cv2.imread(path)
        self.img = self.img_raw[:,:,0]
        self.df_alineacion = df_alineacion
        self.df_diferencia_angulos = df_diferencia_angulos
        self.df_cuadratura = df_cuadratura
        self.name_img = name_img

    '''
    Hallar los valores de intensidad minimo y de grises
    de una imagen
    '''
    def find_min_level(self,imgRoi):
        min = np.amin(imgRoi)
        graylevel = (255-min)*0.5 + min
        return graylevel

    '''
    Hallar las regiones blancas dentro de una imagen recortada con los aprametros
    que le entran a la función y entrega una lista compuesta de:
    - Coordenadas centrales de la region blanca
    - Angulos de cada una de las regiones
    '''
    def find_white_zones_parameters(self, y1_percentage, y2_percentage, x1_percentage, x2_percentage):
        imgray = cv2.cvtColor(self.img_raw, cv2.COLOR_BGR2GRAY)
        w_img, h_img = imgray.shape
        imgray = imgray[int(h_img*y1_percentage) : int(h_img*y2_percentage), int(w_img*x1_percentage) : int(w_img*x2_percentage)]
        _, thresh = cv2.threshold(imgray, 200, 255, 0)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        coordinates_list = []
        angles = [] # contiene lista con el angulo y si la lamina es superior o inferior
        lamina = "no idea"
        for cnt in contours:
            # Las variables "x" y "y" son el centro del contorno
            x,y,w,h = cv2.boundingRect(cnt)
            _,_,angle = cv2.fitEllipse(cnt)
            # coordinates es una lista que contiene dos listas, con dos puntos claves dentro de la región
            # un punto x1,y1 a la izquierda de la region y un punto x2,y2 a la derecha
            # por tanto coordinates es [[x1,y1],[x2.y2]]
            coordinates = [[int((w*0.2)+x+int(w_img*0.12)), int(y+(h/2)+int(h_img*0.12))], [int((w*0.8)+x+int(w_img*0.12)), int(y+(h/2)+int(h_img*0.12))]]
            coordinates_list.append(coordinates) 

            lamina = "Inferior" if y>400 else "Superior" 
            angles.append([angle, lamina])
        return coordinates_list, angles

    # Halla el valor de altura de una región en una imagen
    def find_height(self,img,x,y,w,h):
        # Las variables "x" y "y" son el punto superior izquierdo
        imgRoi = img[y:y+h, x:x+w]
        min_level = self.find_min_level(imgRoi)
        mask = cv2.inRange(imgRoi, 0, min_level)
        contours, _ = cv2.findContours(image=mask, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
        c = contours[1]
        x,y,w,h = cv2.boundingRect(c)
        return h

    def find_alignment(self):
        coordinates_list, _ = self.find_white_zones_parameters(0.12, 0.88, 0.12, 0.88)
        w, h = 20, 130

        diff_heights = [] # Contiene listas con informacion de diferencia de anchos y a que lámina pertenece
        lamina = "no idea"
        for zone in coordinates_list:
            x1, y1, x2, y2 = int(zone[0][0]-w/2), int(zone[0][1]-h/2), int(zone[1][0]-w/2), int(zone[1][1]-h/2)
            height_1 = self.find_height(self.img,x1,y1,w,h)
            height_2 = self.find_height(self.img,x2,y2,w,h)
            diff = height_1 - height_2
            lamina = "Inferior" if y1>400 else "Superior"
            diff_heights.append([diff, lamina])

        return diff_heights


    def alineacion(self, mm_px, tolerance_mm):
        diff_heights = self.find_alignment()
        # print("Tolerancia Alineaión [mm] =", tolerance_mm) 

        error = 0
        for i in diff_heights:
            # print(i*mm_px)
            if abs(i[0])*mm_px > tolerance_mm:
                new_row = {'Image':self.name_img, 'Diferencia ancho [mm]':(round(i[0]*mm_px, 4)), 'Lamina':i[1], 'Resultado':"No pasa"}
                error = 1
            else:
                new_row = {'Image':self.name_img, 'Diferencia ancho [mm]':(round(i[0]*mm_px, 4)), 'Lamina':i[1], 'Resultado':"Pasa"}
            self.df_alineacion = self.df_alineacion.append(new_row, ignore_index=True)


        if error == 1:
            self.resultado_alineacion = "No pasa."
            self.mensaje_alineacion = "Revise angulación en dirección GT y planicidad del EPID."
            mensaje = "\n La prueba excede la tolerancia. Revise: \n 1. El gantry, angulación en direccion GT. \n 2. La planicidad del EPID. \n Puede hacer uso del nivel de burbuja, digitales o semejantes. \n " 
        else:
            self.resultado_alineacion = "Pasa."
            self.mensaje_alineacion = "La prueba cumple los parámetros de evaluación. Alineación."
            mensaje = "\n La prueba cumple los parámetros de evaluación. Alineación. \n"

        return self.df_alineacion, mensaje      

    '''
    Compara los valores de angulos entre dos zonas horizontales dentro de la imagen
    '''
    def comparacion_angulos(self, tolerance_grados):
        _, angles = self.find_white_zones_parameters(0.12, 0.88, 0.12, 0.88)

        diff = 0
        if angles[0][1] == "Superior":
            diff = angles[0][0] - angles [1][0]
        elif angles[0][1] == "Inferior":
            diff = angles[1][0] - angles [0][0]

        error = 1 if (abs(diff) > tolerance_grados) else 0

        if error == 1:
            self.resultado_comparacion = "No pasa."
            self.mensaje_comparacion = "Los bancos de multilaminas parecen no estar alineados."
            mensaje = "\n La prueba excede la tolerancia. \n Los bancos de multilaminas parecen no estar alineados, repita la prueba; en caso de persistir el error comuniquese con el equipo de mantenimiento. \n"
            new_row = {'Image':self.name_img, 'Diferencia angulos [grados]':(round(diff, 4)), 'Resultado':"No pasa"}
        else:
            self.resultado_comparacion = "Pasa."
            self.mensaje_comparacion = "La prueba cumple los parámetros de evaluación. Comparación de ángulos entre láminas."
            mensaje = "\n La prueba cumple los parámetros de evaluación. Comparación de ángulos entre láminas. \n"
            new_row = {'Image':self.name_img, 'Diferencia angulos [grados]':(round(diff, 4)), 'Resultado':"Pasa"}

        self.df_diferencia_angulos = self.df_diferencia_angulos.append(new_row, ignore_index=True)

        return self.df_diferencia_angulos, mensaje

    '''
    Encuentra la diferencia entre los angulos de las láminas y el borde del colimador secundario
    '''
    def cuadratura(self, tolerance_grados):
        # white_zones_angle son las regiones blancas correspondientes al campo obstruido por la lámina
        # reference_edge corresponde al borde inferior de la imagen para referencia
        _, white_zones_angle = self.find_white_zones_parameters(0.12, 0.88, 0.12, 0.88)
        _, reference_edge = self.find_white_zones_parameters(0.88, 1.0, 0.12, 0.88)
        error = 0

        # Verificar que se encuentra un solo borde en la imagen
        if len(reference_edge) == 1:
            reference_edge = reference_edge[0]
        else:
            print("No se encuentra borde inferior")
            error = 1

        # Verificar paralelismo entre campo de las láminas y borde inferior del campo, colimador secundario
        for zone_angle in white_zones_angle:
            diff = zone_angle[0] - reference_edge[0]
            # Se añaden valores al dataframe
            if abs(diff) >= tolerance_grados:
                error = 1
                new_row = {'Image':self.name_img, 'Diferencia angulos [grados]':(round(diff, 4)), "Lamina":zone_angle[1], 'Resultado':"No pasa"}
            else:
                new_row = {'Image':self.name_img, 'Diferencia angulos [grados]':(round(diff, 4)), "Lamina":zone_angle[1], 'Resultado':"Pasa"}

            self.df_cuadratura = self.df_cuadratura.append(new_row, ignore_index=True)

        if error == 1:
            self.resultado_cuadratura = "No pasa"
            self.mensaje_cuadratura = "El colimador secundario y el MLC no parecen estar alineados."
            mensaje = "\n La prueba excede la tolerancia. \n El colimador secundario y el MLC no parecen estar alineados, repita la prueba; en caso de persistir el error comuniquese con el servicio de mantenimiento. \n"
        else:
            self.resultado_cuadratura = "Pasa"
            self.mensaje_cuadratura = "La prueba cumple los parámetros de evaluación. Cuadratura."
            mensaje = "\n La prueba cumple los parámetros de evaluación. Cuadratura. \n"

        return self.df_cuadratura, mensaje

    def generar_pdf(self, nombre_prueba, tolerancia):
        pdf = PDF2()
        pdf.add_page()

        pdf.set_font("Times", size=8)
        pdf.set_margins(10, 60, -1)
        pdf.set_auto_page_break(True, margin = 40)
        # pdf.image('./../GUIs/imagenes_interfaz/formato_reporte.png', x = 0, y = 0, w = 210, h = 297)
        pdf.set_xy(70, 10)
        pdf.set_font('arial', 'B', 14)
        pdf.cell(75, 10, "Reporte "+nombre_prueba, 0, 1, 'L')
        pdf.set_font('arial', '', 6)
        pdf.set_xy(160, 10)
        pdf.cell(40, 10, "Fecha: "+datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss'), 0, 0, 'L')
        pdf.set_font('arial', 'B', 10)
        pdf.set_xy(50, 30)

        if nombre_prueba == "Alineacion":
            pdf.cell(40, 10, "Imagen: "+self.name_img, 0, 0, 'L')
            pdf.set_xy(10, 40)
            pdf.cell(40, 10, "Tolerancia: "+str(tolerancia)+ 'mm', 0, 0, 'L')

            pdf.set_xy(10, 50)
            pdf.cell(40, 10, "Resultado: "+self.resultado_alineacion, 0, 0, 'L')
            pdf.set_xy(10, 60)

            pdf.cell(40, 10, "Mensaje: "+str(self.mensaje_alineacion), 0, 0, 'L')

            nombre_prueba = './reportes/' + nombre_prueba+self.name_img + datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')+'.pdf'
            pdf.output(nombre_prueba)

        elif nombre_prueba == "Comparacion":
            pdf.cell(40, 10, "Imagen: "+self.name_img, 0, 0, 'L')
            pdf.set_xy(10, 40)
            pdf.cell(40, 10, "Tolerancia: "+str(tolerancia)+ ' grados', 0, 0, 'L')

            pdf.set_xy(10, 50)
            pdf.cell(40, 10, "Resultado: "+self.resultado_comparacion, 0, 0, 'L')
            pdf.set_xy(10, 60)

            pdf.cell(40, 10, "Mensaje: "+str(self.mensaje_comparacion), 0, 0, 'L')

            nombre_prueba = './reportes/' + nombre_prueba+self.name_img + datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')+'.pdf'
            pdf.output(nombre_prueba)

        elif nombre_prueba == "Cuadratura":
            pdf.cell(40, 10, "Imagen: "+self.name_img, 0, 0, 'L')
            pdf.set_xy(10, 40)
            pdf.cell(40, 10, "Tolerancia: "+str(tolerancia)+ ' grados', 0, 0, 'L')

            pdf.set_xy(10, 50)
            pdf.cell(40, 10, "Resultado: "+self.resultado_cuadratura, 0, 0, 'L')
            pdf.set_xy(10, 60)

            pdf.cell(40, 10, "Mensaje: "+str(self.mensaje_cuadratura), 0, 0, 'L')

            nombre_prueba = './reportes/' + nombre_prueba+self.name_img + datetime.datetime.now().strftime('%m-%d-%y_%Hh-%Mm-%Ss')+'.pdf'
            pdf.output(nombre_prueba)

'''
CODIGOS IMPORTANTES PARA PRUEBAS

    # cv2.rectangle(self.img_raw, coordinates[0], coordinates[1], (255, 0, 0), 4)
# print(coordinates_list, angles)
# cv2.drawContours(thresh, contours, -1, (0,255,0), 3)
# cv2.imshow("final difference",self.img_raw)
# cv2.imshow("final Thresh",thresh)
# cv2.waitKey()

# cv2.rectangle(mask, (x, y), (x + w, y + h), (0,0,255), 1)
# cv2.imshow("final difference",mask)
# cv2.waitKey()

'''