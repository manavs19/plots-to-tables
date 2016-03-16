import sys
# import ghostscript
import os
import cv2

class Converter:
  def convertPDF(self, pdfPath):
    image_path = '/tmp/pdf_image.png'

    command = "convert -density 400 " + pdfPath + " -quality 100 -sharpen 0x1.0 " + image_path
    os.system(command)

    img = cv2.imread(image_path)
    return img