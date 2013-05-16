#!/usr/bin/env python

# Author James Marshall

# Facilitates the execution of many test runs

import ConfigParser
import os
import shutil
import subprocess
import sys

from stage_utils import *

#####################################################################
# Phase 1: Setup
# Argument should be the name of experiment description file
def print_n_quit():
    print 'usage: James, fill this in please.'
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

# Enough is now known to start player. Need to give it enough time to initialize before main loop.
# TODO: Wait on keypress?
# TODO: Set time for sim?
player_id = subprocess.Popen(["player", new_cfg_name])

# Should we launch a controller just for recording things?
# Will the script have access to each controller's runtime?
# How are we managing all of this?

# DON"T FORGET ABOUT NOISE AND THE OTHER "KNOBS"

print "Number of controllers: %s" % (config.get("controllers", "num"))
print "Controller 1: %s \t %s" % (config.get("controllers", "cont0"), config.get("controllers", "args0"))

#####################################################################
# Phase 2: Run

print "This is where the controllers should be started"

#####################################################################
# Phase 3: Report
