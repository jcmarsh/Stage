#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
import algs
from playerc import *
from stage_utils import *

# Create client object
client = startup(sys.argv, "find_target.cfg")
pos, ran, gra = create_std(client)

client.read()

#offset = Point(pos.px + 8, pos.py + 8)
target_loc = search_pose("find_target.world", "target0")
goal = Point(target_loc[0], target_loc[1])
drive_type = search_text_property("gridcar.inc", "drive")
offset = Point(8, 8)

print "The target is at: %.2f %.2f" % (goal.x, goal.y)
print "The robot  is at: %.2f %.2f" % (pos.px, pos.py)

speed = .2

grid_num = 32

# TODO: This is horrible... for drawing purposes?
path_map = [[False for x in range(grid_num)] for y in range(grid_num)]

interval = 16.0 / grid_num

planner = algs.a_star_planner(grid_num)

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

    planner.add_obstacle(Point(x_g, y_g))

while(True):
    idt = client.read()

    # check for obstacles, for a*
    for i in range(0, ran.ranges_count):
        # figure out location of the obstacle...
        tao = (2 * math.pi * i) / ran.ranges_count
        obs_x = ran.ranges[i] * math.cos(tao)
        obs_y = ran.ranges[i] * math.sin(tao)
        # obs_x and obs_y are relative to the robot, and I'm okay with that.
        add_obstacle(obs_x, obs_y)

    # calculate possible path
    current_node = algs.node(int((pos.px + offset.x) / interval),  int((pos.py + offset.y) / interval), 0)
    goal_node = algs.node(int((goal.x + offset.x) / interval),  int((goal.y + offset.y) / interval), 0)
    path = planner.plan(current_node, goal_node)

    # clear old path
    for i in range(0, grid_num):
        for j in range(0, grid_num):
            path_map[i][j] = False
    for n in path:
        path_map[n.x][n.y] = True

    goal_node = path[len(path) - 2]
    waypoint = trans_point(pos, offset, Point(goal_node.x * interval + (interval / 2.0), goal_node.y * interval + (interval / 2.0)))

    delta, total_factors = algs.potential(pos, ran, waypoint)

    if drive_type == "omni":
        pos.set_cmd_vel(speed * delta.x, speed * delta.y, 0, 1)
    elif drive_type == "diff":        
        rot_vel = speed * math.atan2(delta.y, delta.x)
        if math.fabs(rot_vel) > (math.pi / 2.0):
            vel = 0
        else:
            vel = speed * math.sqrt(math.pow(delta.x, 2) + math.pow(delta.y, 2))
        
        pos.set_cmd_vel(vel, 0.0, rot_vel, 1)
    else:
        print("Unrecognized drive type: ", drive_type)

    draw_all(gra, pos, offset, grid_num, path_map) #grid, path_map)

print("DONE!")

