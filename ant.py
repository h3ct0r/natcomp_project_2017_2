import random
import time
from threading import Thread
import math
import copy


class Ant(Thread):
    def __init__(self, ant_id, alpha, beta, grid, grid_pheromone):
        #super(Ant, self).__init__()
        Thread.__init__(self)

        self.ant_id = ant_id
        self.alpha = alpha
        self.beta = beta

        self.grid = grid
        self.grid_pheromone = grid_pheromone

    def run(self):
        self.next_step()

    def next_step(self):
        p_medians = []

        node_fitness = []
        for n in self.grid:
            node_i = n.node_id
            p_v1 = (self.pheromone_map[node_i] ** self.alpha) * (self.density_map[node_i] ** self.beta)
            p_v2 = sum([((self.pheromone_map[i] ** self.alpha) * (self.density_map[i] ** self.beta)) for i in xrange(len(self.pheromone_map))])
            p_k_i = float(p_v1) / float(p_v2)
            node_fitness.append(p_k_i)

        #t_start = time.time()
        count = 0
        while len(p_medians) < self.p_count:
            # choose random between (0, 1] and test with eq 10
            # to prevent from looping forever
            if count <= self.p_count * 1000:
                chosen_i = self._weighted_random_choice(node_fitness)
            else:
                print "[DEBUG]", "Ant #{} random choose".format(self.ant_id)
                chosen_i = random.randint(0, len(node_fitness) - 1)

            if chosen_i not in p_medians:
                p_medians.append(chosen_i)

            count += 1


        #t_end = time.time()
        #print '[TIME 1]', 'elapsed time:{}'.format(t_end - t_start)

        return self.calculate_result(p_medians)

    def calculate_result(self, p_medians):
        #print '[DEBUG]', 'Ant {} choosing p-medians: {}'.format(self.ant_id, p_medians)
        # t_start = time.time()

        allocations = dict()
        allocated_nodes = []
        allocation_sum = 0

        medians_nodes = [self.grid[i] for i in p_medians]
        medians_nodes = copy.deepcopy(medians_nodes)

        for i in p_medians:
            allocations[i] = []

        for n in self.grid:
            if n.node_id in p_medians:
                continue

            ordered_medians = list(sorted(medians_nodes, key=lambda (a): math.sqrt((a.x - n.x) ** 2 + (a.y - n.y) ** 2)))
            #print 'node:', n.node_id, 'ordered medians:', ordered_medians
            for med in ordered_medians:
                #print '[DEBUG]', 'search:', n.node_id, 'to', med.node_id, math.sqrt(
                #    ((med.x - n.x) ** 2) + ((med.y - n.x) ** 2))
                if n.d <= med.c:
                    med.c -= n.d
                    allocations[med.node_id].append(n.node_id)
                    allocated_nodes.append(n.node_id)
                    allocation_sum += math.sqrt((n.x - med.x) ** 2 + (n.y - med.y) ** 2)
                    break

        #print 'allocated_nodes:{}'.format(allocated_nodes)
        #print '[DEBUG]', 'Ant {} allocations {}'.format(self.ant_id, allocations)
        self.previous_result = allocations

        if len(allocated_nodes) != len(self.grid) - len(p_medians):
            self.previous_result_status = False
        else:
            self.previous_result_status = True

        self.previous_result_sum = allocation_sum

        #print '[DEBUG]', 'Ant {} result is valid? {} {}/{}'.format(self.ant_id, self.previous_result_status, len(allocated_nodes), len(self.data) - len(p_medians))
        return self.previous_result_status


