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

# Euclidean distance
def est_dist(a, b):
    dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
    #print "(%f,%f) -> (%f,%f): %f" % (a.x, a.y, b.x, b.y, dist)
    return dist

# Hmm......
def gen_neighbors(n, known_obstacles):
    # one node in each of the 8 directions of a grid.
    neighbors = []
    for i in range(-1, 2):
        for j in range(-1, 2):
            if not i == j == 0:
                new_node = node(n.x + i, n.y + j, n.cost_to + 1)
                if not new_node in known_obstacles:
                    neighbors.append(new_node)
    return neighbors

def reconstruct_path(n):
    current = n
    path = []
    while not current.back_link is None:
        path.append(current)
        current = current.back_link
    path.append(current)

    return path

# Modeled from the Wikipedia page.
def A(start, goal, known_obstacles):
    closed_set = []
    open_set = [] # heap ordered by estimated cost
    heapq.heappush(open_set, (0 + est_dist(start, goal), start))

    while len(open_set) > 0:
        c_cost, c_node = heapq.heappop(open_set)
        print "Looking at: (%d,%d)" % (c_node.x, c_node.y)

        if c_node == goal:
            print "success. Now reconstruct"
            return reconstruct_path(c_node)
        
        c_node.cost_est = c_cost
        closed_set.append(c_node)

        for n in gen_neighbors(c_node, known_obstacles):
            tent_g_score = c_node.cost_to + est_dist(n, c_node)
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
                heapq.heappush(open_set, (tent_g_score + est_dist(n, goal), n))
                
print("Please work")
g = node(8,8,0)
s = node(2,2,0)

o1 = node(5,5,0)
o2 = node(5,6,0)
known = [o1, o2]

p = A(s, g, known)

for n in reversed(p):
    print "Node: %d,%d" % (n.x, n.y)
            
            
            
    

    
    
