from pytesseract import image_to_string
import Image
import cv2
import numpy as np
import sys

i = sys.argv[1]
fin = 'legends/l'+i+'.png'
fout = 'legends/text'+i+'.png'
img = cv2.imread(fin, 0)
img = cv2.resize(img,None,fx=4, fy=4, interpolation = cv2.INTER_CUBIC)
kernel = np.ones((3,3),np.uint8)
img = cv2.GaussianBlur(img, (5, 5), 0)
# img = cv2.resize(img,None,fx=0.25, fy=0.25, interpolation = cv2.INTER_CUBIC)
img = cv2.erode(img,kernel,iterations = 1)
# img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
cv2.imwrite(fout, img)
print image_to_string(Image.open(fout))