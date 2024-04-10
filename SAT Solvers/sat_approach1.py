'''

Encoding approach 1, keep it only for comparison of different approach.

'''

import re
from pysat.formula import CNF
from pysat.solvers import Solver
import os

HEX = 'hex'
RECT = 'rect'


class Solution():

    def __init__(self, file_name):
        self.clue_file = file_name
        self.type = None
        self.row_size = None
        self.column_size = None
        self.rows = []
        self.columns = []
        self.colors = []
        self.logic = []

        # a dict that contain cnf for each row and column
        self.dnf = {}

        # set of identifier for each cell
        self.identifiers = []

        # tckact variables number for cnf
        self.current_v = 0

        self.cnf = []

    def calculate_max_plus_blocks(self, clue, n):

        blocks = [(seg[-1], int(seg[:-1]) if seg[:-1] != '+' else '+') for seg in clue.split()]

        # Initial space occupied and count of '+' blocks
        occupied_space = 0
        plus_blocks = [block for block in blocks if block[1] == '+']
        before_plus_color = None
        after_plus_color = None

        # Calculate space used by fixed blocks and required separations
        last_color = None
        for i, block in enumerate(blocks):

            if block[1] == '+':
                if i > 0:
                    before_plus_color = blocks[i - 1][0]
                if i < len(blocks) - 1:
                    after_plus_color = blocks[i + 1][0]
                last_color = None

            else:
                occupied_space += block[1]

                #print(block[0], last_color)
                if block[0] == last_color:
                    occupied_space += 1
                last_color = block[0]

        available_space = n - occupied_space

        max_plus = 0
        if plus_blocks:
            # Assuming each '+' block requires only 1 cell
            plus_color = plus_blocks[0][0]
            if plus_blocks[0][0] == before_plus_color:
                available_space -= 1
            if plus_blocks[0][0] == after_plus_color:
                available_space -= 1

            max_plus = available_space

        return max_plus

    def replace_plus_with_length(self, clue, length=1):
        # Find all occurrences of + followed by a letter (color)
        matches = re.findall(r'\+\w', clue)

        for match in matches:
            # Extract the color from the match
            color = match[-1]
            # Replace '+color' with 'length color' in the clue
            replacement = f"{length}{color}"
            clue = clue.replace(match, replacement, 1)  # Replace only the first occurrence

        return clue

    def parse_clues(self):
        # with open(self.clue_file, 'r') as file:
        #     lines = file.readlines()
        #     print(len(lines), 'linejgdj')

        lines = []
        with open(f"clues/{self.clue_file}", 'r') as file:
            while True:
                line = file.readline()

                # Break if line is empty (EOF) before appending to the list
                if not line:
                    break

                lines.append(line)

        meta_info = lines[0].split()

        self.type = meta_info[0]
        self.colors.append(lines[1].strip().split(' '))

        if self.type == RECT:
            self.row_size = int(meta_info[1])
            self.column_size = int(meta_info[2])

        for i, line in enumerate(lines[2:]):
            # print('line', line)
            # print(i,'kshdkhfd', self.rows)

            line = line.strip()

            if i < self.row_size:
                if '+' in line:
                    # let's handle the + by creating as many combination as possible
                    max_plus = self.calculate_max_plus_blocks(line, self.column_size)

                    for j in range(1, max_plus+1):
                         self.rows.append((self.replace_plus_with_length(line, j), i))
                else:
                    self.rows.append((line, i))
            else:

                if '+' in line:
                    # let's handle the + by creating as many combination as possible
                    max_plus = self.calculate_max_plus_blocks(line, self.row_size)

                    for j in range(1, max_plus + 1):
                        self.columns.append((self.replace_plus_with_length(line, j), abs(i - self.row_size)))
                else:
                    self.columns.append((line, abs(i - self.row_size)))


    def generate_logic_for_clue(self, clue, total_length):
        self.logic = []
        configurations = []
        blocks = [(segment[-1], int(segment[:-1])) for segment in clue.split()]

        # Checks if a block can be placed at the given start position
        def can_place_block(config, start, block):
            block_char, block_len = block
            end = start + block_len
            # Ensure no overlap with another block and it fits within the row
            if end > total_length or any(config[i] != '-' for i in range(start, end)):
                return False
            return True

        # Iteratively place blocks based on the clue
        def place_block(config, block_index, start):
            if block_index >= len(blocks):
                self.logic.append(''.join(config))
                return

            for pos in range(start, total_length - blocks[block_index][1] + 1):
                if can_place_block(config, pos, blocks[block_index]):
                    new_config = config[:]
                    block_char, block_len = blocks[block_index]

                    # Place the current block
                    new_config[pos:pos + block_len] = [block_char] * block_len

                    # Determine the starting position for the next block
                    next_start = pos + block_len

                    # Enforce separation for blocks of the same color
                    if block_index < len(blocks) - 1:
                        next_block_char, _ = blocks[block_index + 1]
                        if block_char == next_block_char:  # If the next block is the same color, add a space
                            if next_start < total_length:  # Ensure within bounds
                                new_config[next_start] = '-'
                                next_start += 1

                    place_block(new_config, block_index + 1, next_start)

        # Start the placement process with an initial empty configuration
        initial_config = ['-'] * total_length
        place_block(initial_config, 0, 0)

    def convert_to_dnf(self, key, identifiers):

        #print(key, identifiers)

        if key not in self.dnf:
            self.dnf[key] = []
        for i, l in enumerate(self.logic):
            self.dnf[key].append([])
            for j, c in enumerate(l):

                if c == 'a':
                    self.dnf[key][-1].append(int(identifiers[j][0]))
                    self.dnf[key][-1].append(-int(identifiers[j][1]))
                elif c == 'b':
                    self.dnf[key][-1].append(-int(identifiers[j][0]))
                    self.dnf[key][-1].append(int(identifiers[j][1]))
                else:
                    self.dnf[key][-1].append(-int(identifiers[j][0]))
                    self.dnf[key][-1].append(-int(identifiers[j][1]))



    def convert_to_cnf(self):

        for (k, dnf) in self.dnf.items():

            # create new clause for each row/col

            #if only one clause, no need
            # if len(dnf) < 2:
            #     self.cnf.append(dnf[0])
            #     continue

            d_c = []  # dnf to cnf
            for i in range(len(dnf)):
                d_c.append(self.current_v)
                self.current_v +=1

            self.cnf.append(d_c)


            for i, clause in enumerate(dnf):
               for variable in clause:
                    self.cnf.append([-d_c[i], variable])



    # define unique variable colors for each cell

    def create_indentifier(self):
        self.identifiers = [[[] for _ in range(self.column_size)] for _ in range(self.row_size)]
        n = 1
        #print(self.identifiers)
        for r in range(self.row_size):
            for c in range(self.column_size):
                self.identifiers[r][c] = (n, n + 1)
                n += 2
        self.current_v = n

    def create_sat_file(self):
        # Calculate the number of variables and clauses for the DIMACS header
        num_clauses = len(self.cnf)
        num_variables = self.current_v - 1

        # Use the base name of clue_file and change the extension to .sat
        base_name = os.path.splitext(self.clue_file)[0]
        filename = f"DIMACS/{base_name}.sat"
        # Ensure the directory exists, create if it doesn't
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Open a file to write the CNF formula in DIMACS format
        with open(filename, "w") as cnf_file:
            # Write the header
            cnf_file.write(f"p cnf {num_variables} {num_clauses}\n")

            # Write each clause
            for clause in self.cnf:
                # Each clause ends with a 0
                clause_line = " ".join(map(str, clause)) + " 0\n"
                cnf_file.write(clause_line)

        print(f"The CNF formula has been saved to {filename} in DIMACS format.")

    def create_sol_file(self):

        # Convert the satisfying assignment to a set for efficient lookup
        assignment_set = set(self.sat_assignments)

        # Initialize the grid with placeholders
        grid = [['-' for _ in range(len(row))] for row in self.identifiers]
        # Populate the grid based on the satisfying assignment
        for i, row in enumerate(self.identifiers):
            for j, (a, b) in enumerate(row):
                if a in assignment_set and b in assignment_set:
                    grid[i][j] = 'Error'  # Both variables cannot be positive in this context
                elif a in assignment_set:
                    grid[i][j] = 'a'
                elif b in assignment_set:
                    grid[i][j] = 'b'
                else:
                    grid[i][j] = '-'

        # Write the grid to a file
        base_name = os.path.splitext(self.clue_file)[0]

        filename = f"solutions/{base_name}.solution"
        with open(filename, 'w') as file:
            for row in grid:
                line = ''.join(row) + '\n'
                file.write(line)

        print(f'Grid has been written to {filename} inside solutions directory.')

    def check_satisfiability_from_file(self):
        # Load the CNF formula from a DIMACS format file
        base_name = os.path.splitext(self.clue_file)[0]
        filename = f"DIMACS/{base_name}.sat"
        cnf = CNF(from_file=filename)

        # Use a SAT solver to solve the CNF formula
        with Solver(bootstrap_with=cnf) as solver:
            is_satisfiable = solver.solve()

            # Print the result
            if is_satisfiable:
                print(f"The formula in {filename} is satisfiable.")
                # Get and print a satisfying model
                self.sat_assignments = solver.get_model()
                ##print("A satisfying assignment is:", self.sat_assignments)
                self.create_sol_file()
            else:
                print(f"The formula in {filename} is unsatisfiable.")

    def encode(self):

        # parse the clue
        self.parse_clues()
        self.create_indentifier()


        # solve rows
        for i, row in enumerate(self.rows):
            if row == '' or row == ' ':
                continue
            # generate the logic eg. a_bb_a
            self.generate_logic_for_clue(row[0], self.column_size)
            # make dnf from logic
            key = 'r-' + str(row[1])
            self.convert_to_dnf(key, self.identifiers[int(row[1])])

        # solve cols
        for i, column in enumerate(self.columns):

            # if column == '' or column == ' ':
            #     continue

            # generate the logic eg. a_bb_a
            self.generate_logic_for_clue(column[0], self.row_size)
            # make dnf from logic
            key = 'c-' + str(column[1])
            # make each clouses to dnf

            self.convert_to_dnf(key, [row[column[1]] for row in self.identifiers])


        self.convert_to_cnf()

        # conver cnf to DIMACS file
        self.create_sat_file()

        self.check_satisfiability_from_file()





if __name__ == '__main__':
    #print('styart')

    file_name = 'house.clues'
    e = Solution(file_name)
    e.encode()



