# A standard manager that simply runs the controllers as specified.

# July, 2013 - James Marshall
import multiprocessing
import Basic_Manager

# The Manager. Bam.
class Linked_Manager(Basic_Manager.Basic_Manager):
    dist_sum = 0
    dist_count = 0


    def open_controllers(self):
        command_receive = None
        command_send = None
        command_receive_next = None

        for i in range(len(self.robots)):
            print "Opening controller for %s" % (self.robots[i].name)
            self.robots[i].pipe_robot_end, self.robots[i].pipe_manager_end = multiprocessing.Pipe()

            # Set up communication between the controllers
            # TODO: This should be described in the .ini and set up here accordingly
            # but for now I'm just going to be lazy and assume a linked list style chain
            if i + 1 < len(self.robots):
                command_receive_next, command_send = multiprocessing.Pipe(False)
            else:
                command_receive_next = None # Won't be used, but nice to make it explicit
                command_send = None

            self.robots[i].controller_p = multiprocessing.Process(target=self.robots[i].controller_i.go, args=(self.robots[i].name, self.robots[i].pipe_robot_end, command_receive, command_send))
            command_receive = command_receive_next
            self.robots[i].controller_p.start()

    # Functions concerning stat collection
    def final_stats(self, sim):
        dists = Basic_Manager.getDistances(self.robots, sim)
        ret_str = "\tAvg_Dist: " + str(self.dist_sum / self.dist_count)
        for dist in range(len(dists)):
            ret_str = ret_str + "\tdist_" + str(dist) + ": " + str(dists[dist])

        # reset other stats
        self.dist_sum = 0
        self.dist_count = 0

        return ret_str

    def update_stats(self, sim):
        # This function is overly simple; it assumes that the robots are in the convoy
        # in the same order in which they are stored (0th is leader, 1st is first follower, etc)
        for r in range(len(self.robots) - 1):
            pose0 = sim.get_pose2d(self.robots[r].name)
            pose1 = sim.get_pose2d(self.robots[r + 1].name)
            self.dist_sum = self.dist_sum + Basic_Manager._dist(pose0[1], pose0[2], pose1[1], pose1[2])
            self.dist_count = self.dist_count + 1
        return

