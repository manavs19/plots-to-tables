from pyPdf import PdfFileWriter, PdfFileReader

input1 = PdfFileReader(file("data/3.pdf", "rb"))
output = PdfFileWriter()

print "title = %s" % (input1.getDocumentInfo().title)
page = input1.getPage(0)

# print page.mediaBox.getUpperRight_x(), page.mediaBox.getUpperRight_y()

page.cropBox.lowerLeft = (50, 50)
page.cropBox.upperRight = (600, 790)
output.addPage(page)

outputStream = file("data/out.pdf", "wb")
output.write(outputStream)
outputStream.close()