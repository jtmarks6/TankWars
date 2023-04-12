import heapq

# Define a class to represent each node in the grid
class Node:
    def __init__(self, x, y, cost=float('inf'), parent=None):
        self.x = x
        self.y = y
        self.cost = cost
        self.parent = parent

    def __lt__(self, other):
        return self.cost < other.cost

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


# Define the A* algorithm
def a_star(grid, start, goal):
    # Create an empty set to store visited nodes
    visited = set()

    # Create a priority queue to store nodes to visit
    queue = []

    # Create a start node and add it to the queue
    start_node = Node(start[0], start[1], 0)
    heapq.heappush(queue, start_node)

    # Loop until we find the goal or there are no more nodes to visit
    while queue:
        # Get the node with the lowest cost from the queue
        current_node = heapq.heappop(queue)

        # Check if we've reached the goal
        if current_node.x == goal[0] and current_node.y == goal[1]:
            path = []
            while current_node.parent:
                path.append((current_node.x, current_node.y))
                current_node = current_node.parent
            path.append((current_node.x, current_node.y))
            return path[::-1]

        # Add the current node to the visited set
        visited.add(current_node)

        # Check the neighbors of the current node
        for y_offset, x_offset in ((-1, 0), (0, -1), (1, 0), (0, 1)):
            x, y = current_node.x + x_offset, current_node.y + y_offset
            if x < 0 or y < 0 or x >= len(grid[0]) or y >= len(grid):
                continue
            if grid[y][x] == 0:
                # Compute the cost of moving to the neighbor
                neighbor_cost = current_node.cost + 1
                neighbor = Node(x, y, neighbor_cost, current_node)
                if neighbor in visited:
                    continue
                if neighbor not in queue:
                    heapq.heappush(queue, neighbor)
                else:
                    for q in queue:
                        if q == neighbor and q.cost > neighbor.cost:
                            queue.remove(q)
                            heapq.heappush(queue, neighbor)

    # If we get here, there is no path to the goal
    return None
