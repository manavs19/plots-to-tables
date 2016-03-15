import sys
import math
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

import numpy as np
import cv2
import copy
from bfs import BFS
from pdfManager import PDFManager

def findRectangles(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = img.shape[:2]
    # img = cv2.GaussianBlur(img, (5, 5), 0)
    squares = []
    # for gray in cv2.split(img):
    # for thrs in xrange(0, 255, 26):
    # thrs = 250
    _,img = cv2.threshold(img, 250, 255, 1)
    # if thrs == 0:
    #     bin = cv2.Canny(gray, 0, 50, apertureSize=5)
    #     bin = cv2.dilate(bin, None)
    # else:
    #     retval, bin = cv2.threshold(gray, thrs, 255, 1)
    _,contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    thresholdArea = int((height*width)*0.01)
    for cnt in contours:
        if len(cnt) < 4:
            continue
        contourArea = cv2.contourArea(cnt)
        if (contourArea < thresholdArea):
            continue

        cnt_len = cv2.arcLength(cnt, True)
        cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)

        if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
          cnt = cnt.reshape(-1, 2)
          max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
          if max_cos < 0.1:
              squares.append(cnt)
    return squares

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

if __name__ == "__main__":
	img = cv2.imread("legends/l"+sys.argv[1]+".png")
	rectangles = findRectangles(img)
	print rectangles
