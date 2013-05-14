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
  // Hank
  playerc_client_t *client_h;
  playerc_position2d_t *position_h;
  playerc_planner_t *pla_h;
  boundary_interf_t *device_h;

  // Frank
  playerc_client_t *client_f;
  playerc_position2d_t *position_f;
  playerc_planner_t *pla_f;
  boundary_interf_t *device_f;

  // Samantha
  playerc_client_t *client_s;
  playerc_position2d_t *position_s;
  playerc_planner_t *pla_s;
  boundary_interf_t *device_s;

  double threshold = -40.0;
  double epsilon = 5.0;
  
  // Create a client and connect it to the server.
  client_h = playerc_client_create(NULL, "localhost", 6665);
  if (0 != playerc_client_connect(client_h)) {
    printf ("Could not connect\n");
    return -1;
  }

  position_h = playerc_position2d_create(client_h, 0);
  if (playerc_position2d_subscribe(position_h, PLAYER_OPEN_MODE)) {
    return -1;
  }

  pla_h = playerc_planner_create(client_h, 0);
  if (playerc_planner_subscribe(pla_h, PLAYER_OPEN_MODE)) {
    return -1;
  }

  // Load the plugin interface
  if (playerc_add_xdr_ftable (player_plugininterf_gettable (), 0) < 0)
    printf ("Could not add xdr functions\n");

  // Create and subscribe to a device using the interface.
  device_h = boundary_interf_create(client_h, 0);
  if (boundary_interf_subscribe(device_h, PLAYER_OPEN_MODE) != 0)	{
    printf ("Could not subscribe\n");
    return -1;
  }
  printf("Hank is done initializing.\n");

  /////////////////////////////////////////////////
  // Create a client and connect it to the server.
  client_f = playerc_client_create(NULL, "localhost", 6666);
  if (0 != playerc_client_connect(client_f)) {
    printf ("Could not connect\n");
    return -1;
  }

  position_f = playerc_position2d_create(client_f, 0);
  if (playerc_position2d_subscribe(position_f, PLAYER_OPEN_MODE)) {
    return -1;
  }


  pla_f = playerc_planner_create(client_f, 0);
  if (playerc_planner_subscribe(pla_f, PLAYER_OPEN_MODE)) {
    return -1;
  }

  // Create and subscribe to a device using the interface.
  device_f = boundary_interf_create(client_f, 0);
  if (boundary_interf_subscribe(device_f, PLAYER_OPEN_MODE) != 0)	{
    printf ("Could not subscribe\n");
    return -1;
  }
  printf("Frank is done initializing.\n");

  /////////////////////////////////////////////////////////////
  // Create a client and connect it to the server.
  client_s = playerc_client_create(NULL, "localhost", 6667);
  if (0 != playerc_client_connect(client_s)) {
    printf ("Could not connect\n");
    return -1;
  }

  position_s = playerc_position2d_create(client_s, 0);
  if (playerc_position2d_subscribe(position_s, PLAYER_OPEN_MODE)) {
    return -1;
  }


  pla_s = playerc_planner_create(client_s, 0);
  if (playerc_planner_subscribe(pla_s, PLAYER_OPEN_MODE)) {
    return -1;
  }

  // Create and subscribe to a device using the interface.
  device_s = boundary_interf_create(client_s, 0);
  if (boundary_interf_subscribe(device_s, PLAYER_OPEN_MODE) != 0)	{
    printf ("Could not subscribe\n");
    return -1;
  }
  printf("Samantha is done initializing.\n");

  while (true) {
    playerc_client_read (client_h);
    if (device_h->value < threshold - epsilon) {
      playerc_planner_set_cmd_pose(pla_h, position_h->px + device_h->x_comp * scale, position_h->py + device_h->y_comp * scale, 0);
    } else if (device_h->value > threshold + epsilon) {
      playerc_planner_set_cmd_pose(pla_h, position_h->px - device_h->x_comp * scale, position_h->py - device_h->y_comp * scale, 0);
    } else {
      playerc_planner_set_cmd_pose(pla_h, position_h->px, position_h->py, 0);
    }

    playerc_client_read (client_f);    
    if (device_f->value < threshold - epsilon) {
      playerc_planner_set_cmd_pose(pla_f, position_f->px + device_f->x_comp * scale, position_f->py + device_f->y_comp * scale, 0);
    } else if (device_f->value > threshold + epsilon) {
      playerc_planner_set_cmd_pose(pla_f, position_f->px - device_f->x_comp * scale, position_f->py - device_f->y_comp * scale, 0);
    } else {
      playerc_planner_set_cmd_pose(pla_f, position_f->px, position_f->py, 0);
    }

    playerc_client_read (client_s);
    if (device_s->value < threshold - epsilon) {
      playerc_planner_set_cmd_pose(pla_s, position_s->px + device_s->x_comp * scale, position_s->py + device_s->y_comp * scale, 0);
    } else if (device_s->value > threshold + epsilon) {
      playerc_planner_set_cmd_pose(pla_s, position_s->px - device_s->x_comp * scale, position_s->py - device_s->y_comp * scale, 0);
    } else {
      playerc_planner_set_cmd_pose(pla_s, position_s->px, position_s->py, 0);
    }

  }
  return 0;
}
