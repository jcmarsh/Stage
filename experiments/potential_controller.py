#!/usr/bin/env python

# Simple controller that implements the artificial potential method
# for OMNI drive robots.

# author: James Marshall


import math
import sys
import algs
from playerc import *
from graph_util import *
from parse_world import *
from generic_start import *

client = startup(sys.argv, "find_target.cfg")
pos, ran, gra = create_std(client)

# figure out the location of the target (from the world file)
target_loc = search_pose("find_target.world", "target0")
goal = Point(target_loc[0], target_loc[1])

while(True):
    idt = client.read()

    delta, total_factors = algs.potential(pos, ran, goal)

    gra.clear()
    gra.draw_polyline([(0, 0), (delta.x, delta.y)], 2)

    pos.set_cmd_vel(delta.x, delta.y, 0.0, 1)
print("DONE!")

