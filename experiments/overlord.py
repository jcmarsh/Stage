#!/usr/bin/env python

# Author James Marshall

# Facilitates the execution of many test runs

import ConfigParser
import multiprocessing
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
        self.controller_i = controller
        self.controller_p = None
        self.pipe_recieve = None
        self.pipe_send = None

def _dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))


def getDistances():
    distances = []
    for i in range(0, len(robots)):
        pose = sim.get_pose2d(robots[i].name)
        # TODO: The target location shouldn't be hard coded
        distances.append(_dist(-7, 7, pose[1], pose[2]))
    return distances

#####################################################################
# Phase 1: Setup
# Argument should be the name of experiment description file
def print_n_quit():
    print 'usage: python overlord.py [experiment_description.ini] [results_file.txt]'
    exit()

if len(sys.argv) < 3:
    print_n_quit()

experiment_desc = sys.argv[1]

if os.path.splitext(experiment_desc)[1] != ".ini":
    print_n_quit()
print "Provided description file: %s" % (experiment_desc)

results_file_n = sys.argv[2]
print "Results will be saved to: %s" % (results_file_n)
try:
    results_file = open(results_file_n, "a")
except IOError:
    print "Failed to open results file. Quiting."
    print_n_quit()

config = ConfigParser.ConfigParser()
config.readfp(open(experiment_desc)) # TODO: IOError here?

config_file_name = config.get("files", "cfg")
map_file_name = config.get("files", "map")
print "Config File: %s\t Map File: %s" % (config_file_name, map_file_name)

if WriteFloor(map_file_name) != 0:
    print "Failed to write floor.inc"
    exit()

new_world_name = "run_temp.world"
old_world_name = config.get("files", "world")
new_world_file = open(new_world_name, "w")
old_world_file = open(old_world_name, "r")
    
for line in old_world_file:
    new_world_file.write(line)
old_world_file.close()

new_world_file.write("\n\n")
new_world_file.write("# The following was added by overload.py parsing the .ini experiment file.\n")
for pair in config.items("worldfile"):
    new_world_file.write(pair[0] + " " + pair[1] + "\n")
new_world_file.write("\n")

new_world_file.close()

new_cfg_name = "run_temp.cfg"
if WriteCFG(new_cfg_name, config_file_name, map_file_name) != 0:
    print "Failed to write the config file %s" % (new_cfg_name)
    exit()

# Enough is now known to start player.
player_id = subprocess.Popen(["player", new_cfg_name])
# Give the simulator a chance to startup
time.sleep(4)

# Robot information
num_controllers = int(config.get("controllers", "num"))
robots = []
for i in range(0, num_controllers):
    controller_name = config.get("controllers", "cont" + str(i))
    controller_imp = __import__(controller_name)
    robot_name = config.get("controllers", "name" + str(i))
    loc = search_pose(new_world_name, robot_name)
    print "We've got a robot: %s\t%s - (%f,%f)" % (robot_name, controller_name, loc[0], loc[1])
    robots.append(Robot(robot_name, controller_imp, loc[0], loc[1], 0))

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

# Finally, set up experiment specific configuration
# TODO: This could be cleaned up with a function.
time_scale = 1000000.0
try:
    num_runs = int(config.get("experiment", "runs"))
except (ConfigParser.NoOptionError, ValueError):
    num_runs = 1
    print "Failed to read \"runs\" value from %s, defaulting to 1" % (experiment_desc)
try:
    timeout = int(config.get("experiment", "timeout"))
except (ConfigParser.NoOptionError, ValueError):
    timeout = 600
    print "Failed to read \"timeout\" value from %s, defaulting to 600 seconds" % (experiment_desc)

#####################################################################
# Phase 2: Run
# Launch the .ini described controllers
num_controllers = int(config.get("controllers", "num"))
for i in range(0, len(robots)):
    print "Opening controller for %s" % (robots[i].name)
    robots[i].pipe_recieve, robots[i].pipe_send = multiprocessing.Pipe(False)
    robots[i].controller_p = multiprocessing.Process(target=robots[i].controller_i.go, args=(robots[i].name, robots[i].pipe_recieve, ))
    robots[i].controller_p.start()
    time.sleep(2)

times = []
for run_num in range (0, int(config.get("experiment", "runs"))):
    start_time = sim.get_time(0)
    current_time = start_time

    # Start the controllers
    for i in range(0, len(robots)):
        robots[i].pipe_send.send("START")

    # Test for whatever it is we are measuring
    finished = False
    dists = []
    while (not(finished)):
        dists = getDistances()
        if min(dists) < .25: # The test is complete once any of the robots are within a meter of the target
            finished = True
        else:
            finished = False

        current_time = sim.get_time(0)
        if (current_time - start_time >= timeout * time_scale): # Did it run out fo time?
            finished = True
            print "TIMEOUT!"

    # Record results
    times.append(((current_time - start_time) / time_scale, dists))


    # Reset the controllers
    for i in range(0, len(robots)):
        robots[i].pipe_send.send("RESET")

    time.sleep(1)
    # Reset the robot locations
    for i in range(0, len(robots)):
        sim.set_pose2d(robots[i].name, robots[i].start_x, robots[i].start_y, robots[i].start_a)

    # Take a short break... see if that helps
    time.sleep(2)

print "OVER"
print times
results_file.write(experiment_desc + "\n")
for i in range(0, len(times)): # times is of the structure ((time, (dist0, dist1, ... distn)), ( ... )) I think.
    results_file.write("Time: " + str(times[i][0]) + "\t")
    for j in range(0, len(times[i][1])):
        results_file.write("dist_" + str(j) + ": " + str(times[i][1][j]) + "\t")
    results_file.write("\n")
results_file.write("\n")

# Shut down controllers
for i in range(0, len(robots)):
    robots[i].pipe_send.send("DIE")
time.sleep(2)
for i in range(0, len(robots)):
    robots[i].controller_p.join()

sim.unsubscribe()
client.disconnect()

time.sleep(1)
player_id.terminate()
print "SHUTDOWN COMPLETE"

#####################################################################
# Phase 3: Report
