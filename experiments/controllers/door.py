# Waits for something to pass in front of it, then moves forward when way is cleared.
# James Marshall

import math
import sys
import time
import Basic_Controller
from playerc import *
from stage_utils import *

class DoorCont(Basic_Controller.Basic_Controller):
    baseline_epsilon = .05
    baseline_dist = 0
    crossed = False
    shutting = False

    def state_go(self):
        idt = self.client.read()

        if self.baseline_dist == 0:
            self.baseline_dist = self.ran.ranges[0]

        # if !shutting
        if not(self.shutting):
            # read current distance
            dist = self.ran.ranges[0] # Should only have a forward facing center

            if dist < self.baseline_dist - self.baseline_epsilon:
                self.crossed = True
        
            if dist > self.baseline_dist - self.baseline_epsilon and self.crossed:
                self.shutting = True
        
        else: # The door should be in the process of shutting.
            self.pla.set_cmd_pose(2, 0, 0) # This is almost surely wrong.... probably needs to be absolute...

    def state_reset(self):
        self.pla.set_cmd_pose(0,0,0)
        self.pla.enable(0)
        self.baseline_dist = 0
        self.crossed = False
        self.shutting = False

    def run(self, pipe_in):
        # UPDATE
        STATE = "IDLE"

        while True:
            # Check for state transitions from overlord
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
            elif STATE == "RESET":
                self.state_reset()
                STATE = "IDLE"
            elif STATE != "IDLE":
                print "follower.py has received an improper state: %s" % (STATE)

def go(robot_name, pipe_in, command_receive, command_send):
    controller = DoorCont()
    controller.init(robot_name)
    controller.run(pipe_in)

