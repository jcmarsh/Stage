#!/usr/bin/env python

# Author James Marshall

# The first arg should be the file name of the player config file
# The world files name is read from the config file
# The second arg should be the file name of the picture file to use as the floor plan for player.
import sys
import shutil
import subprocess
from os import path
# needed to parse the name of the worldfile from the config file
from stage_utils import *

def print_n_quit():
    print 'usage: python run_player.py [name_of_config.cfg] [name_of_world.world] [name_of_map.png]'
    exit()

if len(sys.argv) < 4:
    print_n_quit()

config_name = sys.argv[1]
world_name = sys.argv[2]
map_name = sys.argv[3]

if path.splitext(config_name)[1] != ".cfg" or path.splitext(world_name)[1] != ".world" or path.splitext(map_name)[1] != ".png":
    print_n_quit()

print "Config file: ", config_name
print "World file: ", world_name
print "Provided filename: ", map_name

if WriteFloor(map_name) != 0:
    print "Failed to write floor.inc"
    exit()

# Copy the world file to a temporary run file (so that the controller knows the name)
new_world_name = "run_temp.world"
old_world_name = "./worlds/" + world_name

shutil.copyfile(old_world_name, new_world_name)

# Add a map driver to a new .cfg that uses the provided map name
print "Ready to process config file: ", config_name
new_cfg_name = "run_temp.cfg"
if WriteCFG(new_cfg_name, config_name, map_name) != 0:
    print "Failed to write the config file %s" % (new_cfg_name)
    exit()


player_id = subprocess.Popen(["player", new_cfg_name])

print "Complete"
