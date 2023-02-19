import os
import csv
import ast
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
import numpy as np
import random
import time
import itertools
import json

def random_color_part():
    # return random.uniform(0.75, 1)
    return 0.8

def random_color():
    # return (random_color_part(), random_color_part(), random_color_part())
    # return [1, 0, 0]
    # rgb = [106, 212, 106]
    # rgb = [0, 137, 207]
    rgb = [36, 70, 150]
    return [rgb[0]/256, rgb[1]/256, rgb[2]/256]

def random_soft_color_part():
    # return random.uniform(0, 0.5)
    return 0.8

def random_soft_color():
    # return (random_soft_color_part(), random_soft_color_part(), random_soft_color_part())
    rgb = [128, 196, 231]
    return [rgb[0]/256, rgb[1]/256, rgb[2]/256]


def add_base_map(obstacles):
    fig, ax = plt.subplots()
    soft_color = random_soft_color()
    solid_color = random_color()

    for obstacle in obstacles:
        color = []
        if (obstacle["crossing_weight"] == float('inf')):
            color = solid_color
        else:
            color = soft_color
        p = Polygon(obstacle["points"], color = color)
        ax.add_patch(p)

def add_terminals(terminals):
    for terminal in terminals:
        plt.plot(terminal[0], terminal[1], 'go')

def add_edges(edges):
    for edge in edges:
        plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], 'k-')
        plt.plot(edge[0][0], edge[0][1], 'ro')
        plt.plot(edge[1][0], edge[1][1], 'ro')

def add_corner_points(corner_points, obstacles):
    points = []
    for obstacle in obstacles:
        points.append(obstacle["points"])

    obstacle_corners = list(itertools.chain(*points))
    print(obstacle_corners)
    index = 0
    selected_corners = []
    for i in corner_points:
        if i == 1:
            selected_corners.append(obstacle_corners[index])
        index = index + 1
    for corner in selected_corners:
        plt.plot(corner[0], corner[1], 'yo')


def process_trial(path):
    with open(path, 'r') as file:
        csvreader = csv.reader(file)
        obstacles = []
        terminals = []
        for row in csvreader:
            if row[0] == 'OBSTACLES':
                # obstacles = ast.literal_eval(row[1])
                obstacles = json.loads(row[1])

            if row[0] == 'TERMINALS':
                terminals = ast.literal_eval(row[1])
            if row[0] == 'INITIAL_CHROMOSOME':
                add_base_map(obstacles)
                id = row[2]
                title = row[1]
                edges = ast.literal_eval(row[9])
                print(row)
                corner_points = ast.literal_eval(row[7])
                add_edges(edges)
                add_corner_points(corner_points, obstacles)
                add_terminals(terminals)
                global image_path
                plt.savefig(image_path + title + '-' + str(id) + '.jpg')
                # plt.show()
                plt.close()
                # break


image_path = '/home/shreyas/Work/Sheru/roads/roads/solutions-11-8/13/generated_chromosomes/'
path = '/home/shreyas/Work/Sheru/roads/roads/solutions-11-8/13/data_dir/'
results = filter(lambda x: "chromosome" in x, os.listdir(path))
iteration_data = {}

if not os.path.exists(image_path):
    os.makedirs(image_path)

for result in results:
    process_trial(path + result)
    break


