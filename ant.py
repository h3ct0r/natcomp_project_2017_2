import random
import time
import threading
from threading import Thread
import math
import copy
import numpy as np
import networkx as nx


class Ant(Thread):
    def __init__(self, ant_id, alpha, beta, graph, pheromone_dict_red, pheromone_dict_blue, node_index=0):
        super(Ant, self).__init__()

        self.ant_id = ant_id
        self.alpha = alpha
        self.beta = beta

        self.graph = graph
        self.pheromone_dict_red = pheromone_dict_red
        self.pheromone_dict_blue = pheromone_dict_blue

        self.home_node = node_index
        self.node_index = node_index
        self.tabu_set = set([self.node_index])

        self.state = 'explore'
        self.is_transporting_person = False
        self.location_person_node = -1
        self.rescued = 0

    def get_rescued(self):
        return self.rescued

    def get_pos(self):
        return self.graph.node[self.node_index]["pos"]

    def run(self):
        self.next_step()

    def shortest_path(self, src, target, sub_nodes=None):
        sub_g = self.graph
        if sub_nodes is not None:
            sub_g = self.graph.subgraph(sub_nodes)
        return nx.shortest_path(sub_g, source=src, target=target)

    @staticmethod
    def _weighted_random_choice(prob_l):
        max_f = sum(fit for fit in prob_l)
        pick = random.uniform(0, max_f)
        current = 0
        for i in xrange(len(prob_l)):
            fit = prob_l[i]
            current += fit
            if current > pick:
                return i

    def add_pheromone(self, n_id, p_level, p_map):
        if n_id in p_map:
            p_map[n_id] = (p_map[n_id] + p_level) / float(2)
        else:
            p_map[n_id] = p_level

    def next_step(self):
        # get node neighbours that are trasversable
        edges = [e[1] for e in self.graph.edges(self.node_index)]
        nearby_nodes = []
        for e in edges:
            n_type = self.graph.node[e]["node_type"]
            if n_type in [0, 2] and e != self.node_index:
                nearby_nodes.append(e)

        non_visited = [e for e in nearby_nodes if e not in self.tabu_set]
        visited = [e for e in nearby_nodes if e in self.tabu_set]

        if not self.is_transporting_person:
            for e in nearby_nodes:
                if self.graph.node[e]["node_type"] == 2:
                    self.state = "transport_person"
                    self.graph.node[e]["node_type"] = 0
                    self.location_person_node = e
                    self.is_transporting_person = True
                    self.tabu_set.add(e)
                    break

        if self.state is "explore":

            prob_neighbours = self.calculate_prob(nearby_nodes)
            choice_i = Ant._weighted_random_choice(prob_neighbours)

            # leave pheromone on the previous node
            next_node_id = nearby_nodes[choice_i]
            self.node_index = next_node_id
            self.add_pheromone(self.node_index, 1, self.pheromone_dict_red)

        if self.state is "transport_person":
            path = self.shortest_path(self.node_index, self.home_node, sub_nodes=self.tabu_set)
            if len(path) > 1:
                self.node_index = path[1]
                self.add_pheromone(self.node_index, 1, self.pheromone_dict_blue)
            else:
                self.is_transporting_person = False
                self.rescued += 1
                self.state = "return_to_location"

        if self.state is "return_to_location":
            path = self.shortest_path(self.node_index, self.location_person_node, self.tabu_set)
            if len(path) > 1:
                self.node_index = path[1]
                self.add_pheromone(self.node_index, 1, self.pheromone_dict_blue)
            else:
                self.state = "explore"

        self.tabu_set.add(self.node_index)

    def calculate_prob(self, nearby_nodes):
        a_l = []
        b_l = []
        for n in nearby_nodes:
            p_red = self.graph.node[n]["p_red"]
            p_blue = self.graph.node[n]["p_blue"]
            a = p_red ** self.alpha
            b = p_blue ** self.beta
            a_l.append(a)
            b_l.append(b)

        delta_p = 10
        inverse_prob = []
        for e in a_l:
            r = 0.0
            if e > 0.0:
                r = 1 / float(e ** delta_p)
            inverse_prob.append(r)

        inverse_prob = [inverse_prob[i] * b_l[i] for i in xrange(len(inverse_prob))]
        inverse_prob = [inverse_prob[i] / float(sum(inverse_prob)) for i in xrange(len(inverse_prob))]

        #inverse_prob = list(np.asarray(inverse_prob) / np.trapz(inverse_prob))

        # b_l2 = []
        # for e in b_l:
        #     r = 0.0
        #     if e > 0.0:
        #         r = e / float(sum(b_l))
        #     b_l2.append(r)
        #
        # ab = []
        # for i in xrange(len(b_l2)):
        #     a = inverse_prob[i]
        #     b = b_l2[i]
        #
        #     #print a, b
        #     aba = (a / float(a + b)) * a + (b / float(b + a)) * b
        #     ab.append(aba)
        # ab = [e / float(sum(ab)) for e in ab]

        # print "inverse:\t", inverse_prob, len(inverse_prob), sum(inverse_prob)
        # print "b:\t\t\t", b_l2, len(b_l2), sum(b_l2)
        # print "ab:\t\t\t", ab, len(ab), sum(ab)

        return inverse_prob



