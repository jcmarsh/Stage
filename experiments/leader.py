#!/usr/bin/env python

# Copied in part from the player source examples.

import math
import sys
import algs
import a_star
import time
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
    way_time = 1.0 # 1 second
    start_time = 0
    waypoints = []
    pos = None
    
    def init(self, robot_name):
        # A* controller for lead robot
        self.a_star_cont = a_star.AStarCont()
        # TODO: This is horrible.
        self.pos = self.a_star_cont.init(robot_name)

    def add_follower(self, follower):
        self.followers.append(follower)

    def state_die(self):
        self.a_star_cont.state_die()
        self.pos.unsubscribe()
        self.client.disconnect()

    def state_start(self):
        self.a_star_cont.state_start()

    def state_go(self):
        self.a_star_cont.state_go()
        
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        if elapsed_time >= self.way_time:
            # Create new waypoint
            print "New waypoint: (%f, %f, %f)" % (self.pos.px, self.pos.py, self.pos.pa)
            self.waypoints.append((self.pos.px, self.pos.py, self.pos.pa))
            self.start_time = current_time

    def state_reset(self):
        self.a_star_cont.state_reset()
        self.waypoints = []

    def run(self, pipe_in):
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
