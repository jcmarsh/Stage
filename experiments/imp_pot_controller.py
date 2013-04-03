#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
from playerc import *
from graph_util import *
from parse_world import *
from generic_start import *

# Create client object
client = startup(sys.argv, "find_target.cfg")
pos, ran, gra = create_std(client)

# figure out the location of the target (from the world file) in robot coords.
target_loc = search_pose("find_target.world", "target0")
drive_type = search_text_property("gridcar.inc", "drive")
goal = Point(target_loc[0], target_loc[1])
g_r = .1 # radius of goal, in meters
g_e = 2 # extent of field (greater than this, move at maximum speed)
g_s = .5 # scale factor
o_r = .0 # radius of obstacles
o_e = 1.5
o_s = .2

print "The target is at: %.2f %.2f" % (goal.x, goal.y)

old_del_x = 0
old_del_y = 0
speed = 8

while(True):
    id = client.read()

    # Head towards the goal!
    dist = math.sqrt(math.pow(goal.x - pos.px, 2) + math.pow(goal.y - pos.py, 2))
    theta = math.atan2(goal.y - pos.py, goal.x - pos.px) - pos.pa
    
    total_factors = 0
    if (dist < g_r):
        v = 0
        del_x = 0
        del_y = 0
    elif ( g_r <= dist and dist <= g_e + g_r):
        v = g_s * (dist - g_r)
        del_x = v * math.cos(theta)
        del_y = v * math.sin(theta)
        total_factors += 1
    else:
        v = g_s * g_e
        del_x = v * math.cos(theta)
        del_y = v * math.sin(theta)
        total_factors += 1

    for i in range(0, ran.ranges_count):
        # figure out location of the obstacle...
        tao = (2 * math.pi * i) / ran.ranges_count
        obs_x = ran.ranges[i] * math.cos(tao)
        obs_y = ran.ranges[i] * math.sin(tao)
        # obs_x and obs_y are relative to the robot, and I'm okay with that.
        
        dist = math.sqrt(math.pow(obs_x, 2) + math.pow(obs_y, 2))
        theta = math.atan2(obs_y, obs_x) 

        if (dist <= o_e + o_r):
            del_x += -o_s * (o_e + o_r - dist) * math.cos(theta) 
            del_y += -o_s * (o_e + o_r - dist) * math.sin(theta)
            total_factors += 1
        
        z_x = -1 * o_s * (o_e + o_r - dist) * math.cos(theta) 
        z_y = -1 * o_s * (o_e + o_r - dist) * math.sin(theta)

    # Now we have del_x and del_y, which describes the vetor along which the robot should move.
    if drive_type == "omni":
        del_x = del_x / total_factors
        del_y = del_y / total_factors
        pos.set_cmd_vel(speed * del_x, speed * del_y, 0, 1)
    elif drive_type == "diff":
        # Should include current heading to damping sudden changes
        total_factors += 1
        del_x += old_del_x
        del_y += old_del_y
        del_x = del_x / total_factors
        del_y = del_y / total_factors

        gra.clear()
        gra.draw_polyline([(0, 0), (del_x, del_y)], 2)

        vel = speed * math.sqrt(math.pow(del_x, 2) + math.pow(del_y, 2))
        rot_vel = speed * math.atan2(del_y, del_x)
        
        pos.set_cmd_vel(vel, 0.0, rot_vel, 1)
        old_del_x = del_x
        old_del_y = del_y
    else:
        print("Unrecognized drive type: ", drive_type)

print("DONE!")

