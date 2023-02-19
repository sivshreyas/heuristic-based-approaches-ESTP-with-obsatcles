import copy
import itertools
from src.chromosome import Chromosome
from src.chromosome_one import ChromosomeOne
from src.chromosome_two import ChromosomeTwo
from src.chromosome_three import ChromosomeThree
from src.delaunay import Delaunay
from src.plot import Plot
from joblib import Parallel, delayed
import random
from src.mst import Graph
from src.collision import  Collision
import math
from scipy.spatial.distance import pdist
import numpy as np
import os
import uuid
import csv
import json
from  src.fermat import calculate_fermat_point
import atomics

# fitness_evaluations = 0
# fitness_evaluations = atomics.atomic(width=4, atype=atomics.INT)

class Population:
    def __init__(self, obstacles, terminals):
        self.obstacles = obstacles
        self.terminals = terminals
        self.terminalsSet = set(map(lambda x: str(x), terminals))
        # self.fitness_evaluations = atomics.atomic(width=4, atype=atomics.INT)

    # def get_fitness_evaluations(self):
    #     # global fitness_evaluations
    #     print(self.fitness_evaluations)
    #     print(self.fitness_evaluations.load())
    #     return self.fitness_evaluations.load()

    def generate_initial_population(self):
        centroids = Delaunay(self.obstacles, self.terminals).get_centroids()
        self.base_chromosome = ChromosomeOne(centroids, self.obstacles, self.terminals)

        print("CHECKING ChromosomeOne")
        chromosome_one = ChromosomeOne(centroids, self.obstacles, self.terminals)
        chromosome_one.generate_initial_population(5)

        print("CHECKING ChromosomeThree")
        chromosome_three = ChromosomeThree(self.obstacles, self.terminals)
        chromosome_three.generate_initial_population(166)


        print("CHECKING ChromosomeTwo")
        chromosome_two = ChromosomeTwo(self.obstacles, self.terminals)
        chromosome_two.generate_initial_population(166)


        self.chromosome_one = chromosome_one
        self.chromosome_two = chromosome_two
        self.chromosome_three = chromosome_three

    def get_top_initial_members(self):
        print("TAKING CHROMOSOME 1 ", len(self.base_chromosome.centroids))
        # self.initial_members = self.chromosome_one.members[0: int(math.sqrt(len(self.base_chromosome.centroids)))] + random.sample(self.chromosome_two.members, 50) + random.sample(self.chromosome_three.members, 50)
        # self.initial_members = random.sample(self.chromosome_one.members, min(len(self.chromosome_one.members), 1)) + random.sample(self.chromosome_two.members, min(len(self.chromosome_two.members), 50)) + random.sample(self.chromosome_three.members, min(len(self.chromosome_three.members), 50))
        # self.initial_members = random.shuffle(self.chromosome_one.members + self.chromosome_two.members + self.chromosome_three.members)
        self.initial_members = self.chromosome_one.members + self.chromosome_two.members + self.chromosome_three.members
        return self.initial_members

    def plot_chromosome_one_members(self, directory, idx):
        member = self.chromosome_one.members[idx]
        plot = Plot()
        plot.add_lines(member['edges'])
        plot.add_obstacles(self.obstacles)
        plot.add_terminals(self.terminals)
        plot.add_points(Delaunay(self.obstacles, self.terminals).get_centroids())
        plot.plot()
        if (idx < 20):
            plot.save(f'{directory}/top_solutions/chromosome_one_{idx}.png')
        plot.save(f'{directory}/chromosome_one_{idx}.png')
        # print(directory)
        plot.close()

    def plot_chromosome_two_members(self, directory, idx):
        member = self.chromosome_two.members[idx]
        plot = Plot()
        plot.add_lines(member['edges'])
        plot.add_obstacles(self.obstacles)
        plot.add_terminals(self.terminals)
        plot.plot()
        if (idx < 20):
            plot.save(f'{directory}/top_solutions/chromosome_two_{idx}.png')
        plot.save(f'{directory}/chromosome_two_{idx}.png')
        plot.close()

    def plot_chromosome_three_members(self, directory, idx):
        member = self.chromosome_three.members[idx]
        plot = Plot()
        plot.add_lines(member['edges'])
        plot.add_obstacles(self.obstacles)
        plot.add_terminals(self.terminals)
        plot.plot()
        if (idx < 20):
            plot.save(f'{directory}/top_solutions/chromosome_three_{idx}.png')
        plot.save(f'{directory}/chromosome_three_{idx}.png')
        plot.close()

    def check_with_fermat(self, member):
        # print("CHECKING WITH FERMAT", member)
        edges = member['edges']
        points = member['final_points']
        triangles = []
        for point in points:
            is_corner_point = False
            is_terminal_point = False

            for terminal_point in self.terminals:
                if terminal_point == point:
                    is_terminal_point = True
                    break

            for obstacle_point in self.base_chromosome.get_raw_corner_points(points):
                if obstacle_point[1] == point:
                    is_corner_point_included = obstacle_point[0]
                    is_corner_point = True
                    break

            other_points = []
            if not(is_terminal_point or is_corner_point):
                for edge in edges:
                    p1, p2 = edge
                    if p1 == point:
                        other_points.append(p2)
                    elif p2 == point:
                        other_points.append(p1)
                if len(other_points) == 3:
                    triangles.append([point, [other_points[0], other_points[1], other_points[2]]])
        # print(triangles)
        final_points = []
        replaced = {}

        for point in points:
            point_present = None
            base_point = None
            for triangle in triangles:
                if triangle[0] == point:
                    point_present = triangle[1]
                    if str(point_present[0]) in replaced:
                        point_present[0] = replaced[str(point_present[0])]
                    elif str(point_present[1]) in replaced:
                        point_present[1] = replaced[str(point_present[1])]
                    elif str(point_present[2]) in replaced:
                        point_present[2] = replaced[str(point_present[2])]
                    base_point = point
                    break
            if point_present == None:
                final_points.append(point)
            else:
                fermat_point = calculate_fermat_point(point_present[0], point_present[1], point_present[2])
                if (not Collision.is_point_inside_solid_polygons(fermat_point, self.obstacles)):
                    final_points.append(fermat_point)
                    replaced[str(base_point)] = fermat_point
                else:
                    final_points.append(point)
        # print('triangles', final_points)

        graph = self.get_graph(final_points, self.obstacles)
        if graph is not False:
            [minimum_cost, edges] = graph
            # print({'final_points': final_points, 'minimum_cost': minimum_cost, 'edges': edges, 'corner_points': self.base_chromosome.get_corner_points(final_points), 'id': uuid.uuid1()})
            return {'final_points': final_points, 'minimum_cost': minimum_cost, 'edges': edges, 'corner_points': self.base_chromosome.get_corner_points(final_points), 'id': uuid.uuid1()}
        else:
            return False

    def crossover(self, parent1, parent2, crossovers_dir, generation):
        bounding_box = self.chromosome_two.get_bounding_box()
        x = random.uniform(bounding_box[0][0], bounding_box[1][0])
        offspring_1_points = []
        offspring_2_points = []

        rnd = random.randint(0, 1000)

        for point in parent1['final_points']:
            if point[0] <= x:
                offspring_1_points.append(point)
            else:
                offspring_2_points.append(point)

        for point in parent2['final_points']:
            if point[0] > x:
                offspring_1_points.append(point)
            else:
                offspring_2_points.append(point)



        # mutated_offspring_1, mutated_offspring_2 = Parallel(n_jobs=1)(delayed(self.mutate_offsprint)(p, generation) for p in [offspring_1_points, offspring_2_points])
        mutated_offspring_1 = self.mutate_offsprint(offspring_1_points, generation)
        mutated_offspring_2 = self.mutate_offsprint(offspring_2_points, generation)

        return [mutated_offspring_1, mutated_offspring_2]


    def mutate_offsprint(self, offspring_points, generation):
        # global fitness_evaluations
        first_mutation_prob = max(0.99 * (1 - (generation/1000)), 0.60)
        second_third_mutation_prob = 1 - (first_mutation_prob/2)
        mutated_points = copy.deepcopy(offspring_points)
        first_prob = random.uniform(0, 1)
        second_prob = random.uniform(0, 1)
        third_prob = random.uniform(0, 1)
        did_second_mutation = False
        if (first_prob <= first_mutation_prob):
            mutated_points = self.do_first_mutation(mutated_points, generation)
        if (second_prob <= second_third_mutation_prob):
            mutated_points = self.do_second_mutation(mutated_points)
            did_second_mutation = True
        if (third_prob <= second_third_mutation_prob):
            mutated_points = self.do_third_mutation(mutated_points)
        graph = self.get_graph(mutated_points, self.obstacles)
        if graph is not False:
            [minimum_cost, edges] = graph
            evals = 1
            # self.fitness_evaluations.inc()
            if did_second_mutation:
                # self.fitness_evaluations.inc()
                evals = evals + 1
            return {'final_points': mutated_points, 'minimum_cost': minimum_cost, 'edges': edges, 'corner_points': self.base_chromosome.get_corner_points(mutated_points), 'id': uuid.uuid1(), 'evals': evals}
            # return {'final_points': mutated_points, 'minimum_cost': minimum_cost, 'edges': edges, 'corner_points': [], 'id': uuid.uuid1()}
        else:
            # return self.mutate_offsprint(offspring_points, generation)
            graph = self.get_graph(offspring_points, self.obstacles)
            if graph is not False:
                [minimum_cost, edges] = graph
                return {'final_points': offspring_points, 'minimum_cost': minimum_cost, 'edges': edges, 'corner_points': self.base_chromosome.get_corner_points(offspring_points), 'id': uuid.uuid1()}
                # return {'final_points': offspring_points, 'minimum_cost': minimum_cost, 'edges': edges, 'corner_points': [], 'id': uuid.uuid1()}
            else:
                # raise 1
                return {'final_points': mutated_points, 'minimum_cost': float("inf"), 'edges': [], 'corner_points': self.base_chromosome.get_corner_points(mutated_points), 'id': uuid.uuid1()}
                # return {'final_points': mutated_points, 'minimum_cost': float("inf"), 'edges': [], 'corner_points': [], 'id': uuid.uuid1()}


    def get_angle(self, edge1, edge2):
        [[x1, y1], [x2, y2]] = edge1
        [[x3, y3], [x4, y4]] = edge2
        if (x1 == x3):
            dx = x2 - x1
            dy = y2 - y1
        elif (x1 == x4):
            dx = x2 - x3
            dy = y2 - y3
        elif (x2 == x4):
            dx = x3 - x1
            dy = y3 - y1
        elif (x2 == x3):
            dx = x4 - x1
            dy = y4 - y1
        radians = abs(math.atan2(dy, dx))
        return radians

    def do_third_mutation(self, offspring_1_points):
        offspring_1_corner_points = self.base_chromosome.get_raw_corner_points(offspring_1_points)
        prunable_points = []
        for point in offspring_1_points:
            # is_terminal_point = False
            # for terminal_point in self.terminals:
            #     if terminal_point == point:
            #         is_terminal_point = True
            #         break
            is_terminal_point = str(point) in self.terminalsSet
            is_corner_point = False
            for obstacle_point in offspring_1_corner_points:
                if obstacle_point[0] and obstacle_point[1] == point:
                    is_corner_point = True
                    break
            if not is_corner_point and not is_terminal_point:
                prunable_points.append(point)
        if len(prunable_points) == 0:
            return offspring_1_points
        prune_index = random.randint(0, len(prunable_points) - 1)
        # print(prune_index)
        # print(prunable_points[prune_index])
        # print(offspring_1_points)
        offspring_1_points.remove(prunable_points[prune_index])
        # print(offspring_1_points)
        return offspring_1_points


    def do_second_mutation(self, offspring_1_points):
        edges = self.get_graph_edges(offspring_1_points, self.obstacles)
        if edges is False:
            return offspring_1_points
        node_edges = []
        for edge1 in edges:
            [[x1, y1], [x2, y2]] = edge1
            for edge2 in edges:
                [[x3, y3], [x4, y4]] = edge2
                append = (edge1 != edge2) and ((x1 == x3 and y1 == y3) or (x1 == x4 and y1 == y4) or (x2 == x3 and y2 == y3) or (x2 == x4 and y2 == y4))
                if append:
                    node_edges.append([edge1, edge2])
        short_angle_pairs = []
        for edge_pair in node_edges:
            angle = self.get_angle(edge_pair[0], edge_pair[1])
            if (angle < (2 * math.pi / 3)):
                short_angle_pairs.append(edge_pair)

        try_random = True
        if len(short_angle_pairs) > 0:
            pair = random.randint(0, len(short_angle_pairs)-1)
            points = list(itertools.chain(*short_angle_pairs[pair]))
            points_tuple = [tuple(x) for x in points]
            unique_points = sorted(set(points_tuple), key=lambda x: points_tuple.index(x))
            # print(unique_points)
            try:
                centroid = Delaunay([], unique_points).get_centroids()
                if (len(centroid) > 0):
                    offspring_1_points.append(centroid[0])
                    try_random = False
            except:
                try_random = True
        if try_random:
            borders = self.base_chromosome.get_bounding_box()
            point = None
            while point is None:
                x = np.random.uniform(low=borders[0][0], high=borders[1][0], size=(1,))[0]
                y = np.random.uniform(low=borders[0][0], high=borders[1][0], size=(1,))[0]
                if not Collision.is_point_inside_solid_polygons([x, y], self.obstacles):
                    point = [x, y]
            offspring_1_points.append(point)
        return offspring_1_points

    #TODO: FLIP MOVE DISTANCE FIX based on paper, move range, not per axis
    def do_first_mutation(self, offspring_1_points, generation):
        mutated_offspring_1_points = []
        offspring_1_corner_points = self.base_chromosome.get_raw_corner_points(offspring_1_points)
        total_points = 0
        for point in offspring_1_points:
            is_corner_point = False
            for obstacle_point in offspring_1_corner_points:
                if obstacle_point[1] == point:
                    is_corner_point = True
                    break
            if not is_corner_point:
                total_points += 1
        total_points += len(offspring_1_corner_points)

        for point in offspring_1_points:
            action_probability = random.randint(0, total_points)
            # print(action_probability, total_points)
            if action_probability != total_points:
                mutated_offspring_1_points.append(point)
                continue
            is_corner_point = False
            is_corner_point_included = False
            is_terminal_point = False
            #
            # for terminal_point in self.terminals:
            #     if terminal_point == point:
            #         is_terminal_point = True
            #         break
            is_terminal_point = str(point) in self.terminalsSet

            for obstacle_point in offspring_1_corner_points:
                if obstacle_point[1] == point:
                    is_corner_point_included = obstacle_point[0]
                    is_corner_point = True
                    break

            if is_corner_point:
                if not is_corner_point_included:
                    mutated_offspring_1_points.append(point)
            elif not is_terminal_point:
                avg_terminal_distance = np.mean(pdist(np.array(self.terminals)))
                max_move_range = (avg_terminal_distance * max(1 - (generation / 1000), 0.01))

                new_point = None
                while not new_point:
                    tmp_point = [0, 0]
                    # tmp_point[0] = point[0] + random.uniform(-max_move_range, max_move_range)
                    # tmp_point[1] = point[1] + random.uniform(-max_move_range, max_move_range)
                    alpha = 2 * math.pi * random.random()
                    x_move = math.sin(alpha) * max_move_range
                    y_move = math.cos(alpha) * max_move_range
                    tmp_point[0] = point[0] + x_move
                    tmp_point[1] = point[1] + y_move
                    # print(alpha, x_move, y_move)
                    if not Collision.is_point_inside_solid_polygons(tmp_point, self.obstacles):
                        new_point = tmp_point
                        break
                # print("MAYBE MOVING")
                # print(point)
                # print(new_point)
                mutated_offspring_1_points.append(new_point)
            else:
                mutated_offspring_1_points.append(point)

        return mutated_offspring_1_points

    def get_graph_edges(self, final_points, obstacles):
        graph = self.get_graph(final_points, obstacles)
        if graph is not False:
            return self.get_graph(final_points, obstacles)[1]
        else:
            return False

    def get_graph_edges_ignore_obstacles(self, final_points, obstacles):
        graph = Graph(len(final_points))

        for i in range(len(final_points)):
            for j in range(i + 1, len(final_points)):
                graph.add_edge(i, j, math.dist(final_points[i], final_points[j]))

        graph.KruskalMST()

        edges = []

        for edge in graph.result:
            edge = [final_points[edge[0]], final_points[edge[1]]]
            edges.append(edge)

        return edges


    def get_graph(self, final_points, obstacles):
        graph = Graph(len(final_points))
        #
        # for i in range(len(final_points)):
        #     for j in range(i + 1, len(final_points)):
        #         if not Collision.is_line_intersecting_polygons([final_points[i], final_points[j]], obstacles):
        #             graph.add_edge(i, j, math.dist(final_points[i], final_points[j]))
        #         else:
        #             graph.add_edge(i, j, float('inf'))

        graph.add_edges(final_points, obstacles)

        graph.KruskalMST()

        edges = []
        overlap = False

        for edge in graph.result:
            edge = [final_points[edge[0]], final_points[edge[1]]]
            edges.append(edge)
            if Collision.is_line_intersecting_solid_polygons(edge, obstacles):
                overlap = True
                break
        if overlap:
            return False
        else:
            return [graph.minimum_cost, edges]

        # self.plot_custom(self.terminals, self.obstacles, parent1['edges'], parent2['edges'], [[[x, bounding_box[0][1]], [x, bounding_box[1][1]]]], crossovers_dir, "parent")
        #
        # graph = Graph(len(offspring_1_points))
        #
        # for i in range(len(offspring_1_points)):
        #     for j in range(i + 1, len(offspring_1_points)):
        #         if not Collision.is_line_intersecting_polygons([offspring_1_points[i], offspring_1_points[j]], self.obstacles):
        #             graph.add_edge(i, j, math.dist(offspring_1_points[i], offspring_1_points[j]))
        #         else:
        #             graph.add_edge(i, j, float('inf'))
        #
        # graph.KruskalMST()
        # print(graph.result)
        #
        # overlap = False
        # offspring_1_edges = []
        # for edge in graph.result:
        #     edge = [offspring_1_points[edge[0]], offspring_1_points[edge[1]]]
        #     offspring_1_edges.append(edge)
        #     if Collision.is_line_intersecting_polygons(edge, self.obstacles):
        #         overlap = True
        #         break



    def plot(self, directory):
        # print(self.chromosome_one.members)
        # Parallel(n_jobs=8)(delayed(self.plot_chromosome_one_members)(directory, i) for i in range(len(self.chromosome_one.members)))
        # Parallel(n_jobs=8)(delayed(self.plot_chromosome_two_members)(directory, i) for i in range(len(self.chromosome_two.members)))
        # Parallel(n_jobs=8)(delayed(self.plot_chromosome_three_members)(directory, i) for i in range(len(self.chromosome_three.members)))

        # self.save_chromosome_csv(directory)

        print(f"Saved to {directory}")

    def save_chromosome_csv(self, data_dir, trial_id):
        obstacles = []
        for obstacle in self.obstacles:
            obstacles.append({'crossing_weight': obstacle.crossing_weight, 'points': obstacle.points})
        final_data = [['OBSTACLES', json.dumps(obstacles)], ['TERMINALS', self.terminals]]
        i = 0
        for member in self.chromosome_one.members:
            final_data.append(["INITIAL_CHROMOSOME", 'CHROMOSOME ONE', i, member['minimum_cost'], len(member['corner_points']), len(member['edges']), len(member['corner_points']), member['corner_points'], member['final_points'], member['edges']])
            i = i + 1
        i = 0
        for member in self.chromosome_two.members:
            final_data.append(["INITIAL_CHROMOSOME", 'CHROMOSOME TWO', i, member['minimum_cost'], len(member['corner_points']), len(member['edges']), len(member['corner_points']), member['corner_points'], member['final_points'], member['edges']])
            i = i + 1
        i = 0
        for member in self.chromosome_three.members:
            final_data.append(["INITIAL_CHROMOSOME", 'CHROMOSOME THREE', i, member['minimum_cost'], len(member['corner_points']), len(member['edges']), len(member['corner_points']), json.dumps(member['corner_points']), member['final_points'], member['edges']])
            i = i + 1


        with open(data_dir + '/' + 'chromosomes-' + str(trial_id) + '.csv', mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(final_data)

    def plot_custom(self, terminals, obstacles, diagram1, diagram2, separator, directory, name):
        plot = Plot()
        plot.add_obstacles(obstacles)
        plot.add_lines(diagram1)
        plot.add_lines3(separator)
        plot.add_terminals(terminals)

        plot.plot()
        plot.save(f'{directory}/{name}_1.png')

        plot = Plot()
        plot.add_obstacles(obstacles)
        plot.add_terminals(terminals)
        plot.add_lines2(diagram2)
        plot.add_lines3(separator)

        plot.plot()
        plot.save(f'{directory}/{name}_2.png')


# graph = Graph(len(offspring_2_points))
#
# for i in range(len(offspring_2_points)):
#     for j in range(i + 1, len(offspring_2_points)):
#         if not Collision.is_line_intersecting_polygons([offspring_2_points[i], offspring_2_points[j]], self.obstacles):
#             graph.add_edge(i, j, math.dist(offspring_2_points[i], offspring_2_points[j]))
#         else:
#             graph.add_edge(i, j, float('inf'))

# graph.KruskalMST()
# print(graph.result)
#
# overlap = False
# offspring_2_edges = []
# for edge in graph.result:
#     edge = [offspring_2_points[edge[0]], offspring_2_points[edge[1]]]
#     offspring_2_edges.append(edge)
#     if Collision.is_line_intersecting_polygons(edge, self.obstacles):
#         overlap = True
#         break


# print(overlap)

# self.plot_custom(self.terminals, self.obstacles, offspring_1_edges, offspring_2_edges, [[[x, bounding_box[0][1]], [x, bounding_box[1][1]]]], crossovers_dir, "offspring")
