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

# proxy for vfh+ local navigator
#pla = playerc_planner(client, 0)
#if pla.subscribe(PLAYERC_OPEN_MODE) != 0:
#    raise playerc_error_str()

client.read()

#offset = Point(pos.px + 8, pos.py + 8)
target_loc = search_pose("run_temp.world", "target0")
goal = Point(target_loc[0], target_loc[1])
drive_type = search_text_property("gridcar.inc", "drive")
offset = Point(8, 8)

print "The target is at: %.2f %.2f" % (goal.x, goal.y)
print "The robot  is at: %.2f %.2f" % (pos.px, pos.py)

speed = .2

while(True):
    idt = client.read()

print("DONE!")
