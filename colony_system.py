import csv
import os
import random
from ant import Ant
import tqdm
import datetime
import json
import copy


class ColonySystem(object):
    def __init__(self, cfg, grid, grid_pheromone):
        self.cfg = cfg

        self.ant_number = self.cfg["ant_number"]
        self.alpha = self.cfg["alpha"]
        self.beta = self.cfg["beta"]
        self.pheromone_evaporation = self.cfg["pheromone_evaporation"]
        self.pheromone_t0 = self.cfg["pheromone_t0"]

        # Redundant
        self.iterations = self.cfg["iterations"]
        self.repetitions = self.cfg["repetitions"]

        self.grid = grid
        self.grid_pheromone = grid_pheromone

        random.seed(self.cfg["seed"])

        self.ants = []


        pass

    def init_ants(self):
        for i in xrange(self.ant_number):
            self.ants.append(Ant(i, self.alpha, self.beta, self.grid, self.grid_pheromone))
        pass

    def run(self):
        complete_results = []

        # define ants
        ants = []
        print '[INFO]', 'Creating {} ants'.format(self.ant_number)


        iteration_result = []
        # iterate ants
        for it in xrange(self.iterations):
            print '[INFO]', 'Iteration #{} of #{}. Repetition #{} of {}'.format(it + 1, self.iterations, rep_i + 1, self.repetitions)
            print '[INFO]', 'Starting ants...'
            for ant_i in tqdm.trange(self.ant_number):
                ant = ants[ant_i]
                ant.start()

            #print '[INFO]', 'Waiting for ants...'
            for ant_i in tqdm.trange(self.ant_number):
                ant = ants[ant_i]
                ant.join()

            l = sorted(ants, key=lambda (a): a.previous_result_sum)
            best_ant = l[0]
            worst_ant = l[-1]

            if best_ant.previous_result_sum < self.global_best_sum:
                self.global_best_sum = best_ant.previous_result_sum
                self.global_best_p_medians = best_ant.previous_result.keys()
                self.global_best = best_ant.previous_result
                print '[DEBUG]', 'Updated global best to {}'.format(self.global_best_sum)

            for k in best_ant.previous_result.keys():
                # print 'a', (best_ant.previous_result_sum - self.global_best_sum)
                # print 'b', float(worst_ant.previous_result_sum)
                # print 'c', best_ant.previous_result_sum
                try:
                    self.ant_pheromone_map[k] = 1 - ((best_ant.previous_result_sum - self.global_best_sum)/float(worst_ant.previous_result_sum - best_ant.previous_result_sum))
                except Exception as e:
                    self.ant_pheromone_map[k] = 0

            #print '[DEBUG]', 'Best ant ID:{} Sum:{}'.format(best_ant.ant_id, best_ant.previous_result_sum)
            #print '[DEBUG]', 'Worst ant ID:{} Sum:{}'.format(worst_ant.ant_id, worst_ant.previous_result_sum)
            print '[DEBUG]', 'Global best Sum:{}'.format(self.global_best_sum)

            iteration_result.append(self.global_best_sum)

            self.update_pheromone_map()
            #self.print_pheromone_map()
            self.ant_pheromone_map = [0.000000001 for i in xrange(len(self.data))]

            # restart ants because of threads
            for ant_i in xrange(self.ant_number):
                ant = ants[ant_i]

                ant.__init__(ant.ant_id, ant.alpha, ant.beta, ant.data, ant.ant_pheromone_map, ant.pheromone_map, ant.density_map, ant.p_count)
            pass

            print '[INFO]', 'Best solution:{} {}'.format(self.global_best_sum, self.global_best)
            fig_path = os.path.join('plots',
                                    self.cfg['config_file'] + '.rep_' + str(rep_i) +
                                    datetime.datetime.now().strftime("%I-%M%p_%d-%b-%Y") +
                                    '.pdf')
            self.show_network_graph(self.global_best, savefig_path=fig_path)
            complete_results.append({
                'best_solution': copy.deepcopy(self.global_best),
                'best_sum': copy.deepcopy(self.global_best_sum),
                'iterations_sum': copy.deepcopy(iteration_result)
            })

            self.cfg['seed'] = self.cfg['seed'] + 1
            random.seed(self.cfg["seed"])

        # when all repetitions are finished save the results to json file
        run_file = os.path.join('results',
                                self.cfg['config_file'] + '.' +
                                datetime.datetime.now().strftime("%I-%M%p_%d-%b-%Y") +
                                '.json')
        with open(run_file, 'w') as fp:
            json.dump(complete_results, fp)

        print complete_results

    def update_pheromone_map(self):
        t_max = (1.0/(1.0 - self.pheromone_evaporation)) * (1.0/float(self.global_best_sum))
        t_min = t_max / float(2 * len(self.data))

        print '[DEBUG]', 't_max:{} t_min:{}'.format(t_max, t_min)

        for i in xrange(len(self.pheromone_map)):
            self.pheromone_map[i] = (self.pheromone_evaporation * self.pheromone_map[i]) + self.ant_pheromone_map[i]
        pass

    def print_pheromone_map(self):
        print self.ant_pheromone_map
        print self.pheromone_map

    def show_network_graph(self, allocations, savefig_path=None):
        import networkx as nx
        from matplotlib import pyplot as plt

        G = nx.Graph()
        labels = {}
        for n in self.data:
            labels[n.node_id] = n.node_id

        for k, v in allocations.items():
            nk = self.data[k]
            G.add_node(nk.node_id, posxy=(nk.x, nk.y))
            for e in v:
                ne = self.data[e]
                G.add_node(ne.node_id, posxy=(ne.x, ne.y))
                G.add_edge(nk.node_id, ne.node_id)

        color_vals = [(0, 0, 1) if e.node_id in allocations.keys() else (1, 0, 0) for e in self.data]

        positions = nx.get_node_attributes(G, 'posxy')
        nx.draw(G, positions, node_size=len(self.data), node_color=color_vals)
        nx.draw_networkx_labels(G, positions, labels, font_size=6)

        #print '[DEBUG]', 'savefig_path:', savefig_path
        if savefig_path is not None:
            plt.savefig(savefig_path)
        else:
            plt.show()

    def read_database(self):
        if self.cfg['dataset'] is None or not os.path.exists(self.cfg['dataset']):
            raise ValueError('Config file not found {}'.format(self.cfg['dataset']))

        with open(os.path.realpath(self.cfg['dataset']), "r") as f:
            l_count = -1
            for line in f:
                l_count += 1
                d = map(int, line.split())

                if l_count == 0:
                    self.node_count = d[0]
                    self.p_count = d[1]
                    continue
                else:
                    self.data.append(Node(l_count - 1, d[0], d[1], d[2], d[3]))

        print '[INFO]', 'Readed {} nodes from dataset'.format(len(self.data))
        print '[INFO]', 'Dataset has {} p-medians'.format(self.p_count)
