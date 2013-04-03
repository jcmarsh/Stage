#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
from playerc import *
from parse_world import *
from a_star import *
from graph_util import *
from generic_start import *

# Create client object
client = startup(sys.argv, "find_target.cfg")
pos0, ran, gra = create_std(client)

# proxy for position2d:1
pos1 = playerc_position2d(client, 1)
if pos.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# proxy for position2d:1
pla = playerc_planner(client, 0)
if pla.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

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
    
    xp = x0 + pos.px + offset.x
    yp = y0 + pos.py + offset.y

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

    # check for obstacles
    for i in range(0, ran.ranges_count):
        # figure out location of the obstacle...
        tao = (2 * math.pi * i) / ran.ranges_count
        obs_x = ran.ranges[i] * math.cos(tao)
        obs_y = ran.ranges[i] * math.sin(tao)
        # obs_x and obs_y are relative to the robot, and I'm okay with that.
        add_obstacle(obs_x, obs_y)

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

    wp_1 = path[len(path) - 2]
    wp_2 = path[len(path) - 3]
    waypoint = Point( -offset.x + wp_1.x * interval + (interval / 2.0), -offset.y + wp_1.y * interval + (interval / 2.0))
    theta = math.atan2(wp_2.y - wp_1.y, wp_2.x - wp_1.x)

#    print "Target Pose: (%f,%f):%f" % (waypoint.x, waypoint.y, theta)
    pla.set_cmd_pose(waypoint.x, waypoint.y, theta)
    
    draw_all(gra, pos, offset, grid_num, grid, path_map)

print("DONE!")

