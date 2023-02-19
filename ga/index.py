import math
import time
import os
import random
import sys
import itertools
from joblib import Parallel, delayed

from src.plot import Plot
from src.population import Population
from src.reader import Reader
import csv
from functools import reduce

sys.setrecursionlimit(10 ** 6)

fitness_evaluations = 0

def flatten(xss):
    return [x for xs in xss for x in xs]


def do_crossover(population, current_members, puzzle_id, i, j, crossovers_dir):
    # print(f"CALCULATING #{puzzle_id},#{i},#{j}")
    parent1, parent2 = random.sample(current_members, 2)
    children = population.crossover(parent1, parent2, crossovers_dir, i)
    return children


def do_crossover_tournament_initial(population, current_members, puzzle_id, i, j, crossovers_dir):
    # print(f"CALCULATING #{puzzle_id},#{i},#{j}, #{len(current_members)}")
    parents1 = random.sample(current_members, 5)
    parent1 = sorted(parents1, key=lambda item: item['minimum_cost'])[0]

    parents2 = random.sample(current_members, 5)
    parent2 = sorted(parents2, key=lambda item: item['minimum_cost'])[0]

    child1, child2 = population.crossover(parent1, parent2, crossovers_dir, i)
    children = []
    #
    # global fitness_evaluations
    # fitness_evaluations = fitness_evaluations + 10

    if child1['edges'] != []:
        children.append(child1)
    if child2['edges'] != []:
        children.append(child2)

    return children

def get_crossover_tournaments(population, current_members, puzzle_id, i, j, crossovers_dir):
    parents1 = sorted(random.sample(current_members, 5), key=lambda item: item['minimum_cost'])
    parent1 = parents1[0]
    removed_parent_1 = parents1[-1]
    parents2 = sorted(random.sample(list(filter(lambda c: c['id'] != removed_parent_1['id'], current_members)), 5), key=lambda item: item['minimum_cost'])
    parent2 = parents2[0]
    removed_parent_2 = parents2[-1]
    # return remaining_parents_2 + remaining_parents_1 + children
    # global fitness_evaluations
    # fitness_evaluations = fitness_evaluations + 10
    return [[parent1, parent2], [removed_parent_1, removed_parent_2]]
    # return [[parent1, parent2], [{'id': 0}, {"id": 0}]]
    # return current_members + children

def do_crossover_tournament(population, current_members, puzzle_id, i, j, crossovers_dir):
    # print(f"CALCULATING #{puzzle_id},#{i},#{j}, #{len(current_members)}")
    parents = random.sample(current_members, 5)
    parent1 = sorted(parents, key=lambda item: item['minimum_cost'])[0]
    remaining_parents_1 = sorted(parents, key=lambda item: item['minimum_cost'])[0:-1]
    removed_parent_1 = sorted(parents, key=lambda item: item['minimum_cost'])[-1]
    parents = random.sample(current_members, 5)
    parent2 = sorted(parents, key=lambda item: item['minimum_cost'])[0]
    remaining_parents_2 = sorted(parents, key=lambda item: item['minimum_cost'])[0:-1]
    removed_parent_2 = sorted(parents, key=lambda item: item['minimum_cost'])[-1]
    child1, child2 = population.crossover(parent1, parent2, crossovers_dir, i)
    if child1['edges'] == []:
        child1 = []
    if child2['edges'] == []:
        child2 = []
    # return remaining_parents_2 + remaining_parents_1 + children
    return [[child1, child2], [removed_parent_1, removed_parent_2]]
    # return current_members + children


def run_generation(i, population, current_members, puzzle_id, crossovers_dir, weights, required_new_count=0):
    original_length = len(current_members)
    original_members = [] + current_members
    global fitness_evaluations
    # print("CALCULATING ", i, len(current_members), math.floor(len(current_members) / 6), len(weights) >= 1 and weights[-1], len(weights) >= 1 and round(weights[-1], 4))

    new_set_members = []
    s = set()
    for d in current_members:
        if str(d['final_points']) not in s:
            s.add(str(d['final_points']))
            new_set_members.append(d)
    current_members = new_set_members
    current_children = []
    cc = (math.floor(len(current_members) / 6))
    for j in range(0, (required_new_count == 0 and cc) or (math.ceil(required_new_count / 2))):
        children, removed = get_crossover_tournaments(population, current_members, puzzle_id, j, j, crossovers_dir)
        current_members = [x for x in current_members if (not (x['id'] == removed[0]['id']) and not (x['id'] == removed[1]['id']))]
        # print('removed length ', len(removed), len(children), len(current_members))

        current_children.append(children)
        # current_members = list(filter(lambda x : not (x['minimum_cost'] == removed[0]['minimum_cost'] or x == removed[1]['minimum_cost']), current_members))
        # print('current members length', len(current_members))

    # print("STARTING CROSSOVERS FOR", len(current_members))
    current_crossed_over_children = flatten(Parallel(8)(delayed(population.crossover)(current_children[k][0], current_children[k][1], crossovers_dir, i) for k in range(len(current_children))))
    # print("GOT CHILDREN", len(current_crossed_over_children))
    current_crossed_over_children = list(filter(lambda c: c['minimum_cost'] != float('inf'), current_crossed_over_children))
    for member in current_crossed_over_children:
        # print(member)
        if 'evals' in member:
            fitness_evaluations = fitness_evaluations + member['evals']
    # print("GOT FILTERED CHILDREN", len(current_crossed_over_children))
    if required_new_count == 0:
        current_members.extend(current_crossed_over_children)
    else:
        current_members = current_crossed_over_children
    # print("STATUS 1", len(current_members), original_length, required_new_count, math.floor(len(current_members) / 6) - 1)
    # if required_new_count == 0:
    current_members = sorted(current_members, key=lambda item: item['minimum_cost'])
    new_set_members = []
    s = set()
    for d in current_members:
        if str(d['final_points']) not in s:
            s.add(str(d['final_points']))
            new_set_members.append(d)
        # else:
        #     print(d)
    current_members = new_set_members
    if (required_new_count == 0 and len(current_members) < original_length) or (
            required_new_count != 0 and (len(current_members) < required_new_count)):
        if (required_new_count == 0 and len(current_members) < original_length):
            required = original_length - len(current_members)
        elif required_new_count != 0 and (len(current_members) < required_new_count):
            required = required_new_count - len(current_members)
        # print("STATUS 2", len(current_members), original_length, required_new_count, required)

        current_members = sorted(current_members +
                                 run_generation(i, population, original_members, puzzle_id, crossovers_dir, weights,
                                                required)[1], key=lambda item: item['minimum_cost'])
        new_set_members = []
        s = set()
        for d in current_members:
            if str(d['final_points']) not in s:
                s.add(str(d['final_points']))
                new_set_members.append(d)
            # else:
            #     print(d)
        current_members = new_set_members

    current_members = sorted(current_members, key=lambda item: item['minimum_cost'])

    if required_new_count == 0:
        top = current_members[0]
        weights.append(top['minimum_cost'])
        # plot = Plot()
        # plot.add_lines(top['edges'])
        # plot.add_obstacles(population.obstacles)
        # plot.add_terminals(population.terminals)
        # plot.plot()
        # plot.save(f'{crossovers_dir}/best-{i}-{top["minimum_cost"]}.png')
        # plot.close()
    return weights, current_members


def run_generation_1(i, population, current_members, puzzle_id, crossovers_dir, weights, required_new_count=0):
    original_length = len(current_members)
    original_members = [] + current_members
    print("CALCULATING ", i, len(current_members))
    new_set_members = []
    s = set()
    for d in current_members:
        if str(d['final_points']) not in s:
            s.add(str(d['final_points']))
            new_set_members.append(d)
        # else:
        #     print(d)
    current_members = new_set_members
    print("STATUS 0", len(current_members), original_length, required_new_count)
    new_members = []
    if required_new_count == 0:
        tmp_new_members = Parallel(8)(
            delayed(do_crossover_tournament)(population, current_members, puzzle_id, i, j, crossovers_dir) for j in
            range(math.floor(len(current_members) / 6) - 1))
        # tmp_new_members = Parallel(8)(delayed(do_crossover_tournament)(population, current_members, puzzle_id, i, j, crossovers_dir) for j in range(60))
    else:
        tmp_new_members = Parallel(8)(
            delayed(do_crossover_tournament)(population, current_members, puzzle_id, i, j, crossovers_dir) for j in
            range(math.floor(required_new_count / 2) - 1))
    current_members_copy = [] + current_members
    removing = []
    for m in tmp_new_members:
        new_members.append(m[0])

        # current_members_copy.remove(m[1][0])
        # current_members_copy.remove(m[1][1])
        # print(m[1][1])
        # print('removing', len(list(filter(lambda x : (x['minimum_cost'] == m[1][0]['minimum_cost'] or x == m[1][1]['minimum_cost']), current_members_copy))))
        # current_members_copy = list(filter(lambda x : not (x['minimum_cost'] == m[1][0]['minimum_cost'] or x == m[1][1]['minimum_cost']), current_members_copy))
        removing.append([m[1][0], m[1][1]])
    removing = flatten(removing)
    print("STATUS 1", len(current_members), original_length, required_new_count,
          math.floor(len(current_members) / 6) - 1, len(new_members), len(current_members_copy), len(removing))
    new_members = flatten(new_members)
    current_members_copy = list(
        filter(lambda x: len([y for y in removing if x["minimum_cost"] == y['minimum_cost']]) == 0,
               current_members_copy))
    print("STATUS 1-1", len(current_members), original_length, required_new_count,
          math.floor(len(current_members) / 6) - 1, len(new_members), len(current_members_copy), len(removing))

    # print(current_members_copy[0])
    # print(new_members[0])
    current_members_copy.extend(new_members)
    new_set_members = []
    s = set()
    for d in current_members:
        if str(d['final_points']) not in s:
            s.add(str(d['final_points']))
            new_set_members.append(d)
        # else:
        #     print(d)
    current_members = new_set_members

    if (required_new_count == 0 and len(current_members) < original_length) or (
            required_new_count != 0 and (len(current_members) < required_new_count)):
        if (required_new_count == 0 and len(current_members) < original_length):
            required = original_length - len(current_members)
        elif required_new_count != 0 and (len(current_members) < required_new_count):
            required = required_new_count - len(current_members)
        print("STATUS 2", len(current_members), original_length, required_new_count)

        current_members = sorted(current_members +
                                 run_generation(i, population, original_members, puzzle_id, crossovers_dir, weights,
                                                required)[1], key=lambda item: item['minimum_cost'])
        new_set_members = []
        s = set()
        for d in current_members:
            if str(d['final_points']) not in s:
                s.add(str(d['final_points']))
                new_set_members.append(d)
            # else:
            #     print(d)
        current_members = new_set_members
    if required_new_count == 0:
        top = current_members[0]
        # weights.append(round(top['minimum_cost'], 4))
        weights.append(top['minimum_cost'])
        plot = Plot()
        plot.add_lines(top['edges'])
        plot.add_obstacles(population.obstacles)
        plot.add_terminals(population.terminals)
        plot.plot()
        plot.save(f'{crossovers_dir}/best-{i}-{top["minimum_cost"]}.png')
        plot.close()

    return weights, current_members

def average_weight(lst):
    sum_of_list = 0
    for i in range(len(lst)):
        sum_of_list += lst[i]['minimum_cost']
    average = sum_of_list/len(lst)
    return average


def run(puzzle_id, trial_id):
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

    population.generate_initial_population()
    initial_members = population.get_top_initial_members()
    plot_dir = f'10_100_ga/{puzzle_id}/'
    top_solutions_dir = plot_dir + 'top_solutions'
    crossovers_dir = plot_dir + 'crossovers'
    data_dir = plot_dir + 'data_dir'
    if not os.path.exists(top_solutions_dir):
        os.makedirs(top_solutions_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if not os.path.exists(crossovers_dir):
        os.makedirs(crossovers_dir)
    population.plot(plot_dir)
    population.save_chromosome_csv(data_dir, trial_id)
    # return

    # plot = Plot()
    # plot.add_obstacles(obstacles)
    # # plot.add_lines(diagram1)
    # # plot.add_lines3(separator)
    # plot.add_terminals(terminals)
    #
    # plot.plot()
    # plot.save(f'solutions/{puzzle_id}/base.png')
    # plot.close()
    #
    # plot = Plot()
    # plot.add_obstacles(obstacles)
    # plot.add_lines(population.get_graph_edges_ignore_obstacles(terminals, obstacles))
    # # plot.add_lines3(separator)
    # plot.add_terminals(terminals)
    #
    # plot.plot()
    # plot.save(f'solutions/{puzzle_id}/base-graph-mst-no-obstacles.png')
    # plot.close()
    #
    #
    # plot = Plot()
    # plot.add_obstacles(obstacles)
    # plot.add_lines(population.get_graph_edges(terminals, obstacles))
    # # plot.add_lines3(separator)
    # plot.add_terminals(terminals)
    #
    # plot.plot()
    # plot.save(f'solutions/{puzzle_id}/base-graph-mst-obstacles.png')
    # plot.close()

    # population.plot(plot_dir)

    # current_members = initial_members
    # # converging = True
    # converging = True
    # weights = []
    # i = 0
    # while (converging):
    #     new_members = flatten(Parallel(8)(delayed(do_crossover_tournament)(population, current_members, puzzle_id, i, j, crossovers_dir) for j in range(360)))
    #     # new_members.extend(current_members)
    #     current_members = sorted(new_members, key=lambda item: item['minimum_cost'])[0:120]
    #     # current_members = new_members
    #     top = current_members[0]
    #     weights.append(top['minimum_cost'])
    #     plot = Plot()
    #     plot.add_lines(top['edges'])
    #     plot.add_obstacles(population.obstacles)
    #     plot.add_terminals(population.terminals)
    #     plot.plot()
    #     plot.save(f'{crossovers_dir}/best-{i}-{top["minimum_cost"]}.png')
    #     plot.close()
    #     n = 15
    #     i = i + 1
    #     # converging = False
    #     if len(weights) >= n and len(set(weights[-n:])) == 1:
    #         converging = False

    current_members = initial_members
    new_set_members = []

    s = set()
    for d in current_members:
        if str(d['final_points']) not in s:
            s.add(str(d['final_points']))
            new_set_members.append(d)
    current_members = new_set_members
    print("INITIAL MEMBERS BEFORE OFFPSRING ", len(current_members))
    global fitness_evaluations
    while (len(current_members) < 500):
        current_members = sorted(current_members, key=lambda item: item['minimum_cost'])
        # for i in current_members:
        #     print(i['minimum_cost'])
        # return
        new_members = flatten(Parallel(8)(
            delayed(do_crossover_tournament_initial)(population, current_members, puzzle_id, 0, j, crossovers_dir) for j in
            range(math.ceil((500 - (len(current_members))) / 2))))
        new_set_members = []

        for member in new_members:
            # print(member)
            if 'evals' in member:
                fitness_evaluations = fitness_evaluations + member['evals']

        current_members.extend(new_members)

        s = set()
        for d in current_members:
            if str(d['final_points']) not in s:
                s.add(str(d['final_points']))
                new_set_members.append(d)
        current_members = new_set_members
    print("MEMBERS AFTER INITIAL OFFPSRING ", len(current_members))

    # converging = True
    converging = True
    weights = []
    i = 0

    final_data = []
    final_data.append(['OBSTACLES', population.obstacles])
    final_data.append(['TERMINALS', population.terminals])
    start = time.perf_counter_ns()
    top = None
    fitness_evaluations = 0
    with open(data_dir + '/' + str(trial_id) + '.csv', mode='a') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(final_data)
        while (converging):
            local_start = time.perf_counter_ns()
            weights, current_members = run_generation(i, population, current_members, puzzle_id, crossovers_dir, weights)
            # n = 250
            n = 500
            i = i + 1
            # converging = False
            # current_members = sorted(current_members, key=lambda item: item['minimum_cost'])[0:500]
            current_members = sorted(current_members, key=lambda item: item['minimum_cost'])

            top = current_members[0]
            av_weight = average_weight(current_members)
            time_diff = round((time.perf_counter_ns() - start)/ 1000000000)
            final_data.append(["GENERATION", time_diff, fitness_evaluations, top['minimum_cost'], len(top['corner_points']), len(top['edges']), len(top['corner_points']), top['corner_points'], top['final_points'], top['edges'], av_weight])
            sys.stdout.write(("\rGeneration: %d || Time Elapsed: %d || Cost: %f ||  Fitness Evaluations: %d") % (i, time_diff, top['minimum_cost'], fitness_evaluations))
            sys.stdout.flush()

            # if puzzle_id == 7 and len(weights) >= n and len(set(weights[-n:])) == 1 or len(weights) > 1500 or (len(weights) == 50 and weights[-1] > 2.325) or (len(weights) == 100 and weights[-1] > 2.320):
            #     converging = False
            # print("CHECKING CONVERGENCE ", len(set(weights[-n:])), weights[-1], av_weight, top['minimum_cost'], round((av_weight/top['minimum_cost']) * 100, 2))
            # print("GENERATION TOOK ", (local_start - time.perf_counter_ns()) / 1000000000)
            # if puzzle_id == 10 and len(weights) >= n and len(set(weights[-n:])) == 1 or len(weights) > 1500 or (len(weights) == 50 and weights[-1] > 2.450) or (len(weights) == 100 and weights[-1] > 2.435):
            #     converging = False
            # if puzzle_id == 20 and len(weights) >= n and len(set(weights[-n:])) == 1 or len(weights) > 2500 or (len(weights) == 50 and weights[-1] > 2.825) or (len(weights) == 100 and weights[-1] > 2.817):
            #     converging = False
            # if len(weights) >= n and len(set(weights[-n:])) == 1 or len(weights) > 1500:
            # con_limit = round(math.log(len(population.terminals)) * 100)
            # if (len(weights) > con_limit):
            #     weight_diff = weights[0] - weights[-1]
            #     recent_weight_diff = weights[-con_limit] - weights[-1]
            #     print("DIFF + ", con_limit, weight_diff, recent_weight_diff, round(recent_weight_diff * 100 / weight_diff, 2))
            #     if round(recent_weight_diff * 100 / weight_diff, 2) < 1:
            #         converging = False
            # if (len(weights) >= n and len(set(weights[-n:])) == 1) or len(weights) > 2000:
            # if len(weights) >= n:
            #     print("CC %", len(weights), (weights[-n] - weights[-1]) / weights[-n])
            # elif len(weights) > 2:
            #     print("PRE CC %", len(weights),(((weights[0] - weights[-1]) / weights[0])))
            if len(weights) > 2500 or (len(weights) >= n and (((weights[-n] - weights[-1]) / weights[-n]) < 0.0001)):
            # if len(weights) > 2500 or (len(weights) >= n and (((weights[-n] - weights[-1]) / weights[0]) < 0.001)):
                converging = False

            # with open(data_dir + '/' + 'gen-' + str(i) + '-' + str(trial_id) + '-' + str(weights[-1]) + '.csv', mode='w') as file:

            writer.writerow(final_data[-1])

    # population.check_with_fermat(top)
    for member in [current_members[0]]:
        new = population.check_with_fermat(member)
        print("NEW FERMAT", new['minimum_cost'])
        if new is not False:
            current_members.append(new)
    top = current_members[-1]
    plot = Plot()
    plot.add_lines(top['edges'])
    plot.add_obstacles(population.obstacles)
    plot.add_terminals(population.terminals)
    plot.plot()
    plot.save(f'{crossovers_dir}/fermat-{i}-{trial_id}-{top["minimum_cost"]}.png')
    plot.close()


    i = i + 1
    # converging = False
    current_members = sorted(current_members, key=lambda item: item['minimum_cost'])

    top = current_members[0]
    final_data.append(["GENERATION", round((time.perf_counter_ns() - start)/ 1000000000), fitness_evaluations, top['minimum_cost'], len(top['corner_points']), len(top['edges']), len(top['corner_points']), top['corner_points'], top['final_points'], top['edges']])
    plot = Plot()
    plot.add_lines(top['edges'])
    plot.add_obstacles(population.obstacles)
    plot.add_terminals(population.terminals)
    plot.plot()
    plot.save(f'{crossovers_dir}/fermat-post-{i}-{trial_id}-{top["minimum_cost"]}.png')
    plot.close()
    with open(data_dir + '/' + 'gen-' + str(i) + '-' + str(trial_id) + '-' + str(weights[-1]) + '.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(final_data)


# run(100, 0)

# run(7, 0)
# run(100, 0)
# run(13, 0)
# run(26, 0)
# run(10)
# for i in range(30):
#     run(20, random.randint(1,99999999999999))
    # run(i + 1)
#
# for i in range(2):
run(int(sys.argv[1]), random.randint(1,99999999999999))

#     run(10, random.randint(1,99999999999999))
#     run(20, random.randint(1,99999999999999))
# #

# run(7, random.randint(1,99999999999999))

# for i in range(20):
#     run(10, i + 10001)
