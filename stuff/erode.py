import cv2
import numpy as np

img = cv2.imread('data/3rect_0.png',0)	
kernel = np.ones((5,5),np.uint8)
blur = cv2.GaussianBlur(img,(5,5),0)
erosion = cv2.erode(blur,kernel,iterations = 1)
# dilation = cv2.dilate(erosion, kernel, iterations = 1)
cv2.imwrite('data/3eroded.png', erosion)