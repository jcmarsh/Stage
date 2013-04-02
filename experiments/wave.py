#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
from playerc import *
from parse_world import *
from a_star import *
from graph_util import *

# Default port, can be overriden by cla
port = 6665
robot_name = "SAD (Because you didn't name me.)"
# CLA should be the name of a robot in the cfg file
if len(sys.argv) >= 2:
    robot_name = sys.argv[1]
    port = find_port_by_name("find_target.cfg", robot_name) # TODO: Can't assume .cfg name

# Create client object
client = playerc_client(None, 'localhost', port)

# connect
if client.connect() != 0:
    raise playerc_error_str()

# proxy for position2d:1
pos0 = playerc_position2d(client, 0)
if pos0.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# proxy for position2d:1
pla = playerc_planner(client, 0)
if pla.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# proxy for wavefront planner
wav = playerc_planner(client, 1)
if wav.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# proxy for ranger:0
ran = playerc_ranger(client, 0)
if ran.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# graphics, so I can see what is going on.
gra = playerc_graphics2d(client, 0)
if gra.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# get the geometry
if pos0.get_geom() != 0:
    raise playerc_error_str()
print "Robot size: (%.3f,%.3f)" % (pos0.size[0], pos0.size[1])

# figure out the location of the target (from the world file) in robot coords.
# TODO the parser should return points.
robot_loc = search_pose("test_vfh.world", robot_name)
offset = Point(robot_loc[0] + 8, robot_loc[1] + 8)
target_loc = search_pose("test_vfh.world", "target0")
goal = to_robot_coords(Point(robot_loc[0], robot_loc[1]), Point(target_loc[0], target_loc[1]))
drive_type = search_text_property("gridcar.inc", "drive")

print 'Relative to ' + robot_name + ', the target is at: %.2f %.2f' % (goal.x, goal.y)
draw = True

speed = .2

grid_num = 32

interval = 16.0 / grid_num

idt = client.read()

#    print "Target Pose: (%f,%f):%f" % (waypoint.x, waypoint.y, theta)
wav.enable(1)
#wav.set_cmd_pose(goal.x, goal.y, 0)
wav.set_cmd_pose(5, 0, 1)


print "Pose: %f,%f" % (pos0.px, pos0.py)

while True:
    idt = client.read()

print("DONE!")

