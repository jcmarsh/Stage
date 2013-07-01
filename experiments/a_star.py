#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
import algs
from playerc import *
from stage_utils import *
from timer import Timer

class AStarCont:
    client = None
    pos = None
    ran = None
    gra = None
    pla = None
    goal = None
    offset = None
    planner = None

    prev_points = []
    path = []
    c_waypoint = Point(0,0)

    grid_num = 32

    def init(self, robot_name):
        # Create client object
        self.client = startup(("filler", robot_name), "run_temp.cfg")
        self.pos, self.ran, self.gra = create_std(self.client)

        # proxy for the local navigator
        self.pla = playerc_planner(self.client, 0)
        if self.pla.subscribe(PLAYERC_OPEN_MODE) != 0:
            raise playerc_error_str()

        self.client.read()

        target_loc = search_pose("run_temp.world", "target0")
        self.goal = Point(target_loc[0], target_loc[1])
        self.offset = Point(8, 8)
        
#        print "The target is at: %.2f %.2f" % (self.goal.x, self.goal.y)
#        print "The robot  is at: %.2f %.2f" % (self.pos.px, self.pos.py)

        self.planner = algs.a_star_planner(self.grid_num, self.offset)

    def add_obstacle(self, x, y):
        # translate x and y to global coords
        return self.planner.add_obstacle(trans_point_r_g(self.pos, Point(x, y)))

    def state_die(self):
        self.pos.unsubscribe()
        self.ran.unsubscribe()
        self.gra.unsubscribe()
        self.pla.unsubscribe()
        self.client.disconnect()

    def state_start(self):
        self.pla.enable(1)

    def state_go(self):
        idt = self.client.read()
        replan = False

        # check for obstacles, for a*
        for i in range(0, self.ran.ranges_count):
            # figure out location of the obstacle...
            tao = (2 * math.pi * i) / self.ran.ranges_count
            obs_x = self.ran.ranges[i] * math.cos(tao)
            obs_y = self.ran.ranges[i] * math.sin(tao)
            # obs_x and obs_y are relative to the robot, and I'm okay with that.
            if self.add_obstacle(obs_x, obs_y):
                replan = True

            # reached waypoint?
            grid_pos = algs.gridify(Point(self.pos.px, self.pos.py), self.grid_num, self.offset)
            grid_way = algs.gridify(self.c_waypoint, self.grid_num, self.offset)
            if grid_pos == grid_way:
                replan = True

            if replan:
                self.path = self.planner.plan(Point(self.pos.px, self.pos.py), self.goal)

            if self.path == None:
                # Reset the planner.
                self.planner = algs.a_star_planner(self.grid_num, self.offset)
            elif len(self.path) > 2: 
                self.c_waypoint = self.path[1]
                n_waypoint = self.path[2]
                theta = math.atan2(n_waypoint.y - self.c_waypoint.y, n_waypoint.x - self.c_waypoint.x)
                self.pla.set_cmd_pose(self.c_waypoint.x, self.c_waypoint.y, theta)
            elif len(self.path) > 1:
                # Only one waypoint left
                self.c_waypoint = self.path[1]
                theta = self.pos.pa
                self.pla.set_cmd_pose(self.c_waypoint.x, self.c_waypoint.y, theta)
            # No else, should be finished by now.

            self.prev_points.append(draw_all(self.gra, self.pos, self.offset, self.grid_num, None, self.path, self.prev_points))

    def state_reset(self):
        self.prev_points = []
        self.pla.enable(0)
        self.planner = algs.a_star_planner(self.grid_num, self.offset)
        self.c_waypoint = Point(0,0) # Haha! It looks like an owl.
        self.path = []

    def run(self, pipe_in):
        self.prev_points = []
        self.path = []
        STATE = "IDLE"

        while True:
            if pipe_in.poll():
                STATE = pipe_in.recv()
                    
            if STATE == "DIE":
                pipe_in.close()
                self.state_die()
                break
            elif STATE == "START":
                self.state_start()
                STATE = "GO"
            elif STATE == "GO":
                with Timer() as t:
                    self.state_go()
                print "=> elapsed time for GO state: %s secs" % t.secs
            elif STATE == "RESET":
                self.state_reset()
                STATE = "IDLE"
            elif STATE != "IDLE":
                print "a_star.py have recieved an improper state: %s" % (STATE)

        print("DONE!")

def go(robot_name, pipe_in):
    controller = AStarCont()
    controller.init(robot_name)
    controller.run(pipe_in)

