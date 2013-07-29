/*
 * Dumb driver. Just moves to a location
 * 
 * Stripped down version of the artificial potential driver. Just has a goal.
 * Does not respond to obstacles.
 */

#include <unistd.h>
#include <string.h>
#include <math.h>

#include <libplayercore/playercore.h>

////////////////////////////////////////////////////////////////////////////////
// The class for the driver
class DumbDriver : public ThreadedDriver
{
public:
    
  // Constructor; need that
  DumbDriver(ConfigFile* cf, int section);

  // This method will be invoked on each incoming message
  virtual int ProcessMessage(QueuePointer &resp_queue, 
			     player_msghdr * hdr,
			     void * data);
  
private:
  // Main function for device thread.
  virtual void Main();
  virtual int MainSetup();
  virtual void MainQuit();
  
  double vel_scale;
  double dist_epsilon;
  double goal_radius, goal_extent, goal_scale;

  // Set up the underlying odometry device
  int SetupOdom();
  int ShutdownOdom();
  void ProcessOdom(player_msghdr_t* hdr, player_position2d_data_t &data);

  
  void DoOneUpdate();
  // Commands for the position device
  void PutCommand( double speed, double turnrate );

  // Check for new commands
  void ProcessCommand(player_msghdr_t* hdr, player_position2d_cmd_pos_t &);

  // Devices provided
  player_devaddr_t position_id;
  player_devaddr_t planner_id;
  bool planner;
  player_planner_data_t planner_data;

  // Required devices (odometry)
  // Odometry Device info
  Device *odom;
  player_devaddr_t odom_addr;

  double odom_pose[3];
  double odom_vel[3];
  int odom_stall;

  // Control velocity
  double con_vel[3];

  int speed, turnrate;
  bool active_goal;
  double goal_x, goal_y, goal_t;
  int cmd_state, cmd_type;
};

// A factory creation function, declared outside of the class so that it
// can be invoked without any object context (alternatively, you can
// declare it static in the class).  In this function, we create and return
// (as a generic Driver*) a pointer to a new instance of this driver.
Driver* 
DumbDriver_Init(ConfigFile* cf, int section)
{
  // Create and return a new instance of this driver
  return((Driver*)(new DumbDriver(cf, section)));
}

// A driver registration function, again declared outside of the class so
// that it can be invoked without object context.  In this function, we add
// the driver into the given driver table, indicating which interface the
// driver can support and how to create a driver instance.
void DumbDriver_Register(DriverTable* table)
{
  table->AddDriver("dumbdriver", DumbDriver_Init);
}

////////////////////////////////////////////////////////////////////////////////
// Constructor.  Retrieve options from the configuration file and do any
// pre-Setup() setup.
DumbDriver::DumbDriver(ConfigFile* cf, int section)
  : ThreadedDriver(cf, section)
{
  // Check for planner (we provide)
  memset(&(this->planner_id), 0, sizeof(player_devaddr_t));
  memset(&(this->planner_data), 0, sizeof(player_planner_data_t));
  if (cf->ReadDeviceAddr(&(this->planner_id), section, "provides",
			 PLAYER_PLANNER_CODE, -1, NULL) == 0) {
    planner = true;
    if (this->AddInterface(this->planner_id) != 0) {
      this->SetError(-1);
      return;
    }
    // Init planner data

  }
  
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
  this->vel_scale = cf->ReadFloat(section, "vel_scale", 4);
  this->goal_radius = cf->ReadFloat(section, "goal_radius", .1);
  this->goal_extent = cf->ReadFloat(section, "goal_extent", 2);
  this->goal_scale = cf->ReadFloat(section, "goal_scale", .5);
			 
  return;
}

////////////////////////////////////////////////////////////////////////////////
// Set up the device.  Return 0 if things go well, and -1 otherwise.
int DumbDriver::MainSetup()
{   
  puts("Dumb driver initialising");
  this->active_goal = false;
  this->goal_x = this->goal_y = this->goal_t = 0;

  // Initialize the position device we are reading from
  if (this->SetupOdom() != 0)
    return -1;

  puts("Dumb driver ready");

  return(0);
}

////////////////////////////////////////////////////////////////////////////////
// Shutdown the device
void DumbDriver::MainQuit()
{
  puts("Shutting Dumb driver down... Nothing to do... shut down.");
}

////////////////////////////////////////////////////////////////////////////////
// Incoming message!
int DumbDriver::ProcessMessage(QueuePointer & resp_queue, 
                                  player_msghdr * hdr,
                                  void * data)
{
  if(Message::MatchMessage(hdr, PLAYER_MSGTYPE_DATA,
			   PLAYER_POSITION2D_DATA_STATE, this->odom_addr)) {
    assert(hdr->size == sizeof(player_position2d_data_t));
    ProcessOdom(hdr, *reinterpret_cast<player_position2d_data_t *> (data));
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
  } else if (Message::MatchMessage(hdr, PLAYER_MSGTYPE_REQ, 
				   PLAYER_PLANNER_REQ_ENABLE,
				   this->planner_id)) {
    player_planner_enable_req_t *cmd_enable = (player_planner_enable_req_t *) data;
    this->cmd_state = cmd_enable->state;
    this->Publish(this->planner_id, resp_queue, 
		  PLAYER_MSGTYPE_RESP_ACK, PLAYER_PLANNER_REQ_ENABLE);
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
void DumbDriver::Main() 
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

void DumbDriver::DoOneUpdate() {
  double dist, theta, delta_x, delta_y, v, tao, vel, rot_vel;
  
  if (this->InQueue->Empty()) {
    return;
  }

  this->ProcessMessages();

  if (!this->active_goal) {
    return;
  }

  // Head towards the goal! odom_pose: 0-x, 1-y, 2-theta
  dist = sqrt(pow(goal_x - odom_pose[0], 2)  + pow(goal_y - odom_pose[1], 2));
  theta = atan2(goal_y - odom_pose[1], goal_x - odom_pose[0]) - odom_pose[2];

  if (dist < goal_radius) {
    v = 0;
    delta_x = 0;
    delta_y = 0;
  } else if (goal_radius <= dist and dist <= goal_extent + goal_radius) {
    v = goal_scale * (dist - goal_radius);
    delta_x = v * cos(theta);
    delta_y = v * sin(theta);
  } else {
    v = goal_scale; //* goal_extent;
    delta_x = v * cos(theta);
    delta_y = v * sin(theta);
  }

  if (v > 0) {
    //vel = sqrt(pow(delta_x, 2) + pow(delta_y, 2));
    //rot_vel = atan2(delta_y, delta_x);
    //vel = vel_scale * vel * (abs(M_PI - rot_vel) / M_PI);
    //rot_vel = vel_scale * rot_vel;

    // TODO: Should turn to the desired theta, goal_t
    //this->PutCommand(vel, rot_vel);
    this->PutCommand(delta_x, delta_y);
  } else { // within distance epsilon. Give it up, man.
    this->PutCommand(0,0);
  }
}


////////////////////////////////////////////////////////////////////////////////
// Extra stuff for building a shared object.

/* need the extern to avoid C++ name-mangling  */
extern "C" {
  int player_driver_init(DriverTable* table)
  {
    puts("Dumb driver initializing");
    DumbDriver_Register(table);
    puts("Dumb driver done");
    return(0);
  }
}

////////////////////////////////////////////////////////////////////////////////
// Shutdown the underlying odom device.
int DumbDriver::ShutdownOdom()
{

  // Stop the robot before unsubscribing
  this->speed = 0;
  this->turnrate = 0;
  this->PutCommand( speed, turnrate );

  this->odom->Unsubscribe(this->InQueue);
  return 0;
}

////////////////////////////////////////////////////////////////////////////////
// Set up the underlying odom device.
int DumbDriver::SetupOdom()
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
// Process new odometry data
void DumbDriver::ProcessOdom(player_msghdr_t* hdr, player_position2d_data_t &data)
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
// Send commands to underlying position device
void DumbDriver::PutCommand(double cmd_speed, double cmd_turnrate)
{
  player_position2d_cmd_vel_t cmd;

  this->con_vel[0] = cmd_speed;
  this->con_vel[1] = 0;
  this->con_vel[2] = cmd_turnrate;

  memset(&cmd, 0, sizeof(cmd));

  // Stop the robot if the motor state is set to disabled
  if (this->cmd_state == 0) {
    cmd.vel.px = 0;
    cmd.vel.py = 0;
    cmd.vel.pa = 0;
  } else { // Position mode
    cmd.vel.px = this->con_vel[0];
    cmd.vel.py = this->con_vel[1];
    cmd.vel.pa = this->con_vel[2];
  }

  this->odom->PutMsg(this->InQueue,
		     PLAYER_MSGTYPE_CMD,
		     PLAYER_POSITION2D_CMD_VEL,
		     (void*)&cmd, sizeof(cmd), NULL);
}

////////////////////////////////////////////////////////////////////////////////
// Check for new commands from the server
void DumbDriver::ProcessCommand(player_msghdr_t* hdr, player_position2d_cmd_pos_t &cmd)
{
  this->cmd_type = 1;
  this->cmd_state = cmd.state;

  if((cmd.pos.px != this->goal_x) || (cmd.pos.py != this->goal_y) || (cmd.pos.pa != this->goal_t))
  {
    this->active_goal = true;
    this->goal_x = cmd.pos.px;
    this->goal_y = cmd.pos.py;
    this->goal_t = cmd.pos.pa;

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

