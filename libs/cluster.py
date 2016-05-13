import heapq
import numpy as np

# Represents a cluster of points with additional information stored
class Cluster:
	
	## Create cluster of points
	@staticmethod
	def fromPoints(clusterId, points):
		res = Cluster(clusterId);
		res.points = points
		res.maxHeight = 99999
		res.minHeight = 0
		
		# Calculate max and min height by considering top-bottom 10% of points
		res.recalculateBounds()
		return res
		
	## Creates cluster of points only where specified by ids
	@staticmethod
	def fromLabeledPoints(clusterId, points, ids):
		res = Cluster(clusterId);
		res.points = []
		res.maxHeight = 99999
		res.minHeight = 0
		
		# Calculate max and min height by considering top-bottom 10% of points
		zs = []
		for i in range(len(points)):
			if ids[i] == clusterId:
				res.points.append(points[i])
				zs.append(points[i][2])
		
		# Take 10% number of items
		items = len(zs) / 10
		res.maxHeight = np.mean(heapq.nlargest(items, zs))
		res.minHeight = np.mean(heapq.nsmallest(items, zs))
		return res
		
	## Constructor
	def __init__(self, clusterId):
		self.clusterId = clusterId
		self.typess = []
		
	## Recalculate bounds
	def recalculateBounds(self):
		# Calculate max and min height by considering top-bottom 10% of points
		zs = []
		for i in range(len(self.points)):
			zs.append(self.points[i][2])
		
		items = len(zs) / 10
		self.maxHeight = np.mean(heapq.nlargest(items, zs))
		self.minHeight = np.mean(heapq.nsmallest(items, zs))
	
	## Returns the average height of the cluster
	def averageHeight(self):
		return (self.maxHeight - self.minHeight) / 2
		
	## Returns the thickness of the cluster
	def thickness(self):
		return self.maxHeight - self.minHeight
		
	## Append another cluster to this
	def append(self, cluster):
		self.points.extend(cluster.points)
		self.recalculateBounds()
		
	## Split this cluster and return the splitted part
	def split(self, height):
		newPoints = []
		for id, p in reversed(list(enumerate(self.points))):
			if p[2] < height:
				newPoints.append(p)
				self.points.pop(id)
		self.recalculateBounds()
		#Oprint len(self.points), len(newPoints)
		return Cluster.fromPoints(1, newPoints)