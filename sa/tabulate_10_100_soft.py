import os
import csv
from joblib import Parallel, delayed
import subprocess

path = "/home/ubuntu/roads/sa/10_100/"
# results = filter(lambda x: "chromosome" not in x, os.listdir(path))
print(os.listdir(path))
weights = []


def flatten(xss):
    return [x for xs in xss for x in xs]


def get_lowest(puzzle_id, file):
    print("GETTING FOR ", puzzle_id, file)
    lowest = float("inf")
    lowest_line = []
    if "-" in file:
        print(file)
        with open(path + puzzle_id + "/data_dir/" + file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            for i in csv_reader:
                if i[0] != "OBSTACLES" and i[0] != "TERMINALS":
                    # print(list(csv_reader))
                    # print(i)
                    weight = float(i[3])
                    if weight < lowest:
                        lowest = weight
                        lowest_line = i
    return [lowest_line]


rows = []
weights = []
# for puzzle_id in sorted(os.listdir(path), key=lambda x: float(x))[0:5]:
for puzzle_id in sorted(os.listdir(path), key=lambda x: float(x)):
    rets = flatten(Parallel(32)(delayed(get_lowest)(puzzle_id, k) for k in os.listdir(path + puzzle_id + "/data_dir/")))
    print("=====")
    print(rets[0])
    print("=====")
    print(rets[1])
    print("=====")
    # for ret in rets:
    #     print(ret)
    #     print(ret[3])
    # print(len(sorted(rets, key=lambda y: float(y[2]))))
    lowest = sorted(filter(lambda x:  len(x) > 0,rets), key=lambda y: float(y[3]))[0]
    print(lowest)
    weights.append([int(puzzle_id), float(lowest[3]), int(lowest[0]), int(lowest[1])])
    with open('./10_100_data-v2.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(weights)
