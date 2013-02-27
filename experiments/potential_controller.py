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
if p.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# get the geometry
if pos.get_geom() != 0:
    raise playerc_error_str()
print("Robot size: (%.3f,#.3f)" % (pos.size[0], pos.size[1]))


