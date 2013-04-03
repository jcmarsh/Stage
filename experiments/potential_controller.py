#!/usr/bin/env python

# Simple controller that implements the artificial potential method
# for OMNI drive robots.

# author: James Marshall


import math
import sys
from playerc import *
from graph_util import *
from parse_world import *
from generic_start import *

client = startup(sys.argv, "find_target.cfg")
pos, ran, gra = create_std(client)

# figure out the location of the target (from the world file)
target_loc = search_pose("find_target.world", "target0")
goal = Point(target_loc[0], target_loc[1])
g_r = .1 # radius of goal, in meters
g_e = 2 # extent of field (greater than this, move at maximum speed)
g_s = .2 # scale factor
o_r = .0 # radius of obstacles
o_e = 2
o_s = .1

while(True):
    idt = client.read()

    # Head towards the goal!
    dist = math.sqrt(math.pow(goal.x - pos.px, 2) + math.pow(goal.y - pos.py, 2))
    theta = math.atan2(goal.y - pos.py, goal.x - pos.px) - pos.pa
    
    if (dist < g_r):
        v = 0
        del_x = 0
        del_y = 0
    elif ( g_r <= dist and dist <= g_e + g_r):
        v = g_s * (dist - g_r)
        del_x = v * math.cos(theta)
        del_y = v * math.sin(theta)
    else:
        v = g_s * g_e
        del_x = v * math.cos(theta)
        del_y = v * math.sin(theta)

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
        
        z_x = -1 * o_s * (o_e + o_r - dist) * math.cos(theta) 
        z_y = -1 * o_s * (o_e + o_r - dist) * math.sin(theta)

    gra.clear()
    gra.draw_polyline([(0, 0), (del_x, del_y)], 2)

    pos.set_cmd_vel(del_x, del_y, 0.0, 1)
print("DONE!")

