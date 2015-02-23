/*
 * Send driver. Just sends the current time
 */

#include <unistd.h>
#include <string.h>
#include <math.h>

#include <libplayercore/playercore.h>

#define rdtscll(value)                                 \
  __asm__ ("rdtsc\n\t"                                 \
           "shl $(32), %%rdx\n\t"                      \
           "or %%rax, %%rdx" : "=d" (value) : : "rax")


//////////////////////////////////////////////////////////////////////////////
// The class for the driver
class TimeDriver : public ThreadedDriver
{
public:
    
  // Constructor; need that
  TimeDriver(ConfigFile* cf, int section);

  // This method will be invoked on each incoming message
  virtual int ProcessMessage(QueuePointer &resp_queue, 
			     player_msghdr * hdr,
			     void * data);
  
private:
  // Main function for device thread.
  virtual void Main();
  virtual int MainSetup();
  virtual void MainQuit();
  
  // Set up the underlying odometry device
  int SetupOdom();
  int ShutdownOdom();
  
  void DoOneUpdate();

  // Devices provided
  player_devaddr_t time_id;
  player_time_time_req_t time_req;

  long time;
};

// A factory creation function, declared outside of the class so that it
// can be invoked without any object context (alternatively, you can
// declare it static in the class).  In this function, we create and return
// (as a generic Driver*) a pointer to a new instance of this driver.
Driver* 
TimeDriver_Init(ConfigFile* cf, int section)
{
  // Create and return a new instance of this driver
  return((Driver*)(new TimeDriver(cf, section)));
}

// A driver registration function, again declared outside of the class so
// that it can be invoked without object context.  In this function, we add
// the driver into the given driver table, indicating which interface the
// driver can support and how to create a driver instance.
void TimeDriver_Register(DriverTable* table)
{
  table->AddDriver("timedriver", TimeDriver_Init);
}

////////////////////////////////////////////////////////////////////////////////
// Constructor.  Retrieve options from the configuration file and do any
// pre-Setup() setup.
TimeDriver::TimeDriver(ConfigFile* cf, int section)
  : ThreadedDriver(cf, section)
{
  // Check for position2d (we provide)
  memset(&(this->time_id), 0, sizeof(player_devaddr_t));
  if (cf->ReadDeviceAddr(&(this->time_id), section, "provides",
			 PLAYER_TIME_CODE, -1, NULL) == 0) {
    if (this->AddInterface(this->time_id) != 0) {
      this->SetError(-1);
      return;
    }
  }

  return;
}

////////////////////////////////////////////////////////////////////////////////
// Set up the device.  Return 0 if things go well, and -1 otherwise.
int TimeDriver::MainSetup()
{   
  puts("Time driver initialising");
  
  puts("Time driver ready");

  return(0);
}

////////////////////////////////////////////////////////////////////////////////
// Shutdown the device
void TimeDriver::MainQuit()
{
  puts("Shutting Time driver down... Nothing to do... shut down.");
}

////////////////////////////////////////////////////////////////////////////////
// Incoming Message!
int TimeDriver::ProcessMessage(QueuePointer & resp_queue,
			       player_msghdr * hdr,
			       void * data)
{
  unsigned long t;
  if (Message::MatchMessage(hdr, PLAYER_MSGTYPE_REQ,
			    PLAYER_TIME_REQ_GET_TIME,
			    this->time_id)) {

    player_time_time_req_t req_time;
    rdtscll(t);
    req_time.time = t;

    printf("TIME HAS BEEN REQUESTED!!!!\n");

    this->Publish(this->time_id, resp_queue,
		  PLAYER_MSGTYPE_RESP_ACK,
		  PLAYER_TIME_REQ_GET_TIME,
		  (void*)&req_time, sizeof(req_time), NULL);
    return 0;
  }
}

////////////////////////////////////////////////////////////////////////////////
// Main function for device thread
void TimeDriver::Main() 
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

void TimeDriver::DoOneUpdate() {
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
    puts("Time driver initializing");
    TimeDriver_Register(table);
    puts("Time driver done");
    return(0);
  }
}


