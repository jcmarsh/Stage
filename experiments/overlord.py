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

# TODO: This is a horrible hack. I want the manager files in a sub-dir, but need to import them
# TODO: Should check if this is an actual directory and fail if not. Or, you know, actually make the code sane.
sys.path.append('/home/jcmarsh/Research/stage/experiments/managers')

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
# The manager will now deal with the robots and their controllers.
# TODO: error out if this fails.
manager_name = config.get("controllers", "manager")
manager_imp = __import__(manager_name)
manager = manager_imp.Manager()

num_controllers = int(config.get("controllers", "num"))
for i in range(num_controllers):
    controller_name = config.get("controllers", "cont" + str(i))
    robot_name = config.get("controllers", "name" + str(i))
    manager.add_controller(controller_name, new_world_name, robot_name)

# Setup the overlord controller
client = playerc_client(None, 'localhost', 6665)
if client.connect() != 0:
    raise playerc_error_str()
# proxy for the simulator
sim = playerc_simulation(client, 0)
if sim.subscribe(PLAYERC_OPEN_MODE) !=0:
    raise playerc_error_str()

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
manager.open_controllers()

times = []
for run_num in range(int(config.get("experiment", "runs"))):
    start_time = sim.get_time(0)
    current_time = start_time

    manager.start_controllers()

    # Test for whatever it is we are measuring
    finished = False
    dists = []
    while(not(finished)):
        finished = manager.test_finished(sim)

        current_time = sim.get_time(0)
        if (current_time - start_time >= timeout * time_scale): # Did it run out fo time?
            finished = True
            print "TIMEOUT!"

    # Record results
    times.append(((current_time - start_time) / time_scale, dists))

    manager.reset_controllers(sim)

    time.sleep(2)

print "OVER"
print times
results_file.write(experiment_desc + "\n")
for i in range(len(times)): # times is of the structure ((time, (dist0, dist1, ... distn)), ( ... )) I think.
    results_file.write("Time: " + str(times[i][0]) + "\t")
    for j in range(len(times[i][1])):
        results_file.write("dist_" + str(j) + ": " + str(times[i][1][j]) + "\t")
    results_file.write("\n")
results_file.write("\n")

manager.shutdown_controllers()

sim.unsubscribe()
client.disconnect()

time.sleep(1)
player_id.terminate()
print "SHUTDOWN COMPLETE"

#####################################################################
# Phase 3: Report
