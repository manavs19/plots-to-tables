"""  Does bfs on the mask. Returns bounding rectangles for the images."""
from collections import deque
import numpy as np
# 30pixels for 3400 width
# 1/100
# take 1/50 as the radius

ratio = 1.0 / 50.0

class BFS:
	def __init__(self, mask):
		self.mask = mask
		self.height = mask.shape[0]
		self.width = mask.shape[1]
		self.heightRadius = int(self.height * ratio)
		self.widthRadius = int(self.width * ratio)
		print self.heightRadius, self.widthRadius
		self.visited = np.zeros((self.height, self.width))		

	def isValid(self, i, j):
		if i<0 or i>=self.height or j<0 or j>=self.width or self.mask[i][j]==0:
			return False
		return True

	def getRectangles(self):
		rectangles = []
		for i in range(0, self.height):
			for j in range(0, self.width):
				if self.mask[i][j]!=0 and self.visited[i][j]==0:#coloured
					rectangle = self.bfs(i,j)
					rectangles.append(rectangle)
					print i,j, rectangle

		return rectangles

	def bfs(self, i, j):
		queue = deque()
		queue.append((i,j))
		self.visited[i][j] = 1

		minJ = j
		minI = i
		maxJ = j
		maxI = i
		while queue:
			i,j = queue.popleft()
			minJ = min(minJ, j)
			minI = min(minI, i)
			maxJ = max(maxJ, j)
			maxI = max(maxI, i)

			for x in range(i-self.heightRadius, i+self.heightRadius+1):
				for y in range(j-self.widthRadius, j+self.widthRadius+1):
					if self.isValid(x,y) and self.visited[x][y]==0:
						# print x,y
						queue.append((x,y))
						self.visited[x][y] = 1

		rectangle = np.array([[minJ,minI],[maxJ,minI],[maxJ,maxI], [minJ, maxI]], dtype=np.int32)
		return rectangle
