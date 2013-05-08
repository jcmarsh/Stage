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
 * boundary_interf_client.h.
 *
 * boundary_interf_create      Creates a proxy for the interface
 * boundary_interf_destroy     Destroys a proxy for the interface
 * boundary_interf_subscribe   Subscribes to a device that provides the interface
 * boundary_interf_unsubscribe Unsubscribes from a subscribed device
 * boundary_interf_putmsg      Called by the client library whenever a data
 *                             message is received for this proxy
 */

#include <string.h>
#include <stdlib.h>
#include <libplayerc/playerc.h>
#include <libplayercommon/playercommon.h>

#include "boundary_interface.h"
#include "boundary_xdr.h"
#include "boundary_interf_client.h"

void boundary_interf_putmsg (boundary_interf_t *device, player_msghdr_t *header, uint8_t *data, size_t len);

boundary_interf_t *boundary_interf_create (playerc_client_t *client, int index)
{
	boundary_interf_t *device;

	device = (boundary_interf_t*) malloc (sizeof (boundary_interf_t));
	memset (device, 0, sizeof (boundary_interf_t));
	playerc_device_init (&device->info, client, PLAYER_BOUNDARY_CODE, index, (playerc_putmsg_fn_t) boundary_interf_putmsg);

	device->reading = 0;
	return device;
}

void boundary_interf_destroy (boundary_interf_t *device)
{
	playerc_device_term (&device->info);
	//if (device->stuff != NULL)
	//	free (device->stuff);
	free (device);
}

int boundary_interf_subscribe (boundary_interf_t *device, int access)
{
	return playerc_device_subscribe (&device->info, access);
}

int boundary_interf_unsubscribe (boundary_interf_t *device)
{
	return playerc_device_unsubscribe (&device->info);
}

void boundary_interf_putmsg (boundary_interf_t *device, player_msghdr_t *header, uint8_t *data, size_t len)
{
	if((header->type == PLAYER_MSGTYPE_DATA) && (header->subtype == PLAYER_BOUNDARY_DATA_READING))
	{
	  printf("Recieved known message type\n");
	  player_boundary_interf_data_t *stuffData = (player_boundary_interf_data_t *) data;
	  assert(header->size > 0);

	  device->reading = stuffData->reading;
	}
	else
	  printf ("skipping boundary_interf message with unknown type/subtype: %s/%d\n", msgtype_to_str(header->type), header->subtype);
}

