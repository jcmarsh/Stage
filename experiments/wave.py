#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
import time

from playerc import *
from stage_utils import *

# Create client object
client = startup(sys.argv, "run_temp.cfg")
pos, ran, gra = create_std(client)

# proxy for vfh+ local navigator
pla = playerc_planner(client, 0)
if pla.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# proxy for wavefront planner
wav = playerc_planner(client, 1)
if wav.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

idt = client.read()

target_loc = search_pose("run_temp.world", "target0")
goal = Point(target_loc[0], target_loc[1])

wav.enable(1)
wav.set_cmd_pose(goal.x, goal.y, 1)

print "Pose: %f,%f" % (pos.px, pos.py)

prev_points = []
while True:
    idt = client.read()
    
#    prev_points.append(draw_all(gra, pos, Point(0,0), None, None, None, prev_points))
    print "Pose: %f,%f" % (pos.px, pos.py)
    time.sleep(.2)

print("DONE!")

