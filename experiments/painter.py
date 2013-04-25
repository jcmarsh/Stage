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

offset = Point(8, 8)
prev_points = []

while(True):
    idt = client.read()
    prev_points.append(draw_all(gra, pos, offset, None, None, None, prev_points))

print("DONE!")
