import numpy as np
import cv2

class Mask:
    def __init__(self, img):
        self.img = img

    def getLabelMask(self):
        #returns mask for coloured pixels
        imgHSV = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

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

        imgGRAY = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
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

    def getMask(self):
        #returns mask for coloured pixels
        imgHSV = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)        
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

        return mask