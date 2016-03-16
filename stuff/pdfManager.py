from pyPdf import PdfFileWriter, PdfFileReader
import sys
import ghostscript
import os

class PDFManager:
	def __init__(self, pdfPath):
		self.pdfPath = pdfPath
		self.pdf = PdfFileReader(file(pdfPath, "rb"))
		self.page = self.pdf.getPage(0)
		self.width = float(self.page.mediaBox.getUpperRight_x())#float
		self.height = float(self.page.mediaBox.getUpperRight_y())

	#lowerleft, upperright ratios
	#crops this portion of pdf and creates png at pngPath
	def crop(self, lowerX, lowerY, upperX, upperY, pngPath):
		lowerX = lowerX * self.width
		lowerY = lowerY * self.height
		upperX = upperX * self.width
		upperY = upperY * self.height

		self.page = self.pdf.getPage(0)
		self.page.cropBox.lowerLeft = (lowerX, lowerY)
		self.page.cropBox.upperRight = (upperX, upperY)

		output = PdfFileWriter()
		output.addPage(self.page)

		outputStream = file("/tmp/out.pdf", "wb")
		output.write(outputStream)
		outputStream.close()

		# os.system("convert -density 400 /tmp/out.pdf -quality 100 -sharpen 0x1.0 " + pngPath)
		os.system("convert /tmp/out.pdf " + pngPath)

		# args = [
		#     "gs",
		#     "-dNOPAUSE", "-dQUIET", "-dNOPROMPT",
		#     "-sDEVICE=pngalpha",
		#     "-sOutputFile=" + pngPath,
		#     "-r400",
		#     "/tmp/out.pdf",
		#     "-c", "quit"
		# ]

		# ghostscript.Ghostscript(*args)


	def convertPDFToPNG(self, pngPath):
		args = [
		    "gs",
		    "-dNOPAUSE", "-dQUIET", "-dNOPROMPT", "-dBATCH",
		    "-sDEVICE=png16m",
		    "-sOutputFile=" + pngPath,
		    "-r400",
		    self.pdfPath,
		    "-c", "quit"
		]

		ghostscript.Ghostscript(*args)


x = PDFManager("data/3.pdf")
# x.convertPDFToPNG("data/3gs.png")
x.crop(0.25, 0.25, 0.5, 0.5, "data/out.png")
# x.crop(0.75, 0.75, 0.95, 0.95, "data/out1.pdf")
