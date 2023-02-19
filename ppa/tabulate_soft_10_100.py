import os
import csv

path = '/home/ubuntu/roads/ppa/soft_10_100_solutions'


weights = []

for puzzle in sorted(map(lambda x: int(x), os.listdir(path)), key= lambda x: x):
    print(puzzle)
    lowest_weight = float('inf')
    crossover_path = f'{path}/{puzzle}/crossovers'
    for file in os.listdir(crossover_path):
        weight = float(file.split("-")[3].split(".png")[0])
        # print(weight)
        if weight < lowest_weight:
            lowest_weight = weight
    weights.append([puzzle, lowest_weight])


print(weights)

with open('soft_10_100-data.csv', mode='w') as file:
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerows(weights)