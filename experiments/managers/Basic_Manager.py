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
        self.pipe_manager_end = None
        self.pipe_robot_end = None # TODO: The manager probably shouldn't have this bit.

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
    collision = False
    
    def add_controller(self, controller_name, new_world_name, robot_name):
        controller_imp = __import__(controller_name)
        loc = search_pose(new_world_name, robot_name)
        print "We've got a robot: %s\t%s - (%f,%f)" % (robot_name, controller_name, loc[0], loc[1])
        self.robots.append(Robot(robot_name, controller_imp, loc[0], loc[1], 0)) # TODO: look into what controller_imp actually is.

    def open_controllers(self):
        for i in range(len(self.robots)):
            print "Opening controller for %s" % (self.robots[i].name)
            self.robots[i].pipe_robot_end, self.robots[i].pipe_manager_end = multiprocessing.Pipe()

            self.robots[i].controller_p = multiprocessing.Process(target=self.robots[i].controller_i.go, args=(self.robots[i].name, self.robots[i].pipe_robot_end))
            self.robots[i].controller_p.start()


    def start_controllers(self):
        for i in range(len(self.robots)):
            self.robots[i].pipe_manager_end.send("START")

    def test_finished(self, sim):
        dists = getDistances(self.robots, sim)
        if min(dists) < .25: # The test is complete once any of the robots are within the threshold
            return True
        else:
            return False

    def check_messages(self):
        for i in range(len(self.robots)):
            if self.robots[i].pipe_manager_end.poll():
                MSG = self.robots[i].pipe_manager_end.recv()
                if MSG == "COLLISION":
                    print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAh. %d" % (i)
                    self.collision = True

    def check_collision(self):
        return self.collision

    def reset_controllers(self, sim):
        for i in range(len(self.robots)):
            self.robots[i].pipe_manager_end.send("RESET")

        time.sleep(1)

        # Reset the robot locations
        for i in range(len(self.robots)):
            sim.set_pose2d(self.robots[i].name, self.robots[i].start_x, self.robots[i].start_y, self.robots[i].start_a)

        # Reset Collision flag
        self.collision = False

    def shutdown_controllers(self):
        for i in range(len(self.robots)):
            self.robots[i].pipe_manager_end.send("DIE")
        time.sleep(2)
        for i in range(len(self.robots)):
            self.robots[i].controller_p.join()

    # Functions concerning stat collection
    def final_stats(self, sim):
        dists = getDistances(self.robots, sim)
        ret_str = ""
        for dist in range(len(dists)):
            ret_str = ret_str + "\tdist_" + str(dist) + ": " + str(dists[dist])
        return ret_str

    def update_stats(self, sim):
        return
