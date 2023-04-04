# tracker package for speculative communications
#
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np
class scTracker():
	def __init__(self, maxDisappeared=60):
		# initialize
		self.nextObjectID = 0
		self.objects = OrderedDict()
		self.disappeared = OrderedDict()
		self.maxDisappeared = maxDisappeared

	def register(self, centroid):
		# when registering an object
		self.objects[self.nextObjectID] = centroid
		self.disappeared[self.nextObjectID] = 0
		self.nextObjectID += 1

	def deregister(self, objectID):
		# deregister an object ID 
		del self.objects[objectID]
		del self.disappeared[objectID]

	def update(self, rects):
		if len(rects) == 0:
			# loop and mark
			for objectID in list(self.disappeared.keys()):
				self.disappeared[objectID] += 1
				# if missing
				if self.disappeared[objectID] > self.maxDisappeared:
					self.deregister(objectID)
			return self.objects

		# init input centroids 
		inputCentroids = np.zeros((len(rects), 2), dtype="int")
		# loop over boxees
		for (i, (startX, startY, endX, endY)) in enumerate(rects):
			# calculate centroid
			cX = int(startX + endX / 2.0)
			cY = int(startY + endY / 2.0)
			inputCentroids[i] = (cX, cY)
		# if nothing register each item
		if len(self.objects) == 0:
			for i in range(0, len(inputCentroids)):
				self.register(inputCentroids[i])        
		# otherwise, try to match
		else:
			# grab the set of object IDs and corresponding centroids
			objectIDs = list(self.objects.keys())
			objectCentroids = list(self.objects.values())
			# distances
			D = dist.cdist(np.array(objectCentroids), inputCentroids)
			# find the smallest value and sort
			rows = D.min(axis=1).argsort()
			cols = D.argmin(axis=1)[rows]
			usedRows = set()
			usedCols = set()
			# loop over index tuples
			for (row, col) in zip(rows, cols):
				if row in usedRows or col in usedCols:
					continue
				objectID = objectIDs[row]
				self.objects[objectID] = inputCentroids[col]
				self.disappeared[objectID] = 0

				usedRows.add(row)
				usedCols.add(col)
			unusedRows = set(range(0, D.shape[0])).difference(usedRows)
			unusedCols = set(range(0, D.shape[1])).difference(usedCols)
			# potentially disappeared
			if D.shape[0] >= D.shape[1]:
				for row in unusedRows:
					objectID = objectIDs[row]
					self.disappeared[objectID] += 1
					if self.disappeared[objectID] > self.maxDisappeared:
						self.deregister(objectID)
			# register new
			else:
				for col in unusedCols:
					self.register(inputCentroids[col])
		# return the set of trackable objects
		return self.objects

