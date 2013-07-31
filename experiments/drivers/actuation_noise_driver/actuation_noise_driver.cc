/*
 * Actuation Noise driver.
 * 
 * An adapter that adds noise to position2d velocity command messages.
 * Meant to be placed between the stage position2d device and the local navigator (vfh, art_pot).
 */

#include <unistd.h>
#include <string.h>
#include <math.h>

#include <libplayercore/playercore.h>
#include "../noise.h"

////////////////////////////////////////////////////////////////////////////////
// The class for the driver
class ActuationNoiseDriver : public ThreadedDriver
{
public:
    
  // Constructor; need that
  ActuationNoiseDriver(ConfigFile* cf, int section);

  // This method will be invoked on each incoming message
  virtual int ProcessMessage(QueuePointer &resp_queue, 
			     player_msghdr * hdr,
			     void * data);
  
private:
  // Main function for device thread.
  virtual void Main();
  virtual int MainSetup();
  virtual void MainQuit();
  
  double noise_scale;

  // Set up the underlying odometry device
  int SetupOdom();
  int ShutdownOdom();
  void ProcessOdom(player_msghdr_t* hdr, player_position2d_data_t &data);

  void DoOneUpdate();
  
  // Commands for the position device
  void PutCommand(player_position2d_cmd_vel_t &);
  void PutCommand( double speed, double turnrate );

  // Devices provided
  player_devaddr_t position_id;

  // Required Odometry Device info
  Device *odom;
  player_devaddr_t odom_addr;

  double odom_pose[3];
  double odom_vel[3];
  int odom_stall;

  // Control velocity
  double con_vel[3];
};

// A factory creation function, declared outside of the class so that it
// can be invoked without any object context (alternatively, you can
// declare it static in the class).  In this function, we create and return
// (as a generic Driver*) a pointer to a new instance of this driver.
Driver* 
ActuationNoiseDriver_Init(ConfigFile* cf, int section)
{
  // Create and return a new instance of this driver
  return((Driver*)(new ActuationNoiseDriver(cf, section)));
}

// A driver registration function, again declared outside of the class so
// that it can be invoked without object context.  In this function, we add
// the driver into the given driver table, indicating which interface the
// driver can support and how to create a driver instance.
void ActuationNoiseDriver_Register(DriverTable* table)
{
  table->AddDriver("actuationnoisedriver", ActuationNoiseDriver_Init);
}

////////////////////////////////////////////////////////////////////////////////
// Constructor.  Retrieve options from the configuration file and do any
// pre-Setup() setup.
ActuationNoiseDriver::ActuationNoiseDriver(ConfigFile* cf, int section)
  : ThreadedDriver(cf, section)
{
  // Check for position2d (we provide)
  memset(&(this->position_id), 0, sizeof(player_devaddr_t));
  if (cf->ReadDeviceAddr(&(this->position_id), section, "provides",
			 PLAYER_POSITION2D_CODE, -1, NULL) == 0) {
    if (this->AddInterface(this->position_id) != 0) {
      this->SetError(-1);
      return;
    }
  }

  // Check for position2d (we require)
  this->odom = NULL;
  // TODO: No memset for the odom? -jcm
  if (cf->ReadDeviceAddr(&(this->odom_addr), section, "requires",
			 PLAYER_POSITION2D_CODE, -1, NULL) != 0) {
    PLAYER_ERROR("Could not find required position2d device!");
    this->SetError(-1);
    return;
  }

  // Read an option from the configuration file
  this->noise_scale = cf->ReadFloat(section, "noise_scale", 1.0);

  return;
}

////////////////////////////////////////////////////////////////////////////////
// Set up the device.  Return 0 if things go well, and -1 otherwise.
int ActuationNoiseDriver::MainSetup()
{   
  puts("Actuation Noise driver initialising");

  // Initialize the position device we are reading from
  if (this->SetupOdom() != 0)
    return -1;

  puts("Actuation Noise driver ready");

  return(0);
}

////////////////////////////////////////////////////////////////////////////////
// Shutdown the device
void ActuationNoiseDriver::MainQuit()
{
  puts("Shutting Actuation Noise driver down... shutdown complete");
}

////////////////////////////////////////////////////////////////////////////////
// Incoming message!
int ActuationNoiseDriver::ProcessMessage(QueuePointer & resp_queue, 
                                  player_msghdr * hdr,
                                  void * data)
{
  if(Message::MatchMessage(hdr, PLAYER_MSGTYPE_DATA,
			   PLAYER_POSITION2D_DATA_STATE, this->odom_addr)) {
    // Underlying device has updated its odometry information
    assert(hdr->size == sizeof(player_position2d_data_t));
    ProcessOdom(hdr, *reinterpret_cast<player_position2d_data_t *> (data));
    return 0;
  } else if(Message::MatchMessage(hdr, PLAYER_MSGTYPE_CMD,
                                PLAYER_POSITION2D_CMD_VEL,
                                this->position_id)) {
    assert(hdr->size == sizeof(player_position2d_cmd_vel_t));

    
    
    PutCommand(*reinterpret_cast<player_position2d_cmd_vel_t *> (data));
    return 0;
  } else if(Message::MatchMessage(hdr, PLAYER_MSGTYPE_REQ, -1, this->position_id)) {
    // Pass the request on to the underlying position device and wait for
    // the reply.
    Message* msg;

    if(!(msg = this->odom->Request(this->InQueue,
                                   hdr->type,
                                   hdr->subtype,
                                   (void*)data,
                                   hdr->size,
				   &hdr->timestamp))) {
      PLAYER_WARN1("failed to forward config request with subtype: %d\n",
                   hdr->subtype);
      return(-1);
    } 

    player_msghdr_t* rephdr = msg->GetHeader();
    void* repdata = msg->GetPayload();
    // Copy in our address and forward the response
    rephdr->addr = this->position_id;
    this->Publish(resp_queue, rephdr, repdata);
    delete msg;
    return(0);
  } else {
    return -1;
  }
}



////////////////////////////////////////////////////////////////////////////////
// Main function for device thread
void ActuationNoiseDriver::Main() 
{
  // The main loop; interact with the device here
  for(;;)
  {
    // test if we are supposed to cancel
    this->Wait();
    pthread_testcancel();
    this->DoOneUpdate();
    // Sleep (you might, for example, block on a read() instead)
    //usleep(100000);

  }
}

void ActuationNoiseDriver::DoOneUpdate() {
  if (this->InQueue->Empty()) {
    return;
  }

  this->ProcessMessages();
}


////////////////////////////////////////////////////////////////////////////////
// Extra stuff for building a shared object.

/* need the extern to avoid C++ name-mangling  */
extern "C" {
  int player_driver_init(DriverTable* table)
  {
    puts("Actuation Noise driver initializing");
    ActuationNoiseDriver_Register(table);
    puts("Actuation Noise driver done");
    return(0);
  }
}

////////////////////////////////////////////////////////////////////////////////
// Shutdown the underlying odom device.
int ActuationNoiseDriver::ShutdownOdom()
{

  // Stop the robot before unsubscribing
  this->PutCommand(0,0);

  this->odom->Unsubscribe(this->InQueue);
  return 0;
}

////////////////////////////////////////////////////////////////////////////////
// Set up the underlying odom device.
int ActuationNoiseDriver::SetupOdom()
{
  if(!(this->odom = deviceTable->GetDevice(this->odom_addr)))
  {
    PLAYER_ERROR("unable to locate suitable position device");
    return -1;
  }
  if(this->odom->Subscribe(this->InQueue) != 0)
  {
    PLAYER_ERROR("unable to subscribe to position device");
    return -1;
  }

  this->odom_pose[0] = this->odom_pose[1] = this->odom_pose[2] = 0.0;
  this->odom_vel[0] = this->odom_vel[1] = this->odom_vel[2] = 0.0;

  return 0;
}

////////////////////////////////////////////////////////////////////////////////
// Process new odometry data
void ActuationNoiseDriver::ProcessOdom(player_msghdr_t* hdr, player_position2d_data_t &data)
{

  // Cache the new odometric pose, velocity, and stall info
  // NOTE: this->odom_pose is in (mm,mm,deg), as doubles
  this->odom_pose[0] = data.pos.px; // * 1e3;
  this->odom_pose[1] = data.pos.py; // * 1e3;
  this->odom_pose[2] = data.pos.pa; //RTOD(data.pos.pa);
  this->odom_vel[0] = data.vel.px; // * 1e3;
  this->odom_vel[1] = data.vel.py; // * 1e3;
  this->odom_vel[2] = data.vel.pa; //RTOD(data.vel.pa);
  this->odom_stall = data.stall;

  // Also change this info out for use by others
  player_msghdr_t newhdr = *hdr;
  newhdr.addr = this->position_id;
  this->Publish(&newhdr, (void*)&data);
}

void ActuationNoiseDriver::PutCommand(player_position2d_cmd_vel_t &data)
{
  PutCommand(data.vel.px, data.vel.pa);
}

////////////////////////////////////////////////////////////////////////////////
// Send commands to underlying position device
void ActuationNoiseDriver::PutCommand(double cmd_speed, double cmd_turnrate)
{
  player_position2d_cmd_vel_t cmd;
  memset(&cmd, 0, sizeof(cmd));

  if (cmd_speed == 0 && cmd_turnrate == 0) {
    cmd.vel.px = 0;
    cmd.vel.py = 0;
    cmd.vel.pa = 0;
  } else {
    cmd.vel.px = cmd_speed + Noise_Get_Normalized(this->noise_scale);
    cmd.vel.py = 0;
    cmd.vel.pa = cmd_turnrate + Noise_Get_Normalized(this->noise_scale / 2.0);
  }
  
  this->odom->PutMsg(this->InQueue,
		     PLAYER_MSGTYPE_CMD,
		     PLAYER_POSITION2D_CMD_VEL,
		     (void*)&cmd, sizeof(cmd), NULL);
}
