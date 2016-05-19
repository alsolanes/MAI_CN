from tqdm import tqdm
import random
import pickle
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
class Simulation_MC(object):
    def __init__(self, model, n_rep, t_max, t_trans):
        self.model = model
        self.n_rep = n_rep
        self.t_max = t_max
        self.t_trans = t_trans
        self.data = []
        self.average = []

    def single_execution(self):

        simulation_data = []
        for i in xrange(self.t_max):
            self.model.step_sim()
            p = self.model.infected_rate()
            simulation_data.append(p)

        stationary_data = simulation_data[self.t_trans:]

        average_infected_nodes = sum(stationary_data)/len(stationary_data)
        return average_infected_nodes, simulation_data

    def full_execution(self):

        full_average = 0
        for i in xrange(self.n_rep):
            average_infected_nodes, simulation_data = self.single_execution()
            full_average += average_infected_nodes
            if i < self.n_rep - 1:
                self.model.init_graph()
            self.data.append(simulation_data)
            self.average.append(average_infected_nodes)

        full_average /= self.n_rep
        return full_average
