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
#include <math.h>

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
  
  int foop; // TODO: Remove? -jcm

  // Set up the underlying odometry device
  int SetupOdom();
  int ShutdownOdom();
  void ProcessOdom(player_msghdr_t* hdr, player_position2d_data_t &data);

  // Set up the laser device
  int SetupLaser();
  int ShutdownLaser();
  void ProcessLaser(player_laser_data_t &);
  
  // Commands for the position device
  void PutCommand( int speed, int turnrate );

  // Check for new commands
  void ProcessCommand(player_msghdr_t* hdr, player_position2d_cmd_pos_t &);

  // Devices provided
  player_devaddr_t position_id;
  player_devaddr_t planner_id;
  bool planner;
  player_planner_data_t planner_data;

  // Required devices (odometry and laser)
  // Odometry Device info
  Device *odom;
  player_devaddr_t odom_addr;

  double dist_eps; // TODO: Check on remvoing these -jcm
  double ang_eps;
  double odom_pose[3];
  double odom_vel[3];
  int odom_stall;

  // Laser Device info
  Device *laser;
  player_devaddr_t laser_addr;
  int laser_count;
  double laser_ranges[361][2];

  // Control velocity
  double con_vel[3];

  // Should have your art_pot specific code here...
  int speed, turnrate;
  bool active_goal;
  int32_t goal_x, goal_y, goal_t;
  int cmd_state, cmd_type;

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
  printf("HELLLLOOOOOOO!!!!!!!!!!!");
  puts("Artificial Potential driver initialising");
  this->active_goal = false;
  this->goal_x = this->goal_y = this->goal_t = 0;

  // Initialize the position device we are reading from
  if (this->SetupOdom() != 0)
    return -1;

  // Initialize the laser
  if (this->laser_addr.interf && this->SetupLaser() != 0)
    return -1;

  printf("Was foo option given in config file? %d\n", this->foop);
    
  puts("Artificial Potential driver ready");

  return(0);
}

////////////////////////////////////////////////////////////////////////////////
// Shutdown the device
void ArtPotDriver::MainQuit()
{
  puts("Shutting Artificial Potential driver down");

  if(this->laser)
    this->ShutdownLaser();

  puts("Artificial Potential driver has been shutdown");
}

////////////////////////////////////////////////////////////////////////////////
// Incoming message!
int ArtPotDriver::ProcessMessage(QueuePointer & resp_queue, 
                                  player_msghdr * hdr,
                                  void * data)
{
  if(Message::MatchMessage(hdr, PLAYER_MSGTYPE_DATA,
			   PLAYER_POSITION2D_DATA_STATE, this->odom_addr)) {
    assert(hdr->size == sizeof(player_position2d_data_t));
    ProcessOdom(hdr, *reinterpret_cast<player_position2d_data_t *> (data));
    return 0;
  } else if(Message::MatchMessage(hdr, PLAYER_MSGTYPE_DATA,
				  PLAYER_LASER_DATA_SCAN, this->laser_addr)) {
    ProcessLaser(*reinterpret_cast<player_laser_data_t *> (data));
    return 0;
  } else if (Message::MatchMessage(hdr, PLAYER_MSGTYPE_CMD,
				   PLAYER_PLANNER_CMD_GOAL,
				   this->planner_id)) {
    // Message on the planner interface
    // Emulate a message on the position2d interface

    player_position2d_cmd_pos_t cmd_pos;
    player_planner_cmd_t *cmd_planner = (player_planner_cmd_t *) data;

    memset(&cmd_pos, 0, sizeof(cmd_pos));
    cmd_pos.pos.px = cmd_planner->goal.px;
    cmd_pos.pos.py = cmd_planner->goal.py;
    cmd_pos.pos.pa = cmd_planner->goal.pa;
    cmd_pos.state = 1;

    /* Process position2d command */
    ProcessCommand(hdr, cmd_pos);
    return 0;
  } else if(Message::MatchMessage(hdr, PLAYER_MSGTYPE_CMD,
				  PLAYER_POSITION2D_CMD_POS,
				  this->position_id)) {
    assert(hdr->size == sizeof(player_position2d_cmd_pos_t));
    ProcessCommand(hdr, *reinterpret_cast<player_position2d_cmd_pos_t *> (data));
    return 0;
  } else if(Message::MatchMessage(hdr, PLAYER_MSGTYPE_CMD,
                                PLAYER_POSITION2D_CMD_VEL,
                                this->position_id)) {
    assert(hdr->size == sizeof(player_position2d_cmd_vel_t));
    // make a copy of the header and change the address
    player_msghdr_t newhdr = *hdr;
    newhdr.addr = this->odom_addr;
    this->odom->PutMsg(this->InQueue, &newhdr, (void*)data);
    this->cmd_type = 0;
    this->active_goal = false;

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
void ArtPotDriver::Main() 
{
  // The main loop; interact with the device here
  for(;;)
  {
    // test if we are supposed to cancel
    pthread_testcancel();

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

////////////////////////////////////////////////////////////////////////////////
// Shutdown the underlying odom device.
int ArtPotDriver::ShutdownOdom()
{

  // Stop the robot before unsubscribing
  this->speed = 0;
  this->turnrate = 0;
  this->PutCommand( speed, turnrate );

  this->odom->Unsubscribe(this->InQueue);
  return 0;
}

////////////////////////////////////////////////////////////////////////////////
// Shut down the laser
int ArtPotDriver::ShutdownLaser()
{
  this->laser->Unsubscribe(this->InQueue);
  return 0;
}

////////////////////////////////////////////////////////////////////////////////
// Set up the underlying odom device.
int ArtPotDriver::SetupOdom()
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
  this->cmd_state = 1;

  return 0;
}

////////////////////////////////////////////////////////////////////////////////
// Set up the laser
int ArtPotDriver::SetupLaser()
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
// Process new odometry data
void ArtPotDriver::ProcessOdom(player_msghdr_t* hdr, player_position2d_data_t &data)
{

  // Cache the new odometric pose, velocity, and stall info
  // NOTE: this->odom_pose is in (mm,mm,deg), as doubles
  this->odom_pose[0] = data.pos.px * 1e3;
  this->odom_pose[1] = data.pos.py * 1e3;
  this->odom_pose[2] = RTOD(data.pos.pa);
  this->odom_vel[0] = data.vel.px * 1e3;
  this->odom_vel[1] = data.vel.py * 1e3;
  this->odom_vel[2] = RTOD(data.vel.pa);
  this->odom_stall = data.stall;

  // Also change this info out for use by others
  player_msghdr_t newhdr = *hdr;
  newhdr.addr = this->position_id;
  this->Publish(&newhdr, (void*)&data);

 if(this->planner)
 {
   this->planner_data.pos.px = data.pos.px;
   this->planner_data.pos.py = data.pos.py;
   this->planner_data.pos.pa = data.pos.pa;

   this->Publish(this->planner_id,
                 PLAYER_MSGTYPE_DATA,
                 PLAYER_PLANNER_DATA_STATE,
                 (void*)&this->planner_data,sizeof(this->planner_data), NULL);
 }
}

////////////////////////////////////////////////////////////////////////////////
// Process laser data
void ArtPotDriver::ProcessLaser(player_laser_data_t &data)
{
  int i;
  double b, db, r;
  
  b = RTOD(data.min_angle);
  db = RTOD(data.resolution);
  
  this->laser_count = 361;

  for (i = 0; i < laser_count; i++)
    this->laser_ranges[i][0] = -1;

  PLAYER_ERROR("JAMES! Fix this crap!"); // TODO: Seriously. Not playing around -jcm
}

////////////////////////////////////////////////////////////////////////////////
// Send commands to underlying position device
void ArtPotDriver::PutCommand(int cmd_speed, int cmd_turnrate)
{
  player_position2d_cmd_vel_t cmd;

  this->con_vel[0] = (double) cmd_speed;
  this->con_vel[1] = 0;
  this->con_vel[2] = (double) cmd_turnrate;

  memset(&cmd, 0, sizeof(cmd));

  // Stop the robot if the motor state is set to disabled
  if (this->cmd_state == 0) {
    cmd.vel.px = 0;
    cmd.vel.py = 0;
    cmd.vel.pa = 0;
  } else { // Position mode
    PLAYER_ERROR("SHOULD BE SETTING THIS CORRECTLY!");
    cmd.vel.px = 1;
    cmd.vel.py = 0;
    cmd.vel.pa = 0;
  }

  this->odom->PutMsg(this->InQueue,
		     PLAYER_MSGTYPE_CMD,
		     PLAYER_POSITION2D_CMD_VEL,
		     (void*)&cmd, sizeof(cmd), NULL);
}

////////////////////////////////////////////////////////////////////////////////
// Check for new commands from the server
void ArtPotDriver::ProcessCommand(player_msghdr_t* hdr, player_position2d_cmd_pos_t &cmd)
{
  int x,y,t;

  x = (int)rint(cmd.pos.px * 1e3);
  y = (int)rint(cmd.pos.py * 1e3);
  t = (int)rint(RTOD(cmd.pos.pa));

  this->cmd_type = 1;
  this->cmd_state = cmd.state;

  if((x != this->goal_x) || (y != this->goal_y) || (t != this->goal_t))
  {
    this->active_goal = true;
    this->goal_x = x;
    this->goal_y = y;
    this->goal_t = t;

    if(this->planner)
    {
       this->planner_data.goal.px = cmd.pos.px;
       this->planner_data.goal.py = cmd.pos.py;
       this->planner_data.goal.pa = cmd.pos.pa;
       this->planner_data.done = 0;

       this->planner_data.valid = 1;
            /* Not necessarily. But VFH will try anything once */

       this->planner_data.waypoint_idx = -1; /* Not supported */
       this->planner_data.waypoints_count = -1; /* Not supported */
    }
  }
}

