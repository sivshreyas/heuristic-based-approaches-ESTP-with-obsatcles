class Obstacle:
    crossing_weight = 0

    def __init__(self, crossing_weight):
        if crossing_weight.replace(".", "").isdigit():
            self.crossing_weight = float(crossing_weight)
        else:
            self.crossing_weight = float("inf")
        self.points = []
    
    def __str__(self):
        return str(self.points)

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self.points)
