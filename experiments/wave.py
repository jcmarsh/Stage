#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
from playerc import *
from graph_util import *
from generic_start import *

# Create client object
client = startup(sys.argv, "find_target.cfg")
pos, ran, gra = create_std(client)

# proxy for planner:0
pla = playerc_planner(client, 0)
if pla.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# proxy for wavefront planner
wav = playerc_planner(client, 1)
if wav.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()


idt = client.read()

wav.enable(1)
wav.set_cmd_pose(5, 0, 1)

print "Pose: %f,%f" % (pos.px, pos.py)

while True:
    idt = client.read()

print("DONE!")

