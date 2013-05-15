#!/usr/bin/env python

# Author James Marshall

# Facilitates the execution of many test runs

import ConfigParser
import os
import sys

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

print "Config File: %s" % (config.get("files", "cfg"))
print "Map File: %s" % (config.get("files", "map"))




print "Number of controllers: %s" % (config.get("controllers", "num"))
print "Controller 1: %s \t %s" % (config.get("controllers", "cont0"), config.get("controllers", "args0"))


# Phase 2: Run

# Phase 3: Report
