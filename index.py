from snap import *

graph = LoadEdgeList(PNGraph, "celegans_n306.txt", 0, 1)

def simulateSIR(graph, mu, beta, start):
	numNodes = graph.GetNodes()
	nodeArray = [node.GetId() for node in graph.Nodes()]
	allNodes = Set(nodeArray)
	infected = Set([nodeArray[start]])
	susceptible = allNodes.difference(infected)
	recovered = Set()
	while len(infected) > 0:
		for i in range(1, 1+numNodes):
			if i in susceptible and i not in infected:
				node = graph.GetNI(i)
				deg = node.GetDeg()
				for j in range(deg):
					neighbor = node.GetNbrNId(j)
					if neighbor in infected and random.random() < beta:
						susceptible.remove(i)
						infected.add(i)
						break
			elif i in infected:
				if random.random() < mu:
					infected.remove(i)
					recovered.add(i)
	return (len(susceptible), len(recovered))

def processGraph(filename, start):
	graph = LoadEdgeList(PUNGraph, filename, 0, 1)
	numNodes = graph.GetNodes()
	numSus, numRecovered = simulateSIR(graph, .5, .05, start)
	if numSus + numRecovered != numNodes:
		print "WHAT THE FUCK"
	return numRecovered * 1.0 / (numSus + numRecovered)

