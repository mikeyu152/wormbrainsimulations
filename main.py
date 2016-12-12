import numpy as np
import matplotlib.pyplot as plt
from structures import NeuronNetwork
import random
import csv

#########################################################################################
# ------ EXAMPLE 1 ---------
# Visualize A Simple Propogation
#########################################################################################
# Create a neuron network and activate a single neuron.
# Propogate the network for 10 time steps and set visualize to true to generate a series of
# plots corresponding to each time step.
#
# PLOT:
#	- BLUE corresponds to upperside (back) muscle activations on the left and right of the worm
#	- GREEN corresponds to underside (belly) muscle activations on the left and right of the worm
#	- RED corresponds to internal muscle activations
#	- YELLOW corresponds to sensor neuron activations
#
nose_sensors = ["FLPR","FLPL","ASHL","ASHR","IL1VL","IL1VR","OLQDL","OLQDR","OLQVR","OLQVL"]
def simple_visualize():
	nn = NeuronNetwork(neuron_filename="neurons.txt", landmark_filename="landmark.txt")
	for n_id in nose_sensors:
		nn.neurons[n_id].activated = True
	nn.propogate(20, draw = True)

# simple_visualize()

#########################################################################################
# ------ EXAMPLE 2 ---------
# Change distribution of thresholds on neurons
#########################################################################################
def threshold_normal(mean = 6.0, std = 3.0):
	nn = NeuronNetwork(neuron_filename="neurons.txt", landmark_filename="landmark.txt")
	# Iterate through each neuron and set its threshold
	for neuron in nn.neurons.values():
		neuron.threshold = np.random.normal(mean, std)
	for n_id in nose_sensors:
		nn.neurons[n_id].activated = True
	nn.propogate(10, draw = True)

# threshold_normal()

#########################################################################################
# ------ EXAMPLE 3 ---------
# Change decay of neuron activation across time steps (default is 0.0, i.e. each 
# activation only lasts one time step)
#########################################################################################
def activation_decay(threshold = 10, decay = 0.5):
	nn = NeuronNetwork(neuron_filename="neurons.txt", landmark_filename="landmark.txt")
	# Iterate through each neuron and increase its threshold, set decay
	for neuron in nn.neurons.values():
		neuron.threshold = threshold*1.0
		neuron.ts_decay = decay
	for n_id in nose_sensors:
		nn.neurons[n_id].activated = True
	nn.propogate(20, draw = False)

# for i in range(10):
# 	for j in range(10,20):
# 		decay =  .5*i
# 		threshold = j
# 		print "decay,", decay, "threshold,", threshold
# 		activation_decay(threshold, decay)

#########################################################################################
# ------ EXAMPLE 4 ---------
# Apply repeated stimulation at one point
#########################################################################################
def repeated_stimulation(num_steps, draw=False):
	nn = NeuronNetwork(neuron_filename="neurons.txt", landmark_filename="landmark.txt")
	for _ in range(num_steps):
		nn.body.init_landmarks()
		for n_id in nose_sensors:
			nn.neurons[n_id].activated = True
		nn.step_propogate()
		print sum([1 for n in nn.neurons.values() if n.activated]), " neurons activated."
		for n in nn.neurons.values():
			if n.activated: nn.body.activate_landmark(n.id)
		if draw: nn.body.draw()

# repeated_stimulation(20, draw = True)

def simulate_dropout(threshold=5,p=0.1):
	nn = NeuronNetwork(neuron_filename="neurons.txt", landmark_filename="landmark.txt")
	for n_id in nose_sensors:
		nn.neurons[n_id].activated = True
	for neuron in nn.neurons.values():
		if random.random() < p:
			# make it impossible for this neuron to activate by setting high threshold
			neuron.threshold = 10000
		else:
			neuron.threshold = threshold
	nn.propogate(20, draw=False, showActivations=True)

# for p in range(10):
# 	for i in range(100):
# 		prob = .03 * p
# 		print "prob,", prob
# 		simulate_dropout(threshold=10,p=prob)

def simulate_noise(threshold=5,alpha=.05):
	nn = NeuronNetwork(neuron_filename="neurons.txt", landmark_filename="landmark.txt")
	for n_id in nose_sensors:
		nn.neurons[n_id].activated = True
	for neuron in nn.neurons.values():
		neuron.threshold = threshold
	return nn.propogate(20, draw=False, showActivations=True, noise=alpha)

def printNetwork():
	nn = NeuronNetwork(neuron_filename="neurons.txt", landmark_filename="landmark.txt")
	return nn.neuron_ids

with open('noisesimsunfrozensmaller.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(printNetwork())
    for alpha in range(25):
    	print alpha
    	writer.writerow(['alpha', str(alpha)])
    	alpha = .002*alpha
    	for threshold in [3, 5, 10, 20]:
    		print threshold
    		writer.writerow(['threshold', str(threshold)])
    		threshold = threshold * 2
	    	for i in range(1000):
	    		writer.writerow(simulate_noise(alpha=alpha))

simulate_noise(alpha=.5)	
