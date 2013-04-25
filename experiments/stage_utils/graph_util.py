# Some basic utilities to deal with drawing things to the stage graphics2d object.
#
# author: James Marshall 

import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, o):
        return o != None and o.x == self.x and o.y == self.y
    
    def dist(self, other):
        return math.sqrt(math.pow(self.x - other.x, 2) + math.pow(self.y - other.y, 2))

# TODO: Can likely get rid of this, or generalize
def to_robot_coords(robot, target):
    return Point(target.x - robot.x, target.y - robot.y)

# robot coordinates to global cordinates
def trans_point_r_g(pos, point):
    t = pos.pa
    x0 = point.x * math.cos(t) - point.y * math.sin(t)
    y0 = point.x * math.sin(t) + point.y * math.cos(t)
    return Point(x0 + pos.px, y0 + pos.py)

# global coordinates to robot cordinates
def trans_point(pos, offset, point):
    tup = _trans_point(pos, offset, point)
    return Point(tup[0], tup[1])

# Have to have an ugly one since the graphics object wants a tuple, not a Point
def _trans_point(pos, offset, point):
    t = - (pos.pa)
    x = - (pos.px + offset.x) + point.x
    y = - (pos.py + offset.y) + point.y

    xp = x * math.cos(t) - y * math.sin(t)
    yp = x * math.sin(t) + y * math.cos(t)
    return (xp, yp)

# Draw obstacles
def draw_obstacles(gra, pos, offset, grid_num, grid):
    interval = 16.0 / grid_num
    for i in range(0, grid_num):
        for j in range(0, grid_num):
            if grid[i][j] >= 1:
                gra.draw_points([_trans_point(pos, offset, Point(i * interval + (interval / 2.0), j * interval + (interval / 2.0)))], 1)

# Draw the planned path
def draw_path(gra, pos, waypoints):
    offset = Point(0,0)
    for w in waypoints:
        gra.draw_points([_trans_point(pos, offset, w)], 1)
        gra.draw_points([_trans_point(pos, offset, Point(w.x - .1, w.y - .1))], 1)
        gra.draw_points([_trans_point(pos, offset, Point(w.x - .1, w.y + .1))], 1)
        gra.draw_points([_trans_point(pos, offset, Point(w.x + .1, w.y - .1))], 1)
        gra.draw_points([_trans_point(pos, offset, Point(w.x + .1, w.y + .1))], 1)

# Draw the grid
def draw_grid(gra, pos, offset, grid_num):
    # grid
    interval = 16.0 / grid_num

    points = []
    for i in range(0, grid_num + 1):
        points.append(_trans_point(pos, offset, Point(0, i * interval)))
        points.append(_trans_point(pos, offset, Point(16, i * interval)))
    for j in range(0, grid_num + 1):
        points.append(_trans_point(pos, offset, Point(j * interval, 0)))
        points.append(_trans_point(pos, offset, Point(j * interval, 16)))

    gra.draw_multiline(points, (grid_num + 1) * 2 * 2)

def draw_ghosts(gra, pos, offset, ghosts):
    points = []
    for g in ghosts:
        points.append(_trans_point(pos, Point(0, 0), g))
    gra.draw_points(points, len(points))
    return Point(pos.px, pos.py)

# Draw EVERYTHING! This is way too many args.
def draw_all(gra, pos, offset, grid_num, grid, path, ghosts):
    gra.clear()
    if grid_num != None:
        draw_grid(gra, pos, offset, grid_num)
    if grid != None:
        draw_obstacles(gra, pos, offset, grid_num, grid)
    if path != None:
        draw_path(gra, pos, path)
    if ghosts != None:    
        return draw_ghosts(gra, pos, offset, ghosts)
    else:
        return None
