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
 * This file implements a driver using the pluggable interface. See the plugin
 * driver example for details of how it works.
 */

#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <libplayercore/playercore.h>

#include "boundary_interface.h"

////////////////////////////////////////////////////////////////////////////////
// The class for the driver
class BoundaryInterfDriver : public Driver
{
public:

  // Constructor; need that
  BoundaryInterfDriver(ConfigFile* cf, int section);
  
  // Must implement the following methods.
  virtual int Setup();
  virtual int Shutdown();

  // This method will be invoked on each incoming message
  virtual int ProcessMessage(QueuePointer & resp_queue, player_msghdr * hdr, void * data);

private:
  int SetupOdom();
  int ShutdownOdom();
  void ProcessOdom(player_msghdr_t* hdr, player_position2d_data_t &data);

  // Device provided (boundary)
  player_devaddr_t boundary_id;
  //  player_boundary_t boundary_data;

  // Device required (position2d)
  Device *odom;
  player_devaddr_t odom_addr;
  double odom_pose[3];
};

// A factory creation function, declared outside of the class so that it
// can be invoked without any object context (alternatively, you can
// declare it static in the class).  In this function, we create and return
// (as a generic Driver*) a pointer to a new instance of this driver.
Driver* BoundaryInterfDriver_Init(ConfigFile* cf, int section)
{
	// Create and return a new instance of this driver
	return((Driver*)(new BoundaryInterfDriver(cf, section)));
}

// A driver registration function, again declared outside of the class so
// that it can be invoked without object context.  In this function, we add
// the driver into the given driver table, indicating which interface the
// driver can support and how to create a driver instance.
void BoundaryInterfDriver_Register(DriverTable* table)
{
	table->AddDriver("boundaryinterfdriver", BoundaryInterfDriver_Init);
}

////////////////////////////////////////////////////////////////////////////////
// Constructor.  Retrieve options from the configuration file and do any
// pre-Setup() setup.
BoundaryInterfDriver::BoundaryInterfDriver(ConfigFile* cf, int section)
  : Driver(cf, section)
{
  // Check for boundary interface (we provide)
  memset(&(this->boundary_id), 0, sizeof(player_devaddr_t));
  if (cf->ReadDeviceAddr(&(this->boundary_id), section, "provides",
			 PLAYER_BOUNDARY_CODE, -1, NULL) == 0) {
    if (this->AddInterface(this->boundary_id) != 0) {
      this->SetError(-1);
      return;
    }
  }

  // Check for position2d (we requrie)
  this->odom = NULL;
  if (cf->ReadDeviceAddr(&(this->odom_addr), section, "requires",
			 PLAYER_POSITION2D_CODE, -1, NULL) != 0) {
    PLAYER_ERROR("Could not find required position2d device!");
    this->SetError(-1);
    return;
  }

  return;
}

////////////////////////////////////////////////////////////////////////////////
// Set up the device.  Return 0 if things go well, and -1 otherwise.
int BoundaryInterfDriver::Setup()
{
	puts("BoundaryInterfDriver initialising");

	if (this->SetupOdom() != 0)
	  return -1;

	puts("BoundaryInterfDriver ready");

	return(0);
}


////////////////////////////////////////////////////////////////////////////////
// Shutdown the device
int BoundaryInterfDriver::Shutdown()
{
	puts("Shutting BoundaryInterfDriver down");

	puts("BoundaryInterfDriver has been shutdown");

	return(0);
}

int BoundaryInterfDriver::ProcessMessage(QueuePointer &resp_queue, player_msghdr * hdr, void * data)
{
	player_boundary_interf_data resp;

	if (Message::MatchMessage (hdr, PLAYER_MSGTYPE_DATA, PLAYER_POSITION2D_DATA_STATE, this->odom_addr)) {
	  assert(hdr->size == sizeof(player_position2d_data_t));
	  ProcessOdom(hdr, *reinterpret_cast<player_position2d_data_t *> (data));

	  resp.reading = 42.42;
	  printf ("BoundaryInterfDriver: publishing message: %f\n", resp.reading);
	  Publish (device_addr,  PLAYER_MSGTYPE_DATA, PLAYER_BOUNDARY_DATA_READING, &resp, sizeof (resp), NULL);
	  return 0;
	}
	
	return(-1);
}

////////////////////////////////////////////////////////////////////////////////
// Extra stuff for building a shared object.

extern "C" {
	int player_driver_init(DriverTable* table)
	{
		puts("BoundaryInterfDriver initializing");
		BoundaryInterfDriver_Register(table);
		puts("BoundaryInterfDriver done");
		return(0);
	}
}

int BoundaryInterfDriver::ShutdownOdom() {
  this->odom->Unsubscribe(this->InQueue);
  return 0;
}

int BoundaryInterfDriver::SetupOdom() {
  if (!(this->odom = deviceTable->GetDevice(this->odom_addr))) {
    PLAYER_ERROR("unable to locate suitable position device");
    return -1;
  }
  if (this->odom->Subscribe(this->InQueue) != 0) {
    PLAYER_ERROR("unable to subscribe to position device");
    return -1;
  }

  this->odom_pose[0] = this->odom_pose[1] = this->odom_pose[2] = 0.0;
  return 0;
}

void BoundaryInterfDriver::ProcessOdom(player_msghdr_t* hdr, player_position2d_data_t &data) {
  this->odom_pose[0] = data.pos.px;
  this->odom_pose[1] = data.pos.py;
  this->odom_pose[2] = data.pos.pa;
}

