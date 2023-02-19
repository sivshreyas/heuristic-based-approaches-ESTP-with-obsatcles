import matplotlib.pyplot as plt
import copy

class Plot:
    def __init__(self):
        self.points = []
        self.terminals = []
        self.obstacles = []
        self.lines = []
        self.lines2 = []
        self.lines3 = []

    def add_terminals(self, points):
        self.terminals.extend(points)

    def add_points(self, points):
        self.points.extend(points)

    def add_obstacles(self, obstacles):
        self.obstacles = copy.deepcopy(obstacles)

    def add_lines(self, lines):
        self.lines.extend(lines)

    def add_lines2(self, lines):
        self.lines2.extend(lines)

    def add_lines3(self, lines):
        self.lines3.extend(lines)

    def plot(self, show = False):
        plt.figure()

        for obstacle in self.obstacles:
            coord = obstacle.points
            coord.append(coord[0])
            xs, ys = zip(*coord)
            plt.plot(xs, ys)

        for point in self.points:
            plt.plot(point[0], point[1], 'ro') 

        for edge in self.lines:
            plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], 'go-')

        for edge in self.lines2:
            plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], 'yo-')

        for edge in self.lines3:
            plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], 'mo-')

        for terminal in self.terminals:
            plt.plot(terminal[0], terminal[1], 'bo')

        if show:
            plt.show()

    def save(self, path):
        plt.savefig(path)

    def close(self):
        plt.close()

