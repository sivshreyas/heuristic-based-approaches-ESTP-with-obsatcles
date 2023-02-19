import os
import csv
import subprocess
import sys
import csv
import ast
import numpy as np

path = './solid/'
# path = '/home/shreyas/Work/Sheru/roads/roads/solutions-soft-12-28/'
# path = '/home/shreyas/Work/Sheru/roads/roads/solutions-10-100/'
# results = filter(lambda x: "chromosome" not in x, os.listdir(path))
print(os.listdir(path))
weights = []
for puzzle_id in os.listdir(path):
    lowest = float('inf')
    lowest_file = None
    lowest_line = None

    for file in os.listdir(path + puzzle_id + "/data_dir"):
        # if (puzzle_id == '10' and "40406812227295" not in file):
        #     continue
        # if (puzzle_id == '20' and "97009015332044" not in file):
        #     continue
        # if (puzzle_id == '30' and "31119141701242" not in file):
        #     continue
        # if (puzzle_id == '40' and "29130106350320" not in file):
        #     continue
        # if (puzzle_id == '50' and "13554033552988" not in file):
        #     continue
        # if (puzzle_id == '60' and "91598086551321" not in file):
        #     continue
        # if (puzzle_id == '70' and "8311073175361" not in file):
        #     continue
        # if (puzzle_id == '80' and "24248599989735" not in file):
        #     continue
        # if (puzzle_id == '90' and "78025367340972" not in file):
        #     continue
        # if (puzzle_id == '100' and "5142117189049" not in file):
        #     continue
        # print(file)
        # weight = float(file.split("-")[-1].split(".png")[0])
        # if lowest > weight:
        #     lowest = weight
    # puzzle_id = int(puzzle_id)
        last_line = subprocess.check_output(['tail', '-1', path + puzzle_id + "/data_dir/" + file]).decode(sys.stdout.encoding).strip()
        # print()
        data = list(csv.reader([last_line]))[0]
        if len(data) > 0 and data[0] == 'GENERATION':
            weight = float(data[3])
            if lowest >= weight:
                lowest = weight
                lowest_line = data
                lowest_file = path + puzzle_id + "/data_dir/" + file
    second_line = subprocess.check_output(['sed', '-n', '2p', lowest_file]).decode(sys.stdout.encoding).strip()
    third_line = subprocess.check_output(['sed', '-n', '3p', lowest_file]).decode(sys.stdout.encoding).strip()
    terminals_count = len(ast.literal_eval(list(csv.reader([second_line]))[0][1]))
    # print(second_line)
    obstacle_corners = lowest_line[7].count("1")
    fitness_evaluations = int(lowest_line[2])
    steiner_points = len(ast.literal_eval(lowest_line[8])) - terminals_count - obstacle_corners
    time_start = int(list(csv.reader([third_line]))[0][1])
    time_end = int(lowest_line[1])
    total_generations = int(subprocess.check_output(['sed', '-n', '$=', lowest_file]).decode(sys.stdout.encoding).strip())
    time_taken = (time_end - time_start)
    weights.append([int(puzzle_id), lowest, total_generations, terminals_count, obstacle_corners, steiner_points, fitness_evaluations, time_taken])




    # break
#     weights.append([puzzle_id, lowest])
weights = sorted(weights, key=lambda x: x[0])
print(weights)
names = [['puzzle_id', 'lowest', 'total_generations', 'terminals_count', 'obstacle_corners', 'steiner_points', 'fitness_evaluations', 'time_taken']]
np.savetxt('solid.csv', names + weights, delimiter=',', fmt='%s')
