#!/usr/bin/env python

# Demonstrates using the Artificial Potential local navigator plugin. Pretty simple.
# A good example of the different states that a controller is expected to handle.

import math
import sys
import algs
import Basic_Controller
from playerc import *
from stage_utils import *

class Pot(Basic_Controller.Basic_Controller):
    goal = None
    offset = None
    prev_points = []

    def init(self, robot_name):
        super(Pot, self).init(robot_name)

        target_loc = search_pose("run_temp.world", "target0")
        self.goal = Point(target_loc[0], target_loc[1])
        self.offset = Point(8,8)

    def state_go(self):
        idt = self.client.read()
        self.pla.set_cmd_pose(self.goal.x, self.goal.y, 0)
        self.prev_points.append(draw_all(self.gra, self.pos, self.offset, None, None, None, self.prev_points))

    def state_reset(self):
        self.prev_points = []
        self.pla.enable(0)

    def run(self, pipe_in):
        STATE = "IDLE"

        while(True):
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
                self.state_go()
                # Check if a collision has happened
                self.check_collision(pipe_in)
            elif STATE == "RESET":
                self.state_reset()
                STATE = "IDLE"
            elif STATE != "IDLE":
                print "pot_driver.py has recieved an improper state: %s" % (STATE)

        print("DONE!")

def go(robot_name, pipe_in):
    controller = Pot()
    controller.init(robot_name)
    controller.run(pipe_in)


