#!/usr/bin/env python

# Demonstrates using the Artificial Potentail local navigator plugin. Pretty simple.

import math
import sys
import algs
from playerc import *
from stage_utils import *

# Create client object
client = startup(sys.argv, "run_temp.cfg")
pos, ran, gra = create_std(client)

# proxy for vfh+ local navigator
pla = playerc_planner(client, 0)
if pla.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

client.read()

target_loc = search_pose("run_temp.world", "target0")
goal = Point(target_loc[0], target_loc[1])

while(True):
    idt = client.read()

    pla.set_cmd_pose(goal.x, goal.y, 0)

print("DONE!")

