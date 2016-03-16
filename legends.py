import numpy as np
import cv2
import copy
import operator

from plot_rectangles import PlotRectangles
from masker import Mask

class Legends:
  def __init__(self, rectangle, img):
    minX, minY = rectangle[0]
    maxX, maxY = rectangle[2]
    minX += 15
    minY += 15
    maxX -= 15
    maxY -= 15

    self.plot = img[minY:maxY, minX:maxX].copy()

  def getLegend(self, i):
    labels = self.findLabels(i)

    if labels == None:
      #TODO error handling
      return None  

    labelsCopy = copy.copy(labels)
    colourMap = self.findColours(labelsCopy, i)

    return labels, colourMap

  def findLabels(self, i):
    img = self.plot.copy()

    #Returns contours for legend texts inside img(plot)
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    #black
    lowerBlack = np.array([0, 0, 0], dtype=np.uint8)
    upperBlack = np.array([180, 255, 15], dtype=np.uint8)
    mask = cv2.inRange(imgHSV, lowerBlack, upperBlack)

    kernel = np.ones((2,2),np.uint8)
    mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN, kernel)#open to remove white noise
    kernel = np.ones((3,3),np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=25)#dilate to join white pixels in legend

    _,contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    height, width = mask.shape[:2]
    thresholdArea = int((height*width)*0.01)
    
    #Find max area contour
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
      #Legend not found
      return None

    x,y,w,h = cv2.boundingRect(legend)

    #crop legend
    legendImg = img[y:y+h, x:x+w].copy()
    square = PlotRectangles().containsRectangle(legendImg)

    if square!=None:
      x+=square[0][0]+8
      y+=square[0][1]+8
      w=square[2][0] - square[0][0] - 16
      h=square[2][1] - square[0][1] - 16

    legendImg = img[y:y+h, x:x+w].copy()
    offsetX, offsetY = x,y #save 
    imgHSV = cv2.cvtColor(legendImg, cv2.COLOR_BGR2HSV)

    #black
    lowerBlack = np.array([0, 0, 0], dtype=np.uint8)
    upperBlack = np.array([180, 255, 10], dtype=np.uint8)
    mask = cv2.inRange(imgHSV, lowerBlack, upperBlack)

    kernel = np.ones((1,3),np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=5)#dilate to join white pixels in legend

    #Find max area contour
    _,contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    labels = []
    for cnt in contours:
      cnt_len = cv2.arcLength(cnt, True)
      cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
      x,y,w,h = cv2.boundingRect(cnt)
      labels.append((x,y,x+w,y+h))

    mergedLabels = []

    for label in labels:
      temp = []
      mergedLabel = label
      for m in mergedLabels:
        if self.canMergeLabel(mergedLabel, m):
          mergedLabel = self.mergeLabel(mergedLabel, m)
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

  def canMergeLabel(self, label1, label2):
    delta = 5
    if label1[3]+delta<label2[1] or label2[3]+delta<label1[1]:
        return False
    return True

  def mergeLabel(self, label1, label2):
    minX = min(label1[0], label2[0])
    minY = min(label1[1], label2[1])
    maxX = max(label1[2], label2[2])
    maxY = max(label1[3], label2[3])
    return (minX, minY, maxX, maxY)

  def findColours(self, labels, i):
    img = self.plot.copy()

    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    height, width = img.shape[:2]
    expansion = int(width*0.1)
    colouredPixelThreshold = 20#all answers were more than 100

    returnMap = {}
    for index, label in enumerate(labels):
      x1 = (label[0]+4*label[2])/5
      x2 = min(label[2]+expansion, width-1)

      temp = img[label[1]:label[3], x1:x2].copy()
      m = Mask(temp)
      mask = m.getLabelMask()

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

    if len(returnMap)!=0:
      return returnMap

    #look into left
    for index, label in enumerate(labels):
      x1 = max(0, label[0]-expansion)
      x2 = (4*label[0]+label[2])/5

      temp = img[label[1]:label[3], x1:x2].copy()
      mask = getLabelMask(temp)

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
            ans += v2
        mp2[k1] = ans

      sorted_mp = sorted(mp2.items(), key=operator.itemgetter(1))
      sorted_mp.reverse()
      maxHue = sorted_mp[0][0]
      maxCount = sorted_mp[0][1]
      if maxCount<colouredPixelThreshold:#no coloured line found to right
          continue    

      returnMap[index] = maxHue

    return returnMap