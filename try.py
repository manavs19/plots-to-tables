import numpy as np
import cv2

PERCENT_THRESH=0.15
DEBUG=0

##DEBUG =1 for viewing outputs, =0 otherwise

#Function to exract points from a single extracted curve
def extract_points(img, hue,ten_length):
    height, width = img.shape[:2]
    if(ten_length == 0):
        ten_length = width
    extracted_points=[]
    iterated_c=0
    yavg = 0
    yavgcnt=0
    for c in range(width):
        ycol=0
        count=0
        for r in range(height):
            if(img[r,c,0] > hue - 5 and img[r,c,0]< hue + 5):
                count=count+1
                ycol += r
        if(count !=0):
            yavgcnt+=1
            yavg+=int((ycol)/count)
        ycol=count=0
        if(c > 0 and c % int(ten_length/10) == 0):
        #Point ex
            exy=0
            exx= int(iterated_c + int(ten_length / 20))
            if(yavgcnt!=0):
                exy = (int(yavg / yavgcnt))
            extracted_points.append((exx,exy))
            iterated_c = c
            yavg=yavgcnt=0

    if(DEBUG == 1):
        img=cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        for i in range(len(extracted_points)):
            cv2.circle(img,extracted_points[i],4,(255,255,255),2)
        cv2.imshow("curves",img)
        cv2.waitKey(0)

    return extracted_points


##Function to find plots from supplied Hue value list
##img->(Mat) input image of a particular plot
##curveclrHSV-> (integer list) list of hue values
##ten_length->  (int) integer value of the pixel distance between which 10 points are required
def findplot(img,curveclrHSV,ten_length):
    curve_points=[]
    height, width = img.shape[:2]
    for i in range(height):
        for j in range(width):
            a=img[i,j]
            #print a
            if(max(a) - min(a) <2):
                img.itemset((i,j,0),0)
                img.itemset((i,j,1),0)
                img.itemset((i,j,2),0)
    img= cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    nwimg = np.zeros((height,width,3), np.uint8)
    for i in range(len(curveclrHSV)):
        nwimg = np.zeros((height,width,3), np.uint8)
        for j in range(height):
            for k in range(width):
                if(img.item(j,k,0) > curveclrHSV[i] - 5 and img.item(j,k,0) < curveclrHSV[i] +5):
                    nwimg[j,k]=img[j,k]
        curve_points.append(extract_points(nwimg,curveclrHSV[i],ten_length))
        if(DEBUG == 2):
            nwimg=cv2.cvtColor(nwimg,cv2.COLOR_HSV2BGR)
            cv2.imshow("curves",nwimg)
            cv2.waitKey(0)

    return curve_points


##Function to find the hue values and then extract the plots
##img->(Mat) input image of a particular plot
##ten_length->  (int) integer value of the pixel distance between which 10 points are required
def findplot1(img,ten_length):
    height, width = img.shape[:2]
    for i in range(0, height):
        for j in range(0, width):
            a=img[i,j]
            if(max(a) - min(a) <2):
                img.itemset((i,j,0),0)
                img.itemset((i,j,1),0)
                img.itemset((i,j,2),0)
    img=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    clor=[]
    for i in range(360):
        clor.append(0)
    for i in range(height):
        for j in range(width):
            clor[img.item(i,j,0)] +=1
    #for i in range(1,360):
    #    print("%d-->%d" % (i,clor[i]))
    curveclrHSV=[]
    for i in range(1,180):
        if(clor[i] > (height * width) * (PERCENT_THRESH / 100)):
            if(len(curveclrHSV)>0):
                if(abs(curveclrHSV[len(curveclrHSV) - 1] - i) < 3):
                    continue
            if(DEBUG == 4):
                print ("%d-->%d \n" % (i,clor[i]))
            curveclrHSV.append(i)
    curve_points=[]
    nwimg = np.zeros((height,width,3), np.uint8)
    for i in range(len(curveclrHSV)):
        nwimg = np.zeros((height,width,3), np.uint8)
        for j in range(height):
            for k in range(width):
                if(img.item(j,k,0) > curveclrHSV[i] - 5 and img.item(j,k,0) < curveclrHSV[i] +5):
                    nwimg[j,k]=img[j,k]
        curve_points.append(extract_points(nwimg,curveclrHSV[i],ten_length))
        if(DEBUG == 2):
            nwimg=cv2.cvtColor(nwimg,cv2.COLOR_HSV2BGR)
            cv2.imshow("curves",nwimg)
            cv2.waitKey(0)
    cv2.imwrite("last.png",nwimg)

    return curve_points


img = cv2.imread("7.png", 1)
cv2.imshow("original",img)
out=findplot(img,[19,67,115,158],0)
