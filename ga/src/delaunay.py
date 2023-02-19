from scipy.spatial import Delaunay as Dl
import numpy as np
import itertools
from src.collision import Collision


class Delaunay:
    def __init__(self, obstacles, terminals):
        self.points = terminals + list(itertools.chain(*obstacles))
        self.terminals = terminals
        self.obstacles = obstacles

    def get_delaunay_points(self):
        points = np.array(self.points)
        tri = Dl(points)
        return tri

    def get_centroids(self):
        centroids = []
        for simplice in self.get_delaunay_points().simplices:
            x1, y1 = self.points[simplice[0]]
            x2, y2 = self.points[simplice[1]]
            x3, y3 = self.points[simplice[2]]
            cx, cy = [(x1 + x2 + x3) / 3, (y1 + y2 + y3) / 3]
            if not Collision.is_point_inside_solid_polygons([cx, cy], self.obstacles):
                centroids.append([cx, cy])
        return centroids
