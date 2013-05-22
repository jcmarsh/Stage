#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
import algs
from playerc import *
from stage_utils import *

# Create client object
client = startup(sys.argv, "run_temp.cfg")
pos, ran, gra = create_std(client)

client.read()

#offset = Point(pos.px + 8, pos.py + 8)
target_loc = search_pose("run_temp.world", "target0")
goal = Point(target_loc[0], target_loc[1])
drive_type = search_text_property("gridcar.inc", "drive")
offset = Point(8, 8)

print "The target is at: %.2f %.2f" % (goal.x, goal.y)
print "The robot  is at: %.2f %.2f" % (pos.px, pos.py)

speed = 1

grid_num = 16

interval = 16.0 / grid_num
planner = algs.a_star_planner(grid_num, offset)
replan = True

def add_obstacle(x, y):
    return planner.add_obstacle(trans_point_r_g(pos, Point(x, y)))

prev_points = []
path = []
waypoint = Point(0,0)
while(True):
    idt = client.read()

    # Check if replaning is warranted
    # check for obstacles, for a*
    for i in range(0, ran.ranges_count):
        # figure out location of the obstacle...
        tao = (2 * math.pi * i) / ran.ranges_count
        obs_x = ran.ranges[i] * math.cos(tao)
        obs_y = ran.ranges[i] * math.sin(tao)
        # obs_x and obs_y are relative to the robot, and I'm okay with that.
        if add_obstacle(obs_x, obs_y):
            replan = True # New obstacle? Replan.

    # Reached waypoint? Replan.
    if algs.gridify(Point(pos.px, pos.py), grid_num, offset) == algs.gridify(waypoint, grid_num, offset):
        replan = True

    if replan:
        replan = False
        # TODO Need to set a timeout of some sort.
        path = planner.plan(Point(pos.px, pos.py), goal)

    # Should check if goal_node has been reached.
    waypoint = path[1]

    # TODO: Something is incorrect here.
    delta, total_factors = algs.potential(pos, ran, waypoint)

    delta.x = delta.x / total_factors
    delta.y = delta.y / total_factors

    if drive_type == "omni":
        pos.set_cmd_vel(speed * delta.x, speed * delta.y, 0, 1)
    elif drive_type == "diff":        
        rot_vel = speed * math.atan2(delta.y, delta.x)
        vel = speed * math.sqrt(math.pow(delta.x, 2) + math.pow(delta.y, 2))
        
        pos.set_cmd_vel(vel, 0.0, rot_vel, 1)
    else:
        print("Unrecognized drive type: ", drive_type)

    prev_points.append(draw_all(gra, pos, offset, grid_num, None, path, prev_points))

print("DONE!")

