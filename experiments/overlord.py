#!/usr/bin/env python

# Author James Marshall

# Facilitates the execution of many test runs

import ConfigParser
import os
import shutil
import subprocess
import sys
import time

from playerc import *
from stage_utils import *

#####################################################################
# Represents some handy information about a robot
class Robot:
    def __init__(self, name, controller, x, y, a):
        self.start_x = x
        self.start_y = y
        self.start_a = a
        self.name = name
        self.controller_n = controller
        self.controller_p = None

def targetReached():
    for i in range(0, len(robots)):
        pose = sim.get_pose2d(robots[i].name)
        dist = math.sqrt(math.pow(7 - pose[1], 2) + math.pow(7 - pose[2], 2))
        if dist < 1:
            return True
    return False

#####################################################################
# Phase 1: Setup
# Argument should be the name of experiment description file
def print_n_quit():
    print 'usage: python overlord.py [experiment_description.ini]'
    exit()

if len(sys.argv) < 2:
    print_n_quit()

experiment_desc = sys.argv[1]

if os.path.splitext(experiment_desc)[1] != ".ini":
    print_n_quit()

print "Provided description file: %s" % (experiment_desc)

config = ConfigParser.ConfigParser()
config.readfp(open(experiment_desc))

config_file_name = config.get("files", "cfg")
map_file_name = config.get("files", "map")
print "Config File: %s\t Map File: %s" % (config_file_name, map_file_name)

if WriteFloor(map_file_name) != 0:
    print "Failed to write floor.inc"
    exit()

new_world_name = "run_temp.world"
old_world_name = search_text_property(config_file_name, "worldfile")
shutil.copyfile(old_world_name, new_world_name)

new_cfg_name = "run_temp.cfg"
if WriteCFG(new_cfg_name, config_file_name, map_file_name) != 0:
    print "Failed to write the config file %s" % (new_cfg_name)
    exit()

# Enough is now known to start player.
player_id = subprocess.Popen(["player", new_cfg_name])
# Give the simulator a chance to startup
time.sleep(2)

num_controllers = int(config.get("controllers", "num"))
robots = []
for i in range(0, num_controllers):
    controller_name = config.get("controllers", "cont" + str(i))
    robot_name = config.get("controllers", "name" + str(i))
    loc = search_pose(new_world_name, robot_name)
    print "We've got a robot: %s\t%s - (%f,%f)" % (robot_name, controller_name, loc[0], loc[1])
    robots.append(Robot(robot_name, controller_name, loc[0], loc[1], 0))

# Setup our controller
client = playerc_client(None, 'localhost', 6665)
if client.connect() != 0:
    raise playerc_error_str()
# proxy for the simulator
sim = playerc_simulation(client, 0)
if sim.subscribe(PLAYERC_OPEN_MODE) !=0:
    raise playerc_error_str()

# Should we launch a controller just for recording things?
# Will the script have access to each controller's runtime?
# How are we managing all of this?

# DON"T FORGET ABOUT NOISE AND THE OTHER "KNOBS"

#####################################################################
# Phase 2: Run

for run_num in range (0, int(config.get("experiment", "runs"))):
    # Launch the .ini described controllers
    num_controllers = int(config.get("controllers", "num"))
    for i in range(0, len(robots)):
        print "Opening controller for %s" % (robots[i].name)
        robots[i].controller_p = subprocess.Popen(["python", robots[i].controller_n, robots[i].name])

    # Test for whatever it is we are measuring
    finished = False
    while (not(finished)):
            finished = targetReached() # Is experiment complete?

#        if (): # Did it run out fo time?
#            finished = True

    # Record results
    print "Action will be taken!"

    # Shut down controllers
    for i in range(0, len(robots)):
        robots[i].controller_p.terminate()
    
    # Reset the robot locations
    for i in range(0, len(robots)):
        sim.set_pose2d(robots[i].name, robots[i].start_x, robots[i].start_y, robots[i].start_a)



#####################################################################
# Phase 3: Report
