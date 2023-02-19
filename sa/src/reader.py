import csv

from src.obstacle import Obstacle


class Reader:

    def __init__(self, file_path):
        self.file_path = file_path

    def get_obstacles(self):
        with open(self.file_path, newline='\n') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            obstacles = []
            for row in reader:
                if (row != ['', ''] and row != [] and row != ['']):
                    if (len(row) == 1 or row[1] == ''):
                        obstacles.append(Obstacle(row[0]))
                    else:
                        obstacles[-1].points.append([float(row[0]), float(row[1])])
            return obstacles

    def get_terminals(self):
        with open(self.file_path, newline='\n') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader)
            terminals = []
            for row in reader:
                terminals.append([float(row[0]), float(row[1])])
        return terminals
