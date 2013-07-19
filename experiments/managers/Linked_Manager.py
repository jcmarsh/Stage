# A standard manager that simply runs the controllers as specified.

# July, 2013 - James Marshall
import multiprocessing
import Basic_Manager

# The Manager. Bam.
class Linked_Manager(Basic_Manager.Basic_Manager):

    def open_controllers(self):
        command_receive = None
        command_send = None
        command_receive_next = None

        for i in range(len(self.robots)):
            print "Opening controller for %s" % (self.robots[i].name)
            self.robots[i].pipe_recieve, self.robots[i].pipe_send = multiprocessing.Pipe(False)

            # Set up communication between the controllers
            # TODO: This should be described in the .ini and set up here accordingly
            # but for now I'm just going to be lazy and assume a linked list style chain
            if i + 1 < len(self.robots):
                command_receive_next, command_send = multiprocessing.Pipe(False)
            else:
                command_receive_next = None # Won't be used, but nice to make it explicit
                command_send = None

            self.robots[i].controller_p = multiprocessing.Process(target=self.robots[i].controller_i.go, args=(self.robots[i].name, self.robots[i].pipe_recieve, command_receive, command_send))
            command_receive = command_receive_next
            self.robots[i].controller_p.start()



