#include <libplayerc/playerc.h>

// Check these
#include <unistd.h>
#include <sys/types.h>
#include <errno.h>
#include <stdio.h>
#include <sys/wait.h>
#include <stdlib.h>


// Attempt at a controller that spawns three controllers and then allows voting to pick output
// Also needs to muck with the memory

// From http://www.thegeekstuff.com/2012/05/c-fork-function/
// from: http://playerstage.sourceforge.net/doc/Player-svn/player/group__libplayerc__example.html

//#define HOST "192.168.23.201"
#define HOST "127.0.0.1"

void child_loop(int whoAmI) {
  printf("It is I, child %d\n", whoAmI);
}

int main(int argc, const char **argv) {
  int i;
  int amParent = 0;
  playerc_client_t *client;
  playerc_position2d_t *position2d;

  // Children IDs
  pid_t childPID_1;
  pid_t childPID_2;
  pid_t childPID_3;

  // State for the children


  // Create client and connect
  client = playerc_client_create(0, HOST, 6666); // I start at 6666
  if (0 != playerc_client_connect(client)) {
    return -1;
  }

  // Create and subscribe to position2d device
  position2d = playerc_position2d_create(client, 0);
  if (playerc_position2d_subscribe(position2d, PLAYER_OPEN_MODE)) {
    return -1;
  }

  // Create the children
  childPID_1 = fork();

  if(childPID_1 >= 0) { // fork was successful
    if(childPID_1 == 0) { // child 1 process
      child_loop(1);
    } else { // Parent process
      childPID_2 = fork();
      
      if (childPID_2 >= 0) { // fork was successful
	if (childPID_2 == 0) { // child 2 process
	  child_loop(2);
	} else { // Parent process
	  childPID_3 = fork();

	  if (childPID_3 >= 0) { // fork was successful
	    if (childPID_3 == 0) { // child 3 process
	      child_loop(3);
	    } else { // Parent process
	      printf("IT IS I, THE ONE WHICH BEGAT YOU ALL.\n");
	      amParent = 1;
	    }
	  }
	}
      }
    }
  }

  
  if (amParent) {
    // Make robot move
    playerc_position2d_enable(position2d, 1);
    playerc_position2d_set_cmd_vel(position2d, 0.3, 0.2, 0.1, 1);

    while(1) {
      // blah
    }

    // Shutdown
    playerc_position2d_unsubscribe(position2d);
    playerc_position2d_destroy(position2d);
    playerc_client_disconnect(client);
    playerc_client_destroy(client);
  }

  return 0;
}

