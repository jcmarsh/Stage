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

#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <libplayercore/playercore.h>

#include "smrtln_interface.h"

////////////////////////////////////////////////////////////////////////////////
// The class for the driver
class SmrtLNInterfDriver : public Driver
{
public:

  // Constructor; need that
  SmrtLNInterfDriver(ConfigFile* cf, int section);

  // Must implement the following methods.
  virtual int Setup();
  virtual int Shutdown();

  // This method will be invoked on each incoming message
  virtual int ProcessMessage(QueuePointer & resp_queue, player_msghdr * hdr, void * data);
};

// A factory creation function, declared outside of the class so that it
// can be invoked without any object context (alternatively, you can
// declare it static in the class).  In this function, we create and return
// (as a generic Driver*) a pointer to a new instance of this driver.
Driver* SmrtLNInterfDriver_Init(ConfigFile* cf, int section)
{
  // Create and return a new instance of this driver
  return((Driver*)(new SmrtLNInterfDriver(cf, section)));
}

// A driver registration function, again declared outside of the class so
// that it can be invoked without object context.  In this function, we add
// the driver into the given driver table, indicating which interface the
// driver can support and how to create a driver instance.
void SmrtLNInterfDriver_Register(DriverTable* table)
{
  table->AddDriver("smrtlninterfdriver", SmrtLNInterfDriver_Init);
}

////////////////////////////////////////////////////////////////////////////////
// Constructor.  Retrieve options from the configuration file and do any
// pre-Setup() setup.
SmrtLNInterfDriver::SmrtLNInterfDriver(ConfigFile* cf, int section)
    : Driver(cf, section, false, PLAYER_MSGQUEUE_DEFAULT_MAXLEN, PLAYER_SMRTLN_CODE)
{
  return;
}

////////////////////////////////////////////////////////////////////////////////
// Set up the device.  Return 0 if things go well, and -1 otherwise.
int SmrtLNInterfDriver::Setup()
{
  puts("SmrtLNInterfDriver initialising");
  
  srand (static_cast<unsigned int> (time (NULL)));
  
  puts("SmrtLNInterfDriver ready");

  return(0);
}


////////////////////////////////////////////////////////////////////////////////
// Shutdown the device
int SmrtLNInterfDriver::Shutdown()
{
  puts("Shutting SmrtLNInterfDriver down");

  puts("SmrtLNInterfDriver has been shutdown");

  return(0);
}

int SmrtLNInterfDriver::ProcessMessage(QueuePointer &resp_queue, player_msghdr * hdr, void * data)
{
  if (Message::MatchMessage (hdr, PLAYER_MSGTYPE_CMD, PLAYER_SMRTLN_CMD_SET_PARAM, device_addr)) {
    printf ("SmrtLNInterfDriver: Received PARAM command: %d-%f\n", reinterpret_cast<player_smrtlninterf_param_cmd*> (data)->param_index, reinterpret_cast<player_smrtlninterf_param_cmd_t*> (data)->param_value);
    return 0;
  } else if (Message::MatchMessage (hdr, PLAYER_MSGTYPE_CMD, PLAYER_SMRTLN_CMD_SUPPRESS_SENSOR, device_addr)) {
    printf ("SmrtLNInterfDriver: Received SENSOR command: %d-%d\n", reinterpret_cast<player_smrtlninterf_supsensor_cmd_t*> (data)->sensor_index, reinterpret_cast<player_smrtlninterf_supsensor_cmd_t*> (data)->state);
    return 0;
  }

  printf ("What the bloody hell is going on here? Who is sending these messages???\n");
  return(-1);
}

////////////////////////////////////////////////////////////////////////////////
// Extra stuff for building a shared object.

extern "C" {
  int player_driver_init(DriverTable* table) {
    puts("SmrtLNInterfDriver initializing");
    SmrtLNInterfDriver_Register(table);
    puts("SmrtLNInterfDriver done");
    return(0);
  }
}

