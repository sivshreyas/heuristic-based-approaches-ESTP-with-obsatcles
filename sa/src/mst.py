import math
from shapely.geometry import Point, LineString, GeometryCollection, MultiLineString
from shapely.geometry.polygon import Polygon
from src.collision import Collision
import itertools

length_maps = {}
sel_maps = {}

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = []

    def add_edges(self, final_points, obstacles):
        global length_maps
        global sel_maps
        # print(len(final_points))
        # for i in range(len(final_points)):
        #     for j in range(i + 1, len(final_points)):
        # print(len(list(itertools.combinations(range(len(final_points)), 2))))
        for comb in itertools.combinations(range(len(final_points)), 2):
                i, j = comb
                sel =  None
                sel_str = str([final_points[i], final_points[j]])
                if sel_str in sel_maps:
                    sel= sel_maps[sel_str]
                if sel == 1 or (sel == None and Collision.is_line_intersecting_solid_polygons([final_points[i], final_points[j]], obstacles)):
                    self.add_edge(i, j, float("inf"))
                    sel_maps[sel_str] = 1
                elif sel == 2 or (sel == None and Collision.is_line_intersecting_polygons([final_points[i], final_points[j]], obstacles)):
                    sel_maps[sel_str] = 2
                    points_str = str([final_points[i], final_points[j]])
                    if points_str in length_maps:
                        self.add_edge(i, j, length_maps[points_str])
                    else:
                        added = False
                        line = LineString([final_points[i], final_points[j]])
                        intersections_length = 0
                        intersections_weight = 0
                        for k in range(len(obstacles)):
                            obstacle = obstacles[k]
                            if Collision.is_line_intersecting_polygon([final_points[i], final_points[j]], obstacle.points):
                                if obstacle.crossing_weight != float("inf"):
                                    polygon = Polygon(obstacle.points)
                                    intersection = line.intersection(polygon)
                                    if str(intersection.type) == 'MultiLineString' or str(intersection.type) == 'LineString':
                                        intersections_length = intersections_length + intersection.length
                                        intersections_weight = intersections_weight + (intersection.length * obstacle.crossing_weight)
                                        added = True
                        if not added:
                            length_maps[points_str] = float("inf")
                            self.add_edge(i, j, float("inf"))
                        else:
                            changed_length = math.dist(final_points[i], final_points[j]) - intersections_length
                            # print("intersection weight ", intersections_weight, intersections_length)
                            final_length = changed_length + intersections_weight
                            length_maps[points_str] = final_length
                            self.add_edge(i, j, final_length)
                else:
                    self.add_edge(i, j, math.dist(final_points[i], final_points[j]))


    def add_edge(self, u, v, w):
        # print("ADDING ")
        # print([u, v, w])
        self.graph.append([u, v, w])

    def find(self, parent, i):
        if parent[i] == i:
            return i
        return self.find(parent, parent[i])

    def union(self, parent, rank, x, y):
        xroot = self.find(parent, x)
        yroot = self.find(parent, y)

        if rank[xroot] < rank[yroot]:
            parent[xroot] = yroot
        elif rank[xroot] > rank[yroot]:
            parent[yroot] = xroot

        else:
            parent[yroot] = xroot
            rank[xroot] += 1

    def KruskalMST(self):
        result = []
        i = 0
        e = 0

        self.graph = sorted(self.graph, key=lambda item: item[2])

        parent = []
        rank = []

        for node in range(self.V):
            parent.append(node)
            rank.append(0)

        while e < self.V - 1:
            # print(e, i, len(self.graph))
            u, v, w = self.graph[i]
            i = i + 1
            x = self.find(parent, u)
            y = self.find(parent, v)

            if x != y:
                e = e + 1
                result.append([u, v, w])
                self.union(parent, rank, x, y)

        minimum_cost = 0
        for u, v, weight in result:
            minimum_cost += weight

        self.minimum_cost = minimum_cost
        self.result = result
