import itertools


class Chromosome:
    pass

    obstacle_corner_dict = None
    bounding_box = None
    obstacle_corners = None

    def get_obstacle_corners(self):
        if not self.obstacle_corners:
            self.store_obstacle_corners()
        return self.obstacle_corners

    def store_obstacle_corners(self):
        self.obstacle_corners = list(itertools.chain(*self.obstacles))

    def get_total_corners(self):
        return len(self.get_obstacle_corners())

    def get_all_points(self):
        return self.terminals + self.get_obstacle_corners()

    def get_bounding_box(self):
        if not self.bounding_box:
            self.store_bounding_box()
        return self.bounding_box

    def store_bounding_box(self):
        all_points = self.get_all_points()
        max_x = max(all_points, key=lambda x: x[0])[0]
        max_y = max(all_points, key=lambda x: x[1])[1]
        min_x = min(all_points, key=lambda x: x[0])[0]
        min_y = min(all_points, key=lambda x: x[1])[1]
        self.bounding_box = [[min_x, min_y], [max_x, max_y]]

    def is_invalid_constraints(self, steiner_points, terminals, edges):
        # return False
        if edges == [] and len(steiner_points) > len(terminals) - 2:
            return True
        elif edges == []:
            return False
        constraint_2 = False
        # print("GOT COUNT", len(steiner_points), len(edges), edges)

        for point in steiner_points:
            count = 0
            common_edges = []
            for edge in edges:
                if edge[0] == point or edge[1] == point:
                    common_edges.append(edge)
                    count = count + 1
            if count < 3:
                # print("GOT COUNT", count, len(steiner_points), len(edges), len(terminals), point, common_edges)
                constraint_2 = True
                break

        return constraint_2

    def get_raw_corner_points(self, final_points):
        corner_points = []
        for point in self.get_obstacle_corners():
            if point in final_points:
                corner_points.append([True, point])
            else:
                corner_points.append([False, point])
        return corner_points

    def get_corner_points(self, final_points):
        corner_points = []
        for point in self.get_obstacle_corners():
            if point in final_points:
                corner_points.append(1)
            else:
                corner_points.append(0)
        # print("got corner points ", len(self.get_obstacle_corners()), len(self.obstacles), len(corner_points), self.obstacles)
        return corner_points
