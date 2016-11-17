from snap import *

graph = LoadEdgeList(PNGraph, "celegans_n306.txt", 0, 1)

print 'nodes', graph.GetNodes()

print 'average degree', graph.GetEdges()*1.0/graph.GetNodes()

print "clustering coefficient", GetClustCf(graph)

def getDegreeDist(graph):
	degrees = TIntPrV()
	GetOutDegCnt(graph, degrees)
	return [(item.GetVal1(), item.GetVal2()) for item in degrees]

print 'degree distribution', getDegreeDist(graph)