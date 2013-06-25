#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
import algs
from playerc import *
from stage_utils import *

class Leader:
    role = None

    client = None
    pos = None
    ran = None
    gra = None
    pla = None

    planner = None
    goal = None
    offset = None
    
    def init(self, robot_name):
        self.client = startup(("filler", robot_name), "run_temp.cfg")
        self.pos, self.ran, self.gra = create_std(self.client)

        # proxy for the local navigator
        self.pla = playerc_planner(self.client, 0)
        if self.pla.subscribe(PLAYERC_OPEN_MODE) != 0:
            raise playerc_error_str()

        self.client.read()


# First follower, frank
client1 = playerc_client(None, 'localhost', 6666)
if client1.connect() != 0:
    raise playerc_error_str()

pla1 = playerc_planner(client1, 0)
if pla1.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()

# Second follower, samantha
client2 = playerc_client(None, 'localhost', 6667)
if client2.connect() != 0:
    raise playerc_error_str()

pla2 = playerc_planner(client2, 0)
if pla2.subscribe(PLAYERC_OPEN_MODE) != 0:
    raise playerc_error_str()


client.read()

#offset = Point(pos.px + 8, pos.py + 8)
target_loc = search_pose("run_temp.world", "target0")
goal = Point(target_loc[0], target_loc[1])
drive_type = search_text_property("gridcar.inc", "drive")
offset = Point(8, 8)

print "The target is at: %.2f %.2f" % (goal.x, goal.y)
print "The robot  is at: %.2f %.2f" % (pos.px, pos.py)

speed = .2

grid_num = 32

interval = 16.0 / grid_num
planner = algs.a_star_planner(grid_num, offset)
replan = True

def add_obstacle(x, y):
    # translate x and y to global coords
    return planner.add_obstacle(trans_point_r_g(pos, Point(x, y)))

prev_points = []
path = []
c_waypoint = Point(0,0)
while(True):
    idt = client.read()

    # check for obstacles, for a*
    for i in range(0, ran.ranges_count):
        # figure out location of the obstacle...
        tao = (2 * math.pi * i) / ran.ranges_count
        obs_x = ran.ranges[i] * math.cos(tao)
        obs_y = ran.ranges[i] * math.sin(tao)
        # obs_x and obs_y are relative to the robot, and I'm okay with that.
        if add_obstacle(obs_x, obs_y):
            replan = True

    # reached waypoint?
    if algs.gridify(Point(pos.px, pos.py), grid_num, offset) == algs.gridify(c_waypoint, grid_num, offset):
        replan = True

    print "Plan: %s" % (replan)
    if replan:
        print "Replanning."
        replan = False
        path = planner.plan(Point(pos.px, pos.py), goal)

    # Should check if goal_node has been reached.
    c_waypoint = path[1]
    n_waypoint = path[2]

    theta = math.atan2(n_waypoint.y - c_waypoint.y, n_waypoint.x - c_waypoint.x)
    #print "Target pose: %f,%f:%f" % (c_waypoint.x, c_waypoint.y, theta)

    pla.set_cmd_pose(c_waypoint.x, c_waypoint.y, theta)
    pla1.set_cmd_pose(c_waypoint.x, c_waypoint.y, theta)
    pla2.set_cmd_pose(c_waypoint.x, c_waypoint.y, theta)

    gra.setcolor((255, 0, 0, 255))
    prev_points.append(draw_all(gra, pos, offset, None, None, path, prev_points))

print("DONE!")

