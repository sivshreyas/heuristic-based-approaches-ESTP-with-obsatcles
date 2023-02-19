from src.collision import Collision
from src.mst import Graph
from src.chromosome import Chromosome
import random
import math
from joblib import Parallel, delayed
from shapely.geometry import Point, LineString, GeometryCollection, MultiLineString
from shapely.geometry.polygon import Polygon
import uuid

class ChromosomeOne(Chromosome):
    def __init__(self, centroids, obstacles, terminals):
        self.centroids = centroids
        self.obstacles = obstacles
        self.terminals = terminals
        self.members = []
        self.base = self.get_base()

    def get_base(self):
        return [self.centroids, ([0] * self.get_total_corners())]

    def generate_initial_population(self, size):
        members = Parallel(n_jobs=32)(delayed(self.get_member)() for i in range(size))

        # self.members = sorted([x for x in members if x is not None], key=lambda x: x['minimum_cost'])
        self.members = [x for x in members if x is not None]
        # if (size > len(self.members)):
        #     print("LEN MEMBERS ", len(self.members))
        #     return members + self.generate_initial_population(size - len(self.members))
        # else:
        #     return members
        return self.members

    def get_member(self, attempt = 20):
        # print("CURRENT attempt LEN", attempt)
        if attempt == 0:
            return None
        size = random.randint(0, min(len(self.base[0]), len(self.terminals) - 2))
        # size = random.randint(0, len(self.base[0]))
        s_points = random.sample(self.base[0], size)
        # vertices = len(self.terminals) + len(s_points)
        vertices = len(self.terminals) + len(self.base[0])
        # print(s_points, len(self.terminals), len(self.terminals), size, len(self.base[0]))
        # if self.is_invalid_constraints(s_points, self.terminals, []):
        #     return self.get_member(attempt - 1)
        # print(len(self.terminals), len(s_points), size, len(self.base[0]))

        # final_points = s_points
        final_points = self.base[0]
        for terminal in self.terminals:
            final_points.append(terminal)

        graph = Graph(vertices)
        graph.add_edges(final_points, self.obstacles)

        graph.KruskalMST()

        edges = []
        overlap = False

        # print(graph.result)
        for edge in graph.result:
            edge = [final_points[edge[0]], final_points[edge[1]]]
            edges.append(edge)
            if Collision.is_line_intersecting_solid_polygons(edge, self.obstacles):
                overlap = True
                break

        if overlap:
            return self.get_member(attempt - 1)
        # print('len edges', len(edges))
        # if self.is_invalid_constraints(s_points, self.terminals, edges):
        #     return self.get_member(attempt - 1)
        return {'final_points': final_points, 'minimum_cost': graph.minimum_cost, 'edges': edges, 'corner_points': self.get_corner_points(final_points), 'id': uuid.uuid1()}
