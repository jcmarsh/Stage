#!/usr/bin/env python

# Author James Marshall

# The first arg should be the file name of the player config file
# The world files name is read from the config file
# The second arg should be the file name of the picture file to use as the floor plan for player.
import sys
import shutil
from subprocess import call
from os import path
# needed to parse the name of the worldfile from the config file
from stage_utils import *

def print_n_quit():
    print 'usage: python run_player.py [name_of_config.cfg] [name_of_map.png]'
    exit()

if len(sys.argv) < 3:
    print_n_quit()

config_name = sys.argv[1]
map_name = sys.argv[2]

if path.splitext(config_name)[1] != ".cfg" or path.splitext(map_name)[1] != ".png":
    print_n_quit()

print "Provided filename: ", map_name

if WriteFloor(map_name) != 0:
    print "Failed to write floor.inc"
    exit()

# Copy the world file to a temporary run file (so that the controller knows the name)
new_world_name = "run_temp.world"
old_world_name = search_text_property(config_name, "worldfile")

shutil.copyfile(old_world_name, new_world_name)

# Add a map driver to a new .cfg that uses the provided map name
print "Ready to process config file: ", config_name

new_cfg_name = "run_temp.cfg"  #_" + config_name
if WriteCFG(new_cfg_name, config_name, map_name) != 0:
    print "Failed to write the config file %s" % (new_cfg_name)
    exit()

call(["player", new_cfg_name])

print "Complete"
