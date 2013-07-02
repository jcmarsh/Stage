# Basic outline for a controller
# Pay attention to this, since overlord.py assumes some of this
# These functions / the communication should be enforced
# James Marshall

import math
import sys
import algs # Right now just contains a_star (well, art_pot too, but should use the driver instead)
from playerc import *
from stage_utils import * # Helper functions

class ExampleCont:
    # All controllers need a client, and will likely have position, ranger (sensors for the gridcar), graphics, and local planner
    client = None
    pos = None
    ran = None
    gra = None
    pla = None
    
    goal = None
    offset = None
    
    def init(self, robot_name):
        # Create client object and other proxies, using helper functions in stage_utils
        self.client = startup(("filler", robot_name), "run_temp.cfg")
        self.pos, self.ran, self.gra = create_std(self.client)

        # proxy for the local navigator
        self.pla = playerc_planner(self.client, 0)
        if self.pla.subscribe(PLAYERC_OPEN_MODE) != 0:
            raise playerc_error_str()

        self.client.read()

        # run_temp.world is the script generated .world file. For now we only support one target.
        target_loc = search_pose("run_temp.world", "target0")
        self.goal = Point(target_loc[0], target_loc[1])
        self.offset = Point(8, 8)
        
    def run(self, pipe_in):
        prev_points = [] # For drawing the trail of the robot.
        STATE = "IDLE"

        while True:
            if pipe_in.poll():
                STATE = pipe_in.recv()
                    
            if STATE == "DIE":
                pipe_in.close()
                self.cleanup()
                break
            elif STATE == "START":
                self.pla.enable(1) # TODO: See if this is actually needed / used.
                
                STATE = "GO"
            elif STATE == "GO":
                idt = self.client.read()

                # Check sensor readings
                for i in range(0, self.ran.ranges_count):
                    # figure out location of sensed object
                    tao = (2 * math.pi * i) / self.ran.ranges_count
                    obs_x = self.ran.ranges[i] * math.cos(tao)
                    obs_y = self.ran.ranges[i] * math.sin(tao)
                    # obs_x and obs_y are relative to the robot, and I'm okay with that.

                # Planning and movement should be done here.

                # Put pretty things on the screen
                prev_points.append(draw_all(self.gra, self.pos, self.offset, self.grid_num, None, path, prev_points))
            elif STATE == "RESET":
                prev_points = []
                self.pla.enable(0) # TODO: Check if needed
                
                STATE = "IDLE"
            elif STATE != "IDLE":
                print "example.py has recieved an improper state: %s" % (STATE)

        print("DONE!")

    def cleanup(self):
        self.pos.unsubscribe()
        self.ran.unsubscribe()
        self.gra.unsubscribe()
        self.pla.unsubscribe()
        self.client.disconnect()

def go(robot_name, pipe_in):
    controller = ExampleCont()
    controller.init(robot_name)
    controller.run(pipe_in)

