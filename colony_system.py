import csv
import os
import random
from ant import Ant
import tqdm
import datetime
import json
import copy


class ColonySystem(object):
    def __init__(self, cfg, graph):
        self.cfg = cfg

        self.ant_number = self.cfg["ant_number"]
        self.alpha = self.cfg["alpha"]
        self.beta = self.cfg["beta"]
        self.pheromone_evaporation = self.cfg["pheromone_evaporation"]
        self.pheromone_t0 = self.cfg["pheromone_t0"]

        self.graph = graph
        self.pheromone_dict_red = {}
        self.pheromone_dict_blue = {}

        random.seed(self.cfg["seed"])

        self.ants = []
        self.init_ants()

    def init_ants(self):
        print '[INFO]', 'Creating {} ants'.format(self.ant_number)
        for i in xrange(self.ant_number):
            self.ants.append(Ant(i, self.alpha, self.beta, self.graph, self.pheromone_dict_red, self.pheromone_dict_blue))

    def get_ants(self):
        return self.ants

    def run(self):
        for ant_i in xrange(self.ant_number):
            ant = self.ants[ant_i]
            #ant.start()
            ant.run()

        # #print '[INFO]', 'Waiting for ants...'
        # for ant_i in tqdm.trange(self.ant_number):
        #     ant = self.ants[ant_i]
        #     ant.join()

        self.update_pheromone_graph()

        # # restart ants because of threads
        # for ant_i in xrange(self.ant_number):
        #     ant = ants[ant_i]
        #
        #     ant.__init__(ant.ant_id, ant.alpha, ant.beta, ant.data, ant.ant_pheromone_map, ant.pheromone_map, ant.density_map, ant.p_count)

    def update_pheromone_graph(self):
        #print "self.pheromone_dict:", self.pheromone_dict

        for n, d in self.graph.nodes_iter(data=True):
            if d["node_type"] not in [0, 2]:
                continue

            red_p_value = 0.0
            blue_p_value = 0.0
            if n in self.pheromone_dict_red:
                red_p_value = self.pheromone_dict_red[n]

            if n in self.pheromone_dict_blue:
                blue_p_value = self.pheromone_dict_blue[n]

            d["p_red"] = ((1 - self.pheromone_evaporation) * d["p_red"]) + red_p_value
            if d["p_red"] < 0.0:
                d["p_red"] = 0.0

            d["p_blue"] = ((1 - self.pheromone_evaporation) * d["p_blue"]) + blue_p_value
            if d["p_blue"] < 0.0:
                d["p_blue"] = 0.0

        self.pheromone_dict_red.clear()
        self.pheromone_dict_blue.clear()
