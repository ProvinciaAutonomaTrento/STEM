from builtins import range
import numpy as np
import heapq

h_min_type_2=7
thickness_min1=100
h_sterpaglia = 1
perc_min = 0.20
diff_mediane = 5

## Compute the types
def compute_types(clusters):
	minH = clusters[0].minHeight
	maxH = clusters[0].maxHeight
	zs = []
	
	# Recalculate bounds for cluster as one
	for i in range(len(clusters[0].points)):
		zs.append(clusters[0].points[i][2])
		
	if len(clusters) == 2:
		for i in range(len(clusters[1].points)):
			zs.append(clusters[1].points[i][2])
		
		items = len(zs) / 10
		maxH = np.mean(heapq.nlargest(items, zs))
		minH = np.mean(heapq.nsmallest(items, zs))
		
	# Calculate mean Z
	zMean = np.mean(zs)
		
	## Condition for BIPLANE
	if len(clusters) == 2 and maxH > h_min_type_2:
		setType(clusters, 2)
		return
		
	## Condition 1 for MONOPLANE (has to be false for monoplane)
	if (maxH - zMean) >= thickness_min1:
		setType(clusters, 3 if maxH > h_min_type_2 else 1)
		return
		
	# Get number of lower points
	lowerPointsNum = 0
	for z in zs:
		if z < maxH - h_sterpaglia:
			lowerPointsNum += 1
	
	## No lower points
	if lowerPointsNum == 0:
		setType(clusters, 1)
		return
	
	## Too few lower points
	lowerPointsPerc=lowerPointsNum/len(zs)
	if lowerPointsPerc >= perc_min:
		setType(clusters, 3 if maxH > h_min_type_2 else 1)
		return
	
	## Calculate returns
	# Count R2 and R1
	returnsHeights = [[], []]
	for p in clusters[0].points:
		ret = int(p[3])
		# Consider R3s and R4s as R2s
		if ret>2: ret = 2
		returnsHeights[ret-1].append(p[2])
		
	# Add second layer too if needed
	if len(clusters) == 2:
		for p in clusters[1].points:
			ret = int(p[3])
			# Consider R3s and R4s as R2s
			if ret>2: ret = 2
			returnsHeights[ret-1].append(p[2])
	
	# Sort and take the medians
	returnsHeights[0].sort()
	returnsHeights[1].sort()
	
	## MONOPLANE if no r2s
	if len(returnsHeights[0]) == 0 or len(returnsHeights[1]) == 0:
		setType(clusters, 1)
		return
	
	r1Median = returnsHeights[0][len(returnsHeights[0])/2]
	r2Median = returnsHeights[1][len(returnsHeights[1])/2]
	deltaMedian = abs(r1Median - r2Median);
	
	## MONOPLANE if not enough delta
	if deltaMedian < diff_mediane:
		setType(clusters, 1)
		return
	
	setType(clusters, 3 if maxH > h_min_type_2 else 1)
	return
	
	
def setType(clusters, type):
	for i in range(len(clusters[0].points)):
		clusters[0].typess.append(type)
		
	# Consider 2 layer case
	if len(clusters) == 2:
		for i in range(len(clusters[1].points)):
			clusters[1].typess.append(type)
