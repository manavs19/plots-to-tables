import numpy as np
import cv2
import math

from masker import Mask

class PlotRectangles:

  def getRectangles(self, img):
    imgCopy = img.copy()
    all_rectangles = self.findRectangles(imgCopy)
    mask = Mask(img).getMask()
    colored_rectangles = self.findColouredRectangles(all_rectangles, mask)

    return colored_rectangles

  def findColouredRectangles(self, rectangles, mask):
    colouredRectangles = []
    for rectangle in rectangles:
      if self.isColoured(rectangle, mask):
        colouredRectangles.append(rectangle)
    return colouredRectangles

  def isColoured(self, rectangle, mask):
    x1,y1 = rectangle[0]
    x2,y2 = rectangle[2]
    croppedMask = mask[y1:y2, x1:x2].copy()
    numColouredPixels = cv2.countNonZero(croppedMask)
    colouredPixelThreshold = 50
    if numColouredPixels>=colouredPixelThreshold:
      return True
    else:
      return False

  def findRectangles(self, img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    height, width = img.shape[:2]
    rectangles = []

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
      cnt = cv2.approxPolyDP(cnt, 0.001*cnt_len, True)

      thresholdLen = cnt_len * 0.02
      xMin = 1000000
      yMin = 1000000
      xMax = -1
      yMax = -1
      cnt = cnt.tolist()

      for i in range(0, len(cnt)-1):
        if self.getDist(cnt[i][0][0], cnt[i][0][1], cnt[i+1][0][0], cnt[i+1][0][1]) > thresholdLen:
          xMin = min(xMin, cnt[i][0][0])
          xMin = min(xMin, cnt[i+1][0][0])
          yMin = min(yMin, cnt[i][0][1])
          yMin = min(yMin, cnt[i+1][0][1])

          xMax = max(xMax, cnt[i][0][0])
          xMax = max(xMax, cnt[i+1][0][0])
          yMax = max(yMax, cnt[i][0][1])
          yMax = max(yMax, cnt[i+1][0][1])

      if self.getDist(cnt[0][0][0], cnt[0][0][1], cnt[len(cnt)-1][0][0], cnt[len(cnt)-1][0][1]) > thresholdLen:
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
      rectangles.append(cnt)

    return rectangles

  def containsRectangle(self, img):
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
        max_cos = np.max([self.angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
        if max_cos < 0.1:
          if contourArea > maxArea:
            square = cnt
            maxArea = contourArea

    if square!=None:
      square = self.makeConventionalRectangle(square)

    return square

  def makeConventionalRectangle(self, r):
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

  def makeConventionalRectangles(self, rectangles):
    conventionalRectangles = []

    for rectangle in rectangles:
      conventionalRectangles.append(self.makeConventionalRectangle(rectangle))

    return conventionalRectangles

  def angle_cos(self, p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

  def getDist(self, x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)