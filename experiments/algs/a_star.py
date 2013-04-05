import heapq
import math

class node:
    def __init__(self, x, y, cost_to):
        self.x = x
        self.y = y
        self.cost_to = cost_to
        self.cost_est = 10000 # cost_to + estimated cost to goal (10000 = infinity)
        self.back_link = None

    # Scotty overrode __eq__ and I want to be just like him.
    def __eq__(self, o):
        return o != None and o.x == self.x and o.y == self.y

class a_star_planner:
    def __init__(self, num):
        self.grid_num = num
        self.obs_thres = 3
        self.obstacles = [[False for x in range(self.grid_num)] for y in range(self.grid_num)]
        self.obs_count = [[0 for x in range(self.grid_num)] for y in range(self.grid_num)]

    # Euclidean distance
    def _est_dist(self, a, b):
        dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
        # print "(%f,%f) -> (%f,%f): %f" % (a.x, a.y, b.x, b.y, dist)
        return dist

    def add_obstacle(self, loc):
        if loc.x < self.grid_num and loc.y < self.grid_num:
            self.obs_count[loc.x][loc.y] += 1
            if self.obs_count[loc.x][loc.y] >= self.obs_thres:
                self.obstacles[loc.x][loc.y] = True
        else:
            print "ERROR! One of the grid indexes is greater than %d: %d, %d" % (self.grid_num, loc.x, loc.y) 

    # Hmm......
    def _gen_neighbors(self, n):
        # one node in each of the 8 directions of a grid.
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= n.x + i and n.x + i < self.grid_num and 0 <= n.y + j and n.y + j < self.grid_num:
                    if not i == j == 0: # 8 neighbors
                        if i == j or i == -j:
                            new_node0 = node(n.x + i, n.y, 0)
                            new_node1 = node(n.x, n.y + j, 0)
                            if not self.obstacles[n.x + i][n.y] or not self.obstacles[n.x][n.y + j]:
                                new_node = node(n.x + i, n.y + j, n.cost_to + 1.414)
                                if not self.obstacles[n.x + i][n.y + j]:
                                    neighbors.append(new_node)
                        else:
                            new_node = node(n.x + i, n.y + j, n.cost_to + 1)
                            if not self.obstacles[n.x + i][n.y + j]:
                                neighbors.append(new_node)
        return neighbors

    def _reconstruct_path(self, n):
        current = n
        path = []
        while not current.back_link is None:
            path.append(current)
            current = current.back_link
        path.append(current)

        return path

    # Modeled from the Wikipedia page.
    def plan(self, start, goal):
        closed_set = []
        open_set = [] # heap ordered by estimated cost
        heapq.heappush(open_set, (0 + self._est_dist(start, goal), start))

        while len(open_set) > 0:
            c_cost, c_node = heapq.heappop(open_set)

            if c_node == goal:
                return self._reconstruct_path(c_node)
        
            c_node.cost_est = c_cost
            closed_set.append(c_node)

            for n in self._gen_neighbors(c_node):
                tent_g_score = c_node.cost_to + self._est_dist(n, c_node)
                try:
                    index = closed_set.index(n)
                    if tent_g_score < closed_set[index].cost_to:
                        closed_set[index].cost_to = tent_g_score
                        closed_set[index].back_link = c_node
                        continue
                except ValueError:
                    pass
            
                found = False
                for w in open_set:
                    if n == w[1]:
                        found = True
                        break
            
                if not found:
                    n.back_link = c_node
                    heapq.heappush(open_set, (tent_g_score + self._est_dist(n, goal), n))
