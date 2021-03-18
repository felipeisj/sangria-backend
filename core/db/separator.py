import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import os
import glob

def separar(path):
#for img in glob.glob("../dataset/*.JPG"):
    img = cv2.imread(path)
    asd = img
    image = img
    name = path[-12:]
    image = cv2.resize(image, (1080, 1080))
    newPath = "./generated/%s"%name
    nombre_celulas = list()
    try:
        os.mkdir(newPath)
    except OSError:
        print ("Creation of the directory %s failed" % newPath)
    else:
        print ("Successfully created the directory %s " % newPath)
    # convet to gray scale image 
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    #cv2.imwrite('./generated/gray.png', gray) 
    #display(Image.open("./pictures/gen_pic/gray.png"))

    # apply median filter for smoothning 
    blurM = cv2.medianBlur(gray, 3) 
    #cv2.imwrite('./generated/blurM.png', blurM)
    #display(Image.open("./blurM.png"))

    # apply gaussian filter for smoothning 
    blurG = cv2.GaussianBlur(gray, (9, 9), 0) 
    #cv2.imwrite('./generated/blurG.png', blurG) 
    #display(Image.open("./blurG.png"))

    # histogram equalization 
    histoNorm = cv2.equalizeHist(gray) 
    #cv2.imwrite('./generated/histoNorm.png', histoNorm)
    #display(Image.open("./generated/histoNorm.png"))

    # create a CLAHE object for  
    # Contrast Limited Adaptive Histogram Equalization (CLAHE)  
    clahe = cv2.createCLAHE(clipLimit = 2.0, tileGridSize=(8, 8)) 
    claheNorm = clahe.apply(gray) 
    #cv2.imwrite('./generated/claheNorm.png', claheNorm)
    #display(Image.open("./claheNorm.png"))

    # contrast stretching  
    # Function to map each intensity level to output intensity level.  
    def pixelVal(pix, r1, s1, r2, s2): 
        if (0 <= pix and pix <= r1): 
            return (s1 / r1) * pix 
        elif (r1 < pix and pix <= r2): 
            return ((s2 - s1) / (r2 - r1)) * (pix - r1) + s1 
        else: 
            return ((255 - s2) / (255 - r2)) * (pix - r2) + s2 

        # Define parameters.  

    r1 = 50
    s1 = 0
    r2 = 180
    s2 = 255

    # Vectorize the function to apply it to each value in the Numpy array.  
    pixelVal_vec = np.vectorize(pixelVal) 

    # Apply contrast stretching.  
    contrast_stretched = pixelVal_vec(gray, r1, s1, r2, s2) 
    contrast_stretched_blurM = pixelVal_vec(blurM, r1, s1, r2, s2) 

    cv2.imwrite('contrast_stretch.png', contrast_stretched) 
    #cv2.imwrite('contrast_stretch_blurM.png',  

    edgeM = cv2.Canny(blurM, 0, 200) 
    cv2.imwrite('../generated/edgeM.png', edgeM)
    print("")  

    img = cv2.imread('../generated/edgeM.png', 0)   
    # morphological operations
    kernel = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]], dtype=np.uint8)
    #kernel = np.ones((5, 5), np.uint8) 
    dilation = cv2.dilate(image, kernel, iterations = 1) 
    closing = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel) 


    # Initialize the list 
    Cell_count, x_count, y_count = [], [], [] 

    # read original image, to display the circle and center detection   
    dis = image
    dis = cv2.resize(dis, (1080, 1080))

    contours, hierarchy = cv2.findContours(edgeM, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #print("Number of contours = " + str(len(contours)))

    cv2.drawContours(image, contours, -1, (0,255,0), 1)

    #plt.imshow(image)
    #plt.show()
    i=0
    j=0
    for contour in contours:
        inp = asd 
        inp= cv2.resize(inp, (1080, 1080))
        #white = cv2.imread('blanca.jpg')
        #white = cv2.resize(white, (512, 512))
        (x,y),radius = cv2.minEnclosingCircle(contour)
        center = (int(x),int(y))
        radius = int(radius)
        perimeter = cv2.arcLength(contour, True)
        area = cv2.contourArea(contour)
        if(radius > 30):
            #print(j)
            minimoxT = 1000
            maximoxT = 0
            minimoyT = 1000
            maximoyT = 0        
            for tupla in contour:
                #print(tupla)
                minimox = tupla[0,0]
                maximox = tupla[0,0]
                minimoy = tupla[0,1]
                maximoy = tupla[0,1]
                if minimoxT > minimox:
                    minimoxT = minimox
                    if minimoxT-25 < 0:
                        minimoxT = minimoxT + 25
                    #print('minimo x total: ' + str(minimoxT))
                if minimoyT > minimoy:
                    minimoyT = minimoy                
                    #print('minimo y total: ' + str(minimoyT))
                if maximoxT < maximox:
                    maximoxT = maximox
                    #print('maximo x total: ' + str(maximoxT))
                if maximoyT < maximoy:
                    maximoyT = maximoy
                    #print('maximo y total: ' + str(maximoyT))   
            if minimoxT-25 < 0:
                        minimoxT = minimoxT + 25
            if minimoyT-25 < 0:
                        minimoyT = minimoyT + 25
            if maximoxT+25 > 1080:
                        maximoxT = maximoxT - 25
            if maximoyT+25 > 1080:
                        maximoyT = maximoyT - 25
            #cv2.drawContours(white, contours, i, (0,0,0), 0)
            out= inp[minimoyT-25:maximoyT+25, minimoxT-25:maximoxT+25]
            out= cv2.resize(out, (128, 240))
            filename = newPath+'/muestra_%d.jpg'%j
            cv2.imwrite(filename, out)
            nombre_celulas.append(filename)
            j+=1
        i+=1
    #k+=1
    return nombre_celulas