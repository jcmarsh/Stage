/*
 * File: ptest.c
 * Desc: Player test program for use with libstageplugin
 * Author: Richard Vaughan
 * License: GPL v2
 * CVS info:
 *  $Source: /home/tcollett/stagecvs/playerstage-cvs/code/stage/examples/libplayerc/ptest.c,v $
 *  $Author: pooya $
 *  $Revision: 1.1 $
 */

#include <stdio.h>
#include <string.h>
#include <libplayerc/playerc.h>

int main(int argc, const char **argv)
{
  const char *host;
  int port;
  playerc_client_t *client;

  host = "localhost";
  port = 6665;
  
  printf( "Attempting to connect to a Player server on %s:%d\n",
	      host, port );

  // Create a client and connect it to the server.
  client = playerc_client_create(NULL, host, port);
  if (playerc_client_connect(client) != 0) {
    puts( "Failed. Quitting." );
    return -1;
  }

  // Create and subscribe to a local planner
  playerc_position2d_t *loc_pla =  playerc_position2d_create(client, 1);
  if (playerc_position2d_subscribe(loc_pla, PLAYER_OPEN_MODE))
    return -1;
  
  if (playerc_position2d_set_cmd_pose(loc_pla, 7, 7, 0, 1) != 0)
    return -1;
  
  while (true) {
    // Wait for new data from server
    playerc_client_read(client);
    
    // Print current robot pose
    //printf("position : %f %f %f\n", loc_pla->px, loc_pla->py, loc_pla->pa);
  } 
  
  playerc_position2d_unsubscribe(loc_pla);
  playerc_position2d_destroy(loc_pla);

  puts( "Disconnecting" );
  // Shutdown
  playerc_client_disconnect(client);
  playerc_client_destroy(client);

  puts( "Done." );
  return 0;
}
