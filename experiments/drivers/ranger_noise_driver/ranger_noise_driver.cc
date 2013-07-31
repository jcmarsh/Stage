/*
 * Ranger Noise driver.
 * 
 * Simply an adapter from a ranger device to a noisy one.
 * BUT, using the laser interface, since that is what ranger gets converted to anyways.
 */

#include <unistd.h>
#include <string.h>
#include <math.h>

#include <libplayercore/playercore.h>
#include "../noise.h"

////////////////////////////////////////////////////////////////////////////////
// The class for the driver
class RangerNoiseDriver : public ThreadedDriver
{
public:
    
  // Constructor; need that
  RangerNoiseDriver(ConfigFile* cf, int section);

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

  // Setup incoming laser
  int SetupLaser();
  int ShutdownLaser();
  void ProcessLaser(player_laser_data_t &);
  
  void DoOneUpdate();

  // Check for new commands
  void ProcessCommand(player_msghdr_t* hdr, player_position2d_cmd_pos_t &);

  // Devices provided
  player_devaddr_t laser_out_id;
  // TODO: Laser data type?  player_planner_data_t planner_data;

  // Required devices (laser)
  // Laser Device info
  Device *laser;
  player_devaddr_t laser_addr;
  int laser_count;
  double laser_ranges[361];
};

// A factory creation function, declared outside of the class so that it
// can be invoked without any object context (alternatively, you can
// declare it static in the class).  In this function, we create and return
// (as a generic Driver*) a pointer to a new instance of this driver.
Driver* 
RangerNoiseDriver_Init(ConfigFile* cf, int section)
{
  // Create and return a new instance of this driver
  return((Driver*)(new RangerNoiseDriver(cf, section)));
}

// A driver registration function, again declared outside of the class so
// that it can be invoked without object context.  In this function, we add
// the driver into the given driver table, indicating which interface the
// driver can support and how to create a driver instance.
void RangerNoiseDriver_Register(DriverTable* table)
{
  table->AddDriver("rangernoisedriver", RangerNoiseDriver_Init);
}

////////////////////////////////////////////////////////////////////////////////
// Constructor.  Retrieve options from the configuration file and do any
// pre-Setup() setup.
RangerNoiseDriver::RangerNoiseDriver(ConfigFile* cf, int section)
  : ThreadedDriver(cf, section)
{
  // Check for position2d (we provide)
  memset(&(this->laser_out_id), 0, sizeof(player_devaddr_t));
  if (cf->ReadDeviceAddr(&(this->laser_out_id), section, "provides",
			 PLAYER_LASER_CODE, -1, NULL) == 0) {
    if (this->AddInterface(this->laser_out_id) != 0) {
      this->SetError(-1);
      return;
    }
  }

  // The laser we provide
  this->laser = NULL;
  memset(&(this->laser_addr), 0, sizeof(player_devaddr_t));
  if (cf->ReadDeviceAddr(&(this->laser_addr), section, "requires",
			 PLAYER_LASER_CODE, -1, NULL) != 0) {
    PLAYER_ERROR("Could not find required laser device!");
    this->SetError(-1);
    return;
  }

  // Read an option from the configuration file
  this->noise_scale = cf->ReadFloat(section, "noise_scale", 1.0);

  return;
}

////////////////////////////////////////////////////////////////////////////////
// Set up the device.  Return 0 if things go well, and -1 otherwise.
int RangerNoiseDriver::MainSetup()
{   
  puts("Ranger Noise driver initialising");

  // Initialize the laser
  if (this->laser_addr.interf && this->SetupLaser() != 0)
    return -1;

  puts("Ranger Noise driver ready");

  return(0);
}

////////////////////////////////////////////////////////////////////////////////
// Shutdown the device
void RangerNoiseDriver::MainQuit()
{
  puts("Shutting Ranger Noise driver down");

  if(this->laser)
    this->ShutdownLaser();

  puts("Ranger Noise driver has been shutdown");
}

////////////////////////////////////////////////////////////////////////////////
// Incoming message!
int RangerNoiseDriver::ProcessMessage(QueuePointer & resp_queue, 
				      player_msghdr * hdr,
				      void * data)
{
  if(Message::MatchMessage(hdr, PLAYER_MSGTYPE_DATA,
			   PLAYER_LASER_DATA_SCAN, this->laser_addr)) {
    ProcessLaser(*reinterpret_cast<player_laser_data_t *> (data)); // TODO: add header here.
    return 0;
  } else {
    return -1;
  }
}

////////////////////////////////////////////////////////////////////////////////
// Main function for device thread
void RangerNoiseDriver::Main() 
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

void RangerNoiseDriver::DoOneUpdate() {
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
    puts("Ranger Noise driver initializing");
    RangerNoiseDriver_Register(table);
    puts("Ranger Noise driver done");
    return(0);
  }
}

////////////////////////////////////////////////////////////////////////////////
// Shut down the laser
int RangerNoiseDriver::ShutdownLaser()
{
  this->laser->Unsubscribe(this->InQueue);
  return 0;
}

////////////////////////////////////////////////////////////////////////////////
// Set up the laser
int RangerNoiseDriver::SetupLaser()
{
  if(!(this->laser = deviceTable->GetDevice(this->laser_addr))) {
    PLAYER_ERROR("unable to locate suitable laser device");
    return -1;
  }
  if (this->laser->Subscribe(this->InQueue) != 0) {
    PLAYER_ERROR("unable to subscribe to laser device");
    return -1;
  }

  this->laser_count = 0;
  //this->laser_ranges = NULL;
  return 0;
}

////////////////////////////////////////////////////////////////////////////////
// Process laser data
void RangerNoiseDriver::ProcessLaser(player_laser_data_t &data)
{
  int i;
  int r;
  double x;

  laser_count = data.ranges_count;
  for (i = 0; i < data.ranges_count; i++) {
    x = Noise_Get_Normalized(this->noise_scale);

    data.ranges[i] = x + data.ranges[i];
  }

  this->Publish(this->laser_out_id, PLAYER_MSGTYPE_DATA, PLAYER_LASER_DATA_SCAN, reinterpret_cast<void *> (&data), sizeof(data), NULL);
}


