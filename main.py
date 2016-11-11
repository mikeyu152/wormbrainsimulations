import numpy as np
import matplotlib.pyplot as plt
from structures import NeuronNetwork

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

#simple_visualize()

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

#threshold_normal()

#########################################################################################
# ------ EXAMPLE 3 ---------
# Change decay of neuron activation across time steps (default is 0.0, i.e. each 
# activation only lasts one time step)
#########################################################################################
def activation_decay(decay = 0.5):
	nn = NeuronNetwork(neuron_filename="neurons.txt", landmark_filename="landmark.txt")
	# Iterate through each neuron and increase its threshold, set decay
	for neuron in nn.neurons.values():
		neuron.threshold = 10.0
		neuron.ts_decay = 0.5
	for n_id in nose_sensors:
		nn.neurons[n_id].activated = True
	nn.propogate(20, draw = True)

# activation_decay()

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

repeated_stimulation(20, draw = True)
