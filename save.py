def isInsideRectangle(i, j, rectangle):
	dist = cv2.pointPolygonTest(rectangle,(i,j),False)
	if dist==1:
		return 1
	else:
		return 0


def filterRectangles(rectangles, img):
	#filters rectangles that contain at least one coloured pixel
	#merges nearby rectangles. takes max area rectangle

	imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)        
	#white
	lowerWhite = np.array([0,0,0], dtype=np.uint8)
	upperWhite = np.array([0,0,255], dtype=np.uint8)
	maskWhite = cv2.inRange(imgHSV, lowerWhite, upperWhite)

	#black
	lowerBlack = np.array([0, 0, 0], dtype=np.uint8)
	upperBlack = np.array([180, 255, 30], dtype=np.uint8)
	maskBlack = cv2.inRange(imgHSV, lowerBlack, upperBlack)

	mask = cv2.bitwise_or(maskWhite, maskBlack)
	mask = cv2.bitwise_not(mask)

	cv2.imwrite('mask.jpg', mask)
	# print type(mask)
	# print mask.shape
	
	# validRectangles = []
	# height, width = mask.shape
	# for i in range(0, height):
	# 	for j in range(0, width):
	# 		if mask[i][j]!=0:#coloured pixel
	# 			# print mask[i][j]
	# 			tempList = []#list of rectangles that contain pixel i,j		
	# 			for rectangle in rectangles:
	# 				if isInsideRectangle(i, j, rectangle):
	# 					tempList.append(rectangle)

	# 			if tempList:#not empty
	# 				maxArea = 0
	# 				maxRectangle = None
	# 				for rectangle in tempList:
	# 					area = cv2.contourArea(rectangle)
	# 					if area > maxArea:
	# 						maxArea = area
	# 						maxRectangle = rectangle

	# 				temp1 = []
	# 				for r in rectangles:
	# 					temp1.append(r.tolist())
	# 				temp2 = []
	# 				for r in tempList:
	# 					temp2.append(r.tolist())

	# 				tt = [item for item in temp1 if item not in temp2]
	# 				rectangles = []
	# 				for r in tt:
	# 					rectangles.append(np.array(r))
	# 				rectangles.append(maxRectangle)
	# 				validRectangles.append(maxRectangle)

	# return validRectangles