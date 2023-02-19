import os
import csv
import ast
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
import numpy as np
import random
import time
import itertools

def random_color_part():
    # return random.uniform(0.75, 1)
    return 0.8

def random_color():
    # return (random_color_part(), random_color_part(), random_color_part())
    # return [1, 0, 0]
    # rgb = [106, 212, 106]
    # rgb = [0, 137, 207]
    # rgb = [36, 70, 150]
    rgb = [128, 196, 231]
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
        # color = []
        # if (obstacle["crossing_weight"] == float('inf')):
        #     color = solid_color
        # else:
        #     color = soft_color
        p = Polygon(obstacle, color = solid_color)
        ax.add_patch(p)

def add_terminals(terminals):
    for terminal in terminals:
        plt.plot(terminal[0], terminal[1], 'g.')

def add_edges(edges):
    for edge in edges:
        plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], 'k-')
        plt.plot(edge[0][0], edge[0][1], 'r.')
        plt.plot(edge[1][0], edge[1][1], 'r.')

def add_corner_points(corner_points, obstacles):
    obstacle_corners = list(itertools.chain(*obstacles))
    print("ADDING CORNER POINT", corner_points)
    index = 0
    selected_corners = []
    for i in corner_points:
        if i == 1:
            selected_corners.append(obstacle_corners[index])
        index = index + 1
    for corner in selected_corners:
        plt.plot(corner[0], corner[1], 'y.')

def process_file(path, file_weight):
    current_generation = 0
    print("GETTING FOR " , file_weight)

    with open(path, 'r') as file:
        csvreader = csv.reader(file)
        obstacles = []
        terminals = []
        for row in csvreader:
            if row[0] == 'OBSTACLES':
                obstacles = ast.literal_eval(row[1])
            if row[0] == 'TERMINALS':
                terminals = ast.literal_eval(row[1])
            if row[0] == 'GENERATION' and float(row[3]) == file_weight:
                add_base_map(obstacles)
                edges = ast.literal_eval(row[9])
                corner_points = ast.literal_eval(row[7])
                weight = float(row[3])
                add_edges(edges)
                add_terminals(terminals)
                add_corner_points(corner_points, obstacles)
                global image_path
                plt.savefig(image_path + str(current_generation) + '-' + str(weight) + '.jpg')
                # plt.show()
                plt.close()
                current_generation = current_generation + 1
                break



def process_generation(path):
    current_generation = 0
    with open(path, 'r') as file:
        csvreader = csv.reader(file)
        obstacles = []
        terminals = []
        for row in csvreader:
            if row[0] == 'OBSTACLES':
                obstacles = ast.literal_eval(row[1])
            if row[0] == 'TERMINALS':
                terminals = ast.literal_eval(row[1])
            if row[0] == 'GENERATION':
                add_base_map(obstacles, terminals)
                edges = ast.literal_eval(row[9])
                corner_points = ast.literal_eval(row[8])
                add_corner_points(corner_points, obstacles)
                add_edges(edges)
                global image_path
                weight = row[3]
                plt.savefig(image_path + "generation-" + str(current_generation) + '-' + str(weight) + '.jpg')
                # plt.show()
                plt.close()
                current_generation = current_generation + 1
                break


def process_iteration(generations):
    generations = sorted(generations, key=lambda x: x[0], reverse=False)
    print(generations)
    process_generation(generations[-1])




def run(path, image_path, puzzle):
    results = filter(lambda x: "chromosome" not in x, os.listdir(path))
    iteration_data = {}

    lowest_weight = float('inf')
    lowest_weight_file = None

    for result in results:
        _, generation, iteration, weight = result.split("-")
        generation = int(generation)
        iteration = int(iteration)
        f1 = open(path + result, "r")
        try:
            file_weight = float(f1.readlines()[-1].split(",")[3])
            f1.close()
            weight = float(weight.split(".csv")[0])
            if (lowest_weight > file_weight):
                lowest_weight = file_weight
                lowest_weight_file = result
        except:
            1
            # print(result, len(f1.readlines()))
            # print("Error")

    print(lowest_weight_file)

    if not os.path.exists(image_path):
        os.makedirs(image_path)

    process_file(path + lowest_weight_file, lowest_weight)
    with open(path + lowest_weight_file, 'r') as file:
        csvreader = csv.reader(file)
        gen = 0
        data = []
        for row in csvreader:
            if row[0] == 'GENERATION':
                gen = gen + 1
                data.append([i, gen, float(row[1]), float(row[2]), float(row[3])])
        with open('./data_results/' + str(i) + '-data.csv', mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(data)


# for i in [1,2,3,4,5,10,10]:
for i in [10,100,501]:
    image_path = f'/home/shreyas/Work/Sheru/roads/roads/solutions/{str(i)}/generated_images/'
    path = f'/home/shreyas/Work/Sheru/roads/roads/solutions/{str(i)}/data_dir/'
    run(path, image_path, i)
