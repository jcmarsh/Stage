#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
from playerc import *
from stage_utils import *

# Create client object
client = startup(sys.argv, "run_temp.cfg")
pos, ran, gra = create_std(client)

# proxy for vfh+ local navigator (or art_pot... look the same from here.)
pla = playerc_planner(client, 0)
if pla.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# proxy for wavefront planner
wav = playerc_planner(client, 1)
if wav.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# First follower, frank
client1 = playerc_client(None, 'localhost', 6666)
if client1.connect() != 0:
    raise playerc_error_str()

pos1 = playerc_position2d(client1, 1)
if pos1.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

pla1 = playerc_planner(client1, 0)
if pla1.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

client1.read()
print "Where you at frank? (%f,%f)" % (pos1.px, pos1.py)

# Second follower, samantha
client2 = playerc_client(None, 'localhost', 6667)
if client2.connect() != 0:
    raise playerc_error_str()

pos2 = playerc_position2d(client2, 1)
if pos2.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

pla2 = playerc_planner(client2, 0)
if pla2.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

client2.read()
print "Where you at samantha? (%f,%f)" % (pos2.px, pos2.py)


idt = client.read()

target_loc = search_pose("run_temp.world", "target0")
goal = Point(target_loc[0], target_loc[1])
spacing = 1.5
epsilon = 0.5
way1 = Point(pos1.px, pos1.py)
path1 = []
path1.append(way1)
way2 = Point(pos2.px, pos2.py)
path2 = []
path2.append(way2)

wav.enable(1)
wav.set_cmd_pose(goal.x, goal.y, 1)

print "Current Pose: %f,%f" % (pos.px, pos.py)
print "Moving to   : %f,%f" % (goal.x, goal.y)

prev_points = []
while True:
    idt = client.read()
    client1.read()
    client2.read()

    # New waypoints come from the leader
    curr = Point(pos.px, pos.py)
    if len(path1) > 1:
        if curr.dist(path1[-1]) > spacing:
            print "Added waypoint to frank's queue"
            path1.append(curr)
    else:
        if curr.dist(way1):
            print "Added waypoint to frank's queue"
            path1.append(curr)
        
    # At current waypoint?
    if way1.dist(Point(pos1.px, pos1.py)) < epsilon:
        if len(path1) > 1:
            path2.append(way1)
            way1 = path1.pop(0)
            print "Frank is moving to: (%f,%f)" % (way1.x, way1.y)
            pla1.set_cmd_pose(way1.x, way1.y, 0)

    # At current waypoint (but for third robot)
    if way2.dist(Point(pos2.px, pos2.py)) < epsilon:
        if len(path2) > 1:
            way2 = path2.pop(0)
            print "Samantha is moving to: (%f,%f)" % (way2.x, way2.y)
            pla2.set_cmd_pose(way2.x, way2.y, 0)

    prev_points.append(draw_all(gra, pos, Point(0,0), None, None, None, prev_points))

print("DONE!")

