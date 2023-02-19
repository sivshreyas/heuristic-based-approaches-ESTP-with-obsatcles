import sys
import itertools
from joblib import Parallel, delayed

from src.plot import Plot
from src.population import Population
from src.reader import Reader
import csv
from functools import reduce
from scipy.optimize import basinhopping
import numpy as np
from src.mst import Graph
import os

sys.setrecursionlimit(10 ** 6)

fitness_evaluations = 0

class TakeStep:
    def __init__(self, stepsize=0.5):
        print("TAKE STEP")
        self.stepsize = stepsize
        self.rng = np.random.default_rng()

    def __call__(self, x):
        global terminalsSet
        print("stepsize", self.stepsize)
        x = np.reshape(x, (-1, 2)).tolist()
        s = self.stepsize
        for point in x:
            if str(point) not in terminalsSet:
                point[0] += self.rng.uniform(-2.*s, 2.*s)
                point[1] += self.rng.uniform(-2.*s, 2.*s)
        # print("--=--")
        # print(x)
        return flatten(x)

def flatten(xss):
    return [x for xs in xss for x in xs]

def func(x):
    global crossovers_dir
    global obstacles
    global terminals
    x = np.reshape(x, (-1, 2)).tolist()
    graph = Graph(len(x))

    graph.add_edges(x, obstacles)

    graph.KruskalMST()
    edges = []
    for edge in graph.result:
        edge = [x[edge[0]], x[edge[1]]]
        edges.append(edge)

    print(graph.minimum_cost)
    plot = Plot()
    plot.add_lines(edges)
    plot.add_obstacles(obstacles)
    plot.add_terminals(terminals)
    plot.plot()
    plot.save(f'{crossovers_dir}/{graph.minimum_cost}.png')
    plot.close()
    return graph.minimum_cost

class AcceptTest:
    def __init__(self, xmax=[1.1,1.1], xmin=[-1.1,-1.1] ):
        self.xmax = np.array(xmax)
        self.xmin = np.array(xmin)
        print("ACCEPT TEST")

    def __call__(self, **kwargs):
        print(kwargs)
        x = kwargs["x_new"]
        tmax = bool(np.all(x <= self.xmax))
        tmin = bool(np.all(x >= self.xmin))
        return tmax and tmin

top = None
terminalsSet = None
obstacles = None

def run(puzzle_id, trial_id):
    global top
    global terminalsSet
    global obstacles
    global crossovers_dir
    global terminals
    print(f"Running puzzle {puzzle_id}")
    # obstacles = Reader(f'./dataset/SolidObstacles/obstacles{puzzle_id}.csv').get_obstacles()
    # terminals = Reader(f'./dataset/SolidObstacles/terminals{puzzle_id}.csv').get_terminals()

    # print("obstacles", len(list(itertools.chain(*obstacles))), list(itertools.chain(*obstacles)))
    # obstacles = Reader(f'./dataset/SoftObstacles/obstacles{puzzle_id}.csv').get_obstacles()
    # terminals = Reader(f'./dataset/SoftObstacles/terminals{puzzle_id}.csv').get_terminals()
    obstacles = Reader(f'./dataset/SoftObstacles/Sizing/obstacles{puzzle_id}.csv').get_obstacles()
    terminals = Reader(f'./dataset/SoftObstacles/Sizing/terminals{puzzle_id}.csv').get_terminals()
    # obstacles = Reader(f'./dataset/SolidObstacles/Sizing/obstacles{puzzle_id}.csv').get_obstacles()
    # terminals = Reader(f'./dataset/SolidObstacles/Sizing/terminals{puzzle_id}.csv').get_terminals()
    population = Population(obstacles, terminals)
    terminalsSet = population.terminalsSet

    population.generate_initial_population()
    initial_members = population.get_top_initial_members()
    plot_dir = f'solutions/{puzzle_id}/'
    top_solutions_dir = plot_dir + 'top_solutions'
    crossovers_dir = plot_dir + 'crossovers'
    data_dir = plot_dir + 'data_dir'
    if not os.path.exists(top_solutions_dir):
        os.makedirs(top_solutions_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if not os.path.exists(crossovers_dir):
        os.makedirs(crossovers_dir)
    converging = False

    # x0=[1.]
    top = initial_members[0]
    x0 = top['final_points']
    print(top)
    minimizer_kwargs = {"method": "BFGS"}
    take_step = TakeStep()
    accept_test = AcceptTest()
    ret = basinhopping(func, x0, minimizer_kwargs=minimizer_kwargs, niter=2, take_step=take_step, accept_test=accept_test)
    # print("global minimum: x = %.4f, f(x) = %.4f" % (ret.x, ret.fun))
    print(ret)

    # while not converging:
    #     i = i + 1
    #     # top = current_members[0]
    #     # plot = Plot()
    #     # plot.add_lines(top['edges'])
    #     # plot.add_obstacles(population.obstacles)
    #     # plot.add_terminals(population.terminals)
    #     # plot.plot()
    #     # plot.save(f'{crossovers_dir}/{i}-{trial_id}-{top["minimum_cost"]}.png')
    #     converging = False


# run(10, 10)
run(int(sys.argv[1]))
