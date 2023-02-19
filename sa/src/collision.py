from shapely.geometry import Point, LineString, GeometryCollection, MultiPolygon
from shapely.geometry.polygon import Polygon
from shapely.strtree import STRtree
import math
import traceback
from shapely.ops import split

collision_map = {}
solid_collision_map = {}
solid_point_collision_map = {}
point_collision_map = {}

class Collision:
    @staticmethod
    def is_point_inside_solid_polygons(point, obstacles):
        global solid_point_collision_map
        point_string = str(point)
        if point_string in solid_point_collision_map:
            return solid_point_collision_map[point_string]
        inside = False
        for k in range(len(obstacles)):
            obstacle = obstacles[k]
            if obstacle.crossing_weight == float("inf") and Collision.is_point_inside_polygon(point, obstacle.points):
                inside = True
                break
        solid_point_collision_map[point_string] = inside
        return inside

    @staticmethod
    def is_point_inside_polygons(point, polygons):
        inside = False
        for polygon_points in polygons:
            if Collision.is_point_inside_polygon(point, polygon_points):
                inside = True
                break
        return inside

    @staticmethod
    def is_point_inside_polygon(point, polygon_points):
        return Polygon(polygon_points).contains(Point(point))

    def is_line_intersecting_solid_polygons(line, obstacles):
        global solid_collision_map
        line_string = str(line)
        if line_string in solid_collision_map:
            return solid_collision_map[line_string]
        overlap = False
        # print("COLLISION NOT HIT")

        for k in range(len(obstacles)):
            obstacle = obstacles[k]
            if obstacle.crossing_weight == float("inf") and Collision.is_line_intersecting_polygon(line, obstacle.points):
                overlap = True
                break
        solid_collision_map[line_string] = overlap
        return overlap

    @staticmethod
    def is_line_intersecting_polygons(line, polygons):
        global collision_map
        line_string = str(line)
        if line_string in collision_map:
            return collision_map[line_string]
        overlap = False
        for polygon_points in polygons:
            if Collision.is_line_intersecting_polygon(line, polygon_points):
                # print("INTERSECTING ", line, polygon_points)
                overlap = True
                break
        collision_map[line_string] = overlap
        return overlap

    # @staticmethod
    # def is_line_intersecting_solid_polygons(line, obstacles):
    #     solid_obstacles = []
    #     for obstacle in obstacles:
    #         if obstacle.crossing_weight == float("inf"):
    #             solid_obstacles.append(Polygon(obstacle.points))
    #     mp = MultiPolygon(solid_obstacles)
    #     # intersection = mp.intersection(LineString(line))
    #     # type = str(intersection.type)
    #     # if type == 'MultiLineString' or type == 'GeometryCollection':
    #     #     return True
    #     # elif type == 'MultiPoint' or type == 'Point':
    #     #     return False
    #     # # print(split(mp, intersection))
    #     # return len(split(mp, intersection).geoms) != 1
    #     # if type != 'GeometryCollection':
    #     #     return intersection.boundary.area != 0.0
    #     # else:
    #     #     return True
    #     ls = LineString(line)
    #     crossing = ls.crosses(mp)
    #     if not crossing:
    #         return not ls.covers(mp)
    #     return crossing
    #
    # @staticmethod
    # def is_line_intersecting_polygons(line, polygons):
    #     obstacles = []
    #     for obstacle in polygons:
    #         obstacles.append(Polygon(obstacle.points))
    #     mp = MultiPolygon(obstacles)
    #     # intersection = mp.intersection(LineString(line))
    #     # type = str(intersection.type)
    #     # if type == 'MultiLineString' or type == 'GeometryCollection':
    #     #     return True
    #     # elif type == 'MultiPoint' or type == 'Point':
    #     #     return False
    #     # # print(split(mp, intersection))
    #     # return len(split(mp, intersection).geoms) != 1
    #     # if type != 'GeometryCollection':
    #     #     return intersection.boundary.area != 0.0
    #     # else:
    #     #     return True
    #     ls = LineString(line)
    #     crossing = ls.crosses(mp)
    #     if not crossing:
    #         return not ls.covers(mp)
    #     return crossing

    @staticmethod
    def is_line_intersecting_polygon(line, polygon_points):
        original_line = line
        # print(line)
        line = LineString(line)
        polygon = Polygon(polygon_points)
        # return False
        try:
            if not line.intersects(polygon):
                return False
            intersection = line.intersection(polygon)
            if str(intersection.type) == 'LineString' and str(intersection) == 'LINESTRING EMPTY':
                return False
            elif str(intersection.type) == 'LineString' and str(intersection) != 'LINESTRING EMPTY':
                return (original_line[0] != list(intersection.coords[0]) or original_line[1] != list(intersection.coords[1]) or (polygon.contains(line.interpolate(0.5, True))))
            if str(intersection.type) != 'GeometryCollection':
                return not line.intersection(polygon).boundary.is_empty
            else:
                return True
        except Exception as e:
            print("ERROR ", original_line, "=---=", polygon_points, e, str(line.intersection(polygon)))
            traceback.print_exc()


    @staticmethod
    def is_line_intersecting_polygon_2(line, polygon_points):
        original_line = line
        line = LineString(line)
        polygon = Polygon(polygon_points)
        if not line.intersects(polygon):
            return False
        intersection = line.intersection(polygon)
        if str(intersection.type) == 'LineString':
            # print(Collision.get_angle([list(intersection.coords[0]), list(intersection.coords[1])], original_line), [list(intersection.coords[0]), list(intersection.coords[1])], original_line)
            intersection_line = LineString([list(intersection.coords[0]), list(intersection.coords[1])])
            # if Collision.get_angle([list(intersection.coords[0]), list(intersection.coords[1])], original_line) < 10**5:
            #     print(Collision.get_angle([list(intersection.coords[0]), list(intersection.coords[1])], original_line), [list(intersection.coords[0]), list(intersection.coords[1])], original_line)
            # # print(original_line, "---", polygon_points)
            # # print(Collision.get_angle([list(intersection.coords[0]), list(intersection.coords[1])], original_line))
            # # return not (Point(original_line[0][0], original_line[0][1]).distance(polygon) == 0 and Point(original_line[1][0], original_line[1][1]).distance(polygon))
            # return Collision.get_angle([list(intersection.coords[0]), list(intersection.coords[1])], original_line) < 10**5
            # print(intersection.area)
            # if intersection_line.crosses(polygon):
            #     print("CROSSES", list(intersection.coords[1]), original_line)
            # else:
            #     print("OVERLAP", list(intersection.coords[1]), original_line)
            return not intersection_line.touches(polygon) #and (not polygon.contains(intersection_line.interpolate(0.5))) and polygon.touches(intersection_line.interpolate(0.5))
        if str(intersection.type) != 'GeometryCollection':
            return not line.intersection(polygon).boundary.is_empty
        else:
            return True

    def slope(x1, y1, x2, y2): # Line slope given two points:
        # print(x1,y1,x2,y2)
        return (y2-y1)/(x2-x1)

    def angle(s1, s2):
        return math.degrees(math.atan((s2-s1)/(1+(s2*s1))))

    @staticmethod
    def get_angle(edge1, edge2):
        # dy,dx = [0, 0]
        # print(type(edge1[0]), edge1, type(edge2), edge2)
        # if (edge1[1][0]-edge1[0][0]) != 0 and (edge2[1][0]-edge2[0][0]):
        #     m1 = (edge1[1][1]-edge1[0][1])/(edge1[1][0]-edge1[0][0])
        #     m2 = (edge2[1][1]-edge2[0][1])/(edge2[1][0]-edge2[0][0])
        #     angle_rad = abs(math.atan(m1) - math.atan(m2))
        #     angle_deg = angle_rad*180/math.pi
        #
        #     return angle_deg
        # else:
        #     print(edge1, edge2)
        #     return 0

        # slope1 = Collision.slope(edge1[0][0], edge1[0][1], edge1[1][0], edge1[1][1])
        # slope2 = Collision.slope(edge2[0][0], edge2[0][1], edge2[1][0], edge2[1][1])
        # return Collision.angle(slope1, slope2);
        return getAngle(edge1, edge2)

# the lines are in the format (x1, y1, x2, y2)
def getAngle(line_1, line_2):
    angle1 = math.atan2(line_1[0][1] - line_1[1][1], line_1[0][0] - line_1[1][0])
    angle2 = math.atan2(line_2[0][1] - line_2[1][1], line_2[0][0] - line_2[1][0])

    result = math.degrees(abs(angle1 - angle2))
    if result < 0:
        result += 360

    return result


def dot(vA, vB):
    return vA[0]*vB[0]+vA[1]*vB[1]

def ang(lineA, lineB):
    # Get nicer vector form
    vA = [(lineA[0][0]-lineA[1][0]), (lineA[0][1]-lineA[1][1])]
    vB = [(lineB[0][0]-lineB[1][0]), (lineB[0][1]-lineB[1][1])]
    # Get dot prod
    dot_prod = dot(vA, vB)
    # Get magnitudes
    magA = dot(vA, vA)**0.5
    magB = dot(vB, vB)**0.5
    # Get cosine value
    cos_ = dot_prod/magA/magB
    # Get angle in radians and then convert to degrees
    angle = math.acos(dot_prod/magB/magA)
    # Basically doing angle <- angle mod 360
    ang_deg = math.degrees(angle)%360

    if ang_deg-180>=0:
        # As in if statement
        return 360 - ang_deg
    else:

        return ang_deg
