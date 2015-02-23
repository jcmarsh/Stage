#!/usr/bin/env python

# 

import math
import sys
import algs
import Basic_Controller
from playerc import *
from stage_utils import *

class Time():
    client = None
    pos = None
    ran = None
    gra = None

    tim = None

    goal = None
    offset = None

    def init(self, robot_name):
        # Create client object
        self.client = startup(("filler", robot_name), "run_temp.cfg")
        self.pos, self.ran, self.gra = create_std(self.client)

        self.tim = playerc_time(self.client, 0)
        if self.tim.subscribe(PLAYERC_OPEN_MODE) != 0:
            raise playerc_error_str()

        self.client.read()        

        self.offset = Point(8,8)

    def state_die(self):
        self.pos.unsubscribe()
        self.ran.unsubscribe()
        self.gra.unsubscribe()
        self.client.disconnect()

    def state_start(self):
        pass

    def check_collision(self, pipe):
        pass

    def state_go(self):
        idt = self.client.read()
        self.tim.get_time()

    def state_reset(self):
        pass

    def run(self, pipe_in):
        STATE = "IDLE"

        while(True):
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
                # Check if a collision has happened
                self.check_collision(pipe_in)
            elif STATE == "RESET":
                self.state_reset()
                STATE = "IDLE"
            elif STATE != "IDLE":
                print "time_driver.py has recieved an improper state: %s" % (STATE)

        print("DONE!")

def go(robot_name, pipe_in):
    controller = Time()
    controller.init(robot_name)
    controller.run(pipe_in)


