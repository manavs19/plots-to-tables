# Python 2/3 compatibility
import sys
import math
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

import numpy as np
import cv2
import copy

#for plots, this comes to be 20%
#for bar plot, 15% - bad!!
def getMask(img):
	#returns mask for coloured pixels
	imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)        
	#white
	lowerWhite = np.array([0,0,0], dtype=np.uint8)
	upperWhite = np.array([0,0,255], dtype=np.uint8)
	maskWhite = cv2.inRange(imgHSV, lowerWhite, upperWhite)

	#black
	lowerBlack = np.array([0, 0, 0], dtype=np.uint8)
	upperBlack = np.array([180, 255, 30], dtype=np.uint8)
	maskBlack = cv2.inRange(imgHSV, lowerBlack, upperBlack)

	mask = cv2.bitwise_or(maskWhite, maskBlack)
	mask = cv2.bitwise_not(mask)
	cv2.imwrite('mask.jpg', mask)
	return mask

if __name__ == '__main__':
    from glob import glob
    for fn in glob('data/3.png'):
    	img = cv2.imread(fn)
    	height, width = img.shape[:2]

    	mask = getMask(img)
    	coloured=0
    	for x in range(0, width):
    		for y in range(0, height):
    			if mask[y][x]!=0:
    				coloured+=1

    	print coloured, height*width, float(coloured)/(height*width)