import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np

class CompareImages():
    def __init__(self,pathA, pathB):
        self.imageA = cv2.imread(pathA)[:,:,0]
        self.imageB = cv2.imread(pathB)[:,:,0]
        # cv2.imshow("imageA",self.imageA)
        # cv2.waitKey()
    def dist_manhattan(self,imgA,imgB):
            """        
            dist_manhattan = sum(abs(i1 - i2)) / i1.size
            """
            pass
    def dist_ncc(self,imgA,imgB):
        """        
        dist_ncc = sum( (i1 - mean(i1)) * (i2 - mean(i2)) ) / (
        #   (i1.size - 1) * stdev(i1) * stdev(i2) )
        """
        pass
    def cor(self,imgA,imgB):
        cc = np.sum(imgA*imgB)
        cc /= (np.sum(imgA)*np.sum(imgB))   
        return cc    
    def mse(self,imgA,imgB):
        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;
        # NOTE: the two images must have the same dimension
        err = np.sum((imgA.astype("float") - imgB.astype("float")) ** 2)
        err /= float(imgA.shape[0] * imgA.shape[1])
        
        # return the MSE, the lower the error, the more "similar"
        return err
    def get_best_shift(self,iter):
        mse_min=100
        self.i_min = 0
        self.j_min = 0
        Img_temp=self.imageB
        for i in range (-iter,iter):
            for j in range (-iter,iter):
                Img_temp=np.roll(self.imageB,[i,j],axis=(0,1))
                mse_1 =self.mse(self.imageA,Img_temp)
                if mse_1 < mse_min:
                    self.i_min = i
                    self.j_min = j
                    mse_min = mse_1 

        print(f"i: {self.i_min} - j: {self.j_min}, MSE = {mse_min}")

        self.imageshifted=np.roll(self.imageB,[self.i_min,self.j_min],axis=(0,1))
    
        return self.imageshifted,self.i_min,self.j_min,mse_min

    def Pixel2mm(self,mmpx):
        """
        - mm to pixel conversion:
        ejemplo de uso:
        Se asume que entre la primer linea y la ultima hay 100 mm
        El inicio de la primer linea empieza a los 79px y la ultima linea finaliza en los 959px
        959-79 = 880
        100/880 = 0.11mm/px
        
        """

        shift_x_mm = self.i_min*mmpx
        shift_y_mm = self.j_min*mmpx
        print(f"image 2 is different to image 1 in x: {shift_x_mm} mm, y:{shift_y_mm} mm")

    def evaluate_simility(self):
        self.initial_simility = ssim(self.imageA, self.imageB)
        self.final_simility = ssim(self.imageA, self.imageshifted)


    def evaluate_error(self):
        self.initialError = self.mse(self.imageA, self.imageB)
        self.finalError = self.mse(self.imageA, self.imageshifted)

    def display_difference(self):
        subtracted = cv2.subtract(self.imageA, self.imageB).astype("uint8")
        subtracted_init = cv2.threshold(subtracted, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        subtracted_final = cv2.subtract(self.imageA, self.imageshifted).astype("uint8")
        subtracted_final = cv2.threshold(subtracted_final, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        cv2.imshow("initial difference",subtracted_init)
        cv2.imshow("final difference",subtracted_final)
        cv2.waitKey()
        cv2.destroyAllWindows()
    def display_images(self):
        cv2.imshow("initial difference",self.imageA)
        cv2.imshow("final difference",self.imageB)
        cv2.waitKey()
        cv2.destroyAllWindows()
    def save_shifted_image(self,output_path):
        cv2.imwrite(output_path, self.imageshifted)

    def display_results(self):
        self.evaluate_simility()
        self.evaluate_error()
        print(f'initial similarity: {self.initial_simility}')
        print(f'final similarity: {self.final_simility}')
        print(f'initial error: {self.initialError}')
        print(f'final error: {self.finalError}')

    def evaluate_images(self,number_iterations,mm_px):
        self.get_best_shift(number_iterations)
        self.Pixel2mm(mm_px)
        self.display_results()
        self.display_difference()
