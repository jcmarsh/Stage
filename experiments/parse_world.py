#!/usr/bin/env python

# We need to be able to read the robot's initial pose and that of it's target.
# Or rather, it would be very helpful for the simplier examples.

import string

def search_pose(file_name, name):
    matched = False
    f = open(file_name, "r")
    for line in f:
        if matched: # found name, return next pose
            if "pose" in line:
                print("Pose: " + line)
                args = ((line.partition("[")[2]).partition("]"))
                args = args[0].strip(" ")
                args = args.split(" ")
                retVal = (float(args[0]), float(args[1]))
                return retVal
        else:
            if name in line:
                matched = True

def to_robot_coords(robot, target):
    return (target[0] - robot[0], target[1] - robot[1])

target = search_pose("find_target.world", "target0")
robot = search_pose("find_target.world", "hank")
print("DONE!")
print("Point 1:", robot[0], robot[1])
print("Point 2:", target[0], target[1])
print("Relative: ", to_robot_coords(robot, target))
