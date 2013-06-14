#!/usr/bin/env python

# Demonstrates using the Artificial Potentail local navigator plugin. Pretty simple.
# A good example of the different states that the planner is expected to handle.

import math
import sys
import algs
from playerc import *
from stage_utils import *

class Pot:
    client = None
    pos = None
    ran = None
    gra = None
    goal = None
    offset = None
    pla = None

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
        self.offset = Point(8,8)

    def run(self, pipe_in):
        prev_points = []
        STATE = "IDLE"

        while(True):
            if pipe_in.poll():
                STATE = pipe_in.recv()

            if STATE == "DIE":
                pipe_in.close()
                self.cleanup()
            elif STATE == "START":
                self.pla.enable(0)
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

    def cleanup(self):
        self.pos.unsubscribe()
        self.ran.unsubscribe()
        self.gra.unsubscribe()
        self.wav.unsubscribe()
        self.client.disconnect()

def go(robot_name, pipe_in):
    controller = Pot()
    controller.init(robot_name)
    controller.run(pipe_in)


