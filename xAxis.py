import numpy as np
import operator
import cv2
import time
import os

from axisOcr import OCR

class XAxis:

  def __init__(self, img):
    self.img = img

  def findXScale(self, rectangle, i):
    img = self.img.copy()

    minX, minY = rectangle[0]
    maxX, maxY = rectangle[2]

    h, w = maxY-minY, maxX-minX

    cropped = img[int(maxY+0.01*h):int(maxY+0.1*h), minX:maxX].copy()
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

    temp = []

    for number in numbers:
      numCenter = number[1] + number[3]/2
      if maxCenter - 5 <= numCenter and numCenter <= maxCenter + 5:
        temp.append(number)

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

    if len(mp)<2: #could not find 2 numbers
      xStart, xDelta = self.handle_ocr_failure(rectangle, img)
      return scale, mx, xStart, xDelta

    sorted_mp = sorted(mp.items(), key=operator.itemgetter(0))

    leastCount = 100000000
    store = None

    for var in range(0, len(sorted_mp)-1):
      if sorted_mp[var+1][0] - sorted_mp[var][0] < leastCount:
        leastCount = sorted_mp[var+1][0] - sorted_mp[var][0]
        store = var

    pixelDiff = sorted_mp[store+1][1] - sorted_mp[store][1]
    divisionsInBetween = round(pixelDiff/float(scale))

    delta = float(leastCount)/divisionsInBetween
    xStart = sorted_mp[store][0] - round(sorted_mp[store][1]/float(scale))*delta#0

    # scale is number of pixels in a division
    # xStart is actual start value
    # delta is the actual difference between 2 consecutive values
    return scale, mx, xStart, delta

  def handle_ocr_failure(self, rectangle, img):
    minX, minY = rectangle[0]
    maxX, maxY = rectangle[2]
    currH,currW = maxY-minY, maxX-minX

    userImage = img[int(maxY-0.01*currH):int(maxY+0.1*currH), int(minX-0.1*currW):int(maxX + 0.05*currW)].copy()

    print "The OCR engine could not recognize the x-axis markings.Press any key to close the window and enter the required values."

    WINDOW_NAME = "X-Axis"
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, 800, 400);
    cv2.startWindowThread()
    cv2.imshow(WINDOW_NAME, userImage)

    time.sleep(0.5) #0.5 seconds
    os.system("wmctrl -a X-Axis") #bring to front
    cv2.waitKey(0)
    cv2.destroyWindow(WINDOW_NAME)

    print "Enter the starting x value:"
    xStart = float(raw_input())
    print "Enter the x axis division:"
    xDelta = float(raw_input())

    return xStart, xDelta

  def findXLabel(self, rectangle, mx, i):
    img = self.img.copy()
    
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

    mx = xLabel[1]+xLabel[3] + mx
    xLabel = cc[xLabel[1]:xLabel[1]+xLabel[3], xLabel[0]:xLabel[0]+xLabel[2]]

    return xLabel, mx