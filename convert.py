import sys
# import ghostscript
import os
import cv2

class Converter:
  def convertPDF(self, pdfPath):
    image_path = '/tmp/pdf_image.png'

    # command = "pdftoppm -r 400 -png -f 1 " + pdfPath + " > " + image_path
    command = "convert -density 400 " + pdfPath + " -quality 100 -sharpen 0x1.0 " + image_path
    # command = 'gs -sstdout=%stderr -dNOPAUSE -dQUIET -dNOPROMPT -dBATCH -sDEVICE=pngalpha -sOutputFile=' + image_path + ' -r400 ' + pdfPath  + ' -c quit 2 >/dev/null'
    os.system(command)

    # args = [
    #   "gs",
    #   "-sstdout=%stderr",
    #   "-dNOPAUSE", "-dQUIET", "-dNOPROMPT", "-dBATCH",
    #   "-sDEVICE=png16m",
    #   "-sOutputFile=" + image_path,
    #   "-r400",
    #   pdfPath,
    #   "-c", "quit", "2>/dev/null"
    # ]

    # ghostscript.Ghostscript(*args)
    

    img = cv2.imread(image_path)
    return img