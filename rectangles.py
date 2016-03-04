#!/usr/bin/env python

'''
Simple "Rectangle Detector" program.
'''

# Python 2/3 compatibility
import sys
import math
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

import numpy as np
import cv2
import copy


def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def findRectangles(img):
    img = cv2.GaussianBlur(img, (5, 5), 0)
    squares = []
    for gray in cv2.split(img):
        for thrs in xrange(0, 255, 26):
            if thrs == 0:
                bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                bin = cv2.dilate(bin, None)
            else:
                retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            bin, contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                    if max_cos < 0.1:
                        squares.append(cnt)
                    # flag=0
                    # for i in xrange(4):
                    # 	cos = angle_cos(cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4])
                    # 	if cos < 0 or cos > 0.05233595624:
                    # 		print cos, math.acos(cos)*180/3.14159
                    # 		flag=1
                    #     	break
                    # if flag==0:
                    # 	squares.append(cnt)
    return squares

def isBoundaryRectangle(r, imgArea):
	contourArea = cv2.contourArea(r)
	# print contourArea, imgArea
	#check if are is 80%
	if float(contourArea) > 0.9 * float(imgArea):
		return 1
	return 0

def sortRectangle(r):
	#Counter-clock, 1st point is top left
	r = r.tolist()
	r.sort(key=lambda x: x[0])
	if r[0][1] > r[1][1]:
		r[0], r[1] = r[1], r[0]

	if r[3][1] > r[2][1]:
		r[3], r[2] = r[2], r[3]

	r = np.array(r)
	return r

def isInsideRectangle(i, j, rectangle):
	dist = cv2.pointPolygonTest(rectangle,(i,j),False)
	if dist==1:
		return 1
	else:
		return 0


def filterRectangles(rectangles, img):
	#filters rectangles that contain at least one coloured pixel
	#merges nearby rectangles. takes max area rectangle

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

	# print type(mask)
	# print mask.shape
	
	validRectangles = []
	height, width = mask.shape
	for i in range(0, height):
		for j in range(0, width):
			if mask[i][j]!=0:#coloured pixel
				# print mask[i][j]
				tempList = []#list of rectangles that contain pixel i,j		
				for rectangle in rectangles:
					if isInsideRectangle(i, j, rectangle):
						tempList.append(rectangle)

				if tempList:#not empty
					maxArea = 0
					maxRectangle = None
					for rectangle in tempList:
						area = cv2.contourArea(rectangle)
						if area > maxArea:
							maxArea = area
							maxRectangle = rectangle

					temp1 = []
					for r in rectangles:
						temp1.append(r.tolist())
					temp2 = []
					for r in tempList:
						temp2.append(r.tolist())

					tt = [item for item in temp1 if item not in temp2]
					rectangles = []
					for r in tt:
						rectangles.append(np.array(r))
					rectangles.append(maxRectangle)
					validRectangles.append(maxRectangle)

	return validRectangles
	
# yo = np.array([[ 736,   488], [1724,  489], [1723, 2021], [ 732, 2018]])
# yo = sortRectangle(yo)
# print yo

# def isColoured(img, r):
# 	r = sortRectangle(r)
# 	xStart = max(r[0][0], r[1][0])
# 	xEnd = min(r[2][0], r[3][0])

# 	yStart = max(r[0][1], r[3][1])
# 	yEnd = min(r[1][1], r[2][1])


# 	for y in range(yStart, yEnd+1):
# 		for x in range(xStart, xEnd+1):
# 			if img[x][y][0] > 5 and img[x][y][0] < 250:
# 				return 1
# 			if img[x][y][1] > 5 and img[x][y][1] < 250:
# 				return 1
# 			if img[x][y][2] > 5 and img[x][y][2] < 250:
# 				return 1
# 	return 0 #not coloured

if __name__ == '__main__':
    from glob import glob
    for fn in glob('data/3.png'):
    	img = cv2.imread(fn)

    	height, width = img.shape[:2]
    	imgArea = height * width

    	imgCopy = img.copy()
        rectangles = findRectangles(imgCopy)
        print len(rectangles)
        validRectangles = []
        for rectangle in rectangles:
        	if not isBoundaryRectangle(rectangle, imgArea):
        		validRectangles.append(rectangle)

        print len(validRectangles) 
        rectangles = validRectangles

        validRectangles = filterRectangles(rectangles, img)
        print len(validRectangles) 

        cv2.drawContours(imgCopy, validRectangles, -1, (0, 255, 0), 3 )
        cv2.imwrite('rectangles.png', imgCopy)
        # cv2.imshow('rectangles', img)
        
        ch = 0xFF & cv2.waitKey()
        if ch == 27:
            break
    cv2.destroyAllWindows()
