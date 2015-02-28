/*
 * Connects to a position2d device (number 1) at the specified IP.
 */

#include <unistd.h>
#include <libplayerc/playerc.h>

// from: http://playerstage.sourceforge.net/doc/Player-svn/player/group__libplayerc__example.html
int main(int argc, const char **argv) {
  playerc_client_t *robot_client;
  playerc_ranger_t *robot_ranger;
  playerc_client_t *sim_client;
  playerc_simulation_t *simulation;

  if (argc < 2) {
    puts("Usage: basic <ip_address>");
    return 0;
  }

  // Create client for the sim commands and connect
  sim_client = playerc_client_create(0,  argv[1], 6665);
  if (0 != playerc_client_connect(sim_client)) {
    return -1;
  }

  // Create and subscribe to sim device (to reset position)
  simulation = playerc_simulation_create(sim_client, 0);
  if (playerc_simulation_subscribe(simulation, PLAYER_OPEN_MODE)) {
    return -1;
  }

  robot_client = playerc_client_create(0,  argv[1], 6666);
  if (0 != playerc_client_connect(robot_client)) {
    printf("Failed to connect to robot client.\n");
    return -1;
  }

  robot_ranger = playerc_ranger_create(robot_client, 1);
  if (playerc_ranger_subscribe(robot_ranger, PLAYER_OPEN_MODE)) {
    printf("Failed to subscribe to robot's ranger device.\n");
    return -1;
  }


/* call to get_config seg faults for some reason.
  double *min_angle, *max_angle, *angular_res, *min_range, *max_range, *range_res, *frequency;
  if (playerc_ranger_get_config(robot_ranger, min_angle, max_angle, angular_res, min_range, max_range, range_res, frequency)) {
    printf("Failed to get config for robot ranger.]n");
    return -1;
  }

  printf("Ranger fequency (%f) and stats:\n", *frequency);
  printf("\tMin and max angles and resolution: %f - %f: %f\n", *min_angle, *max_angle, *angular_res);
  printf("\tMin and max ranges and resolution: %f - %f: %f\n", *min_range, *max_range, *range_res);
*/

  int index = 0;
  long prev_time = playerc_simulation_get_time(simulation, 0);
  printf("Previous time = %ld\n", prev_time);
  while(1) {
    usleep(1000);
    // Calculate velocity and minimum distance from an obstacle.
    // I hope that this is accurate.
    // For velocity I will also need to track time. Lame.
    // Should also check distance from start and from goal to trigger the start of the stats and the end.

    // check if haven't start or already done

    // Velocity
    // read data

    long current_time = playerc_simulation_get_time(simulation, 0);
    double pos_x, pos_y, pos_a;
    playerc_simulation_get_pose2d(simulation, "hank", &pos_x, &pos_y, &pos_a);
    printf("Pos at time %ld is (%f, %f) - %f\n", current_time, pos_x, pos_y, pos_a);

    
    // get position
    // get time
    // calc velocity

    // obstacle distance
    // Read data
    playerc_client_read(robot_client);
    double min = 1000; // approximately infinite.
    for (index = 0; index < 16; index++) {
      if (robot_ranger->ranges[index] < min) {
        min = robot_ranger->ranges[index];
      }
    }

    // print if all
    printf("Min dist: %f\n", min);
  }

  // Shutdown
  playerc_client_disconnect(sim_client);
  playerc_client_destroy(sim_client);

  return 0;
}

