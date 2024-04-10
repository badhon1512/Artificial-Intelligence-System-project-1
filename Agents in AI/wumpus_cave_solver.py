from enum import Enum
import os
import numpy as np

DIRECTIONS = ['E', 'N', 'W', 'S']
DIRECTION_OFFSETS = {'N': (-1, 0), 'S': (1, 0), 'E': (0, 1), 'W': (0, -1)}
WALL = 'X'
DIRT = ' '
START = 'S'


class Plans(Enum):
    CHECK_PLAN = 'CHECK PLAN'
    FIND_PLAN = 'FIND PLAN'


class Directions(Enum):
    EAST = 0
    NORTH = 1
    WEST = 2
    SOUTH = 3


class WumpusCave:
    def __init__(self) -> None:
        
        self.txt_pb_files = None
        self.pb_directory_path = './problems/'
        self.sln_directory_path = './solutions/'
        self.x = None
        self.y = None
        self.map = None
        self.instructions = None
        self.contents = None
        self.plan_type = None
        self.plans = [] # contain all plans
        self.direction = Directions.EAST.value
        self.file_name = None
        self.connected_nodes = {} # contain a graph from map
        self.dirty_positions = np.array([])

    def load_problem_files(self):

        if not os.path.exists(self.sln_directory_path):
            os.makedirs(self.sln_directory_path)
        # get all problem files
        files = os.listdir(self.pb_directory_path)
        # Filter out only the .txt files
        self.txt_pb_files = [file for file in files if file.endswith('.txt')]
    
    def do_plans(self):

        self.load_problem_files()
        for txt_file in self.txt_pb_files:
            self.file_name = txt_file
            with open(os.path.join(self.pb_directory_path, txt_file), 'r') as file:
                self.contents = file.readlines()
            self.plan_type = self.contents[0].strip()
            if self.plan_type == Plans.CHECK_PLAN.value:
                self.dirty_positions = np.array([])
                self.get_map()
                self.plans = self.contents[1].strip()
                if not np.count_nonzero(self.map == START):
                    starts = np.argwhere(self.map == DIRT)
                    for start in starts:
                        self.get_map()
                        self.x = start[0]
                        self.y = start[1]
                        self.check_plan()
                        dirt = np.argwhere(self.map == DIRT)

                        dirt = dirt.reshape(-1)
                        self.dirty_positions = np.append(self.dirty_positions, dirt)
                    rows = len(self.dirty_positions) // 2
                    self.dirty_positions = self.dirty_positions.reshape((rows, 2)).astype(int)

                else:
                    self.get_map()
                    start = np.argwhere(self.map == START)[0]
                    self.x = start[0]
                    self.y = start[1]
                    self.check_plan()
                    self.dirty_positions = np.argwhere(self.map == DIRT)
                self.write_solution()

            if self.plan_type == Plans.FIND_PLAN.value:
                self.find_plan()
    
    # Check a plan whether it's good or not
    def check_plan(self):

        self.map[self.x, self.y] = 1
        for plan in self.plans:
            self.direction = DIRECTIONS.index(plan)
            self.move()

    '''1. N: The vacuum cleaner moves one square north (up).
    #2. E: The vacuum cleaner moves one square east (right).
    #3. S: The vacuum cleaner moves one square south (down).
    #4. W: The vacuum cleaner moves one square west (left).'''

    def move(self):
        x, y = self.get_new_position()
        if self.map[x,y] != 'X':
            self.x = x
            self.y = y
            self.map[self.x, self.y] = 1

    # Create the file with solution content using the directory and filename
    def write_solution(self):
        if not os.path.exists(self.sln_directory_path):
            os.makedirs(self.sln_directory_path)
        self.file_name = self.file_name.replace("problem", "solution")    
        file_path = os.path.join(self.sln_directory_path, self.file_name)

        with open(file_path, 'w') as file:
            if self.plan_type == Plans.CHECK_PLAN.value:
                if not self.dirty_positions.size:
                    file.write("GOOD PLAN\n")
                else:
                    file.write("BAD PLAN\n")
                    for position in self.dirty_positions:
                        file.write(", ".join(map(str, position[::-1])) + "\n") # swapping the index value as required

            elif self.plan_type == Plans.FIND_PLAN.value:
                file.write(''.join(self.plans))

    def get_map(self):
        if self.plan_type == Plans.FIND_PLAN.value:
            self.map = np.array([list(line.replace('\n', '')) for line in self.contents[1:]])  # Get the rest of the lines in a list as a map
        else:
            self.map = np.array([list(line.replace('\n', '')) for line in self.contents[2:]])  # Get the rest of the lines in a list as a map

    def get_new_position(self):
        dx, dy = DIRECTION_OFFSETS.get(DIRECTIONS[self.direction])
        # % will handle the appearance in opposite sides
        return (self.x + dx) % self.map.shape[0], (self.y + dy) % self.map.shape[1]

    def get_connected_nodes(self):
        self.connected_nodes = {}
        rows, cols = self.map.shape
        for x in range(rows):
            for y in range(cols):
                if self.map[x, y] != WALL:  # Check if the current cell is not a wall
                    neighbors = []

                    # Check North, with wraparound
                    north = (x - 1) % rows
                    if self.map[north, y] != WALL:
                        neighbors.append(((north, y), 'N'))

                    # Check South, with wraparound
                    south = (x + 1) % rows
                    if self.map[south, y] != WALL:
                        neighbors.append(((south, y), 'S'))

                    # Check West, with wraparound
                    west = (y - 1) % cols
                    if self.map[x, west] != WALL:
                        neighbors.append(((x, west), 'W'))

                    # Check East, with wraparound
                    east = (y + 1) % cols
                    if self.map[x, east] != WALL:
                        neighbors.append(((x, east), 'E'))

                    self.connected_nodes[(x, y)] = neighbors

    def dfs(self):
        # Initialize DFS structures
        start = (self.x, self.y)
        stack = [(start, None)]  # Stack of (node, direction to reach node)
        map_backtrack_path = {}  # dict to keep track of backtracking steps
        map_parent = {}
        visited = set()
        self.get_connected_nodes()  # this will provide a graph based on the map

        map_backtrack_path[start] = []

        while stack:

            current_node, direction = stack.pop()
            if current_node not in visited:
                visited.add(current_node)
                if direction:  # Avoid for the start node
                    self.plans.append(direction)
                    if current_node not in map_backtrack_path:
                        map_backtrack_path[current_node] = []
                    # adding backtracking path
                    parent_path = map_backtrack_path[map_parent[current_node]].copy()
                    parent_path.append(self.get_reverse_direction(direction))
                    map_backtrack_path[current_node].extend(parent_path)

                # Check for unvisited neighbors
                unvisited_neighbors = [neighbor for neighbor, _ in self.connected_nodes[current_node] if
                                       neighbor not in visited]
                if not unvisited_neighbors and stack:  # All neighbors visited, start backtracking
                    # if no node available to visit then need to go back to
                    #  next available node to back track
                    # getting next not visited node
                    # cause one node could be child of multiple parent
                    next_node = None
                    for i  in range(len(stack) - 1, -1, -1):
                        n, _ = stack[i]
                        if n not in visited:
                            next_node = n
                            break

                    if next_node:
                        next_parent_indexs = map_parent[next_node]
                        current_node_backtrack_path = map_backtrack_path[current_node]
                        parent_node_backtrack_path = map_backtrack_path[next_parent_indexs]
                        length_of_p = len(parent_node_backtrack_path)
                        self.plans.extend(current_node_backtrack_path[length_of_p:][::-1])

                else:
                    # Add unvisited neighbors to stack and record backtrack steps
                    current_direction = self.plans[-1] if self.plans else None
                    sorted_neighbors = sorted(self.connected_nodes[current_node],
                                                 key=lambda x: x[1] == current_direction)
                    for neighbor, dir_to_neighbor in sorted_neighbors:
                        if neighbor not in visited:
                            # keep parent for back tracking if multiple entry come it will keep updated one
                            map_parent[neighbor] = current_node
                            stack.append((neighbor, dir_to_neighbor))

        return self.plans

    def get_reverse_direction(self, direction):
        return {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}.get(direction, '')


    def get_unique_plan(self):

        """
        start from a node and find a path using dfs and check this path for next node,
        clean remaining dirt and add those directions to path,
        continue this and our final path will clean all dirt from any of starting nodes
        """
        possible_start_nodes = np.argwhere(self.map == DIRT)
        for start in possible_start_nodes:
            self.get_map()
            self.x = start[0]
            self.y = start[1]
            self.check_plan()
            dirty_positions = np.count_nonzero(self.map == DIRT)
            if dirty_positions:
                self.dfs()
                self.get_map()
                self.x = start[0]
                self.y = start[1]
                self.check_plan()
                dirty_positions = np.count_nonzero(self.map == DIRT)
                if dirty_positions:
                    print('Something wrong in logic!')

    def find_plan(self):

        self.plans = []
        self.map = []
        self.get_map()
        if np.count_nonzero(self.map == START) != 0:
            start = np.argwhere(self.map == START)[0]
            self.x = start[0]
            self.y = start[1]
            self.map[self.x, self.y] = 1
            self.dfs()
            self.check_plan()
            dirty_positions = np.count_nonzero(self.map == DIRT)
            if dirty_positions:
                print('Something wrong in logic!')
        else:
            # find a solution path that work no matter where start
            self.get_unique_plan()
        self.write_solution()


if __name__ == "__main__":
   wp = WumpusCave()
   wp.do_plans()
