import numpy as np
import cv2

class PlotName:
  def __init__(self, img):
    self.img = img

  def getPlotName(self, rectangle, i, mx=0):
    img = self.img

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
      #Now we search up
      h,w = maxY-minY, maxX-minX
      cropped = img[max(int(minY-h*0.20), 0):minY, int(minX-0.05*w):maxX].copy()
      cc = cropped.copy()

      cropped = cv2.cvtColor(cc, cv2.COLOR_BGR2GRAY)
      _,cropped = cv2.threshold(cropped, 250, 255, 1)

      kernel = np.ones((3,3),np.uint8)
      cropped = cv2.dilate(cropped, kernel, iterations=10)#dilate to get numbers
      _,contours, hierarchy = cv2.findContours(cropped, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      
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
      plotName = cc[plotName[1]:plotName[1]+plotName[3], plotName[0]:plotName[0]+plotName[2]]

    plotNamePath = '/tmp/plotName' + str(i) + '.png'
    cv2.imwrite(plotNamePath, plotName)

    return plotNamePath
