# A simple failure in which at a certain time a robot is reset at random

# August, 2013 - James Marshall

import random

class Standard_Failure:
      occured = False
      time = -1

      def consider_anarchy(self, robots, elapsed_time):
            if elapsed_time >= self.time and not(self.occured):
                  self.occured = True
                  target = random.randint(0, len(robots) - 1)
                  # Pick a robot at random to destroy!
                  robots[target].pipe_manager_end.send("RESET")

      def add_param(self, name, value):
            if name == "time":
                  self.time = float(value)
            elif name == "manager":
                  # Sometimes it's nice to know who you are. Now is not one of those times.
                  return
            else:
                  print "Standard_Failure does not recognize parameter: %s - %s" % (name, value)

      def reset(self):
            self.occured = False

