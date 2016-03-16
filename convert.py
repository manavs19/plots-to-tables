import sys
import ghostscript
import os
import cv2

class Converter:
  def convertPDF(self, pdfPath):
    image_path = '/tmp/pdf_image.png'

    args = [
      "gs",
      "-dNOPAUSE", "-dQUIET", "-dNOPROMPT", "-dBATCH",
      "-sDEVICE=png16m",
      "-sOutputFile=" + image_path,
      "-r400",
      pdfPath,
      "-c", "quit"
    ]

    ghostscript.Ghostscript(*args)

    img = cv2.imread(image_path)
    return img