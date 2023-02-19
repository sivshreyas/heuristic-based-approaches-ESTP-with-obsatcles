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
from simanneal import Annealer
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
    time_diff = round((time.perf_counter_ns() - start)/ 1000000000)
    final_data.append(['OBSTACLES', obstacles])
    final_data.append(['TERMINALS', terminals])
    fitness_evaluations = 0
    start = time.perf_counter_ns()
    for i, state in enumerate(states):
        if 'evals' in state:
            fitness_evaluations = fitness_evaluations + state['evals']
        final_data.append(
            [i, fitness_evaluations, time_diff, state['minimum_cost'], len(state['corner_points']), len(state['edges']), len(state['corner_points']),
             state['corner_points'], state['final_points'], state['edges']])
    return final_data


class Stp(Annealer):
    def move(self):
        # print("MOVING", self.state['minimum_cost'])
        global terminalsSet
        global obstacles
        global terminals
        global boundingBox
        global population
        self.state = population.mutate_offsprint(self.state['final_points'], self.current_step)

    def energy(self):
        global terminalsSet
        global obstacles
        global terminals
        global data_dir
        global i
        i = i + 1
        return self.state['minimum_cost']


def flatten(xss):
    return [x for xs in xss for x in xs]


top = None
terminalsSet = None
obstacles = None
boundingBox = None

step = 1000


def run_anneal(member, trial_id, local_step):
    global step
    auto_schedule = {'tmax': 10, 'tmin': 1e-05, 'steps': local_step, 'updates': 100}

    s = Stp(member)
    # population.total_steps = step / 2
    population.total_steps = local_step
    s.set_schedule(auto_schedule)

    ret, weight = s.anneal()

    with open(data_dir + '/data-'+ str(trial_id) + '.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(to_weights(s.best_states))

    rets = [ret]

    with open(data_dir + '/data.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(to_weights(s.best_states))
    return rets



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
    p_count = 6
    total_steps = 30000
    print(f"Running puzzle {puzzle_id}")
    obstacles = Reader(f'./dataset/SoftObstacles/Sizing/obstacles{puzzle_id}.csv').get_obstacles()
    terminals = Reader(f'./dataset/SoftObstacles/Sizing/terminals{puzzle_id}.csv').get_terminals()

    population = Population(obstacles, terminals)
    terminalsSet = population.terminalsSet

    population.generate_initial_population()
    initial_members = population.get_top_initial_members()

    boundingBox = population.chromosome_two.get_bounding_box()
    # print(boundingBox)
    plot_dir = f'10_100/{puzzle_id}/'
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
    converging = False
    population.plot(plot_dir)

    top = initial_members[0]
    # tops = [top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top, top]
    tops = [top for _ in range(p_count)]
    # for i in range(p_count):
    #     if i >= len(initial_members):
    #         tops.append(random.choice(initial_members))
    #     else:
    #         tops.append(initial_members[i])
    # tops = 
    x0 = top['final_points']
    trial_ids = []
    for i in range(p_count):
        trial_ids.append(random.randint(1,99999999999999))
    final_rets = []
    global step
    while(step < total_steps):
        step = step + 2000
        # rets = flatten(Parallel(p_count)(delayed(run_anneal)(tops[k], trial_ids[k], step / 2) for k in range(p_count)))
        rets = flatten(Parallel(p_count)(delayed(run_anneal)(tops[k], trial_ids[k], step / 2) for k in range(p_count)))
        random.shuffle(rets)

        tops = rets

        new_tops = []
        
        for i in range(round(p_count / 2)):
            new_tops.append(population.crossover(tops[i], tops[p_count - 1 - i], step))
        tops.extend(flatten(new_tops))
        # base_tops = flatten(new_tops)
        # tops = []
        # for i in range(p_count):
        #     if i >= len(tops) or f['minimum_cost'] == float('inf'):
        #         tops.append(random.choice(base_tops))
        #     else:
        #         tops.append(base_tops[i])
        print(len(tops))
        # random.shuffle(tops)
        tops = sorted(tops, key= lambda x: x['minimum_cost'])
        finals = copy.deepcopy(tops)
        tops = []
        for f in finals:
            if f['minimum_cost'] != float('inf'):
                tops.append(f)
        local_tops = sorted(tops, key=lambda item: item['minimum_cost'])
        top = local_tops[0]
        plot = Plot()
        plot.add_lines(top['edges'])
        plot.add_obstacles(population.obstacles)
        plot.add_terminals(population.terminals)
        plot.plot()
        plot.save(f'{crossovers_dir}/final-{step}-{top["minimum_cost"]}.png')
        plot.close()
        print("weight: ", local_tops[0]['minimum_cost'], "\n")
        
    final_rets = sorted(flatten(final_rets), key=lambda item: item['minimum_cost'])

    for ret in final_rets[0:10]:
        new = population.check_with_fermat_2(ret['final_points'])
        if new != False:
            final_rets.append(new)

    print("----------")
    final_rets = sorted(final_rets, key=lambda item: item['minimum_cost'])

    for ret in final_rets[0:10]:
        top = ret
        plot = Plot()
        plot.add_lines(top['edges'])
        plot.add_obstacles(population.obstacles)
        plot.add_terminals(population.terminals)
        plot.plot()
        plot.save(f'{crossovers_dir}/afinals-{top["minimum_cost"]}.png')
        plot.close()


run(int(sys.argv[1]))
