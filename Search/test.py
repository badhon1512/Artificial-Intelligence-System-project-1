

def cube_to_axial(cube_coord):
    x, _, z = cube_coord
    return (x, z)

def cube_distance(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))

def hex_distance(a, b):
    ac = axial_to_cube(a)
    bc = axial_to_cube(b)
    return cube_distance(ac, bc)
# Initialize an empty board with all positions set to None
def initialize_board():
    board = {}
    for x in range(-6, 7):
        for y in range(-6, 7):
            # The sum of the coordinates must also be in the range to form a hexagonal shape
            if -6 <= x-y <= 6 and -6 <= x+y <= 6:
                board[(x, y)] = {'conn_coors': [], 'heuristic': [None, None, None], 'type': 'normal', 'hold': None}
    return board

# Set up the starting positions for players A, B, and C
def set_starting_positions(board):
    # The starting positions will depend on the game; these are placeholders
    starting_positions_A = [(0, -3), (0, -4), (1, -4)]  # etc.
    starting_positions_B = [(3, 0), (3, -1), (4, -1)]  # etc.
    starting_positions_C = [(-3, 3), (-3, 2), (-2, 2)]  # etc.
    # Assign starting positions for each player
    for pos in starting_positions_A:
        board[pos]['hold'] = 'A'
    for pos in starting_positions_B:
        board[pos]['hold'] = 'B'
    for pos in starting_positions_C:
        board[pos]['hold'] = 'C'
    # Set goal types
    for pos in starting_positions_A:
        board[pos]['type'] = 'A_home'
    for pos in starting_positions_B:
        board[pos]['type'] = 'B_home'
    for pos in starting_positions_C:
        board[pos]['type'] = 'C_home'
# Assign heuristic values based on distance from each position to the goal
def axial_to_cube(hex_coord):
    # Expecting hex_coord to be a tuple (x, z)
    try:
        x, z = hex_coord
        return (x, -x-z, z)
    except ValueError as e:
        print(f"Incorrect hex_coord passed to axial_to_cube: {hex_coord}")
        raise e

# ... [rest of your functions here] ...

# Assign heuristic values based on distance from each position to the goal
def assign_heuristic_values(board, player_goals):
    for pos in board.keys():
        # Assuming player_goals is a dict with player index as keys
        for player in player_goals:
            goal = cube_to_axial(player_goals[player])
            board[pos]['heuristic'][player] = hex_distance(pos, goal)
    print(board)
# Initialize board and set starting positions
board = initialize_board()
print(len(board))
set_starting_positions(board)

# Define goals for each player using cube coordinates
player_goals = {
    0: axial_to_cube((3, -6)),  # Goal position for player A
    1: axial_to_cube((-3, 3)),  # Goal position for player B
    2: axial_to_cube((0, 3)),   # Goal position for player C
}

# Assign heuristic values to the board
assign_heuristic_values(board, player_goals)
