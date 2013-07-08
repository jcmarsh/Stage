# Keeps a queue of waypoints that are sent to it, and then goes to them.
# James Marshall

import math
import sys
#import algs # TODO: needed?
import time
from playerc import *
from stage_utils import *

class FollowerCont:
    way_dist = .1 # TODO: Parameterize?
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
        print "Robot name: %s" % (robot_name)
        self.client = startup(("filler", robot_name), "run_temp.cfg")
        self.pos, self.ran, self.gra = create_std(self.client)

        # proxy for the local navigator
        self.pla = playerc_planner(self.client, 0)
        if self.pla.subscribe(PLAYERC_OPEN_MODE) != 0:
            raise playerc_error_str()

        self.client.read()

    def state_die(self):
        self.pos.unsubscribe()
        self.ran.unsubscribe()
        self.gra.unsubscribe()
        self.pla.unsubscribe()
        self.client.disconnect()

    def state_start(self):
        self.pla.enable(1)

    def state_go(self, command_send):
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        if not(command_send == None): # May be the last in the line of robots.
            if elapsed_time >= self.way_time:
                # Create new waypoint
#                print "New waypoint: (%f, %f, %f)" % (self.pos.px, self.pos.py, self.pos.pa)
#                self.waypoints.append((self.pos.px, self.pos.py, self.pos.pa))
                command_send.send(str(self.pos.px) + " " + str(self.pos.py) + " " + str(self.pos.pa))
                self.start_time = current_time

        if len(self.waypoints) >= 1:
            w_x = self.waypoints[0][0]
            w_y = self.waypoints[0][1]
            dist = math.sqrt(math.pow(self.pos.px - w_x, 2) + math.pow(self.pos.py - w_y, 2))
            if  dist < self.way_dist:
                self.waypoints.pop()

        if len(self.waypoints) >= 1:
            self.pla.set_cmd_pose(self.waypoints[0][0], self.waypoints[0][1], self.waypoints[0][2])

    def state_reset(self):
        self.pla.enable(0)
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
                command_receive.close()
                # Hmm.... the receiver always closes, since the sender pipe might not exist.
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
                print "leader.py has received an improper state: %s" % (STATE)

            # Check for new waypoints
            if command_receive.poll():
                waypoint = command_receive.recv().split() # TODO: verify correct format
                w_x = float(waypoint[0])
                w_y = float(waypoint[1])
                w_a = float(waypoint[2])
                print "received waypoint: %f, %f, %f" % (w_x, w_y, w_a)
                self.waypoints.append((w_x, w_y, w_a))


def go(robot_name, pipe_in, command_receive, command_send):
    if command_receive == None:
        print "Perhaps you do not understand what \"Follower\" means."
        return
    controller = FollowerCont()
    controller.init(robot_name)
    controller.run(pipe_in, command_receive, command_send)

