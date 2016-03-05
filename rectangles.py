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
from bfs import BFS

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

def canMerge(rectangle1, rectangle2):
	# If one rectangle is on left side of other
	if rectangle1[0][0] > rectangle2[2][0] or rectangle2[0][0] > rectangle1[2][0]:
		return False
	# If one rectangle is above other
	if rectangle1[0][1] > rectangle2[2][1] or rectangle2[0][1] > rectangle1[2][1]:
		return False
	return True

def merge(rectangle1, rectangle2):
	# merges 2 rectangles
	minX = min(rectangle1[0][0], rectangle2[0][0])
	maxX = max(rectangle1[2][0], rectangle2[2][0])
	minY = min(rectangle1[0][1], rectangle2[0][1])
	maxY = max(rectangle1[2][1], rectangle2[2][1])

	return np.array([[minX,minY],[minX,maxY],[maxX,maxY], [maxX, minY]], dtype=np.int32)

def expandRectangle(rectangle, height, width):
	#exapnd 10% on all sides
	ratio = 0.1 #10%
	minX = rectangle[0][0]
	maxX = rectangle[2][0]
	minY = rectangle[0][1]
	maxY = rectangle[2][1]

	deltaX = int((maxX - minX)*ratio)
	deltaY = int((maxY - minY)*ratio)

	minX -= deltaX
	maxX += deltaX
	minY -= deltaY
	maxY += deltaY

	minX = max(0, minX)
	maxX = min(width-1, maxX)
	minY = max(0, minY)
	maxY = min(height-1, maxY)

	return np.array([[minX,minY],[minX,maxY],[maxX,maxY], [maxX, minY]], dtype=np.int32)

def pruneRectangles(rectangles, height, width):
	#should be at least one hundredth of area
	thresholdArea = int((height*width)*0.01)
	prunedRectangles = []
	for rectangle in rectangles:
		contourArea = cv2.contourArea(rectangle)
		if contourArea > thresholdArea:
			prunedRectangles.append(rectangle)

	return prunedRectangles

def mergeRectangles(rectangles, height, width):
	#expand all rectangles
	expandedRectangles = []
	for rectangle in rectangles:
		expandedRectangles.append(expandRectangle(rectangle, height, width))
	rectangles = expandedRectangles

	print expandedRectangles

	ans = []
	for rectangle in rectangles:
		currAns = []
		mergedRect = rectangle
		for r2 in ans:
			if canMerge(mergedRect, r2):
				mergedRect = merge(mergedRect, r2)
			else:
				currAns.append(r2)
		currAns.append(mergedRect)
		ans = currAns
	return ans
	
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
    for fn in glob('data/1_verylow.png'):
    	img = cv2.imread(fn)
    	height, width = img.shape[:2]
    	
    	mask = getMask(img)
    	rectangles = BFS(mask).getRectangles()
    	print len(rectangles)
    	rectangles = pruneRectangles(rectangles, height, width)
    	print len(rectangles)
    	rectangles = mergeRectangles(rectangles, height, width)
    	print len(rectangles)


    	# imgArea = height * width

    	# imgCopy = img.copy()
     #    rectangles = findRectangles(imgCopy)
     #    print len(rectangles)
     #    validRectangles = []
     #    for rectangle in rectangles:
     #    	if not isBoundaryRectangle(rectangle, imgArea):
     #    		validRectangles.append(rectangle)

     #    print len(validRectangles) 
     #    rectangles = validRectangles

        # validRectangles = filterRectangles(rectangles, img)
        # print len(validRectangles) 

        cv2.drawContours(img, rectangles, -1, (0, 255, 0), 3 )
        cv2.imwrite('rectangles.png', img)
        
        ch = 0xFF & cv2.waitKey()
        if ch == 27:
            break
    cv2.destroyAllWindows()
