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
 * This file implements a C client proxy for the interface defined in
 * eginterf_client.h. The following functions are essential, others depend on
 * the design of your interface:
 *
 * eginterf_create      Creates a proxy for the interface
 * eginterf_destroy     Destroys a proxy for the interface
 * eginterf_subscribe   Subscribes to a device that provides the interface
 * eginterf_unsubscribe Unsubscribes from a subscribed device
 * eginterf_putmsg      Called by the client library whenever there a data
 *                      message is received for this proxy
 */

#include <string.h>
#include <stdlib.h>

#include "playerc.h"

void playerc_smrtln_putmsg(playerc_smrtln_t *device,
			   player_msghdr_t *header,
			   uint8_t *data, size_t len); // TODO: check data

playerc_smrtln_t *playerc_smrtln_create(playerc_client_t *client, int index)
{
  playerc_smrtln_t *device;

  device = malloc(sizeof(playerc_smrtln_t));
  memset(device, 0, sizeof(playerc_smrtln_t));
  playerc_device_init(&device->info, client, PLAYER_SMRTLN_CODE, index, 
		       (playerc_putmsg_fn_t) playerc_smrtln_putmsg);
  return device;
}

void playerc_smrtln_destroy(playerc_smrtln_t *device)
{
  playerc_device_term(&device->info);
  free(device);
}

int playerc_smrtln_subscribe(playerc_smrtln_t *device, int access)
{
  return playerc_device_subscribe(&device->info, access);
}

int playerc_smrtln_unsubscribe(playerc_smrtln_t *device)
{
  return playerc_device_unsubscribe(&device->info);
}

void playerc_smrtln_putmsg(playerc_smrtln_t *device, player_msghdr_t *header, uint8_t *data, size_t len)
{
  printf("skipping playerc_smrtln message with unknown type/subtype: %s/%d\n", msgtype_to_str(header->type), header->subtype);
}

int playerc_smrtln_set_param(playerc_smrtln_t *device, int index, double value)
{
  player_smrtln_param_cmd_t cmd;
  memset(&cmd, 0, sizeof(player_smrtln_param_cmd_t));
  cmd.param_index = index;
  cmd.param_value = value;

  return playerc_client_write(device->info.client, &device->info, PLAYER_SMRTLN_CMD_SET_PARAM, &cmd, NULL);
}

int playerc_smrtln_sup_sensor(playerc_smrtln_t *device, int index, int state)
{
  player_smrtln_supsensor_cmd_t cmd;
  memset(&cmd, 0, sizeof (player_smrtln_supsensor_cmd_t));
  cmd.sensor_index = index;
  cmd.state = state;

  return playerc_client_write(device->info.client, &device->info, PLAYER_SMRTLN_CMD_SUPPRESS_SENSOR, &cmd, NULL);
}
