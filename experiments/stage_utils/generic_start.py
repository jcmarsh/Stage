# Common code for initiallizing the system
#
# author: James Marshall
from playerc import *
from parse_world import *

d_port = 6665
d_name = "sad"

def startup(args, cfg_file):
    robot_name = d_name
    port = d_port
    if len(args) >= 2:
        robot_name = args[1]
        port = find_port_by_name(cfg_file, robot_name)
        
    print "For %s, port: %d" % (robot_name, port)
    client = playerc_client(None, 'localhost', port)

    # connect
    if client.connect() != 0:
        raise playerc_error_str()

    return client

# position2d, ranger, and graphics
def create_std(client):
    # proxy for position2d:0
    pos = playerc_position2d(client, 0)
    if pos.subscribe(PLAYERC_OPEN_MODE) != 0:
        raise playerc_error_str()

    # proxy for ranger:0
    ran = playerc_ranger(client, 0)
    if ran.subscribe(PLAYERC_OPEN_MODE) != 0:
        raise playerc_error_str()

    # graphics, so I can see what is going on.
    gra = playerc_graphics2d(client, 0)
    if gra.subscribe(PLAYERC_OPEN_MODE) != 0:
        raise playerc_error_str()

    # get the geometry
    if pos.get_geom() != 0:
        raise playerc_error_str()
#    print "Robot size: (%.3f,%.3f)" % (pos.size[0], pos.size[1])

    return pos, ran, gra



