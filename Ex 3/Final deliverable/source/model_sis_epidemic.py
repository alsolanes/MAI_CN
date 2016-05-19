from tqdm import tqdm
import random
import pickle
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
class Sis_epidemic_model(object):

    def __init__(self, name, graph, mu, beta, p0, seed = None):
        self.name = name
        self.graph = graph
        self.mu = mu
        self.beta = beta
        self.p0 = p0

        if seed:
            random.seed(seed)

        self.init_graph()

    def init_graph(self):
        """ Graph initialization """
        self.infected_nodes = []
        self.susceptible_nodes = []

        #set default infected and susceptible nodes
        for node_id in self.graph.nodes():
            is_infected = random.random() < self.p0
            if is_infected:
                self.graph.node[node_id] = 'I'
                self.infected_nodes.append(node_id)
            else:
                self.graph.node[node_id] = 'S'
                self.susceptible_nodes.append(node_id)

    def infected_rate(self):
        return float(len(self.infected_nodes)) / self.graph.number_of_nodes()

    def step_sim(self):
        """
        simulation of the step as specified in Details-SIS.pdf
        """
        future_infected_nodes = []
        future_susceptible_nodes = []

 
        for infected_node in self.infected_nodes:
            if random.random() < self.mu:
                future_susceptible_nodes.append(infected_node)
            else:
                future_infected_nodes.append(infected_node)

        for susceptible_node in self.susceptible_nodes:
            neighbors = self.graph.neighbors(susceptible_node)
            num_neighbors = len(neighbors)
            i = 0
            is_infected = False
            while i < num_neighbors and not is_infected:
                neighbor = neighbors[i]
                if self.graph.node[neighbor] == 'I':
                    is_infected = random.random() < self.beta
                i += 1

            if is_infected:
                future_infected_nodes.append(susceptible_node)
            else:
                future_susceptible_nodes.append(susceptible_node)

        for future_infected_node in future_infected_nodes:
            self.graph.node[future_infected_node] = 'I'

        for future_susceptible_node in future_susceptible_nodes:
            self.graph.node[future_susceptible_node] = 'S'

        self.infected_nodes = future_infected_nodes
        self.susceptible_nodes = future_susceptible_nodes
