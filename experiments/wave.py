#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
import time

from playerc import *
from stage_utils import *

#client = None
#pos = None
#ran = None
#gra = None
#wav = None
#goal = None

#def init(robot_name):
def go(robot_name):
    print "INITING"
    # Create client object
    client = startup(("filler", robot_name), "run_temp.cfg")
    pos, ran, gra = create_std(client)

    # proxy for vfh+ local navigator
    pla = playerc_planner(client, 0)
    if pla.subscribe(PLAYERC_OPEN_MODE) != 0:
        raise playerc_error_str()

    # proxy for wavefront planner
    wav = playerc_planner(client, 1)
    if wav.subscribe(PLAYERC_OPEN_MODE) != 0:
        print "THIS FAILED!!!!!!!!!!!!!!!!!!!!!!!"
        raise playerc_error_str()

    idt = client.read()

    target_loc = search_pose("run_temp.world", "target0")
    goal = Point(target_loc[0], target_loc[1])
    print "DONE INITING"

#def run():
    wav.enable(1)
    wav.set_cmd_pose(goal.x, goal.y, 1)

    print "Pose: %f,%f" % (pos.px, pos.py)

    prev_points = []

    while True:
        idt = client.read()
    
        prev_points.append(draw_all(gra, pos, Point(0,0), None, None, None, prev_points))

    print("DONE!")

#def cleanup():
    print "FINISH THE CLEANUP FUNCTION IN WAVE.PY (AND ALL OTHER CONTROLLERS FOR THAT MATTER)"

#def go(robot_name):
#    init(robot_name)
#    run()
#    cleanup()

