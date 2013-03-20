#!/usr/bin/env python

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
                retVal = (float(args[0]), float(args[1]))
                return retVal
        else:
            if name in line:
                matched = True

def to_robot_coords(robot, target):
    return (target[0] - robot[0], target[1] - robot[1])

def search_text_property(file_name, property_name):
    f = open(file_name, "r")
    for line in f:
        if property_name in line:
            print("Line: " + line)
            args = (line.partition('"')[2]).partition('"')[0]
            return args

#def find_port_by_name(file_name, robot_name):
#    f = open(file_name, "r")
#    search_str = "model \"" + robot_name +"\""
#    while True:
#        line = f.next()
#        if line.contsearch_str = 

# Test code
target = search_pose("find_target.world", "target0")
robot = search_pose("find_target.world", "hank")
drive_type_0 = search_text_property("gridcar.inc", "drive")
#drive_type_1 = search_text_property("diff_gridcar.inc", "drive")
print("DONE!")
print("Point 1:", robot[0], robot[1])
print("Point 2:", target[0], target[1])
print("Relative: ", to_robot_coords(robot, target))
print("-------------------")
print("gridcar.inc drive type:", drive_type_0)
#print("diff_gridcar.inc drive type:", drive_type_1)
