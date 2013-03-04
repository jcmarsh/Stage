#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
from playerc import *
from parse_world import *

# Default port, can be overriden by cla
port = 6665
if len(sys.argv) >= 2:
    port = int(sys.argv[1])

# Create client object
client = playerc_client(None, 'localhost', port)
# connect
if client.connect() != 0:
    raise playerc_error_str()

# proxy for position2d:0
pos = playerc_position2d(client, 0)
if pos.subscribe(PLAYERC_OPEN_MODE) != 0:
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
if pos.get_geom() != 0:
    raise playerc_error_str()
print "Robot size: (%.3f,%.3f)" % (pos.size[0], pos.size[1])

# figure out the location of the target (from the world file) in robot coords.
robot_loc = search_pose("find_target.world", "hank")
target_loc = search_pose("find_target.world", "target0")
target_loc_rel = to_robot_coords(robot_loc, target_loc)
g_x = target_loc_rel[0]
g_y = target_loc_rel[1]
g_r = .1 # radius of goal, in meters
g_e = 2 # extent of field (greater than this, move at maximum speed)
g_s = .2 # scale factor
o_r = .0 # radius of obstacles
o_e = 2
o_s = .1

print 'Relative to Hank, the target is at: %.2f %.2f' % (target_loc_rel[0], target_loc_rel[1])
draw = True

while(True):
    id = client.read()
    scan_str = ""
#    for i in range (0, ran.ranges_count):
#        scan_str += ': %.3f ' % ran.ranges[i]
#    print scan_str

    # current location
    print "Position: %f, %f: %f" % (pos.px, pos.py, pos.pa)

        # Head towards the goal!
    dist = math.sqrt(math.pow(g_x - pos.px, 2) + math.pow(g_y - pos.py, 2))
    theta = math.atan2(g_y - pos.py, g_x - pos.px)
    print 'Theta: %f: ' % theta
    
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

#    points = []
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

#        points.append((obs_x, obs_y))
#        points.append((obs_x + z_x, obs_y + z_y))

#    if draw:
#        gra.clear()
#        gra.draw_multiline(points, ran.ranges_count * 2)


    gra.clear()
    gra.draw_polyline([(0, 0), (del_x, del_y)], 2)


    pos.set_cmd_vel(del_x, del_y, 0.0, 1)



print("DONE!")

