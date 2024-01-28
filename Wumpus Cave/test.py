class GridCleaner:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    def is_wall(self, x, y):
        return self.grid[x][y] == 'X'

    def create_cleaning_path(self):
        path = []
        direction = 'E'  # Start moving east
        x, y = 0, 0  # Starting position

        while len(path) < self.rows * self.cols:
            if not self.is_wall(x, y):
                path.append(direction)  # Add free space to path

            if direction == 'E':
                if y + 1 == self.cols or self.is_wall(x, y + 1):
                    direction = 'S'  # Change direction to south
                    x = (x + 1) % self.rows
                else:
                    y += 1
            elif direction == 'W':
                if y == 0 or self.is_wall(x, y - 1):
                    direction = 'S'  # Change direction to south
                    x = (x + 1) % self.rows
                else:
                    y -= 1
            elif direction == 'S':
                # Change horizontal direction
                direction = 'E' if direction == 'W' else 'W'

        return path

# Example usage
grid = [
    "X   XXXXXXXXXX    ",
    "X   XXXXXXXXXXXX X",
    "X   XXXXXXXXXXXXEE",
    "X   XXXXXXXXXXWWWS",
    "    XXXXXXXXXXX   ",
    "X   XXXXXXXXXXXXXX",
    "XXX XXXXXXXXXXXXXX",
    "XX    XXXXXXXXXXXX",
    "XX    XXXXXXXXX XX",
    "XXX  XXXXXXXXXX XX",
    " XX  XXXXXXXXXX   ",
    "  X XXXXXXXXXX    "
]
cleaner = GridCleaner(grid)
cleaning_path = cleaner.create_cleaning_path()
print("Cleaning Path:", cleaning_path)
