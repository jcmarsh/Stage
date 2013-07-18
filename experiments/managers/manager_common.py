# functions / structs used by multiple managers

# July, 2013 - James Marshall

#####################################################################
# Represents some handy information about a robot
# TODO: Consider moving to a separate file; needed for many managers.
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
