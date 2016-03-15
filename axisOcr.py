from pytesseract import pytesseract as pt
try:
	import Image
except ImportError:
	from PIL import Image

xAxisFile = '/tmp/x.png'
yAxisFile = '/tmp/y.png'
class OCR:
	
	def XaxisData(self):
		try:
			pt.run_tesseract(xAxisFile, '/tmp/x_temp', None, True, '-psm 7 nobatch digits')
			filename = '/tmp/x_temp.box'
			xData = open(filename , "r")
			d = xData.read()
			xData.close()
			data_lines = d.split('\n')
			del d
			data = []
			for line in data_lines:
				l = []
				x = line.split(" ")
				if(len(x) == 6):
					if(x[0].isdigit() or x[0] == '.' or x[0] == '-'):
						l.append(0)
					else:
						l.append(1)

					l.append(x[0])
					l.append(int(x[1]))
					l.append(int(x[2]))
					l.append(int(x[3]))
					l.append(int(x[4]))
					data.append(l)

			# here first data being 0 means first is a number 
			# now the tough part begins here 
			# we will go through all the thichkness and get the maximum thichkness
			max = 0
			for line in data:
				if(abs(line[4] - line[2]) > max):
					max = abs(line[4] - line[2])

			l = []
			new_data = []
			for i in range(len(data) - 1):
				l.append(data[i])
				if(abs(data[i][4]-data[i+1][2]) > max):
					new_data.append(list(l))
					l[:] = []

			l.append(data[-1])
			new_data.append(list(l))

			for data in list(new_data):
				for d in data:
					if(d[0] == 1):
						new_data.remove(data)
						break

			new_new_data = []
			for data in new_data:
				l = []
				s = ""
				for d in data:
					s = s + d[1]
				l.append(float(s))
				if(len(data)%2 == 0):
					avg = (data[(len(data)-1)/2][2] + data[(len(data)-1)/2][4])/2
					l.append(avg)
				else:
					avg = (data[(len(data))/2 -1][2] + data[(len(data)-1)/2][4])/2
					l.append(avg)
				new_new_data.append(l)

			return new_new_data
		except:
			return []

	def YaxisData(self):
		try:
			pt.run_tesseract(yAxisFile, '/tmp/y_temp', None, True, '-psm 3 nobatch digits')
			filename = '/tmp/y_temp.box'
			yData = open(filename , "r")
			d = yData.read()
			yData.close()
			data_lines = d.split('\n')
			del d
			data = []
			for line in data_lines:
				l = []
				x = line.split(" ")
				if(len(x) == 6):
					if(x[0].isdigit() or x[0] == '.' or x[0] == '-'):
						l.append(0)
					else:
						l.append(1)

					l.append(x[0])
					l.append(int(x[1]))
					l.append(int(x[2]))
					l.append(int(x[3]))
					l.append(int(x[4]))
					data.append(l)

			# we need to take max distance between 2 and 4
			max = 0
			for line in data:
				if(abs(line[5] - line[3]) > max):
					max = abs(line[5] - line[3])

			l = []
			new_data = []
			for i in range(len(data) - 1):
				l.append(data[i])
				if(abs(data[i][3]-data[i+1][5]) > max):
					new_data.append(list(l))
					l[:] = []

			l.append(data[-1])
			new_data.append(list(l))

			for data in list(new_data):
				for d in data:
					if(d[0] == 1):
						new_data.remove(data)
						break

			new_new_data = []
			for data in new_data:
				l = []
				s = ""
				for d in data:
					s = s + d[1]
				l.append(float(s))
				avg = (data[-1][5] + data[-1][3])/2
				l.append(avg)
				new_new_data.append(l)

			return new_new_data
		except:
			return []


