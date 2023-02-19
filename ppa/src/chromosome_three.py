from src.collision import Collision
from src.mst import Graph
from src.chromosome import Chromosome
import random
import numpy as np
import math
import itertools
from joblib import Parallel, delayed
import uuid

class ChromosomeThree(Chromosome):
    def __init__(self, obstacles, terminals):
        self.obstacles = obstacles
        self.terminals = terminals
        self.members = []

    def generate_initial_population(self, size):
        members = Parallel(n_jobs=32)(delayed(self.get_member)() for i in range(size))

        # self.members = sorted([x for x in members if x is not None], key=lambda x: x['minimum_cost'])
        self.members = [x for x in members if x is not None]
        return members

    def get_member(self, attempt = 20):
        if attempt == 0:
            return None
        obstacle_points = list(itertools.chain(*self.obstacles))
        k = len(obstacle_points)
        obstacle_binary = np.random.randint(low=0, high=2, size=(k,))
        final_points = []
        for i in range(0, k):
            if obstacle_binary[i]:
                final_points.append(obstacle_points[i])

        final_points.extend(self.terminals)

        graph = Graph(len(final_points))

        graph.add_edges(final_points, self.obstacles)

        graph.KruskalMST()

        edges = []
        overlap = False

        for edge in graph.result:
            edge = [final_points[edge[0]], final_points[edge[1]]]
            edges.append(edge)
            if Collision.is_line_intersecting_solid_polygons(edge, self.obstacles):
                overlap = True
                break

        if overlap:
            return self.get_member(attempt - 1)

        return {'final_points': final_points, 'minimum_cost': graph.minimum_cost, 'edges': edges, 'corner_points': obstacle_binary.tolist() , 'id': uuid.uuid1()}
