import numpy as np
import cv2
import operator
import time
import os

from axisOcr import OCR

class YAxis:

  def __init__(self, img):
    self.img = img

  def findYScale(self, rectangle, i, no_interrupt):
    img = self.img.copy()

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

    h,w = cropped.shape[:2]
    thresholdArea = h*w*0.01
    numbers = []
    for cnt in contours:
      if len(cnt)<4:
        continue

      box = cv2.boundingRect(cnt)

      contourArea = box[2]*box[3]
      if contourArea < thresholdArea:
        continue

      numbers.append(box)

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

    temp = []

    for number in numbers:
      numCenter = number[0] + number[2]/2
      if maxCenter - 5 <= numCenter and numCenter <= maxCenter + 5:
        temp.append(number)

    numbers = temp
    mx = 100000000

    for number in numbers:
      mx = min(mx, number[0])
    
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
      if no_interrupt:
        yStart = 0
        yDelta = scale
      else:
        yStart, yDelta = self.handle_ocr_failure(rectangle, img)
      return scale, mx, yStart, yDelta

    sorted_mp = sorted(mp.items(), key=operator.itemgetter(0))
    leastCount = 100000000
    store = None

    for var in range(0, len(sorted_mp)-1):
      if sorted_mp[var+1][0] - sorted_mp[var][0] < leastCount:
        leastCount = sorted_mp[var+1][0] - sorted_mp[var][0]
        store = var

    pixelDiff = sorted_mp[store][1] - sorted_mp[store+1][1]
    divisionsInBetween = round(pixelDiff/float(scale))
    yDelta = float(leastCount)/divisionsInBetween#1
    yStart = sorted_mp[store][0] - round((h-sorted_mp[store][1])/float(scale))*yDelta#0

    #scale is number of pixels in a division
    #xStart is actual start value
    #delta is the actual difference between 2 consecutive values
    return scale, mx, yStart, yDelta

  def handle_ocr_failure(self, rectangle, img):
    minX, minY = rectangle[0]
    maxX, maxY = rectangle[2]
    currH, currW = maxY-minY, maxX-minX

    user_image = img[int(minY-0.05*currH):int(maxY+0.1*currH), int(minX-0.1*currW):int(minX+0.01*currW)].copy()

    print "The OCR engine could not recognize the y-axis markings.Press any key to close the window and enter the required values."
    
    WINDOW_NAME = "Y-Axis"
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 400, 800);
    cv2.startWindowThread()
    cv2.imshow(WINDOW_NAME, user_image)

    time.sleep(0.5) #0.5seconds
    os.system("wmctrl -a Y-Axis") #bring to front
    cv2.waitKey(0)
    cv2.destroyWindow(WINDOW_NAME)

    while True:
      try:
        print "Enter the starting y value:"
        yStart = float(raw_input())
        break
      except ValueError:
        print "Enter valid y value"

    while True:
      try:
        print "Enter the y axis division:"
        yDelta = float(raw_input())
        break
      except ValueError:
        print "Enter valid y axis division value"

    return yStart, yDelta

  def findYLabel(self, rectangle, mx, i):
    img = self.img.copy()

    minX, minY = rectangle[0]
    maxX, maxY = rectangle[2]
    h,w = maxY-minY, maxX-minX
    
    cropped = img[int(minY+0.1*h):int(maxY-0.1*h), max(0, int(minX - 0.2*w)):max(0, int(minX-0.1*w+mx))].copy()
    cc = cropped.copy()

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

    if yLabel != None:
      yLabel = cc[yLabel[1]:yLabel[1]+yLabel[3], yLabel[0]:yLabel[0]+yLabel[2]].copy()
      yLabel = np.rot90(yLabel, 3)

    yLabelPath = '/tmp/ylabel' + str(i) + '.png'
    cv2.imwrite(yLabelPath, yLabel)

    return yLabelPath