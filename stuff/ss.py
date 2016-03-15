import os

filename = "data/1 (copy).png"
tempfilename = "data/temp1 (copy).png"
tempOCRoutput = "temp_data.txt"
os.system("convert "+filename+" -resize 400% "+tempfilename)
os.system("tesseract "+tempfilename+" stdout digits > "+tempOCRoutput)
with open(tempOCRoutput,'r') as output:
	outputdata = output.read()
os.system("rm "+tempfilename+" "+tempOCRoutput)
print outputdata
