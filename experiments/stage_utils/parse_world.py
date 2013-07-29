#!/usr/bin/env python

import math

# We need to be able to read the robot's initial pose and that of it's target.
# Or rather, it would be very helpful for the simplier examples.

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
                radian_alpha = (float(args[3]) / 360) * 2 * math.pi # .world uses degrees, everything else radians.
                retVal = (float(args[0]), float(args[1]), radian_alpha) # args[2] should be z offset. Not used.
                return retVal
        else:
            if name in line:
                matched = True

def search_text_property(file_name, property_name):
    f = open(file_name, "r")
    for line in f:
        if property_name in line:
            print("Line: " + line)
            args = (line.partition('"')[2]).partition('"')[0]
            return args

def find_port_by_name(file_name, robot_name):
    f = open(file_name, "r")
    search_str = "model \"" + robot_name +"\""
    while True:
        line = f.next()
        if search_str in line:
            # Found robot with correct name
            while True:
                line = f.next()
                if "provides" in line:
                    print("Line: " + line)
                    return int((line.partition(':')[2]).partition(':')[0])                    
            break

'''
# Test code
target = search_pose("find_target.world", "target0")
robot = search_pose("find_target.world", "hank")
drive_type_0 = search_text_property("gridcar.inc", "drive")
port = find_port_by_name("find_target.cfg", "hank")
#drive_type_1 = search_text_property("diff_gridcar.inc", "drive")
print("DONE!")
print("Point 1:", robot[0], robot[1])
print("Point 2:", target[0], target[1])
print("Relative: ", to_robot_coords(robot, target)) # Will fail, to_robot_coords now in graph_util
print("-------------------")
print("gridcar.inc drive type:", drive_type_0)
print("port: ", port)
#print("diff_gridcar.inc drive type:", drive_type_1)
'''
