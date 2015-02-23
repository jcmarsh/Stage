import heapq
import math
from stage_utils import Point

map_size = 16.0

class node:
    def __init__(self, x, y, g_score):
        self.x = x
        self.y = y
        self.g_score = g_score
        # cost_est is held by the heap
        # self.cost_est = 10000 # g_score + estimated cost to goal (10000 = infinity)
        self.back_link = None

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ") " + str(self.g_score)

    # Scotty overrode __eq__ and I want to be just like him.
    def __eq__(self, o):
        return o != None and o.x == self.x and o.y == self.y

def gridify(a, grid_num, offset):
    interval = map_size / grid_num
    b = Point(0,0)
    b.x = int((a.x + offset.x) / interval)
    b.y = int((a.y + offset.y) / interval)
    if b.x == grid_num:
        b.x = grid_num - 1 # Edge case
    if b.y == grid_num:
        b.y = grid_num - 1 # Edge case
    return b

def degridify(a, offset, grid_num):
    interval = map_size / grid_num
    b = Point(0,0)
    b.x = a.x * interval + (interval / 2.0) - offset.x
    b.y = a.y * interval + (interval / 2.0) - offset.y
    return b

class a_star_planner:
    def __init__(self, num, offset):
        self.grid_num = num
        self.offset = offset
        self.obs_thres = 3
        self.obstacles = [[False for x in range(self.grid_num)] for y in range(self.grid_num)]
        self.obs_count = [[0 for x in range(self.grid_num)] for y in range(self.grid_num)]

    # Euclidean distance
    def _est_dist(self, a, b):
        dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
        return dist

    def add_obstacle(self, loc):
        obs = gridify(loc, self.grid_num, self.offset)
        if obs.x < self.grid_num and obs.y < self.grid_num:
            self.obs_count[obs.x][obs.y] += 1
            if self.obs_count[obs.x][obs.y] >= self.obs_thres:
                if not(self.obstacles[obs.x][obs.y]):
                    self.obstacles[obs.x][obs.y] = True
                    return True
                else:
                    return False
            else:
                return False
        else:
            print "ERROR! One of the grid indexes is greater than %d: %d, %d" % (self.grid_num, obs.x, obs.y) 

    # Hmm......
    def _gen_neighbors(self, n):
        # one node in each of the 8 directions of a grid.
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= n.x + i and n.x + i < self.grid_num and 0 <= n.y + j and n.y + j < self.grid_num:
                    if not i == j == 0: # 8 neighbors
                        if i == j or i == -j:
                            # Diagonal neighbor. Make sure way is blocked on either side.
                            if not self.obstacles[n.x + i][n.y] or not self.obstacles[n.x][n.y + j]: # this looks wrong. What about i = 1 and j = 1?
                                new_node = node(n.x + i, n.y + j, n.g_score + 1.414) # units the number of grid spaces
                                if not self.obstacles[n.x + i][n.y + j]:
                                    neighbors.append(new_node)
                        else:
                            new_node = node(n.x + i, n.y + j, n.g_score + 1) # see comment above
                            if not self.obstacles[n.x + i][n.y + j]:
                                neighbors.append(new_node)
        return neighbors

    def _reconstruct_path(self, n):
        current = n
        path = []
        while not current.back_link is None:
            path.insert(0, degridify(current, self.offset, self.grid_num))
            current = current.back_link
        path.insert(0, degridify(current, self.offset, self.grid_num))

        return path

    # Modeled from the Wikipedia page.
    def plan(self, start_p, goal_p):
        s_g = gridify(start_p, self.grid_num, self.offset)
        g_g = gridify(goal_p, self.grid_num, self.offset)
        start = node(s_g.x, s_g.y, 0)
        goal = node(g_g.x, g_g.y, 0)
        closed_set = []
        open_set = [] # heap ordered by estimated cost
        heapq.heappush(open_set, (0 + self._est_dist(start, goal), start))

        while len(open_set) > 0:
            c_cost, c_node = heapq.heappop(open_set)

            if c_node == goal:
                return self._reconstruct_path(c_node)
        
            # c_node.cost_est = c_cost
            closed_set.append(c_node)

            for n in self._gen_neighbors(c_node):
                tent_g_score = c_node.g_score + self._est_dist(n, c_node) # huh? looks like f score
                try:
                    index = closed_set.index(n) # in closed set
                    if tent_g_score >= n.g_score:
                        continue
                    else: # Can this ever happen?
                        closed_set[index].g_score = tent_g_score
                        closed_set[index].back_link = c_node
                        continue
                except ValueError:
                    pass
            
                found = False
                for w in open_set:
                    if n == w[1]:
                        found = True
                        break
            
                if not found or tent_g_score < n.g_score:
                    n.g_score = tent_g_score
                    n.back_link = c_node
                    heapq.heappush(open_set, (tent_g_score + self._est_dist(n, goal), n))

#        print "Failed! No path"
        return None
