from tqdm import tqdm
import random
import pickle
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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
        for model_cfg in self.models_cfg:
            graph_class = model_cfg["graph"]
            graph_name = model_cfg["name"]
            graph_args = model_cfg["args"]
            for num_nodes in tqdm(self.list_num_nodes):
                graph = graph_class(n = num_nodes, seed = self.seed, **graph_args)
                graphType = graph_name.replace(' ', '_')
                pajek_filename = "net/%s_n_%d.net" % (graphType, num_nodes)
                nx.write_pajek(graph, pajek_filename)
                for mu in tqdm(self.mu_values):
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
                        beta_list.append(beta)
                        p_list.append(sim_data)
                        data_simulations.append({'data': simulation.data,'average': simulation.average})
                        beta += 0.02
                    data['beta_list'] = beta_list
                    data['p_list'] = p_list
                    data['simulations'] = data_simulations

                    list_data.append(data)
        return list_data
