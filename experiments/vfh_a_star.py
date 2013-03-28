#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
from playerc import *
from parse_world import *
from a_star import *
from graph_util import *

# Default port, can be overriden by cla
port = 6665
robot_name = "SAD (Because you didn't name me.)"
# CLA should be the name of a robot in the cfg file
if len(sys.argv) >= 2:
    robot_name = sys.argv[1]
    port = find_port_by_name("find_target.cfg", robot_name)

# Create client object
client = playerc_client(None, 'localhost', port)

# connect
if client.connect() != 0:
    raise playerc_error_str()

# proxy for position2d:1
pos = playerc_position2d(client, 1)
if pos.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# proxy for position2d:1
pla = playerc_planner(client, 0)
if pla.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# proxy for ranger:0
ran = playerc_ranger(client, 0)
if ran.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# graphics, so I can see what is going on.
gra = playerc_graphics2d(client, 0)
if gra.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# get the geometry
if pos.get_geom() != 0:
    raise playerc_error_str()
print "Robot size: (%.3f,%.3f)" % (pos.size[0], pos.size[1])

# figure out the location of the target (from the world file) in robot coords.
# TODO the parser should return points.
robot_loc = search_pose("test_vfh.world", robot_name)
offset = Point(robot_loc[0] + 8, robot_loc[1] + 8)
target_loc = search_pose("test_vfh.world", "target0")
goal = to_robot_coords(Point(robot_loc[0], robot_loc[1]), Point(target_loc[0], target_loc[1]))
drive_type = search_text_property("gridcar.inc", "drive")

print 'Relative to ' + robot_name + ', the target is at: %.2f %.2f' % (goal.x, goal.y)
draw = True

speed = .2

grid_num = 32

grid = [[0 for x in range(grid_num)] for y in range(grid_num)]
path_map = [[False for x in range(grid_num)] for y in range(grid_num)]
obstacles = [[False for x in range(grid_num)] for y in range(grid_num)]

interval = 16.0 / grid_num

def add_obstacle(x, y):
    # translate x and y to global coords
    t = pos.pa

    x0 = x * math.cos(t) - y * math.sin(t)
    y0 = x * math.sin(t) + y * math.cos(t)
    
    xp = x0 + pos.px + offset_x
    yp = y0 + pos.py + offset_y

    # Gridify
    x_g = int(xp / interval)
    y_g = int(yp / interval)

    if x_g == grid_num:
        x_g = grid_num - 1 # Edge case
    if y_g == grid_num:
        y_g = grid_num - 1 # Edge case

    if x_g < grid_num and y_g < grid_num:
        grid[x_g][y_g] = grid[x_g][y_g] + 0.3 # AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
        if grid[x_g][y_g] >= 1:
            obstacles[x_g][y_g] = True
    elif x_g > grid_num or y_g > grid_num:
        print "ERROR! One of the grid indexes is greater than %d: %d, %d" % (grid_num, x_g, y_g)        

while(True):
    idt = client.read()

    # calculate possible path
    current_node = node(int((pos.px + offset.x) / interval),  int((pos.py + offset.y) / interval), 0)
    goal_node = node(int((goal.x + 1.0) / interval),  int((goal.y + 1.0) / interval), 0)
    path = a_star_A(current_node, goal_node, obstacles)

    # clear old path
    for i in range(0, grid_num):
        for j in range(0, grid_num):
            path_map[i][j] = False
    for n in path:
        path_map[n.x][n.y] = True

    goal_node = path[len(path) - 2]
    goal_n_loc = trans_point(pos, offset, Point(goal_node.x * interval + (interval / 2.0), goal_node.y * interval + (interval / 2.0)))
    
    draw_all(gra, pos, offset, grid_num, grid, path_map)

print("DONE!")

