/*
 * Artificial Potential driver.
 * 
 * Similar to (and based off of) the Player provided vfh driver
 * shared object.
 */

#if !defined (WIN32) || defined (__MINGW32__)
  #include <unistd.h>
#endif
#include <string.h>

#include <libplayercore/playercore.h>

////////////////////////////////////////////////////////////////////////////////
// The class for the driver
class ArtPotDriver : public ThreadedDriver
{
  public:
    
    // Constructor; need that
    ArtPotDriver(ConfigFile* cf, int section);

    // This method will be invoked on each incoming message
    virtual int ProcessMessage(QueuePointer &resp_queue, 
                               player_msghdr * hdr,
                               void * data);

  private:

    // Main function for device thread.
    virtual void Main();
    virtual int MainSetup();
    virtual void MainQuit();

    int foop;
};

// A factory creation function, declared outside of the class so that it
// can be invoked without any object context (alternatively, you can
// declare it static in the class).  In this function, we create and return
// (as a generic Driver*) a pointer to a new instance of this driver.
Driver* 
ArtPotDriver_Init(ConfigFile* cf, int section)
{
  // Create and return a new instance of this driver
  return((Driver*)(new ArtPotDriver(cf, section)));
}

// A driver registration function, again declared outside of the class so
// that it can be invoked without object context.  In this function, we add
// the driver into the given driver table, indicating which interface the
// driver can support and how to create a driver instance.
void ArtPotDriver_Register(DriverTable* table)
{
  table->AddDriver("artpotdriver", ArtPotDriver_Init);
}

////////////////////////////////////////////////////////////////////////////////
// Constructor.  Retrieve options from the configuration file and do any
// pre-Setup() setup.
ArtPotDriver::ArtPotDriver(ConfigFile* cf, int section)
    : ThreadedDriver(cf, section, false, PLAYER_MSGQUEUE_DEFAULT_MAXLEN, 
             PLAYER_POSITION2D_CODE)
{
  // Read an option from the configuration file
  this->foop = cf->ReadInt(section, "foo", 0);

  return;
}

////////////////////////////////////////////////////////////////////////////////
// Set up the device.  Return 0 if things go well, and -1 otherwise.
int ArtPotDriver::MainSetup()
{   
  puts("Artificial Potential driver initialising");

  // Here you do whatever is necessary to setup the device, like open and
  // configure a serial port.

  printf("Was foo option given in config file? %d\n", this->foop);
    
  puts("Artificial Potential driver ready");

  return(0);
}


////////////////////////////////////////////////////////////////////////////////
// Shutdown the device
void ArtPotDriver::MainQuit()
{
  puts("Shutting Artificial Potential driver down");

  // Here you would shut the device down by, for example, closing a
  // serial port.

  puts("Artificial Potential driver has been shutdown");
}

int ArtPotDriver::ProcessMessage(QueuePointer & resp_queue, 
                                  player_msghdr * hdr,
                                  void * data)
{
  // Process messages here.  Send a response if necessary, using Publish().
  // If you handle the message successfully, return 0.  Otherwise,
  // return -1, and a NACK will be sent for you, if a response is required.
  return(0);
}



////////////////////////////////////////////////////////////////////////////////
// Main function for device thread
void ArtPotDriver::Main() 
{
  // The main loop; interact with the device here
  for(;;)
  {
    // test if we are supposed to cancel
    pthread_testcancel();

    // Process incoming messages.  ExampleDriver::ProcessMessage() is
    // called on each message.
    ProcessMessages();

    // Interact with the device, and push out the resulting data, using
    // Driver::Publish()

    // Sleep (you might, for example, block on a read() instead)
    usleep(100000);
  }
}

////////////////////////////////////////////////////////////////////////////////
// Extra stuff for building a shared object.

/* need the extern to avoid C++ name-mangling  */
extern "C" {
  int player_driver_init(DriverTable* table)
  {
    puts("Artificial Potential driver initializing");
    ArtPotDriver_Register(table);
    puts("Artificial Potential driver done");
    return(0);
  }
}

