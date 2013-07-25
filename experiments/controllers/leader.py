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

    def state_die(self):
        # TODO: Close the pipes?
        self.a_star_cont.state_die() # Takes care of the proxies and client.

    def state_start(self):
        self.a_star_cont.state_start()

    def state_go(self, command_send):
        self.a_star_cont.state_go()
        
        if not(command_send == None) :
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            if elapsed_time >= self.way_time:
                # Create new waypoint
                self.waypoints.append((self.pos.px, self.pos.py, self.pos.pa))
                command_send.send(str(self.pos.px) + " " + str(self.pos.py) + " " + str(self.pos.pa))
                self.start_time = current_time

    def state_reset(self):
        self.a_star_cont.state_reset()
        self.waypoints = []

    def run(self, pipe_in, command_send):
        STATE = "IDLE"

        while True:
            # Check if a collision has happened
            self.a_star_cont.check_collision(pipe_in)

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
                self.state_go(command_send)
            elif STATE == "RESET":
                self.state_reset()
                STATE = "IDLE"
            elif STATE != "IDLE":
                print "leader.py has recieved an improper state: %s" % (STATE)

def go(robot_name, pipe_in, command_receive, command_send):
    if not(command_receive == None): # THE LEADER TAKES COMMANDS FROM NO ONE!
        print "Leader.py takes commands from no one!"
    controller = LeaderCont()
    controller.init(robot_name)
    controller.run(pipe_in, command_send)
