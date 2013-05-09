/*
Copyright (c) 2007, Geoff Biggs
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of the Player Project nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/*
 * This simple client illustrates the use of a plugin interface. It subscribes
 * to a device providing the interface, then tests each message.
 *
 * The important point to note for the purposes of this example is the call to
 * playerc_add_xdr_ftable(). This function adds the XDR serialisation functions
 * to Player's internal table so that messages sent and received by this client
 * can be serialised correctly.
 */

#include <stdio.h>
#include <libplayerc/playerc.h>

#include "boundary_interf_client.h"

playerxdr_function_t* player_plugininterf_gettable (void);

int main(int argc, const char **argv)
{
  double scale = .01;
  int i;
  double read;
  playerc_client_t *client;
  playerc_position2d_t *position;
  playerc_planner_t *pla;
  boundary_interf_t *device;
  
  // Create a client and connect it to the server.
  client = playerc_client_create(NULL, "localhost", 6665);
  if (0 != playerc_client_connect(client)) {
    printf ("Could not connect\n");
    return -1;
  }

  position = playerc_position2d_create(client, 0);
  if (playerc_position2d_subscribe(position, PLAYER_OPEN_MODE)) {
    return -1;
  }

  pla = playerc_planner_create(client, 0);
  if (playerc_planner_subscribe(pla, PLAYER_OPEN_MODE)) {
    return -1;
  }

  // Load the plugin interface
  if (playerc_add_xdr_ftable (player_plugininterf_gettable (), 0) < 0)
    printf ("Could not add xdr functions\n");

  // Create and subscribe to a device using the interface.
  device = boundary_interf_create(client, 0);
  if (boundary_interf_subscribe(device, PLAYER_OPEN_MODE) != 0)	{
    printf ("Could not subscribe\n");
    return -1;
  }

  while (true) {
    playerc_client_read (client);
    printf("Value: %f\tVector: (%f,%f)\n", device->value, device->x_comp, device->y_comp);
    
    playerc_planner_set_cmd_pose(pla, position->px + device->x_comp * scale, position->py + device->y_comp * scale, 0);
  }

  // Shutdown
  boundary_interf_unsubscribe(device);
  boundary_interf_destroy(device);
  playerc_client_disconnect(client);
  playerc_client_destroy(client);
  
  return 0;
}
