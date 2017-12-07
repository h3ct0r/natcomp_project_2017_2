import pygame
import random
import json
import os
import networkx as nx

from colony_system import ColonySystem


class GridSystem(object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.colors = {
            'black': (0, 0, 0),
            'w': (254, 254, 254),
            'g': (0, 255, 0),
            'r': (255, 0, 0),
            'b': (0, 0, 254),
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
        #self.generate_random_obstacles_and_persons()

        self.colony_s = ColonySystem(self.cfg, self.graph)

        self.anim_done = False
        self.init_pygame()
        self.init_colony()

    def init_colony(self):
        pass

    def load_grid(self):
        with open(os.path.realpath(self.cfg["dataset"])) as data_file:
            self.grid = json.load(data_file)

    def init_graph(self):
        graph = nx.Graph()

        # create nodes
        for i in xrange(self.col_number):
            for j in xrange(self.row_number):
                cell_type = self.grid[i][j]
                graph.add_node(GridSystem.gen_node_id(i, j), {
                    'pos': (i, j),
                    'p_red': 0.0,
                    'p_blue': 0.0,
                    'node_type': cell_type
                })

        # add edges
        for i in xrange(self.col_number):
            for j in xrange(self.row_number):
                neighbours = list(GridSystem.get_neighbours_of_edge(i, j, self.col_number, self.row_number))
                c_node_id = GridSystem.gen_node_id(i, j)
                for n_id in neighbours:
                    graph.add_edge(c_node_id, n_id)

        return graph

    @staticmethod
    def gen_node_id(i, j):
        cell_id_str = str(i) + str(j)
        cell_id = int(cell_id_str)
        return cell_id

    @staticmethod
    def get_neighbours_of_edge(ax, ay, col_size, row_size, full_neighbours=False):

        if full_neighbours:
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    dx = ax + i
                    dy = ay + j
                    if 0 <= dx < col_size and 0 <= dy < row_size:
                        yield GridSystem.gen_node_id(dx, dy)
        else:
            for e in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                dx = ax + e[0]
                dy = ay + e[1]
                if 0 <= dx < col_size and 0 <= dy < row_size:
                    yield GridSystem.gen_node_id(dx, dy)

    @staticmethod
    def gen_grid(row_n, col_n):
        g = []
        for r in range(row_n):
            g.append([])
            for c in range(col_n):
                g[r].append(0)
        return g

    def generate_random_obstacles_and_persons(self, obstacle=100, person=10):
        for i in xrange(obstacle):
            r = random.randint(0, self.row_number - 1)
            c = random.randint(0, self.col_number - 1)
            self.grid[r][c] = 1

        #last_person = None
        for i in xrange(person):
            r = random.randint(0, self.row_number - 1)
            c = random.randint(0, self.col_number - 1)
            self.grid[r][c] = 2
            #last_person = (r, c)

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.screen_alpha = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA, 32)

    def start(self):
        clock = pygame.time.Clock()

        while not self.anim_done:

            self.colony_s.run()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.anim_done = True

            # Set the screen background
            self.screen.fill(self.colors['black'])
            #self.screen_alpha.fill((255, 0, 0, 128)) # 255 full # 0 none

            # Draw the grid
            for row in range(self.row_number):
                for column in range(self.col_number):
                    color = self.colors['w']
                    if self.grid[row][column] == 1:
                        color = self.colors['black']
                    elif self.grid[row][column] == 2:
                        color = self.colors['b']

                    pygame.draw.rect(self.screen_alpha,
                                     color,
                                     [(self.window_margin + self.square_size) * column + self.window_margin,
                                      (self.window_margin + self.square_size) * row + self.window_margin,
                                      self.square_size,
                                      self.square_size])

            # Limit to 60 frames per second
            clock.tick(60)

            self.screen.blit(self.screen_alpha, (0, 0))

            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

        # Be IDLE friendly. If you forget this line, the program will 'hang' on exit.
        pygame.quit()
        pass


