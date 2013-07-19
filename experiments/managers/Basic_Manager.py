# functions / structs used by multiple managers

# July, 2013 - James Marshall

#####################################################################
# Represents some handy information about a robot
# TODO: Consider moving to a separate file; needed for many managers.


import multiprocessing
import time
from playerc import *
from stage_utils import *

class Robot:
    def __init__(self, name, controller, x, y, a):
        self.start_x = x
        self.start_y = y
        self.start_a = a
        self.name = name
        self.controller_i = controller
        self.controller_p = None
        self.pipe_recieve = None
        self.pipe_send = None

def _dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

def getDistances(robots, sim):
    distances = []
    for i in range(len(robots)):
        pose = sim.get_pose2d(robots[i].name)
        # TODO: The target location shouldn't be hard coded
        distances.append(_dist(7, 7, pose[1], pose[2]))
    return distances

class Basic_Manager:
    robots = []
    
    def add_controller(self, controller_name, new_world_name, robot_name):
        controller_imp = __import__(controller_name)
        loc = search_pose(new_world_name, robot_name)
        print "We've got a robot: %s\t%s - (%f,%f)" % (robot_name, controller_name, loc[0], loc[1])
        self.robots.append(Robot(robot_name, controller_imp, loc[0], loc[1], 0)) # TODO: look into what controller_imp actually is.

    def open_controllers(self):
        for i in range(len(self.robots)):
            print "Opening controller for %s" % (self.robots[i].name)
            self.robots[i].pipe_recieve, self.robots[i].pipe_send = multiprocessing.Pipe(False)

            self.robots[i].controller_p = multiprocessing.Process(target=self.robots[i].controller_i.go, args=(self.robots[i].name, self.robots[i].pipe_recieve))
            self.robots[i].controller_p.start()


    def start_controllers(self):
        for i in range(len(self.robots)):
            self.robots[i].pipe_send.send("START")

    def test_finished(self, sim):
        dists = getDistances(self.robots, sim)
        if min(dists) < .25: # The test is complete once any of the robots are within the threshold
            return True
        else:
            return False

    def reset_controllers(self, sim):
        for i in range(len(self.robots)):
            self.robots[i].pipe_send.send("RESET")

        time.sleep(1)

        # Reset the robot locations
        for i in range(len(self.robots)):
            sim.set_pose2d(self.robots[i].name, self.robots[i].start_x, self.robots[i].start_y, self.robots[i].start_a)

    def shutdown_controllers(self):
        for i in range(len(self.robots)):
            self.robots[i].pipe_send.send("DIE")
        time.sleep(2)
        for i in range(len(self.robots)):
            self.robots[i].controller_p.join()
