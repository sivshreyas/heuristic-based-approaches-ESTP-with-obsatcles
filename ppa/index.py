import copy
import sys
import itertools
from joblib import Parallel, delayed
import time
from src.plot import Plot
from src.population import Population
from src.reader import Reader
import csv
from functools import reduce
from scipy.optimize import basinhopping
import random
import numpy as np
from src.mst import Graph
import os
from scipy.spatial.distance import pdist
import shutil
import random

i = 0

start = time.perf_counter_ns()

def to_weights(states):
    global terminals
    global obstacles
    final_data = []
    global start
    global fitness_evaluations
    time_diff = round((time.perf_counter_ns() - start)/ 1000000000)
    final_data.append(['OBSTACLES', obstacles])
    final_data.append(['TERMINALS', terminals])
    # fitness_evaluations = 0
    # start = time.perf_counter_ns()
    for i, state in enumerate(states):
        # if 'evals' in state:
        #     fitness_evaluations = fitness_evaluations + state['evals']
        final_data.append(
            [i, state['fitness_evaluations'], time_diff, state['minimum_cost'], len(state['corner_points']), len(state['edges']), len(state['corner_points']),
             state['corner_points'], state['final_points'], state['edges'], state['function_evaluations']])
    return final_data



def flatten(xss):
    return [x for xs in xss for x in xs]


top = None
terminalsSet = None
obstacles = None
boundingBox = None
generation = 0
step = 1000
nmax = 5
pop_size = 500
s = 1000000
fitness_evaluations = 0
function_evaluations = 0

def normalize_costs(members):
    global nmax
    global s
    global fitness_evaluations
    global function_evaluations
    members = list(filter(lambda x: x['minimum_cost'] != float('inf'), members))
    min_cost = members[0]['minimum_cost']
    max_cost = members[-1]['minimum_cost']
    new_members = []
    print(max_cost, min_cost, max_cost - min_cost, fitness_evaluations)
    for member in members:
        function_evaluations = function_evaluations + 1
        member['normalized_cost'] = (max_cost - member['minimum_cost']) / (max_cost - min_cost)
        member['fitness'] = 0.5 * (np.tanh((4 * member['normalized_cost']) - (2 * (1 + (function_evaluations / s)))) + 1)
        member['offspring_count'] = round(nmax * member['fitness'] * random.random())
        new_members.append(member)
    return new_members

def run_mutations(member):
    global population
    global generation
    prob_1 = abs(2 * (random.random() - 0.5)*(1 - member['fitness']))
    prob_2 = abs(2 * (random.random() - 0.5)*(1 - member['fitness']))
    prob_3 = abs(2 * (random.random() - 0.5)*(1 - member['fitness']))
    # prob_1 = abs(2 * (random.random()) * (1 - member['fitness']))
    # prob_2 = abs(2 * (random.random()) * (1 - member['fitness']))
    # prob_3 = abs(2 * (random.random()) * (1 - member['fitness']))

    members = []
    # print("GEnerating ", member['offspring_count'], prob_1, prob_2, prob_3)
    for i in range(member['offspring_count']):
        members.append(population.mutate_offspring(member['final_points'], generation, prob_1, prob_2, prob_3))
    return members
        


def run(puzzle_id):
    global top
    global terminalsSet
    global obstacles
    global crossovers_dir
    global terminals
    global boundingBox
    global population
    global data_dir
    global i
    global p_count
    global total_steps
    global generation
    global pop_size
    global fitness_evaluations
    global function_evaluations

    print(f"Running puzzle {puzzle_id}")
    obstacles = Reader(f'./dataset/SoftObstacles/Sizing/obstacles{puzzle_id}.csv').get_obstacles()
    terminals = Reader(f'./dataset/SoftObstacles/Sizing/terminals{puzzle_id}.csv').get_terminals()
    # obstacles = Reader(f'./dataset/SoftObstacles/obstacles{puzzle_id}.csv').get_obstacles()
    # terminals = Reader(f'./dataset/SoftObstacles/terminals{puzzle_id}.csv').get_terminals()

    population = Population(obstacles, terminals)
    terminalsSet = population.terminalsSet
    population.generate_initial_population()
    initial_members = population.get_top_initial_members()
    boundingBox = population.chromosome_two.get_bounding_box()
    
    plot_dir = f'soft_10_100_solutions/{puzzle_id}/'
    top_solutions_dir = plot_dir + 'top_solutions'
    crossovers_dir = plot_dir + 'crossovers'
    data_dir = plot_dir + 'data_dir'
    
    if not os.path.exists(top_solutions_dir):
        os.makedirs(top_solutions_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    # if os.path.exists(crossovers_dir):
    #     shutil.rmtree(crossovers_dir)
    if not os.path.exists(crossovers_dir):
        os.makedirs(crossovers_dir)
    
    # population.plot(plot_dir)

    print(len(initial_members))


    # j = 0
    members = initial_members
    tops = []
    p_count = 8
    normalized_members = normalize_costs(members)
    trial_id = random.randint(1,99999999999999)
    final_tops = []
    while generation < 1000:
        gen_members = []
        # for member in normalized_members:
        # print("RUNNING JOB")
        start = time.perf_counter()
        rets = flatten(Parallel(n_jobs=p_count)(delayed(run_mutations)(member) for member in normalized_members))
            # Parallel(n_jobs=1)(delayed(self.mutate_offsprint)(p, generation) for p in [offspring_1_points, offspring_2_points])
            # gen_members.extend(run_mutations(member))
        for ret in rets:
            if ('evals' in ret):
                fitness_evaluations = fitness_evaluations + ret['evals']
        print("END IN ", time.perf_counter() - start)
        gen_members.extend(rets)
        gen_members.extend(normalized_members)
        # print(normalized_members[0])
        # print(run_mutations(normalized_members[0]))
        members = sorted(gen_members, key=lambda x: x['minimum_cost'])

        # members = gen_members
        top = members[0]
        top['fitness_evaluations'] = fitness_evaluations + 0
        top['generation'] = generation
        top['function_evaluations'] = function_evaluations
        final_tops.append(top)
        tops.append(top)
        plot = Plot()
        plot.add_lines(top['edges'])
        plot.add_obstacles(population.obstacles)
        plot.add_terminals(population.terminals)
        plot.plot()
        plot.save(f'{crossovers_dir}/finals-gen-{generation}-{top["minimum_cost"]}.png')
        plot.close()
        generation = generation + 1
        new_set_members = []
        s = set()
        for d in members:
            if str(d['final_points']) not in s:
                s.add(str(d['final_points']))
                new_set_members.append(d)
        members = new_set_members
        members = sorted(members, key=lambda x: x['minimum_cost'])[0:pop_size]
        normalized_members = normalize_costs(members)
        tops = sorted(tops, key=lambda x: x['minimum_cost'])
        print("lowest weight ", tops[0]['minimum_cost'], generation, flush=True)
        with open(data_dir + '/data-'+ str(trial_id) + '.csv', mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(to_weights(final_tops))


run(int(sys.argv[1]))
