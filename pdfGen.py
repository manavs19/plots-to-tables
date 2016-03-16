from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

class PdfGen:
  
  def __init__(self, filename, csv=False):
    self.filename = filename
    self.elements = []
    self.doc = SimpleDocTemplate(self.filename, pagesize=letter)
    self.csv = csv
    self.tableCount = 0

  def exportAsCsv(self, values):
    csvFile = str(self.tableCount) + '.csv'
    f = open(csvFile, 'w')
    for value in values:
      line=''
      for i in value:
        line=line+str(i)+','
      if len(value)>=1:
        line=line[:-1]
      f.write(line)
      f.write('\n')
    f.close()
    return csvFile

  def add_table(self, graphName, yAxisTitle, labels, values):
    # container for the 'Flowable' objects
    self.tableCount += 1
    graphNameImg = Image(graphName)
    width=7.5*inch
    graphNameImg.drawHeight = width*graphNameImg.drawHeight / graphNameImg.drawWidth
    graphNameImg.drawWidth = width
      
    self.elements.append(graphNameImg)       
   
    yAxisTitleImg = Image(yAxisTitle)
    width=7.5*inch
    yAxisTitleImg.drawHeight = width*yAxisTitleImg.drawHeight / yAxisTitleImg.drawWidth
    yAxisTitleImg.drawWidth = width
      
    self.elements.append(yAxisTitleImg)       
   
    styleSheet = getSampleStyleSheet()
    
    finalLabels=[]
    noOfCols=len(labels)
    for label in labels:
      I = Image(label)
      width=7*inch/noOfCols
      I.drawHeight = width*I.drawHeight / I.drawWidth
      I.drawWidth = width
      finalLabels.append(I)

    noOfRows=len(values)
    data=[finalLabels]
    for x in values:
      data.append(x)
    
    t=Table(data, style=[('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
      ('BOX', (0,0), (-1,-1), 0.25, colors.black),])
    
    self.elements.append(t)
    
    if self.csv == True:
      csvFile = self.exportAsCsv(values)
      ptext = '<font size=24>CSV exported to %s</font>' % csvFile
      self.elements.append(Paragraph(ptext, styleSheet["Normal"]))
    
    self.elements.append(PageBreak())
    
  def print_file(self):
    self.doc.build(self.elements)
