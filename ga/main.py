import csv
from tkinter import Y
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import numpy as np
import random
from mst import Graph
import math
import shapely.geometry

def point_inside_polygon(x, y, poly, include_edges=False):
    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if p1y == p2y:
            if y == p1y:
                if min(p1x, p2x) <= x <= max(p1x, p2x):
                    inside = include_edges
                    break
                elif x < min(p1x, p2x):
                    inside = not inside
        else:
            if min(p1y, p2y) <= y <= max(p1y, p2y):
                xinters = (y - p1y) * (p2x - p1x) / float(p2y - p1y) + p1x

                if x == xinters:
                    inside = include_edges
                    break

                if x < xinters:
                    inside = not inside

        p1x, p1y = p2x, p2y

    return inside


class Points(list):
    pass

    def __str__(self):
        return " | ".join([str(point) for point in self])

    def to_array(self):
        return [[point.x, point.y] for point in self]


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str(self.x) + ", " + str(self.y)


class Obstacles(list):
    pass

    def __str__(self):
        return "\n============\n" + "\n".join([str(obstacle) for obstacle in self]) + "\n============\n"


class Obstacle:
    crossing_weight = 0

    def __init__(self, crossing_weight):
        self.crossing_weight = crossing_weight
        self.points = Points()

    def __str__(self):
        return "Weight: " + str(self.crossing_weight) + ",  Points: " + str(self.points)


def get_all_points_array(obstacles, terminals):
    points = []
    for obstacle in obstacles:
        for point in obstacle.points:
            points.append([point.x, point.y])
    for point in terminals:
        points.append([point.x, point.y])
    return points


def get_delaunay_points(points):
    points = np.array(points)
    tri = Delaunay(points)
    return tri

def get_map_edges(data):
    max_x = max(data, key=lambda x: x[0])[0]
    max_y = max(data, key=lambda x: x[1])[1]
    min_x = min(data, key=lambda x: x[0])[0]
    min_y = min(data, key=lambda x: x[1])[1]
    return [[min_x, min_y], [max_x, max_y]]

def line_inside_polygon(p1, p2, obstacle_points):
    line = shapely.geometry.LineString([p1, p2])
    polygon = shapely.geometry.Polygon(obstacle_points)
    return line.intersects(polygon)

def get_total_corners(obstacles):
    corners = 0
    for obstacle in obstacles:
        corners = corners + len(obstacle.points)
    return corners

def get_chromosome_points_1(centroids, obstacles):
    total_corners = get_total_corners(obstacles)
    return [centroids, ([0] * total_corners)]

def get_chromosome_points_2(terminals, obstacles):
    k = get_total_corners(obstacles)
    n = len(terminals)
    required_points = n + k
    borders = get_map_edges(all_points_array)
    points = []
    while (len(points) < required_points):
        x = np.random.uniform(low=borders[0][0], high=borders[1][0], size=(1,))[0]
        y = np.random.uniform(low=borders[0][0], high=borders[1][0], size=(1,))[0]
        inside = False
        for obstacle in obstacles:
            if (point_inside_polygon(x, y, obstacle.points.to_array())):
                inside = True
                break
        if inside == False:
                points.append([x, y])
    return points

def get_chromosome_points_3(obstacles):
    k = get_total_corners(obstacles)
    return np.random.randint(low=0, high=2, size=(k,))

# def get_initial_population():

def get_chromosome_1_initial_population(terminals, chromosome_points, obstacles):
    size = random.randint(0, len(chromosome_points[0]))
    s_points = random.sample(chromosome_points[0], size)
    vertices = len(terminals) + len(s_points)
    final_points = s_points
    for terminal in terminals:
        final_points.append([terminal.x, terminal.y])        
    
    # shapely_points = []
    # for point in final_points:
    #     shapely_points.append(shapely.geometry.Point(final_points[0], final_points[1]))

    graph = Graph(vertices)
    overlap = False
    for i in range(len(final_points)):
        for j in range(i + 1, len(final_points)):
            graph.addEdge(i, j, math.dist(final_points[i], final_points[j]))
  
    mst = graph.KruskalMST()
    edges = []
    for edge in mst:
        edges.append([final_points[edge[0]], final_points[edge[1]]])
        # print(edge)
        for obstacle in obstacles:
            if (line_inside_polygon(final_points[edge[0]], final_points[edge[1]], obstacle.points.to_array())):
                    overlap = True
                    break
    if overlap == True:
        return get_chromosome_1_initial_population(terminals, chromosome_points, obstacles)

    return [edges, final_points + chromosome_points[1]]

with open('./dataset/SolidObstacles/obstacles1.csv', newline='\n') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    obstacles = Obstacles()
    for row in reader:
        if (row != ['', '']):
            if (row[1] == ''):
                obstacles.append(Obstacle(row[0]))
            else:
                obstacles[-1].points.append(Point(float(row[0]), float(row[1])))

with open('./dataset/SolidObstacles/terminals1.csv', newline='\n') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    next(reader)
    terminals = Points()
    for row in reader:
        terminals.append(Point(float(row[0]), float(row[1])))

all_points_array = get_all_points_array(obstacles, terminals)
delaunay_points = get_delaunay_points(all_points_array)
centroids = []

for simplice in delaunay_points.simplices:
    x1, y1 = all_points_array[simplice[0]]
    x2, y2 = all_points_array[simplice[1]]
    x3, y3 = all_points_array[simplice[2]]
    cx, cy = [(x1 + x2 + x3) / 3, (y1 + y2 + y3) / 3]
    inside = False
    for obstacle in obstacles:
        if (point_inside_polygon(cx, cy, obstacle.points.to_array())):
            inside = True
            break
    if inside == False:
        centroids.append([cx, cy])


# print(all_points_array)
# get_map_edges(all_points_array)
# print("==============> CHROMOSOME 1")
# chromosome_1 = get_chromosome_points_1(centroids, obstacles)
# print(chromosome_1)

# print("==============> CHROMOSOME 2")
# chromosome_2 = get_chromosome_points_2(terminals, obstacles)
# print(chromosome_2)

# print("==============> CHROMOSOME 3")
# chromosome_3 = get_chromosome_points_3(obstacles)
# print(chromosome_3)

# type1_population = []
# for i in range(1):
#     type1_population.append(get_chromosome_1_initial_population(terminals, chromosome_1, obstacles))

# print(type1_population)

# plt.figure()

# for obstacle in obstacles:
#     coord = obstacle.points.to_array()
#     coord.append(coord[0])
#     xs, ys = zip(*coord)
#     plt.plot(xs,ys)

# for centroid in centroids:
#     plt.plot(centroid[0], centroid[1],'ro') 

# for terminal in terminals:
#     plt.plot(terminal.x, terminal.y,'bo') 

# for edge in pop1:
#     plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], 'go-')

plt.show()
print("===========")
print(centroids)

