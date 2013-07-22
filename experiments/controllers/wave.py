#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
import time

from playerc import *
from stage_utils import *

class WaveCont:
    client = None
    pos = None
    ran = None
    gra = None
    wav = None
    goal = None

    def init(self, robot_name):
        # Create client object
        self.client = startup(("filler", robot_name), "run_temp.cfg")
        self.pos, self.ran, self.gra = create_std(self.client)

        # proxy for vfh+ local navigator
        self.pla = playerc_planner(self.client, 0)
        if self.pla.subscribe(PLAYERC_OPEN_MODE) != 0:
            raise playerc_error_str()

        # proxy for wavefront planner
        self.wav = playerc_planner(self.client, 1)
        if self.wav.subscribe(PLAYERC_OPEN_MODE) != 0:
            raise playerc_error_str()

        idt = self.client.read()

        target_loc = search_pose("run_temp.world", "target0")
        self.goal = Point(target_loc[0], target_loc[1])

    def run(self, pipe_in):
        #print "Pose: %f,%f" % (pos.px, pos.py)
        prev_points = []
        STATE = "IDLE"

        while True:
            if pipe_in.poll():
                STATE = pipe_in.recv()

            if STATE == "DIE":
                # Shutdown!
                pipe_in.close()
                self.cleanup()
                break
            elif STATE == "START":
                self.wav.enable(1)
                self.wav.set_cmd_pose(self.goal.x, self.goal.y, 1)
                STATE = "GO"
            elif STATE == "GO":
                idt = self.client.read()
                prev_points.append(draw_all(self.gra, self.pos, Point(0,0), None, None, None, prev_points))
            elif STATE == "RESET":
                prev_points = []
                self.wav.enable(0)
                STATE = "IDLE"
            elif STATE != "IDLE":
                print "wave.py has recieved an improper state: %s" % (STATE)

        print("DONE!")

    def cleanup(self):
        self.pos.unsubscribe()
        self.ran.unsubscribe()
        self.gra.unsubscribe()
        self.wav.unsubscribe()
        self.client.disconnect()

def go(robot_name, pipe_in):
    controller = WaveCont()
    controller.init(robot_name)
    controller.run(pipe_in)

