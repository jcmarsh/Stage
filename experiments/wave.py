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
        self.wav.enable(1)
        self.wav.set_cmd_pose(self.goal.x, self.goal.y, 1)

        #print "Pose: %f,%f" % (pos.px, pos.py)

        self.prev_points = []

        while True:
            if (pipe_in.poll() and pipe_in.recv() == "DIE"):
                # Shutdown!
                pipe_in.close()
                self.cleanup()
                break

            idt = self.client.read()
    
            # self.prev_points.append(draw_all(self.gra, self.pos, Point(0,0), None, None, None, self.prev_points))

        print("DONE!")

    def cleanup(self):
        print "IWASRUNOHMYGODTHISISSOEXCITING!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        self.pos.unsubscribe()
        self.ran.unsubscribe()
        self.gra.unsubscribe()
        self.wav.unsubscribe()
        self.client.disconnect()

    def __exit__(self, type, value, traceback):
        self.cleanup()

def go(robot_name, pipe_in):
    controller = WaveCont()
    controller.init(robot_name)
    controller.run(pipe_in)

