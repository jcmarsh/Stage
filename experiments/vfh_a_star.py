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

# proxy for vfh+ local navigator
pla = playerc_planner(client, 0)
if pla.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

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
replan = True

def gridify(a):
    b = Point(0,0)
    b.x = int((a.x + offset.x) / interval)
    b.y = int((a.y + offset.y) / interval)
    if b.x == grid_num:
        b.x = grid_num - 1 # Edge case
    if b.y == grid_num:
        b.y = grid_num - 1 # Edge case
    return b

def degridify(a):
    b = Point(0,0)
    b.x = a.x * interval + (interval / 2.0) - offset.x
    b.y = a.y * interval + (interval / 2.0) - offset.y
    return b

def add_obstacle(x, y):
    # translate x and y to global coords
    t = pos.pa

    x0 = x * math.cos(t) - y * math.sin(t)
    y0 = x * math.sin(t) + y * math.cos(t)
    
    xp = x0 + pos.px
    yp = y0 + pos.py

    # Gridify
    obs_loc = gridify(Point(xp, yp))

    return planner.add_obstacle(obs_loc)

prev_points = []
path = []
c_waypoint = Point(0,0)
while(True):
    idt = client.read()

    # check for obstacles, for a*
    for i in range(0, ran.ranges_count):
        # figure out location of the obstacle...
        tao = (2 * math.pi * i) / ran.ranges_count
        obs_x = ran.ranges[i] * math.cos(tao)
        obs_y = ran.ranges[i] * math.sin(tao)
        # obs_x and obs_y are relative to the robot, and I'm okay with that.
        if add_obstacle(obs_x, obs_y):
            replan = True

    # calculate possible path
    #position = gridify(Point(pos.px, pos.py))
    #waypoint = gridify(c_waypoint)
    #print "G. Position: %d,%d\tG. Waypoint: %d,%d" % (position.x, position.y, waypoint.x, waypoint.y)
    if gridify(Point(pos.px, pos.py)) == gridify(c_waypoint):
        print "HAHAHAHAHAHAHAHA"
        replan = True

    print "Plan: %s" % (replan)
    if replan:
        print "Replanning."
        replan = False
        current_node = algs.node(int((pos.px + offset.x) / interval),  int((pos.py + offset.y) / interval), 0)
        goal_node = algs.node(int((goal.x + offset.x) / interval),  int((goal.y + offset.y) / interval), 0)
        path = planner.plan(current_node, goal_node)

        # clear old path
        for i in range(0, grid_num):
            for j in range(0, grid_num):
                path_map[i][j] = False
        for n in path:
            path_map[n.x][n.y] = True

    # Should check if goal_node has been reached.
    c_waypoint = degridify(path[1])
    n_waypoint = degridify(path[2])

    theta = math.atan2(n_waypoint.y - c_waypoint.y, n_waypoint.x - c_waypoint.x)
    #print "Target pose: %f,%f:%f" % (c_waypoint.x, c_waypoint.y, theta)

    pla.set_cmd_pose(c_waypoint.x, c_waypoint.y, theta)
    # pla.set_cmd_pose(-4, -4, -3)

    prev_points.append(draw_all(gra, pos, offset, grid_num, None, path_map, prev_points))

print("DONE!")

