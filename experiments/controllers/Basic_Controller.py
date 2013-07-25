# Base class for controllers

# July, 2013 - James Marshall

from stage_utils import *

class Basic_Controller(object):
    client = None
    pos = None # Robot position
    ran = None # Range sensors (No noise)
    gra = None # Graphics layer
    pla = None # Local Navigator
    
    prev_no_collision = True

    def init(self, robot_name):
        # Create client object
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

    def check_collision(self, pipe):
        # print "Stalled? %d" % (self.pos.stall)
        if self.pos.stall and self.prev_no_collision:
            self.prev_no_collision = False
            pipe.send("COLLISION")
        elif not(self.pos.stall):
            self.prev_no_collision = True
        
