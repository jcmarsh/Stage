# Keeps a queue of waypoints that are sent to it, and then goes to them.
# James Marshall

import math
import sys
import algs # TODO: needed?
import time
from playerc import *
from stage_utils import *

class FollowerCont:
    way_time = 1.0 # 1 second # TODO: Needed?
    start_time = 0
    waypoints = []
    pos = None

    client = None
    pos = None
    ran = None
    gra = None
    pla = None

    def init(self, robot_name):
        # Create client object and other proxies, using helper functions in stage_utils
        self.client = startup(("filler", robot_name), "run_temp.cfg")
        self.pos, self.ran, self.gra = create_std(self.client)

        # proxy for the local navigator
        self.pla = playerc_planner(self.client, 0)
        if self.pla.subscribe(PLAYERC_OPEN_MODE) != 0:
            raise playerc_error_str()

        self.client.read()

    def state_die(self):
        # TODO: close the channels?
        self.pos.unsubscribe()
        self.ran.unsubscribe()
        self.gra.unsubscribe()
        self.pla.unsubscribe()
        self.client.disconnect()

    def state_start(self):
        # UPDATE
        self.a_star_cont.state_start()

    def state_go(self, command_send):
        # UPDATE
        self.a_star_cont.state_go()
        
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        if elapsed_time >= self.way_time:
            # Create new waypoint
            print "New waypoint: (%f, %f, %f)" % (self.pos.px, self.pos.py, self.pos.pa)
            self.waypoints.append((self.pos.px, self.pos.py, self.pos.pa))
            command_send(str(self.pos.px) + " " + str(self.pos.py) + " " + str(self.pos.pa))
            self.start_time = current_time

    def state_reset(self):
        # UPDATE
        self.a_star_cont.state_reset()
        self.waypoints = []

    def run(self, pipe_in, command_receive, command_send):
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
                self.state_go(command_send)
            elif STATE == "RESET":
                self.state_reset()
                STATE = "IDLE"
            elif STATE != "IDLE":
                print "leader.py has recieved an improper state: %s" % (STATE)

            # Check for new waypoints
            if not(command_receive == None) and command_receive.poll():
                waypoint = command_receive.split() # TODO: verify correct format
                print "received waypoint: %f, %f, %f" % (waypoint[0], waypoint[1], waypoint[2])
                #waypoints.append(....)

def go(robot_name, pipe_in, command_receive, command_send):
        # UPDATE
    controller = LeaderCont()
    controller.init(robot_name)
    controller.run(pipe_in, command_recieve, command_send)

