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
import time
import copy
from bfs import BFS
from pdfManager import PDFManager
import operator
from axisOcr import OCR
import os
import subprocess

def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def getDist(x1,y1,x2,y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

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
        cnt = cv2.approxPolyDP(cnt, 0.001*cnt_len, True)

        # print type(cnt)

        thresholdLen = cnt_len * 0.02
        xMin = 1000000
        yMin = 1000000
        xMax = -1
        yMax = -1
        cnt = cnt.tolist()
        # cnt = cnt[0]
        # print cnt
        for i in range(0, len(cnt)-1):
            if getDist(cnt[i][0][0], cnt[i][0][1], cnt[i+1][0][0], cnt[i+1][0][1]) > thresholdLen:
                xMin = min(xMin, cnt[i][0][0])
                xMin = min(xMin, cnt[i+1][0][0])
                yMin = min(yMin, cnt[i][0][1])
                yMin = min(yMin, cnt[i+1][0][1])

                xMax = max(xMax, cnt[i][0][0])
                xMax = max(xMax, cnt[i+1][0][0])
                yMax = max(yMax, cnt[i][0][1])
                yMax = max(yMax, cnt[i+1][0][1])

        if getDist(cnt[0][0][0], cnt[0][0][1], cnt[len(cnt)-1][0][0], cnt[len(cnt)-1][0][1]) > thresholdLen:
            xMin = min(xMin, cnt[0][0][0])
            xMin = min(xMin, cnt[len(cnt)-1][0][0])
            yMin = min(yMin, cnt[0][0][1])
            yMin = min(yMin, cnt[len(cnt)-1][0][1])

            xMax = max(xMax, cnt[0][0][0])
            xMax = max(xMax, cnt[len(cnt)-1][0][0])
            yMax = max(yMax, cnt[0][0][1])
            yMax = max(yMax, cnt[len(cnt)-1][0][1])

        cnt = [[xMin, yMin], [xMin, yMax], [xMax, yMax], [xMax, yMin]]
        cnt = np.array(cnt, dtype=np.int32)
        squares.append(cnt)

        # if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
        #   cnt = cnt.reshape(-1, 2)
        #   max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
        #   if max_cos < 0.1:
        #       squares.append(cnt)
    return squares

def findXScale(img, rectangle, i):
    minX, minY = rectangle[0]
    maxX, maxY = rectangle[2]
    h,w = maxY-minY, maxX-minX
    cropped = img[int(maxY+0.01*h):int(maxY+0.1*h), minX:maxX].copy()
    cc = cropped.copy()
    
    cropped = cv2.cvtColor(cc, cv2.COLOR_BGR2GRAY)
    _,cropped = cv2.threshold(cropped, 250, 255, 1)

    kernel = np.ones((1,3),np.uint8)
    cropped = cv2.dilate(cropped, kernel, iterations=2)#dilate to get numbers
    _,contours, hierarchy = cv2.findContours(cropped, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # print len(contours)
    # cv2.drawContours(cropped, contours, -1, (127), 3 )
    h,w = cropped.shape[:2]
    thresholdArea = h*w*0.01
    numbers = []
    for cnt in contours:
        if len(cnt)<4:
            continue
        box = cv2.boundingRect(cnt)
        # contourArea = cv2.contourArea(cnt)
        contourArea = box[2]*box[3]
        if contourArea < thresholdArea:
            continue
        # print contourArea, thresholdArea
        numbers.append(box)
        # cv2.rectangle(cc,(box[0],box[1]),(box[0]+box[2],box[1]+box[3]),(127),1)

    # print len(numbers)

    mp = {}
    for number in numbers:
        centerY = number[1] + number[3]/2
        if centerY not in mp:
            mp[centerY]=0
        mp[centerY]+=1

    mp2 = {}
    for k,v in mp.iteritems():
        mp2[k] = 0
        for k2 in range(k-5, k+6):
            if k2 in mp:
                mp2[k] += mp[k]

    sorted_mp = sorted(mp2.items(), key=operator.itemgetter(1))
    sorted_mp.reverse()

    maxCenter = sorted_mp[0][0]
    # print sorted_mp[0]

    temp = []

    for number in numbers:
        numCenter = number[1] + number[3]/2
        if maxCenter - 5 <= numCenter and numCenter <= maxCenter + 5:
            # cv2.rectangle(cc,(number[0],number[1]),(number[0]+number[2],number[1]+number[3]),(127),1)
            temp.append(number)
    # cv2.imwrite('cropped'+str(i)+'.png', cc)

    numbers = temp
    #find lowest point of number boxes
    mx = -1
    for number in numbers:
        mx = max(mx, number[1]+number[3])
    mx += 0.01*(maxY-minY)

    # print len(numbers)
    centerX = []
    for number in numbers:
        center = number[0] + number[2]/2
        centerX.append(center)
    centerX = sorted(centerX)
    scale = 100000000
    for var in range(0, len(centerX)-1):
        diff = centerX[var+1] - centerX[var]
        scale = min(scale, diff)

    scale += 18#compensation
    # print scale

    mp = {}
    for number in numbers:
        numberCropped = cc[number[1]:number[1]+number[3], number[0]:number[0]+number[2]].copy()
        cv2.imwrite("/tmp/x.png", numberCropped)
        try:
            num = OCR().XaxisData()
            if len(num)==0:
                continue
            num = num[0]
            if len(num)==0:
                continue
            data = float(num[0])#is a number
            position = number[0] + number[2]/2
            mp[data] = position            
        except:
            continue

    if len(mp)<2:#could not find 2 numbers
        minX, minY = rectangle[0]
        maxX, maxY = rectangle[2]
        currH,currW = maxY-minY, maxX-minX
        cc1 = img[int(maxY-0.01*currH):int(maxY+0.1*currH), int(minX-0.1*currW):int(maxX + 0.05*currW)].copy()
        print "The OCR engine could not recognize the x-axis markings.Press any key to close the window and enter the required values."
        WINDOW_NAME = "X-Axis"
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_NAME, 800, 400);
        cv2.startWindowThread()
        cv2.imshow(WINDOW_NAME, cc1)

        # activateWindow(WINDOW_NAME)
        time.sleep(0.5)#0.1seconds
        os.system("wmctrl -a X-Axis")#bring to front
        cv2.waitKey(0)
        cv2.destroyWindow(WINDOW_NAME)
        # cv.waitKey(1)
        print "Enter the starting x value:"
        xStart = float(raw_input())
        print "Enter the x axis division:"
        delta = float(raw_input())        
        return scale, mx, xStart, delta

    sorted_mp = sorted(mp.items(), key=operator.itemgetter(0))
    leastCount = 100000000
    store = None
    for var in range(0, len(sorted_mp)-1):
        if sorted_mp[var+1][0] - sorted_mp[var][0] < leastCount:
            leastCount = sorted_mp[var+1][0] - sorted_mp[var][0]
            store = var
    pixelDiff = sorted_mp[store+1][1] - sorted_mp[store][1]
    divisionsInBetween = round(pixelDiff/float(scale))
    delta = float(leastCount)/divisionsInBetween#1
    xStart = sorted_mp[store][0] - round(sorted_mp[store][1]/float(scale))*delta#0

    #scale is number of pixels in a division
    #xStart is actual start value
    #delta is the actual difference between 2 consecutive values
    return scale, mx, xStart, delta

def findYScale(img, rectangle, i):
    minX, minY = rectangle[0]
    maxX, maxY = rectangle[2]
    h,w = maxY-minY, maxX-minX
    cropped = img[minY:maxY, int(minX-0.1*w):int(minX-0.01*w)].copy()
    cc = cropped.copy()
    
    cropped = cv2.cvtColor(cc, cv2.COLOR_BGR2GRAY)
    _,cropped = cv2.threshold(cropped, 250, 255, 1)

    kernel = np.ones((1,3),np.uint8)
    cropped = cv2.dilate(cropped, kernel, iterations=2)#dilate to get numbers
    _,contours, hierarchy = cv2.findContours(cropped, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # print len(contours)
    # cv2.drawContours(cropped, contours, -1, (127), 3 )
    h,w = cropped.shape[:2]
    thresholdArea = h*w*0.01
    numbers = []
    for cnt in contours:
        if len(cnt)<4:
            continue
        box = cv2.boundingRect(cnt)
        # contourArea = cv2.contourArea(cnt)
        contourArea = box[2]*box[3]
        if contourArea < thresholdArea:
            continue
        # print contourArea, thresholdArea
        numbers.append(box)
        # cv2.rectangle(cc,(box[0],box[1]),(box[0]+box[2],box[1]+box[3]),(127),1)

    # print len(numbers)

    mp = {}
    for number in numbers:
        centerX = number[0] + number[2]/2
        if centerX not in mp:
            mp[centerX]=0
        mp[centerX]+=1

    mp2 = {}
    for k,v in mp.iteritems():
        mp2[k] = 0
        for k2 in range(k-5, k+6):
            if k2 in mp:
                mp2[k] += mp[k]

    sorted_mp = sorted(mp2.items(), key=operator.itemgetter(1))
    sorted_mp.reverse()

    maxCenter = sorted_mp[0][0]
    # print sorted_mp[0]

    temp = []

    for number in numbers:
        numCenter = number[0] + number[2]/2
        if maxCenter - 5 <= numCenter and numCenter <= maxCenter + 5:
            # cv2.rectangle(cc,(number[0],number[1]),(number[0]+number[2],number[1]+number[3]),(127),1)
            temp.append(number)
    # cv2.imwrite('cropped'+str(i)+'.png', cc)
    numbers = temp
    mx = 100000000
    for number in numbers:
        mx = min(mx, number[0])
    
    # print len(numbers)
    centerY = []
    for number in numbers:
        center = number[1] + number[3]/2
        centerY.append(center)
    centerY = sorted(centerY)
    scale = 100000000
    for var in range(0, len(centerY)-1):
        diff = centerY[var+1] - centerY[var]
        scale = min(scale, diff)

    scale += 18#compensation
    # print scale

    mp = {}
    for number in numbers:
        numberCropped = cc[number[1]:number[1]+number[3], number[0]:number[0]+number[2]].copy()
        cv2.imwrite("/tmp/y.png", numberCropped)
        try:
            num = OCR().YaxisData()
            if len(num)==0:
                continue
            num = num[0]
            if len(num)==0:
                continue
            data = float(num[0])#is a number
            # print data
            position = number[1] + number[3]/2
            mp[data] = position            
        except:
            continue

    if len(mp)<2:#could not find 2 numbers
        minX, minY = rectangle[0]
        maxX, maxY = rectangle[2]
        currH,currW = maxY-minY, maxX-minX
        cc1 = img[int(minY-0.05*currH):int(maxY+0.1*currH), int(minX-0.1*currW):int(minX+0.01*currW)].copy()
        print "The OCR engine could not recognize the y-axis markings.Press any key to close the window and enter the required values."
        WINDOW_NAME = "Y-Axis"
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_NAME, 400, 800);
        cv2.startWindowThread()
        cv2.imshow(WINDOW_NAME, cc1)

        # activateWindow(WINDOW_NAME)
        time.sleep(0.5)#0.1seconds
        os.system("wmctrl -a Y-Axis")#bring to front
        cv2.waitKey(0)
        cv2.destroyWindow(WINDOW_NAME)
        print "Enter the starting y value:"
        yStart = float(raw_input())
        print "Enter the y axis division:"
        delta = float(raw_input())
        return scale, mx, yStart, delta
    sorted_mp = sorted(mp.items(), key=operator.itemgetter(0))
    leastCount = 100000000
    store = None
    for var in range(0, len(sorted_mp)-1):
        if sorted_mp[var+1][0] - sorted_mp[var][0] < leastCount:
            leastCount = sorted_mp[var+1][0] - sorted_mp[var][0]
            store = var
    # print sorted_mp[store][0], sorted_mp[store+1][0]
    pixelDiff = sorted_mp[store][1] - sorted_mp[store+1][1]
    divisionsInBetween = round(pixelDiff/float(scale))
    delta = float(leastCount)/divisionsInBetween#1
    yStart = sorted_mp[store][0] - round((h-sorted_mp[store][1])/float(scale))*delta#0

    #scale is number of pixels in a division
    #xStart is actual start value
    #delta is the actual difference between 2 consecutive values
    return scale, mx, yStart, delta

def findPlotName(img, rectangle, i, mx=0):
    minX, minY = rectangle[0]
    maxX, maxY = rectangle[2]
    h,w = maxY-minY, maxX-minX

    imgH, imgW = img.shape[:2]

    #first we search below
    cropped = img[min(int(maxY+mx), imgH-1):min(int(maxY+h*0.35), imgH-1), int(minX-0.05*w):maxX].copy()
    cc = cropped.copy()

    cropped = cv2.cvtColor(cc, cv2.COLOR_BGR2GRAY)
    _,cropped = cv2.threshold(cropped, 250, 255, 1)

    kernel = np.ones((3,3),np.uint8)
    cropped = cv2.dilate(cropped, kernel, iterations=10)#dilate to get numbers
    _,contours, hierarchy = cv2.findContours(cropped, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print len(contours)
    
    maxArea = -1
    plotName = None
    h,w = cc.shape[:2]
    areaThreshold = 0.05 * h * w
    for cnt in contours:
        box = cv2.boundingRect(cnt)
        contourArea = box[2]*box[3]

        if contourArea < areaThreshold:
            continue

        if contourArea > maxArea:
            maxArea = contourArea
            plotName = box

    if plotName == None:
        #first we search below
        h,w = maxY-minY, maxX-minX
        cropped = img[max(int(minY-h*0.20), 0):minY, int(minX-0.05*w):maxX].copy()
        cc = cropped.copy()

        cropped = cv2.cvtColor(cc, cv2.COLOR_BGR2GRAY)
        _,cropped = cv2.threshold(cropped, 250, 255, 1)

        kernel = np.ones((3,3),np.uint8)
        cropped = cv2.dilate(cropped, kernel, iterations=10)#dilate to get numbers
        _,contours, hierarchy = cv2.findContours(cropped, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(cropped, contours, -1, (127), 3 )
        # cv2.imwrite('yoyo'+str(i)+'.png', cropped)
        print "lenyy=",len(contours)
        
        maxArea = -1
        h,w = cc.shape[:2]
        areaThreshold = 0.01 * h * w
        for cnt in contours:
            box = cv2.boundingRect(cnt)
            contourArea = box[2]*box[3]

            if contourArea < areaThreshold:
                continue

            if contourArea > maxArea:
                maxArea = contourArea
                plotName = box

    if plotName != None:
    # cv2.rectangle(cc,(plotName[0],plotName[1]),(plotName[0] + plotName[2],plotName[1] + plotName[3]),(0,255,0),1)
    # cv2.imwrite('plotName' + str(i) + '.png', cc)
        plotName = cc[plotName[1]:plotName[1]+plotName[3], plotName[0]:plotName[0]+plotName[2]]
        cv2.imwrite('plotName' + str(i) + '.png', plotName)

    # print plotName
    return plotName

def findXLabel(img, rectangle, mx, i):
    #returns image object reprsenting the x label
    minX, minY = rectangle[0]
    maxX, maxY = rectangle[2]
    h,w = maxY-minY, maxX-minX
    cropped = img[int(maxY+mx):int(maxY+0.2*h), int(minX+0.1*w):int(maxX-0.1*w)].copy()
    cc = cropped.copy()

    cropped = cv2.cvtColor(cc, cv2.COLOR_BGR2GRAY)
    _,cropped = cv2.threshold(cropped, 250, 255, 1)

    kernel = np.ones((1,3),np.uint8)
    cropped = cv2.dilate(cropped, kernel, iterations=10)#dilate to get numbers
    _,contours, hierarchy = cv2.findContours(cropped, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    topY = 100000000
    xLabel = None
    h,w = cc.shape[:2]
    thresholdArea = 0.01*h*w
    for cnt in contours:
        box = cv2.boundingRect(cnt)
        contourArea = box[2]*box[3]
        if contourArea < thresholdArea:
            continue
        if (box[1]+box[3]/2) < topY:
            topY = box[1]+box[3]/2
            xLabel = box

    # cv2.rectangle(cc,(xLabel[0],xLabel[1]),(xLabel[0] + xLabel[2],xLabel[1] + xLabel[3]),(0,255,0),1)
    # cv2.imwrite('xLabel' + str(i) + '.png', cc)
    mx = xLabel[1]+xLabel[3] + mx
    xLabel = cc[xLabel[1]:xLabel[1]+xLabel[3], xLabel[0]:xLabel[0]+xLabel[2]]
    cv2.imwrite('xLabel' + str(i) + '.png', xLabel)
    return xLabel, mx

def findYLabel(img, rectangle, mx, i):
    #returns image object reprsenting the y label
    minX, minY = rectangle[0]
    maxX, maxY = rectangle[2]
    h,w = maxY-minY, maxX-minX
    cropped = img[int(minY+0.1*h):int(maxY-0.1*h), max(0, int(minX - 0.2*w)):max(0, int(minX-0.1*w+mx))].copy()
    cc = cropped.copy()

    # cv2.imwrite('cropped'+str(i)+'.png', cropped)

    cropped = cv2.cvtColor(cc, cv2.COLOR_BGR2GRAY)
    _,cropped = cv2.threshold(cropped, 250, 255, 1)

    kernel = np.ones((3,1),np.uint8)
    cropped = cv2.dilate(cropped, kernel, iterations=10)#dilate to get numbers
    _,contours, hierarchy = cv2.findContours(cropped, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    yLabel = None
    maxArea = -1
    for cnt in contours:
        box = cv2.boundingRect(cnt)
        contourArea = box[2]*box[3]
        if contourArea > maxArea:
            maxArea = contourArea
            yLabel = box

    # cv2.rectangle(cc,(yLabel[0],yLabel[1]),(yLabel[0] + yLabel[2],yLabel[1] + yLabel[3]),(0,255,0),1)
    # cv2.imwrite('yyLabel' + str(i) + '.png', cc)
    if yLabel != None:
        yLabel = cc[yLabel[1]:yLabel[1]+yLabel[3], yLabel[0]:yLabel[0]+yLabel[2]].copy()
        yLabel = np.rot90(yLabel, 3)
        cv2.imwrite('yLabel' + str(i) + '.png', yLabel)
    return yLabel

def containsRectangle(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    height, width = img.shape[:2]
    square = None
    maxArea = -1
    _,img = cv2.threshold(img, 250, 255, 1)
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
                if contourArea > maxArea:
                    square = cnt
                    maxArea = contourArea
    if square!=None:
        square = makeConventionalRectangle(square)
    return square

def canMergeLabel(label1, label2):
    delta = 5
    if label1[3]+delta<label2[1] or label2[3]+delta<label1[1]:
        return False
    return True

def mergeLabel(label1, label2):
    minX = min(label1[0], label2[0])
    minY = min(label1[1], label2[1])
    maxX = max(label1[2], label2[2])
    maxY = max(label1[3], label2[3])
    return (minX, minY, maxX, maxY)

def findLabels(i, img):
    #Returns contour for legend text inside img(plot)
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)        
    #black
    lowerBlack = np.array([0, 0, 0], dtype=np.uint8)
    upperBlack = np.array([180, 255, 15], dtype=np.uint8)
    mask = cv2.inRange(imgHSV, lowerBlack, upperBlack)

    kernel = np.ones((2,2),np.uint8)
    mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN, kernel)#open to remove white noise
    kernel = np.ones((3,3),np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=25)#dilate to join white pixels in legend
    # cv2.imwrite('mask'+str(i)+'.png', mask)

    #Find max area contour
    _,contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    height, width = mask.shape[:2]
    thresholdArea = int((height*width)*0.01)
    legend = None
    maxArea = -1
    for cnt in contours:
        if len(cnt) < 4:
            continue
        contourArea = cv2.contourArea(cnt)
        if (contourArea < thresholdArea):
            continue

        if contourArea < maxArea:
            continue
        cnt_len = cv2.arcLength(cnt, True)
        cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
        legend = cnt
        maxArea = cv2.contourArea(cnt)
    
    if legend == None:
      print "legend not found"
      return None

    x,y,w,h = cv2.boundingRect(legend)
    #crop legend
    legendImg = img[y:y+h, x:x+w].copy()
    square = containsRectangle(legendImg)
    if square!=None:
        x+=square[0][0]+8
        y+=square[0][1]+8
        w=square[2][0] - square[0][0] - 16
        h=square[2][1] - square[0][1] - 16

    #Draw legend on img
    cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),1)
    cv2.imwrite('legend'+str(i)+'.png', img)

    legendImg = img[y:y+h, x:x+w].copy()
    offsetX, offsetY = x,y #save 
    imgHSV = cv2.cvtColor(legendImg, cv2.COLOR_BGR2HSV)        
    #black
    lowerBlack = np.array([0, 0, 0], dtype=np.uint8)
    upperBlack = np.array([180, 255, 10], dtype=np.uint8)
    mask = cv2.inRange(imgHSV, lowerBlack, upperBlack)

    # mask = cv2.erode(mask, kernel, iterations=1)
    # kernel = np.ones((3,3),np.uint8)
    # mask = cv2.dilate(mask, kernel, iterations=2)#dilate once in all directions
    kernel = np.ones((1,3),np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=5)#dilate to join white pixels in legend
    cv2.imwrite('horizontalmask'+str(i)+'.png', mask)

    #Find max area contour
    _,contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    labels = []
    for cnt in contours:
        cnt_len = cv2.arcLength(cnt, True)
        cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
        x,y,w,h = cv2.boundingRect(cnt)
        labels.append((x,y,x+w,y+h))

    # for (x1,y1,x2,y2) in labels:
    #     cv2.rectangle(legendImg,(x1,y1),(x2,y2),(0,255,0),1)

    mergedLabels = []
    for label in labels:
        temp = []
        mergedLabel = label
        for m in mergedLabels:
            if canMergeLabel(mergedLabel, m):
                mergedLabel = mergeLabel(mergedLabel, m)
            else:
                temp.append(m)
        temp.append(mergedLabel)
        mergedLabels = temp
    
    height, width = legendImg.shape[:2]
    thresholdArea = height*width*(1.0/60.0) #1/60 of area
    labels = []
    for m in mergedLabels:
        if (m[2]-m[0])*(m[3]-m[1]) > thresholdArea:
            labels.append((m[0]+offsetX, m[1]+offsetY, m[2]+offsetX, m[3]+offsetY))#make label w.r.t plot

    return labels

def findColours(labels, img, i):
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    height, width = img.shape[:2]
    expansion = int(width*0.1)
    colouredPixelThreshold = 20#all answers were more than 100

    returnMap = {}
    for index, label in enumerate(labels):
        x1 = (label[0]+4*label[2])/5
        x2 = min(label[2]+expansion, width-1)
        # cv2.imwrite('label'+str(index)+'.png', img[label[1]:label[3], x1:x2])
        temp = img[label[1]:label[3], x1:x2].copy()
        mask = getLabelMask(temp)
        
        # cv2.imwrite('labelmask'+str(index)+'.png', mask)

        mp = {}
        h,w = mask.shape[:2]
        for x in range(0, w):
            for y in range(0, h):
                if mask[y][x]!=0:#coloured
                    hue = imgHSV[y+label[1]][x+x1][0]
                    if hue not in mp:
                        mp[hue] = 0
                    mp[hue]+=1

        maxCount = -1
        maxHue = None
        for hue in mp:
            if mp[hue] > maxCount:
                maxCount = mp[hue]
                maxHue = hue
        
        if maxHue == None:
            # print index
            continue
        sorted_mp = sorted(mp.items(), key=operator.itemgetter(1))
        sorted_mp.reverse()
        size = min(10, len(sorted_mp))
        sorted_mp = sorted_mp[0:size]
        mp2 = {}
        for k1,v1 in sorted_mp:
            ans=0
            for k2,v2 in sorted_mp:
                if k1-5<k2 and k2<k1+5:#nearby hue
                    ans+=v2
            mp2[k1] = ans

        sorted_mp = sorted(mp2.items(), key=operator.itemgetter(1))
        sorted_mp.reverse()
        maxHue = sorted_mp[0][0]
        maxCount = sorted_mp[0][1]
            
        # print maxHue, maxCount
        if maxCount<colouredPixelThreshold:#no coloured line found to right
            continue    

        returnMap[index] = maxHue

    if len(returnMap)!=0:
        return returnMap


    #look into left
    for index, label in enumerate(labels):
        x1 = max(0, label[0]-expansion)
        x2 = (4*label[0]+label[2])/5
        # cv2.imwrite('label'+str(i)+str(index)+'.png', img[label[1]:label[3], x1:x2])
        temp = img[label[1]:label[3], x1:x2].copy()
        mask = getLabelMask(temp)
        
        # cv2.imwrite('labelmask'+str(i)+str(index)+'.png', mask)

        mp = {}
        h,w = mask.shape[:2]
        for x in range(0, w):
            for y in range(0, h):
                if mask[y][x]!=0:#coloured
                    hue = imgHSV[y+label[1]][x+x1][0]
                    if hue not in mp:
                        mp[hue] = 0
                    mp[hue]+=1

        maxCount = -1
        maxHue = None
        for hue in mp:
            if mp[hue] > maxCount:
                maxCount = mp[hue]
                maxHue = hue
        
        if maxHue == None:
            # print index
            continue        
        sorted_mp = sorted(mp.items(), key=operator.itemgetter(1))
        sorted_mp.reverse()
        size = min(10, len(sorted_mp))
        sorted_mp = sorted_mp[0:size]
        mp2 = {}
        for k1,v1 in sorted_mp:
            ans=0
            for k2,v2 in sorted_mp:
                if k1-5<k2 and k2<k1+5:#nearby hue
                    ans+=v2
            mp2[k1] = ans

        sorted_mp = sorted(mp2.items(), key=operator.itemgetter(1))
        sorted_mp.reverse()
        maxHue = sorted_mp[0][0]
        maxCount = sorted_mp[0][1]
        if maxCount<colouredPixelThreshold:#no coloured line found to right
            continue    

        returnMap[index] = maxHue
        # cv2.imwrite('yoyo'+str(i)+'.png', img)

    return returnMap

def isBoundaryRectangle(r, imgArea):
    contourArea = cv2.contourArea(r)
    # print contourArea, imgArea
    #check if area is 90%
    if float(contourArea) > 0.9 * float(imgArea):
        return True
    return False

def makeConventionalRectangle(r):
    #Counter-clock, 1st point is top left
    #makes proper rectangle
    r = r.tolist()
    r.sort(key=lambda x: x[0])
    if r[0][1] > r[1][1]:
        r[0], r[1] = r[1], r[0]

    if r[3][1] > r[2][1]:
        r[3], r[2] = r[2], r[3]

    minX = min(r[0][0], r[1][0])
    maxX = max(r[2][0], r[3][0])
    minY = min(r[0][1], r[3][1])
    maxY = max(r[1][1], r[2][1])

    r = [[minX, minY], [minX, maxY], [maxX, maxY], [maxX, minY]]
    r = np.array(r, dtype=np.int32)
    return r

def makeConventionalRectangles(rectangles):
    conventionalRectangles = []
    for rectangle in rectangles:
        conventionalRectangles.append(makeConventionalRectangle(rectangle))
    return conventionalRectangles

def getLabelMask(img):
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

    imgGRAY = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lowerWhite = np.array([250], dtype=np.uint8)
    upperWhite = np.array([255], dtype=np.uint8)
    maskWhite = cv2.inRange(imgGRAY, lowerWhite, upperWhite)

    lowerBlack = np.array([0], dtype=np.uint8)
    upperBlack = np.array([5], dtype=np.uint8)
    maskBlack = cv2.inRange(imgGRAY, lowerBlack, upperBlack)

    mask1 = cv2.bitwise_or(maskWhite, maskBlack)
    mask1 = cv2.bitwise_not(mask1)

    mask = cv2.bitwise_and(mask, mask1)

    return mask

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
    #and not boundary rectangle
    thresholdArea = int((height*width)*0.01)
    prunedRectangles = []
    for rectangle in rectangles:
        contourArea = cv2.contourArea(rectangle)
        if (contourArea > thresholdArea) and (not isBoundaryRectangle(rectangle, height*width)):
            prunedRectangles.append(rectangle)

    return prunedRectangles

def mergeRectangles(rectangles, height, width): 
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

def isColoured(rectangle, mask):
    x1,y1 = rectangle[0]
    x2,y2 = rectangle[2]
    croppedMask = mask[y1:y2, x1:x2].copy()
    numColouredPixels = cv2.countNonZero(croppedMask)
    colouredPixelThreshold = 50
    if numColouredPixels>=colouredPixelThreshold:
        return True
    else:
        return False

    # minX, minY = rectangle[0]
    # maxX, maxY = rectangle[2]
    
    # #optimization: intead of looking in complete rectangle
    # #look into a 20% width strip in middle of rectangle
    # stripWidth = int((maxX - minX)*0.1)
    # midX = (minX + maxX)/2
    # xStart = max(0, midX - stripWidth)
    # xEnd = min(maxX, midX + stripWidth)

    # numColouredPixels = 0 #avoid stray coloured pixels inside tables
    # colouredPixelThreshold = 10#less because only in strip
    # for x in range(xStart, xEnd+1):
    #     for y in range(minY, maxY+1):
    #         if mask[y][x]!=0:#coloured pixel
    #             numColouredPixels += 1
    #             if numColouredPixels >= colouredPixelThreshold:
    #                 return True
    # return False #not coloured

def getColouredRectangles(rectangles, mask):
    colouredRectangles = []
    for rectangle in rectangles:
        if isColoured(rectangle, mask):
            colouredRectangles.append(rectangle)
    return colouredRectangles

if __name__ == '__main__':
    from glob import glob
    for fn in glob('data/'+sys.argv[1]+'.png'):
        img = cv2.imread(fn)
        height, width = img.shape[:2]       
        
        imgCopy = img.copy()
        rectangles = findRectangles(imgCopy)
        print "all rectangles = ", len(rectangles)
        # rectangles = pruneRectangles(rectangles, height, width)
        # print "pruned rectangle = ", len(rectangles)
        # rectangles = makeConventionalRectangles(rectangles)#make proper rectangles
        # rectangles = mergeRectangles(rectangles, height, width)
        # print "merged rectangles = ", len(rectangles)

        mask = getMask(img)
        rectangles = getColouredRectangles(rectangles, mask)
        print "coloured rectangles = ", len(rectangles)

        for i, rectangle in enumerate(rectangles):
            ret = findXScale(img.copy(), rectangle, i)#ret/10 reduces arror a lot
            xLabel, mx = findXLabel(img.copy(), rectangle, ret[1], i)
            xScale = ret[0]
            xStart = ret[2]
            xDelta = ret[3]
            
            #do for y axis
            ret = findYScale(img.copy(), rectangle, i)#ret/10 reduces arror a lot
            yLabel = findYLabel(img.copy(), rectangle, ret[1], i)
            yScale = ret[0]
            yStart = ret[2]
            yDelta = ret[3]

            plotName = findPlotName(img.copy(), rectangle, i, mx)


        for i, rectangle in enumerate(rectangles):
            minX, minY = rectangle[0]
            maxX, maxY = rectangle[2]
            minX += 15
            minY += 15
            maxX -= 15
            maxY -= 15
            plot = img[minY:maxY, minX:maxX]
            plotCopy = plot.copy()
            labels = findLabels(i, plotCopy)
            if labels == None:#could not find legend
                #TODO:error handling
                print "legend not found"
                continue
            plotCopy = plot.copy()
            labelsCopy = copy.copy(labels)
            colourMap = findColours(labelsCopy, plotCopy, i)
            print colourMap            
        
        cv2.drawContours(img, rectangles, -1, (0, 255, 0), 3 )
        cv2.imwrite('rectangles.png', img)

        
        # ch = 0xFF & cv2.waitKey()
        # if ch == 27:
        #     break
    # cv2.destroyAllWindows()
