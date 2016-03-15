import os

filename = 'data/temp2.png'
tempfilename = 'data/temp11.png'
tempOCRoutput = 'temp_data.txt'
os.system('convert ' + filename + ' -resize 400% ' + tempfilename)
os.system('tesseract ' + tempfilename + ' stdout digits > ' + tempOCRoutput)
with open(tempOCRoutput,'r') as output:
	outputdata = output.read()
os.system('rm ' + tempfilename + ' ' + tempOCRoutput)
print outputdata