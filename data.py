import os

class Data:
  def getData(self, plotFilename, xStart, xDelta, xScale, yStart, yDelta, yScale, colorMap):
    extractedDatafile = '/tmp/extractedDatafile.txt'

    extractCommand = './dataExtractor ' + plotFilename +  " " + extractedDatafile + " "
    extractCommand += str(xStart) + " "
    extractCommand += str(xDelta) + " "
    extractCommand += str(xScale) + " " 
    extractCommand += str(yStart) + " "
    extractCommand += str(yDelta) + " "
    extractCommand += str(yScale) + " "     
    
    for k,v in colorMap.iteritems():
      extractCommand += str(v) + " "

    os.system(extractCommand)
    
    data = []
    with open(extractedDatafile, 'r') as fin:
      for line in fin:
        line = line.strip().split()
        data.append(line)
    # print data
    return data