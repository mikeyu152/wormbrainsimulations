import numpy as np
import matplotlib.pyplot as plt
import random

ELEGANS_BODY_WIDTH = 0.25
ELEGANS_BODY_HEIGHT = 3.0
SCATTER = 0.1

class Edge:
	def __init__(self, connections={}, weight = 0.0):
		self.connections = connections
		self.weight = weight

	def add_connection(self, n_type, weight):
		if n_type not in self.connections:
			self.connections[n_type] = 0.0
		self.connections[n_type] += weight
		self.weight += weight

class Neuron:
	def __init__(self, neuron_id, activation = 0.0, threshold = 5.0, activated = False, ts_decay = 0.0):
		if neuron_id == None: error("Must have a neuron id to create a neuron")
		self.id = neuron_id
		self.activation = activation
		self.future_activation = 0.0
		self.threshold = threshold
		self.activated = activated
		self.ts_decay = ts_decay
		self.freeze = False

	def tick(self,noise=0):
		# Shift the neuron to its next time state
		self.activation = self.future_activation

		# If the state is now "active"
		if not self.freeze and (self.activated or self.activation >= self.threshold):
			self.activated = True

		if random.random() < noise:
			self.activated = not self.activated
			self.freeze = True

		# Set the future activation to be a copy of the current starting activation,
		# decay the activation accordingly
		self.future_activation = self.ts_decay * self.activation

	def stimulate(self, weight):
		# Add stimulation weight to the future time step
		self.future_activation += weight

class NeuronNetwork:
	"""A class for representing a neuronal network graph with methods for running various simulations."""
	def __init__(self, neuron_filename = None, edges = None, landmark_filename = None, neuron_map = None):
		if neuron_filename == None and edges == None:
			return error("Must have either a filename argument input or an input for the edges lookup.")
		if neuron_filename == None: self.edges = edges
		else: self.edges = self.read_neuron_file(neuron_filename)
		self.neuron_ids = self.edges.keys()
		for n_id in self.neuron_ids:
			neighbors = self.edges[n_id]
			for n2_id in neighbors:
				if n2_id not in self.neuron_ids:
					self.neuron_ids.append(n2_id)
					self.edges[n2_id] = []
		self.neurons = self.create_neuron_dict()
		self.body = EleganRobot(filename=landmark_filename)

	def read_neuron_file(self, filename):
		edges = {}
		with open(filename, 'r') as f:
			# Start from the second line, since the first will be a key header
			for line in f.readlines()[1:]:
				n1, n2, n_type, nbr = line.split('\t')
				nbr = float(nbr)
				# Add edges to dictionary (only need to add under first node, since the opposite order also
				# appears in the file)
				if n1 not in edges: edges[n1] = {}
				if n2 not in edges[n1]: edges[n1][n2] = Edge()
				edges[n1][n2].add_connection(n_type, nbr)
		return edges

	def create_neuron_dict(self):
		neurons = {}
		for n_id in self.neuron_ids:
			neurons[n_id] = Neuron(n_id)
		return neurons

	def step_propogate(self,noise=0):
		# Move all neurons one time step forward, reset all that have reached their
		# time limit active
		for neuron in self.neurons.values():
			if neuron.activated and not self.body.terminal(neuron.id):
				neighbors = self.edges[neuron.id]
				for n2_id in neighbors:
					# Propogate weighted signal to each neighbor
					self.neurons[n2_id].stimulate(self.edges[neuron.id][n2_id].weight)
		for neuron in self.neurons.values(): neuron.tick(noise)

	def propogate(self, num_steps, draw=False, showActivations=False, noise=0):
		for _ in range(num_steps):
			self.body.init_landmarks()
			self.step_propogate(noise)
			# print sum([1 for neuron in self.neurons.values() if neuron.activated]), " neurons activated."
			for neuron in self.neurons.values():
				if neuron.activated: self.body.activate_landmark(neuron.id)
			if draw: self.body.draw()
		if showActivations:
			activated = []
			for neuron in self.neurons.values():
				if neuron.activated: activated.append(neuron.id)
			print activated

class Firing:
	def __init__(self, landmark = "N/A", position = 0.0, weight = 0.0):
		self.landmark = landmark
		self.weight = weight
		self.x = 0.0
		self.y = ELEGANS_BODY_HEIGHT*position
		self.z = 0.0
		self.locate_landmark()

	def locate_landmark(self):
		code = self.landmark[:3]
		if code == "MDL":
			self.x = -ELEGANS_BODY_WIDTH + SCATTER*np.random.rand() # left is -
			self.z = -ELEGANS_BODY_WIDTH + SCATTER*np.random.rand() # distral is -
		elif code == "MDR":
			self.x = ELEGANS_BODY_WIDTH - SCATTER*np.random.rand() # right is +
			self.z = -ELEGANS_BODY_WIDTH + SCATTER*np.random.rand() # distral is -
		elif code == "MVR":
			self.x = ELEGANS_BODY_WIDTH - SCATTER*np.random.rand() # right is +
			self.z = ELEGANS_BODY_WIDTH - SCATTER*np.random.rand() # ventral is +
		elif code == "MVL":
			self.x = -ELEGANS_BODY_WIDTH + SCATTER*np.random.rand() # left is -
			self.z = ELEGANS_BODY_WIDTH - SCATTER*np.random.rand() # ventral is +

class EleganRobot:
	def __init__(self, filename = None, neuron_map = {}):
		if filename == None and len(neuron_map) == 0: error("Requires either a filenmae or a neuron map for landmark mappings")
		if filename == None:
			self.neuron_map = neuron_map
		else: self.neuron_map = self.read_landmark_file(filename)
		self.muscles = {}
		self.sensors = {}
		self.init_landmarks()

	def terminal(self, neuron):
		if neuron not in self.neuron_map: return True
		return False
		# for f in self.neuron_map[neuron]:
		# 	if f.landmark[0] == "S": return False
		# return True

	def read_landmark_file(self, filename):
		neuron_map = {}
		with open(filename, 'r') as f:
			# Start from the second line, since the first will be a key header
			for line in f.readlines()[1:]:
				n_id, lm, pos, weight = line.split('\t')
				pos, weight = float(pos), float(weight)
				# Add neurons to dictionary with their Firing object mapping
				if n_id not in neuron_map: neuron_map[n_id] = []
				neuron_map[n_id].append(Firing(lm, pos, weight))
		return neuron_map

	def init_landmarks(self):
		# List of x,y,z,w where x is left or right (left being -1 and right being +1), y is the float position along 
		# the A-P axis (head to tail) given by the position criteria in the file, and z is the dorsal or ventral (+1 being
		# dorsal and -1 being ventral). For the elegans, dorsal is the back and ventral is the belly of the worm.
		self.muscles = {}
		self.muscles['x'] = []
		self.muscles['y'] = []
		self.muscles['z'] = []
		self.muscles['landmarks'] = []
		self.muscles['weights'] = []
		self.sensors = {}
		self.sensors['x'] = []
		self.sensors['y'] = []
		self.sensors['z'] = []
		self.sensors['landmarks'] = []
		self.sensors['weights'] = []

	def activate_landmark(self, n_id):
		# Check that the neuron has a landmark it is mapped to
		if n_id not in self.neuron_map: return

		for stimuli in self.neuron_map[n_id]:
			if "Sensory" in stimuli.landmark:
				# If there is already an activation present, add to it
				if stimuli.landmark in self.sensors['landmarks']:
					idx = self.sensors['landmarks'].index(stimuli.landmark)
					self.sensors['weights'][idx] += stimuli.weight
				# Otherwise add a new data point
				else:
					self.sensors['x'].append(0.0)
					self.sensors['y'].append(stimuli.y)
					self.sensors['z'].append(0.0)
					self.sensors['weights'].append(stimuli.weight)
					self.sensors['landmarks'].append(stimuli.landmark)
				continue

			# If the neuron is not a sensory one, activate a muscle landmark
			if stimuli.landmark in self.muscles['landmarks']:
				idx = self.muscles['landmarks'].index(stimuli.landmark)
				self.muscles['weights'][idx] += stimuli.weight
			else:
				self.muscles['landmarks'].append(stimuli.landmark)
				self.muscles['weights'].append(stimuli.weight)
				self.muscles['x'].append(stimuli.x)
				self.muscles['y'].append(stimuli.y)
				self.muscles['z'].append(stimuli.z)


	def draw(self):
		plt.scatter(self.sensors['x'], self.sensors['y'], c='orange', alpha=0.5, s=300*self.sensors['weights'])#, cmap=plt.get_cmap('Oranges'))
		
		# Separate the distral and ventral muscles by color (since they are overlayed on the graph)
		d_muscles_idx = [i for i in range(len(self.muscles['z'])) if self.muscles['z'][i] < 0]
		v_muscles_idx = [i for i in range(len(self.muscles['z'])) if self.muscles['z'][i] > 0]
		i_muscles_idx = [i for i in range(len(self.muscles['z'])) if self.muscles['z'][i] == 0]

		plt.scatter(np.array(self.muscles['x'])[d_muscles_idx], np.array(self.muscles['y'])[d_muscles_idx], c='blue', alpha=0.5, s=200*np.array(self.muscles['weights'])[d_muscles_idx])#, cmap=plt.get_cmap('Blues'))
		plt.scatter(np.array(self.muscles['x'])[v_muscles_idx], np.array(self.muscles['y'])[v_muscles_idx], c='green', alpha=0.5, s=200*np.array(self.muscles['weights'])[v_muscles_idx])
		plt.scatter(np.array(self.muscles['x'])[i_muscles_idx], np.array(self.muscles['y'])[i_muscles_idx], c='red', alpha=0.5, s=200*np.array(self.muscles['weights'])[i_muscles_idx])
		plt.show()
