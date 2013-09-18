/*
 *  libplayerc : a Player client library
 *  Copyright (C) Andrew Howard 2002-2003
 *
 *  This program is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU General Public License
 *  as published by the Free Software Foundation; either version 2
 *  of the License, or (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA.
 *
 */
/*
 *  Player - One Hell of a Robot Server
 *  Copyright (C) Andrew Howard 2003
 *
 *
 *  This library is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU Lesser General Public
 *  License as published by the Free Software Foundation; either
 *  version 2.1 of the License, or (at your option) any later version.
 *
 *  This library is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  Lesser General Public License for more details.
 *
 *  You should have received a copy of the GNU Lesser General Public
 *  License along with this library; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
 */
/***************************************************************************
 * Desc: Time device proxy
 * Author: Andrew Howard
 * Date: 26 May 2002
 * CVS: $Id: dev_time.c 9120 2013-01-07 00:18:52Z jpgr87 $
 **************************************************************************/

#include <assert.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#include "playerc.h"
#include "error.h"

// Local declarations
void playerc_time_putmsg(playerc_time_t *device,
                               player_msghdr_t *header,
                               void *data, size_t len);

// Create a new time proxy
playerc_time_t *playerc_time_create(playerc_client_t *client, int index)
{
  playerc_time_t *device;

  device = malloc(sizeof(playerc_time_t));
  memset(device, 0, sizeof(playerc_time_t));
  playerc_device_init(&device->info, client, PLAYER_TIME_CODE, index,
                      (playerc_putmsg_fn_t) playerc_time_putmsg);

  return device;
}


// Destroy a time proxy
void playerc_time_destroy(playerc_time_t *device)
{
  playerc_device_term(&device->info);
  free(device);
}


// Subscribe to the time device
int playerc_time_subscribe(playerc_time_t *device, int access)
{
  return playerc_device_subscribe(&device->info, access);
}


// Un-subscribe from the time device
int playerc_time_unsubscribe(playerc_time_t *device)
{
  return playerc_device_unsubscribe(&device->info);
}

// Get the current time (in cycles)
int playerc_time_get_time(playerc_time_t *device)
{
  player_time_time_req_t *request;

  if(playerc_client_request(device->info.client,
			    &device->info,
			    PLAYER_TIME_REQ_GET_TIME,
			    NULL, (void**)&request) < 0)
    return -1;

  device->time = request->time;
  return 0;
}

// Process incoming data
void playerc_time_putmsg(playerc_time_t *device,
                               player_msghdr_t *header,
                               void *data, size_t len)
{
  PLAYERC_WARN2("skipping time message with unknown type/subtype: %s/%d\n",
		msgtype_to_str(header->type), header->subtype);
  return;
}

