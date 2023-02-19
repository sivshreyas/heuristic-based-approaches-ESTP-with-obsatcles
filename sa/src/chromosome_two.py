from src.collision import Collision
from src.mst import Graph
from src.chromosome import Chromosome
import random
import numpy as np
import math
import itertools
from joblib import Parallel, delayed
import uuid

class ChromosomeTwo(Chromosome):
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
        n = len(self.terminals)
        required_points = random.randint(0, n + k)
        # required_points = random.randint(0, n - 2)
        borders = self.get_bounding_box()
        points = []
        while len(points) < required_points:
            x = np.random.uniform(low=borders[0][0], high=borders[1][0], size=(1,))[0]
            y = np.random.uniform(low=borders[0][0], high=borders[1][0], size=(1,))[0]
            if not Collision.is_point_inside_solid_polygons([x, y], self.obstacles):
                points.append([x, y])

        final_points = points + self.terminals

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

        # if self.is_invalid_constraints(points, self.terminals, edges):
        #     return self.get_member(attempt - 1)

        return {'final_points': final_points, 'minimum_cost': graph.minimum_cost, 'edges': edges, 'corner_points': self.get_corner_points(final_points), 'id': uuid.uuid1()}
