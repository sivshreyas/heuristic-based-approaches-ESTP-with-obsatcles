import os
import csv
from joblib import Parallel, delayed
import subprocess

path = "/home/ubuntu/roads/soft/"
# results = filter(lambda x: "chromosome" not in x, os.listdir(path))
print(os.listdir(path))
weights = []


def flatten(xss):
    return [x for xs in xss for x in xs]


def get_lowest(puzzle_id, file):
    print("GETTING FOR ", puzzle_id, file)
    lowest = float("inf")
    lowest_line = None
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
    return lowest_line


rows = []

# for puzzle_id in sorted(os.listdir(path), key=lambda x: float(x))[0:5]:
for puzzle_id in sorted(os.listdir(path), key=lambda x: float(x)):
    print(puzzle_id)
    lowest = float("inf")
    for i in os.listdir(path + puzzle_id + "/crossovers/"):
        print(i)
        weight = float(i.split("-")[2].split(".png")[0])
        if lowest >= weight:
            lowest = weight
        # print(weight)
    # print(f"find {path + puzzle_id + '/data_dir/'} -maxdepth 1 -name \"*{lowest}*\" -print")
    # command = f"grep '{path + puzzle_id + '/data_dir/'}' -e '{lowest}' -m 1 | head -1"
    # command = f'grep -o -a -m 1 -h -r "{lowest}" {path + puzzle_id + "/data_dir/"} | head -1'
    # command = f'rg -m 1 "{lowest}" {path + puzzle_id + "/data_dir/"} | head -1'
    command = f'rg -m 1 "{lowest}" {path + puzzle_id + "/data_dir/"} | head -1'

    x = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        # universal_newlines=True
    )
    # csv.reader([x])
    
    print(x)
    row = list(csv.reader([x.stdout.decode("utf-8").strip()]))
    print(row)
    weights.append([int(puzzle_id), float(row[0][3]), int(row[0][0].split(":")[1]), row[0][1]])

    weights = sorted(weights, key=lambda x: x[0], reverse=False)
    print(weights)

    final_data = [
        ["puzzle_id","lowest","total_generations","fitness_evaluations"]
    ]

    for weight in weights:
        final_data.append(weight)

    with open('./soft-data.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(weights)

    # rets = flatten(Parallel(8)(delayed(get_lowest)(puzzle_id, k) for k in os.listdir(path + puzzle_id + "/data_dir/")))
    # print(rets)
    # break
    # for file in os.listdir(path + puzzle_id + "/data_dir/"):
    #     print(file)

    # break
    # print(puzzle_id, lowest)

    # for row in csv_reader:
#         if ("afinals" in file):
#             # print(file)
#             weight = float(file.split("-")[1].split(".png")[0])
#             if lowest > weight:
#                 lowest = weight
#     puzzle_id = int(puzzle_id)

#     weights.append([puzzle_id, lowest])
#     # break
# weights = sorted(weights, key=lambda x: x[0], reverse=False)
# print(weights)

# final_data = [
#     ["puzzle_id","lowest","total_generations","fitness_evaluations"]
# ]

# for weight in weights:
#     final_data.append(weight)

# with open('./soft-data.csv', mode='w') as file:
#     writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#     writer.writerows(weights)
