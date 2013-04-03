import math
from playerc import *

g_r = .1 # radius of goal, in meters
g_e = 2 # extent of field (greater than this, move at maximum speed)
g_s = .5 # scale factor
o_r = .0 # radius of obstacles
o_e = 1.5
o_s = .2

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def potential(pos, ran, goal):
    # Head towards the goal!
    dist = math.sqrt(math.pow(goal.x - pos.px, 2) + math.pow(goal.y - pos.py, 2))
    theta = math.atan2(goal.y - pos.py, goal.x - pos.px) - pos.pa

    delta = Point(0,0)

    total_factors = 0
    if (dist < g_r):
        v = 0
        delta.x = 0
        delta.y = 0
    elif ( g_r <= dist and dist <= g_e + g_r):
        v = g_s * (dist - g_r)
        delta.x = v * math.cos(theta)
        delta.y = v * math.sin(theta)
        total_factors += 1
    else:
        v = g_s * g_e
        delta.x = v * math.cos(theta)
        delta.y = v * math.sin(theta)
        total_factors += 1

    for i in range(0, ran.ranges_count):
        # figure out location of the obstacle...
        tao = (2 * math.pi * i) / ran.ranges_count
        obs = Point(ran.ranges[i] * math.cos(tao), ran.ranges[i] * math.sin(tao))
        # obs.x and obs.y are relative to the robot, and I'm okay with that.
        
        dist = math.sqrt(math.pow(obs.x, 2) + math.pow(obs.y, 2))
        theta = math.atan2(obs.y, obs.x) 

        if (dist <= o_e + o_r):
            delta.x += -o_s * (o_e + o_r - dist) * math.cos(theta) 
            delta.y += -o_s * (o_e + o_r - dist) * math.sin(theta)
            total_factors += 1

    return delta, total_factors
