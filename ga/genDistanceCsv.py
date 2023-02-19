# puzzles = [7, 10, 20]
import csv
import ast
import numpy as np

base_path = '/home/shreyas/Work/Sheru/roads/roads/solutions-pf-1/'
files = [base_path + "20/data_dir/gen-1879-25112121762253-2.804379461108543.csv", base_path + "10/data_dir/gen-1502-38455299963651-2.4211348034273685.csv", base_path + "7/data_dir/gen-465-14467785803407-2.3158257807431766.csv"]
puzzles = [20, 10, 7]
i = 0

for file in files:
    with open(file, 'r') as file:
        csvreader = csv.reader(file)
        gen = 0
        data = []
        for row in csvreader:
            if row[0] == 'GENERATION':
                gen = gen + 1
                data.append([puzzles[i], gen, float(row[1]), float(row[2]), float(row[3])])
        with open(str(puzzles[i]) + '-data.csv', mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(data)
    i = i + 1



