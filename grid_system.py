import pygame
import random
import json
import os
import math
import networkx as nx
import time

from colony_system import ColonySystem


class GridSystem(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.colors = {
            'black': (0, 0, 0),
            'white': (254, 254, 254),
            'green': (0, 255, 0),
            'red': (255, 0, 0),
            'blue': (0, 0, 254),
            'gray': (105, 105, 105)
        }

        self.square_size = 8

        self.window_margin = 1
        self.grid = []

        if self.cfg["dataset"]:
            self.load_grid()

            self.row_number = len(self.grid)
            self.col_number = len(self.grid[0])
        else:
            self.row_number = self.cfg['row_number']
            self.col_number = self.cfg['col_number']

        self.window_width = self.col_number * self.square_size + ((self.window_margin * 2) + (self.window_margin * self.col_number))
        self.window_height = self.row_number * self.square_size + ((self.window_margin * 2) + (self.window_margin * self.row_number))

        self.graph = self.gen_graph()

        self.colony_s = ColonySystem(self.cfg, self.graph)

        self.screen = None
        self.screen_alpha_red = None
        self.screen_alpha_blue = None

        self.anim_done = False
        self.draw_grid = True
        self.init_pygame()

    def load_grid(self):
        with open(os.path.realpath(self.cfg["dataset"])) as data_file:
            self.grid = json.load(data_file)

    def gen_graph(self):
        graph = nx.Graph()

        # create nodes
        for i in xrange(self.col_number):
            for j in xrange(self.row_number):
                node_type = self.grid[i][j]
                graph.add_node(GridSystem.gen_node_id(i, j, self.col_number), {
                    'pos': (i, j),
                    'p_red': self.cfg["pheromone_t0"] if node_type in [0, 2] else 0.0,
                    'p_blue': 0.001 if node_type in [0, 2] else 0.0,
                    'node_type': node_type
                })

        # add edges
        for i in xrange(self.col_number):
            for j in xrange(self.row_number):
                neighbours = list(GridSystem.get_neighbours_of_edge(i,
                                                                    j,
                                                                    self.col_number,
                                                                    self.row_number,
                                                                    full_neighbours=False))
                c_node_id = GridSystem.gen_node_id(i, j, self.col_number)
                for n_id in neighbours:
                    graph.add_edge(c_node_id, n_id)

        return graph

    @staticmethod
    def gen_node_id(i, j, col_size):
        return (i * col_size) + j

    @staticmethod
    def get_neighbours_of_edge(ax, ay, col_size, row_size, full_neighbours=False):

        if full_neighbours:
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    dx = ax + i
                    dy = ay + j
                    if 0 <= dx < col_size and 0 <= dy < row_size:
                        yield GridSystem.gen_node_id(dx, dy, col_size)
        else:
            for e in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                dx = ax + e[0]
                dy = ay + e[1]
                if 0 <= dx < col_size and 0 <= dy < row_size:
                    yield GridSystem.gen_node_id(dx, dy, col_size)

    @staticmethod
    def gen_grid(row_n, col_n):
        g = []
        for r in range(row_n):
            g.append([])
            for c in range(col_n):
                g[r].append(0)
        return g

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.screen_alpha_red = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA, 32)
        self.screen_alpha_blue = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA, 32)

    def start(self):
        clock = pygame.time.Clock()

        run_ants = True

        # Draw the pheromones
        max_r_pheromones = 1
        max_b_pheromones = 1
        iterations = 0

        while not self.anim_done:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.anim_done = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        run_ants = True
                        pass

            if run_ants:
                self.colony_s.run()

                # Set the screen background
                self.screen.fill(self.colors['black'])

                # check if all persons are rescued
                rescued = 0
                for ant in self.colony_s.get_ants():
                    rescued += ant.get_rescued()

                if rescued >= self.colony_s.persons_to_rescue:
                    print "[INFO]", "All rescued, finishing animation"
                    self.anim_done = True
                    run_ants = False

                # Draw the grid
                if self.draw_grid:
                    r_pheromones = []
                    b_pheromones = []

                    for n, d in self.graph.nodes_iter(data=True):
                        x, y = d["pos"]
                        r_pheromones.append(d["p_red"])
                        b_pheromones.append(d["p_blue"])

                        if d["node_type"] == 1:
                            color = self.colors['black']
                        elif d["node_type"] == 2:
                            color = self.colors['blue']
                        else:
                            color = self.colors['white']

                        pygame.draw.rect(self.screen,
                                         color,
                                         [(self.window_margin + self.square_size) * y + self.window_margin,
                                          (self.window_margin + self.square_size) * x + self.window_margin,
                                          self.square_size,
                                          self.square_size])

                    # Draw the ants
                    for ant in self.colony_s.get_ants():
                        x, y = ant.get_pos()
                        radius = int(math.floor(self.square_size / float(2)))

                        # square top left pos + radius to get the circle exactly at the center of the square
                        circle_pos = [((self.window_margin + self.square_size) * y + self.window_margin) + radius,
                                      ((self.window_margin + self.square_size) * x + self.window_margin) + radius]

                        pygame.draw.circle(self.screen, self.colors['green'], circle_pos, radius)

                        if ant.is_transporting_person:
                            pygame.draw.circle(self.screen, self.colors['blue'], circle_pos, int(radius/float(2)) -1)
                        if ant.state is "return_to_location":
                            pygame.draw.circle(self.screen, self.colors['black'], circle_pos, int(radius / float(2)) -1)
                        pass

                    #print r_pheromones
                    if max(r_pheromones) > max_r_pheromones:
                        max_r_pheromones = max(r_pheromones)

                    if max(b_pheromones) > max_b_pheromones:
                        max_b_pheromones = max(b_pheromones)

                    for n, d in self.graph.nodes_iter(data=True):
                        x, y = d["pos"]
                        r_p_norm = (d["p_red"] / float(max_r_pheromones))
                        r_p = int(r_p_norm * 255)
                        rgb_a_red = (255, 0, 0, r_p)

                        b_p_norm = (d["p_blue"] / float(max_b_pheromones))
                        #print b_p_norm
                        b_p = int(b_p_norm * 255)
                        rgb_a_blue = (0, 0, 255, b_p)

                        #print "real", d["p_red"], "r_p_norm", r_p_norm, "r_p", r_p, "max", max_r_pheromones, d["pos"]

                        if d["node_type"] in [0, 2]:
                            pygame.draw.rect(self.screen_alpha_red,
                                             rgb_a_red,
                                             [(self.window_margin + self.square_size) * y + self.window_margin,
                                      (self.window_margin + self.square_size) * x + self.window_margin,
                                      self.square_size,
                                      self.square_size])

                            pygame.draw.rect(self.screen_alpha_blue,
                                             rgb_a_blue,
                                             [(self.window_margin + self.square_size) * y + self.window_margin,
                                              (self.window_margin + self.square_size) * x + self.window_margin,
                                              self.square_size,
                                              self.square_size])

                # Limit to 60 frames per second
                clock.tick(60)

                self.screen.blit(self.screen_alpha_red, (0, 0))
                self.screen.blit(self.screen_alpha_blue, (0, 0))

                # Go ahead and update the screen with what we've drawn.
                pygame.display.flip()
                #time.sleep(0.1)
                #run_ants = False
                iterations += 1

        print "[INFO]", "iterations:", iterations

        # Be IDLE friendly. If you forget this line, the program will 'hang' on exit.
        pygame.quit()
        pass


