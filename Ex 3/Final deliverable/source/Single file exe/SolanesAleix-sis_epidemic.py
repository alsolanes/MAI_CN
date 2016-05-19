#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tqdm import tqdm
import random
import pickle
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class Sis_epidemic_model(object):
    """
    graph = scale-free, erdos_renyi, etc..
    mu = spontaneous recovery probability
    beta = infection probability of a susceptible (S) individual when it is contacted by an infected (I) one
    p0 = initial fraction of infected nodes. [0-1) value
    seed = random seed
    """
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
        """initialize the graph"""
        self.infected_nodes = []
        self.susceptible_nodes = []

        #initialize the graph with Susceptible or Infected individuals
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
        1.- For each infected node at time step t, we recover it with probability µ: we generate
        a uniform random number between 0.0 and 1.0, and if the value is lower than µ
        the state of that node in the next time step t+1 will be susceptible, otherwise it will
        remain being infected.
        2.- For each susceptible node at time step t, we traverse all of its neighbors. For each
        infected neighbor (at time step t), the reference node becomes infected with
        probability β. For example, if node A has 6 neighbors, 4 of them being infected, we
        repeat 4 times the generation of a random number and its comparison with β. If at
        the third attempt the random number is lower than β, node A will be infected in
        the next time step t+1, and we may stop the generation of the remaining random
        number; otherwise, node A will continue to be susceptible at time step t+1. Of
        course, the larger the number of infected neighbors, the larger the probability of
        becoming infected.
        """
        future_infected_nodes = []
        future_susceptible_nodes = []

        #we full_execution the recovery plot2file to infected nodes
        for infected_node in self.infected_nodes:
            if random.random() < self.mu:
                #the individual is not infected anymore
                future_susceptible_nodes.append(infected_node)
            else:
                #the individual remain infected
                future_infected_nodes.append(infected_node)

        #we full_execution the infection plot2file to susceptibles nodes
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
                #the individual get infected
                future_infected_nodes.append(susceptible_node)
            else:
                #the individual remain susceptible
                future_susceptible_nodes.append(susceptible_node)

        #update the new states of the nodes
        for future_infected_node in future_infected_nodes:
            self.graph.node[future_infected_node] = 'I'

        for future_susceptible_node in future_susceptible_nodes:
            self.graph.node[future_susceptible_node] = 'S'

        self.infected_nodes = future_infected_nodes
        self.susceptible_nodes = future_susceptible_nodes

class Simulation_MC(object):
    def __init__(self, model, n_rep, t_max, t_trans):
        self.model = model
        self.n_rep = n_rep
        self.t_max = t_max
        self.t_trans = t_trans

        #debug data
        self.data = []
        self.average = []

    def single_execution(self):
        """
        full_execution t_max steps from model and get the data for each one
        """
        simulation_data = []
        for i in xrange(self.t_max):
            #we full_execution one simulation from model and save the fraction in data
            self.model.step_sim()
            p = self.model.infected_rate()
            simulation_data.append(p)

        stationary_data = simulation_data[self.t_trans:]

        average_infected_nodes = sum(stationary_data)/len(stationary_data)
        return average_infected_nodes, simulation_data

    def full_execution(self):
        """
        full_execution n_rep complete simulations and get the average of infected_rate
        """
        full_average = 0
        for i in xrange(self.n_rep):
            average_infected_nodes, simulation_data = self.single_execution()
            full_average += average_infected_nodes
            if i < self.n_rep - 1:
                #we don't need to init_graph the graph in the last iteration
                self.model.init_graph()

            #debug data
            self.data.append(simulation_data)
            self.average.append(average_infected_nodes)

        full_average /= self.n_rep
        return full_average

class MainExecution(object):
    def __init__(self):
        self.pickle_save = 'backup.pkl'
        self.seed = 200
        self.n_rep = 1
        self.t_max = 1000
        self.t_trans = 900
        self.p0 = 0.2

        self.list_num_nodes = [500, 1000]
        self.mu_values = [0.1, 0.5, 0.9]

        self.models_cfg = [
            {"name": "Barabasi Albert","graph": nx.barabasi_albert_graph,"args": { "m": 10 }},
            {"name": "Erdos Renyi","graph": nx.erdos_renyi_graph,"args": { "p": 0.4 }},
            {"name": "Random network","graph": nx.random_regular_graph,"args": { "d": 10 }}
        ]

    def loadFile(self):
        data = None
        try:
            with open(self.pickle_save, 'rb') as filecache:
                cache_data = pickle.load(filecache)
	    print 'data loaded correctly'
            data = cache_data['data']
        except:
            print("Not found backup file. If you have it, please copy it in the same folder as this file with the name 'backup.pkl'.")
        return data

    def saveFile(self, data):
        try:
            with open(self.pickle_save, 'wb') as filecache:
                pickle.dump({'version': self.version, 'data': data}, filecache)
        except:
            print("Something gone wrong, file not saved.")

    def transPlot(self, data_list):
        """
        Receives a data with graph results and draw the transitions with gnuplot
        """

        t = range(1000)
        for j,data in enumerate(data_list):
	    print 'iter plot trans:',j

            legend = []
            i_l = [2,4,8,9,10,20,30,45]
	    x_dat = []
            y_dat = []
            for i in i_l:
                beta = i * 0.02
                legend.append(r'$\beta$ = %0.2f' % beta)
                p_t = data['simulations'][i]['data'][0]
                plt.plot(t, p_t,'b')
            plt.legend(legend, loc='lower right')
            plt.xlabel('t')
            plt.ylabel(r'$\rho$')

            args = ['%s = %s' % (arg, data['args'][arg]) for arg in data['args']]
            image_title = r"SF (N = %s, %s), SIS(%s, $\mu$ = %s, $\rho$0 = %s)" % (data['num_nodes'], ', '.join(args),data['graph_name'], data['mu'], data['p0'])

            plt.title(image_title)
            plt.axis([0, 1000, 0, 0.7])
            graphType = data['graph_name'].replace(' ', '_')
            filename = "transitionPlot/%s_N_%d_%d.png" % (graphType, data['num_nodes'], i)
            plt.savefig(filename)
	    print 'pre-filename3'
            plt.close()
            print 'p'

    def plot2file(self, data_list):
        """
        Receives a data with graph results and draw the info with gnuplot
        """
	print 'plotting'
        self.transPlot(data_list)
	print 'transitions done'
        def convertList2string(float_list): return [ "%0.2f" %  float_value for float_value in float_list ]
        i = 0
        for data in data_list:
            beta_data = data['beta_list'][:5]
            beta_data.extend(data['beta_list'][-5:])
            p_data = data['p_list'][:5]
            p_data.extend(data['p_list'][-5:])

            beta_data = convertList2string(beta_data)
            p_data = convertList2string(p_data)

            plt.plot(data['beta_list'], data['p_list'], 'ro')
            plt.xlabel(r'$\beta$')
            plt.ylabel('P')

            args = [ '%s = %s' % (arg, data['args'][arg]) for arg in data['args'] ]

            plt.title("SF (N = %s, %s), SIS (%s, $\mu$ = %s, p0 = %s)" % (data['num_nodes'], ', '.join(args), data['graph_name'], data['mu'], data['p0']))
            plt.axis([0, 1, 0, 1])

            graphType = data['graph_name'].replace(' ', '_')
            filename = "plotP-Beta/%s_N_%d_%d.png" % (graphType, data['num_nodes'], i)
            plt.savefig(filename)
            i += 1
            plt.close()

    def main_run(self):
        error_code = 0
        data = None
        save_data = False

        data = self.loadFile()

        if not data:
            data = self.start()
            save_data = True

        if data:
            if save_data:
                self.saveFile(data)
            self.plot2file(data)
        else:
            print("Error: Error in the simulation")
            error_code = 1

        return error_code

    def start(self):
        list_data = []
        #we full_execution the simulation in all the models
        for model_cfg in self.models_cfg:
            graph_class = model_cfg["graph"]
            graph_name = model_cfg["name"]
            graph_args = model_cfg["args"]

            #we full_execution simulations for several number of nodes
            for num_nodes in tqdm(self.list_num_nodes):
                graph = graph_class(n = num_nodes, seed = self.seed, **graph_args)

                #export graph in pajek format
                graphType = graph_name.replace(' ', '_')
                pajek_filename = "net/%s_n_%d.net" % (graphType, num_nodes)
                nx.write_pajek(graph, pajek_filename)

                #we full_execution simulations for several mu values
                for mu in tqdm(self.mu_values):
                    #we full_execution simulations for several beta values. Δβ=0.02
                    beta = 0

                    data = {
                        "graph_name": graph_name,
                        "args": graph_args,
                        "seed": self.seed,
                        "p0": self.p0,
                        "num_nodes": num_nodes,
                        "mu": mu
                    }

                    beta_list = []
                    p_list = []

                    data_simulations = []

                    for i in tqdm(xrange(0, 51)):
                        Sis_epidemic_model = Sis_epidemic_model(graph_name, graph, mu, beta, self.p0, self.seed)
                        simulation = Simulation_MC(Sis_epidemic_model, self.n_rep, self.t_max, self.t_trans)
                        sim_data = simulation.full_execution()

                        #saving data
                        beta_list.append(beta)
                        p_list.append(sim_data)

                        #debug data
                        data_simulations.append({
                            'data': simulation.data,
                            'average': simulation.average
                        })

                        beta += 0.02
                    data['beta_list'] = beta_list
                    data['p_list'] = p_list
                    data['simulations'] = data_simulations

                    list_data.append(data)
        return list_data


MainExecution = MainExecution()
MainExecution.main_run()
