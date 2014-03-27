/*
 * Connects to a planner device (number 0) at the specified IP.
 */

#include <libplayerc/playerc.h>

// from: http://playerstage.sourceforge.net/doc/Player-svn/player/group__libplayerc__example.html
int main(int argc, const char **argv) {
  int i;
  playerc_client_t *client;
  playerc_position2d_t *position2d;
  playerc_planner_t *planner;

  if (argc < 2) {
    puts("Usage: basic <ip_address>");
    return 0;
  }

  // Create client and connect
  client = playerc_client_create(0, argv[1], 6666); // I start at 6666
  if (0 != playerc_client_connect(client)) {
    return -1;
  }

  // Create and subscribe to position2d device
  //  position2d = playerc_position2d_create(client, 0);
  //  if (playerc_position2d_subscribe(position2d, PLAYER_OPEN_MODE)) {
  //    return -1;
  //  }

  // Create and subscribe to position2d device
  planner = playerc_planner_create(client, 0);
  if (playerc_planner_subscribe(planner, PLAYER_OPEN_MODE)) {
    return -1;
  }

  // Make robot move
  //  playerc_position2d_enable(position2d, 1);
  playerc_planner_set_cmd_pose(planner, 7.0, 7.0, 0.0);

  while(1) {
    // blah
  }

  // Shutdown
  playerc_position2d_unsubscribe(position2d);
  playerc_position2d_destroy(position2d);
  playerc_client_disconnect(client);
  playerc_client_destroy(client);

  return 0;
}

