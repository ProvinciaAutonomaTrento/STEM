from sklearn.cluster import KMeans
import numpy as  np
from cluster import Cluster
import math

class LayersComputation():

    def initialize(self,
                   perc_min_points = None,
                   delta_h_min = None,
                   thickness_min = None,
                   R2_min_perc = None,
                   delta_R = None,
                   delta_h = None,
                   stacco = None):
        self.perc_min_points = perc_min_points if perc_min_points is not None else 0.15
        self.delta_h_min = delta_h_min if delta_h_min is not None else 3
        self.thickness_min = thickness_min if thickness_min is not None else 9
        self.R2_min_perc = R2_min_perc if R2_min_perc is not None else 0.10
        self.delta_R = delta_R if delta_R is not None else 3
        self.delta_h = delta_h if delta_h is not None else 2
        self.stacco = stacco if stacco is not None else 0.3

    ## Compute the layers
    def compute_layers(self, points, max_return_num):
        #print("---Number of points in the tile:" + str(len(points)))

        # First, divide the points in 1 or 2 clusters (considering cluster's point percentage must be >15%)
        clusters = clusterify(points)

        # If there are 2 layers, check minum distance and merge if needed
        if len(clusters) == 2:
            mergeLayers(clusters)

        # One layer check (may return to 2 layers)
        if len(clusters) == 1:
            splitLayers(clusters, max_return_num)

        # Merge again if needed
        if len(clusters) == 2:
            mergeLayers(clusters)

        return clusters

    ## Extract 1 or 2 layers using KMeans clusterification
    def clusterify(self, points):
        # Don't even try with less than 10 points
        if len(points) < 10:
            return [Cluster.fromPoints(0, points)]

        # Try 2 clusters
        ids = KMeans(n_clusters=2).fit_predict(points)

        # Make sure that there are enough points on both clusters
        minPoints = int(len(points) * self.perc_min_points)

        clusterSizes = [0, 0]

        enoughPoints = False
        for id in ids:
            clusterSizes[id] += 1

            # Check exit condition
            if clusterSizes[0] > minPoints and clusterSizes[1] > minPoints:
                enoughPoints = True
                break


        if enoughPoints:
            #Init and return the 2 clusters
            cluster1 = Cluster.fromLabeledPoints(1, points, ids)
            cluster2 = Cluster.fromLabeledPoints(0, points, ids)

            # Return the higher layer as first! ^-^
            if cluster1.averageHeight() < cluster2.averageHeight():
                return [cluster2, cluster1]
            else:
                cluster2.clusterId = 1
                cluster1.clusterId = 0
                return [cluster1, cluster2]

        # If points are not enough, 1 cluster is fine
        return [Cluster.fromPoints(0, points)]

    ## Check that layers have a minimum distance and if not, merge
    def mergeLayers(self, clusters):
        if clusters[0].minHeight - clusters[1].maxHeight < self.self.delta_h_min:
            # Reduce to 1 layer
            clusters[0].append(clusters[1])
            clusters.remove(clusters[1])

    def splitLayers(self, clusters, max_return_num):
        # Don't even try with less than 10 points
        if len(clusters[0].points) < 10: return

        ## Condition 1 - thickness
        if clusters[0].thickness() <= self.thickness_min: return

        # Count R2 and R1
        returns = [0 for x in range(max_return_num)]
        returnsHeights = [0 for x in range(max_return_num)]
        for p in clusters[0].points:
            returns[int(p[3])-1] += 1
            returnsHeights[int(p[3])-1] += p[2]

        ## Condition 2 - number of r2s
        if returns[1] <= len(clusters[0].points) * self.R2_min_perc: return

        # Calculate r1 and r2 average
        r1AvgHeight = returnsHeights[0] / returns[0]
        r2AvgHeight = returnsHeights[1] / returns[1]

        ##Condition 3 - delta average return heights
        if r1AvgHeight - r2AvgHeight <= self.delta_R: return;

        # Calculate Z discrete histogram
        stripsNum = int(math.ceil(clusters[0].thickness() /  self.delta_h))
        strips = [0] * stripsNum

        stripSize = (clusters[0].thickness() + self.delta_h) / stripsNum
        stripStart = clusters[0].minHeight - self.delta_h/2
        for p in clusters[0].points:
            stripId = int((p[2] - stripStart) / stripSize)
            if stripId >=0 and stripId <len(strips):
                strips[stripId] += 1

        ## Condition 4 - z histogram concavity
        stripsAverage = np.mean(strips)

        concave= False
        concaveStripNum = 0
        for s in range(1, stripsNum-1):
            if strips[s-1] > strips[s] and strips[s+1] > strips[s]:
                ## Condition 5 - concavity factor
                if (stripsAverage - strips[s]) / stripsAverage > self.stacco:
                    concave = True
                    concaveStripNum = s
                    break;

        if not concave: return

        ## All conditions met, do the split!!
        splitHeight = stripStart + s*stripSize
        clusters.append(clusters[0].split(splitHeight))