#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
from playerc import *

# Default port, can be overriden by cla
port = 6665
if len(sys.argv) >= 2:
    port = int(sys.argv[1])

# Create client object
c = playerc_client(None, 'localhost', port)
# connect
if c.connect() != 0:
    raise playerc_error_str()

# proxy for position2d:0
pos = playerc_position2d(c,0)
if pos.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# proxy for ranger:0
ran = playerc_ranger(c,0)
if ran.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# get the geometry
if pos.get_geom() != 0:
    raise playerc_error_str()
print "Robot size: (%.3f,%.3f)" % (pos.size[0], pos.size[1])

print "Let's read some ranges! I'm excited. Are you?"
for i in range (0, 15):
    if i >= ran.scan_count:
        break
    scan_str += '%.3f ' % ran.ranges[i]
print scan_str

print("DONE!")

