#!/usr/bin/env python

# Demonstrates using the Artificial Potentail local navigator plugin. Pretty simple.
# A good example of the different states that the planner is expected to handle.

import math
import sys
import algs
import Basic_Controller
from playerc import *
from stage_utils import *

class Pot(Basic_Controller.Basic_Controller):
    goal = None
    offset = None

    def init(self, robot_name):
        Basic_Controller.init(robot_name)

        target_loc = search_pose("run_temp.world", "target0")
        self.goal = Point(target_loc[0], target_loc[1])
        self.offset = Point(8,8)

    def run(self, pipe_in):
        prev_points = []
        STATE = "IDLE"

        while(True):
            # Check if a collision has happened
            self.check_collision(pipe_in)

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
                idt = self.client.read()

                self.pla.set_cmd_pose(self.goal.x, self.goal.y, 0)
                prev_points.append(draw_all(self.gra, self.pos, self.offset, None, None, None, prev_points))
            elif STATE == "RESET":
                prev_points = []
                self.pla.enable(0)
                STATE = "IDLE"
            elif STATE != "IDLE":
                print "pot_driver.py has recieved an improper state: %s" % (STATE)

        print("DONE!")

def go(robot_name, pipe_in):
    controller = Pot()
    controller.init(robot_name)
    controller.run(pipe_in)


