#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
from playerc import *
from parse_world import *
from a_star import *

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
drive_type = search_text_property("gridcar.inc", "drive")
g_x = target_loc_rel[0]
g_y = target_loc_rel[1]
g_r = 0 # radius of goal, in meters
g_e = 4 # extent of field (greater than this, move at maximum speed)
g_s = 1 # scale factor

print 'Relative to Hank, the target is at: %.2f %.2f' % (target_loc_rel[0], target_loc_rel[1])
draw = True

speed = 2

grid_num = 32

grid = [[0 for x in range(grid_num)] for y in range(grid_num)]
path_map = [[False for x in range(grid_num)] for y in range(grid_num)]
obstacles = [[False for x in range(grid_num)] for y in range(grid_num)]

interval = 16.0 / grid_num

def add_obstacle(x, y):
    # translate x and y to global coords
    t = pos.pa

    x0 = x * math.cos(t) - y * math.sin(t)
    y0 = x * math.sin(t) + y * math.cos(t)
    
    xp = x0 + pos.px + 1
    yp = y0 + pos.py + 1

    # Gridify
    x_g = int(xp / interval)
    y_g = int(yp / interval)

    if x_g == grid_num:
        x_g = grid_num - 1 # Edge case
    if y_g == grid_num:
        y_g = grid_num - 1 # Edge case

    if x_g < grid_num and y_g < grid_num:
        grid[x_g][y_g] = grid[x_g][y_g] + 0.3 # AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
        if grid[x_g][y_g] >= 1:
            obstacles[x_g][y_g] = True
    elif x_g > grid_num or y_g > grid_num:
        print "ERROR! One of the grid indexes is greater than %d: %d, %d" % (grid_num, x_g, y_g)        

# global coordinates to robot cordinates
def trans_point(p_x, p_y):
    t = - (pos.pa)
    x = - (pos.px + 1) + p_x
    y = - (pos.py + 1) + p_y

    xp = x * math.cos(t) - y * math.sin(t)
    yp = x * math.sin(t) + y * math.cos(t)
    return (xp, yp)

# Draw the grid
def draw_grid():
    # grid
    points = []
    for i in range(0, grid_num + 1):
        points.append(trans_point(0, i * interval))
        points.append(trans_point(16, i * interval))
    for j in range(0, grid_num + 1):
        points.append(trans_point(j * interval, 0))
        points.append(trans_point(j * interval, 16))

    gra.clear()
    gra.draw_multiline(points, (grid_num + 1) * 2 * 2)

    # obstacles
    for i in range(0, grid_num):
        for j in range(0, grid_num):
            if grid[i][j] >= 1:
                gra.draw_points([trans_point(i * interval + (interval / 2.0), j * interval + (interval / 2.0))], 1)
    # path
    for i in range(0, grid_num):
        for j in range(0, grid_num):
            if path_map[i][j]:
                gra.draw_points([trans_point(i * interval + (interval / 2.0), j * interval + (interval / 2.0))], 1)
                gra.draw_points([trans_point(i * interval + (interval / 2.0) - .1, j * interval + (interval / 2.0) - .1)], 1)
                gra.draw_points([trans_point(i * interval + (interval / 2.0) + .1, j * interval + (interval / 2.0) + .1)], 1)
                gra.draw_points([trans_point(i * interval + (interval / 2.0) - .1, j * interval + (interval / 2.0) + .1)], 1)
                gra.draw_points([trans_point(i * interval + (interval / 2.0) + .1, j * interval + (interval / 2.0) - .1)], 1)


while(True):
    draw_grid()

    idt = client.read()

    # check for obstacles
    for i in range(0, ran.ranges_count):
        # figure out location of the obstacle...
        tao = (2 * math.pi * i) / ran.ranges_count
        obs_x = ran.ranges[i] * math.cos(tao)
        obs_y = ran.ranges[i] * math.sin(tao)
        # obs_x and obs_y are relative to the robot, and I'm okay with that.
        add_obstacle(obs_x, obs_y)

    # calculate possible path
    current_node = node(int((pos.px + 1.0) / interval),  int((pos.py + 1.0) / interval), 0)
    goal_node = node(int((g_x + 1.0) / interval),  int((g_y + 1.0) / interval), 0)
    path = a_star_A(current_node, goal_node, obstacles)

    # clear old path
    for i in range(0, grid_num):
        for j in range(0, grid_num):
            path_map[i][j] = False
    for n in path:
        path_map[n.x][n.y] = True

    goal_node = path[len(path) - 2]
#    goal = trans_point(goal_node.x * interval + (interval / 2.0), goal_node.y * interval + (interval / 2.0))
    [goal_x, goal_y] = trans_point(goal_node.x * interval + (interval / 2.0), goal_node.y * interval + (interval / 2.0))
    print "Goal: %f, %f" % (goal_x, goal_y)

    dist = math.sqrt(math.pow(goal_x - pos.px, 2) + math.pow(goal_y - pos.py, 2))
    theta = math.atan2(goal_y - pos.py, goal_x - pos.px)
    
    del_x = goal_x
    del_y = goal_y
    #if (g_r <= dist and dist <= g_e + g_r):
    #    v = g_s * (dist - g_r)
    #    del_x = v * math.cos(theta)
    #    del_y = v * math.sin(theta)
    #elif dist > g_e + g_r:
    #v = g_s * g_e
    #del_x = v * math.cos(theta)
    #del_y = v * math.sin(theta)


#    gra.clear()
#    gra.draw_polyline([(0, 0), (del_x, del_y)], 2)
#    gra.draw_polyline([(0, 0), (goal_x, goal_y)], 2)
 
    # Now we have del_x and del_y, which describes the vetor along which the robot should move.
    if drive_type == "omni":
        pos.set_cmd_vel(speed * del_x, speed * del_y, 0, 1)
    elif drive_type == "diff":
        vel = speed * math.sqrt(math.pow(del_x, 2) + math.pow(del_y, 2))
        rot_vel = math.atan2(del_y, del_x)
        
        print "Velocities: %f %f" % (vel, rot_vel)
        pos.set_cmd_vel(vel, 0.0, rot_vel, 1)
    else:
        print("Unrecognized drive type: ", drive_type)


print("DONE!")

