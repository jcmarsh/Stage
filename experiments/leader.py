#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
import algs
import a_star
from playerc import *
from stage_utils import *

class LeaderCont:
    ''' 
    A lot to figure out here.
    1. How does the leader figure out its followers?
    2. How do the followers know about the leader?
    '''
    followers = []
    a_star_cont = None
    waypoints = []
    
    def init(self, robot_name):
        # A* controller for lead robot
        a_star_cont = AStarCont()
        a_star_cont.init(robot_name)

        # Position proxy

    def add_follower(follower):
        followers.append(follower)

    def state_die(self):
        a_star_cont.state_die()
        self.pos.unsubscribe()
        self.client.disconnect()

    def state_start(self):
        a_star_cont.state_start()

    def state_go(self):
        a_star_cont.state_go()

    def state_reset(self):
        a_star_cont.state_reset()

    def run(self, pipe_in):
        prev_points = []
        path = []
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
                self.state_go()
            elif STATE == "RESET":
                self.state_reset()
                STATE = "IDLE"
            elif STATE != "IDLE":
                print "leader.py has recieved an improper state: %s" % (STATE)

def go(robot_name, pipe_in):
    controller = LeaderCont()
    controller.init(robot_name)
    controller.run(pipe_in)
