import os
import csv
path = '/home/shreyas/Work/Sheru/roads/roads/solutions/'
# results = filter(lambda x: "chromosome" not in x, os.listdir(path))
print(os.listdir(path))
weights = []
for puzzle_id in os.listdir(path):
    lowest = float('inf')
    for file in os.listdir(path + puzzle_id + "/crossovers/"):
        weight = float(file.split("-")[-1].split(".png")[0])
        if lowest > weight:
            lowest = weight
    puzzle_id = int(puzzle_id)

    weights.append([puzzle_id, lowest])
    # break

path = '/home/shreyas/Work/Sheru/roads/roads/solutions-all-solid/'
# results = filter(lambda x: "chromosome" not in x, os.listdir(path))
print(os.listdir(path))
for puzzle_id in os.listdir(path):
    lowest = float('inf')
    for file in os.listdir(path + puzzle_id + "/crossovers/"):
        weight = float(file.split("-")[-1].split(".png")[0])
        if lowest > weight:
            lowest = weight
    puzzle_id = int(puzzle_id)

    weights.append([puzzle_id, lowest])

weights = sorted(weights, key=lambda x: x[0], reverse=False)
print(weights)

with open('./tabulated.csv', mode='w') as file:
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerows(weights)