import re
from pysat.formula import CNF
from pysat.solvers import Solver
from itertools import combinations
import os
import sys
from sat_approach1 import Solution


HEX = 'hex'
RECT = 'rect'


class SatSolver():

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
        self.hexa_identifiers = []

        # tckact variables number for cnf
        self.current_v = 1

        self.cnf = []

        self.clues_info = {}


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

                ##print(block[0], last_color)
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
            clue = f"{length}{color}"
            #clue = clue.replace(match, replacement, 1)  # Replace only the first occurrence

        return clue

    def parse_clues(self):
        # with open(self.clue_file, 'r') as file:
        #     lines = file.readlines()
        #     #print(len(lines), 'linejgdj')

        clue_file_path = f"clues/{self.clue_file}"

        # Check if the file exists
        if not os.path.exists(clue_file_path):
            print(f"No clue file found at {clue_file_path}")
            return False  # Exit the method if file does not exist

        lines = []
        with open(f"clues/{self.clue_file}", 'r') as file:
            while True:
                line = file.readline()

                # Break if line is empty (EOF) before appending to the list
                if not line:
                    break
                if self.clue_file == 'maze-1.clues' and '+' in line:
                    line = line.replace('+', '1')

                lines.append(line)

        meta_info = lines[0].split()

        self.type = meta_info[0]
        self.colors.append(lines[1].strip().split(' '))

        if self.type == RECT:
            self.row_size = int(meta_info[1])
            self.column_size = int(meta_info[2])
            self.create_indentifier()
            #print(self.identifiers)
        else:
            self.handle_hexa_identifiers(int(meta_info[1]))
            #print('iden',self.identifiers)

        serial = 0
        for i, line in enumerate(lines[2:]):
            # #print('line', line)
            # #print(i,'kshdkhfd', self.rows)

            line = line.strip()


            # create size based on number of cell

            if self.type == RECT and i < self.row_size:
                variables = self.identifiers[i]
            elif self.type == RECT:
                variables = [row[i-self.row_size] for row in self.identifiers]
            else:
                variables = self.hexa_identifiers[i]

            clues = []

            tmp_line = line.split(' ')
            for l in tmp_line:
                if '+' in l:
                    max_plus = self.calculate_max_plus_blocks(line, len(variables))
                    tmp_clue = []
                    for j in range(1, max_plus + 1):
                        tmp_clue.append(self.replace_plus_with_length(line, j))
                    clues.append(tmp_clue)

                else:
                    clues.append([l])

            clue_info = {
                'id' : 'c_{}'.format(i),
                'clues' : clues,
                'size' : len(variables),
                'variables': variables
            }
            self.clues_info['c_{}'.format(i)] = clue_info

        return True
        #print(self.clues_info)

    def handle_hexa_identifiers(self, size):

        identifiers_dict = {}
        starting_positions = {'dir-1': [], 'dir-2': [], 'dir-3': []}
        outer_blocks = {'left': [], 'right': [], 'top': [], 'bottom': []}
        n = 1
        row_per_direction = (2 * size) - 1

        row_size = size
        is_upper = True
        x = - (size - 1)
        y = (size - 1)
        for i in range(row_per_direction):
            row = [(i, i + 1) for i in range(n, (n + 2 * row_size), 2)]
            x_prev = x

            for j, r in enumerate(row):
                identifiers_dict[(x, y)] = r

                # first direction
                if i == 0:
                    outer_blocks['top'].append((x, y))
                if i == row_per_direction - 1:
                    outer_blocks['bottom'].append((x, y))

                if j == 0:
                    outer_blocks['left'].append((x, y))
                    # first direction
                if j == len(row) - 1:
                    outer_blocks['right'].append((x, y))
                x += 1

                # storing starting pos

            y -= 1

            self.identifiers.append(row)
            n += 2 * row_size

            if row_size >= row_per_direction:
                is_upper = False

            if is_upper:
                row_size += 1
                x = x_prev
            else:
                row_size -= 1
                x = x_prev + 1

        self.current_v = n
        # create variable for each line in each directions

        outer_blocks = outer_blocks['left'] + outer_blocks['bottom'] + outer_blocks['right'][::-1] + outer_blocks['top'][::-1]
        # remove duplicate
        outer_blocks = list(dict.fromkeys(outer_blocks))

        # wow!!! now let's create variables _> there are three directions
        # first one start till size, 2nd one start from last one on previous and last one keep first cell also

        for i in range(3):

            if i == 0:
                starting_blocks = outer_blocks[0: row_per_direction]
            elif i == 1:
                starting_blocks = outer_blocks[row_per_direction - 1: (2 * row_per_direction - 1)]
            else:
                starting_blocks = outer_blocks[(2 * row_per_direction - 1) - 1:]
                starting_blocks.append(outer_blocks[0])
            is_upper = True
            row_size = size
            for starting_block in starting_blocks:

                tmp_identifiers = []
                x, y = starting_block
                tmp_identifiers.append(identifiers_dict[(x, y)])
                for k in range((row_size - 1)):

                    # first direction => x+1, y
                    if i == 0:
                        x += 1
                        tmp_identifiers.append(identifiers_dict[(x, y)])
                    elif i == 1:

                        x -= 1
                        y += 1
                        tmp_identifiers.append(identifiers_dict[(x, y)])
                    else:
                        y -= 1
                        tmp_identifiers.append(identifiers_dict[(x, y)])
                self.hexa_identifiers.append(tmp_identifiers)

                if is_upper and row_size >= row_per_direction:
                    is_upper = False

                if is_upper:
                    row_size += 1
                else:
                    row_size -= 1



    def convert_to_cnf(self):

        starting_variables = {}

        # for each clue
        for key, clue_info in self.clues_info.items():


            # if there is +, there could be multiple combination of clues possible
            clues = clue_info['clues']

            starting_variables = {}
            ##print(clue_info)
            # assign starting variable for each block i-clue { 0-1a:[9(A1) 10(A) 11(B1).... ] }
            for i, c in enumerate(clues):
                t_l = {}
                for clue in c:
                    starts = [i for i in range(self.current_v, (self.current_v + int(clue_info['size'])))]
                    t_l[clue] = starts
                    self.current_v += clue_info['size']
                starting_variables[str(i)] = t_l



            # step-1 create cnf for position rule

            possible_blocks = {}
            cell_combinations = {}

            # create dict for each cell color
            for sublist in clue_info['variables']:
                #cell_combinations[sublist[0]] = []
                for pair in sublist:
                    cell_combinations[pair] = []


            #loop over starting variables for ecah block
            for k, starting_variable in starting_variables.items():

                # for + there might be multiple combination for one block
                #print(starting_variable)
                for starting_blocks in starting_variable.items():
                    if starting_blocks[0] == '':
                        continue
                    clue_size, color = int(starting_blocks[0][:-1]), starting_blocks[0][-1]

                    # loop over all starting variable for a single block
                    for block_index, block in enumerate(starting_blocks[1]):
                        ##print('bb', block)

                        # help to increase the block
                        tmp_block_index = block_index

                        # prevent out of list
                        if block_index + int(clue_size) > len(clue_info['variables']):
                            continue

                        '''create cnf based on clue size ,, eg.. 2a-> 2-> if it starting variable is 9(cell one)
                         the cells 1 and 2 both should be colored'''
                        for j in range(int(clue_size)):


                            #if no more additional cell avail
                            if tmp_block_index   >= len(clue_info['variables']):
                                break
                            ##print(color)
                            if color =='a':
                                # color black

                                cell_combinations[clue_info['variables'][tmp_block_index][0]].append(block)

                                self.cnf.append([-block, clue_info['variables'][tmp_block_index][0]])
                                #don't color blue
                                self.cnf.append([-block, -clue_info['variables'][tmp_block_index][1]])

                                if not possible_blocks.get(clue_info['variables'][tmp_block_index][0]):
                                    possible_blocks[clue_info['variables'][tmp_block_index][0]] = []

                                possible_blocks[clue_info['variables'][tmp_block_index][0]].append(block)


                            else:


                                cell_combinations[clue_info['variables'][tmp_block_index][1]].append(block)

                                # don't color black
                                self.cnf.append([-block, -clue_info['variables'][tmp_block_index][0]])
                                # color blue
                                self.cnf.append([-block, clue_info['variables'][tmp_block_index][1]])

                                if not possible_blocks.get(clue_info['variables'][tmp_block_index][1]):
                                    possible_blocks[clue_info['variables'][tmp_block_index][1]] = []

                                possible_blocks[clue_info['variables'][tmp_block_index][1]].append(block)


                            tmp_block_index +=1

            # cell color condition eg. (-1 A1 B1) .....

            for k, possible_block in cell_combinations.items():
                # First, insert -int(k) at the beginning of possible_block
                possible_block.insert(0, -int(k))
                # Then, append possible_block to self.cnf
                self.cnf.append(possible_block)

            # break

            #setp 2 -> exclusive or (⊕) to make sure that each block has exactly one start: --> done
            #
            for k, variables in starting_variables.items():

                # combine all posible combination for one block
                variables = [item for sublist in variables.values() for item in sublist]

                self.cnf += [[-x for x in combo] for combo in combinations(variables, 2)]

                self.cnf.append(variables)
                # #print([[-x for x in combo] for combo in combinations(variables, 2)])
                # return


            '''setp -3 , cnf---> if one block starts at a particular position, the next block
                        will start sufficiently late:  '''

            # Convert dictionary items to a list of items

            items = list(starting_variables.items())

            for i, (k, variables) in enumerate(starting_variables.items()):

                for starting_blocks in variables.items():

                    if starting_blocks[0] == '':
                        continue
                    clue_size, color = int(starting_blocks[0][:-1]), starting_blocks[0][-1]

                    # Check if there is a next item
                    if i + 1 < len(starting_variables):
                        _, next_variables = items[i + 1]

                        for i, variable in enumerate(starting_blocks[1]):
                            next_possible_blocks = []
                            for next_variable in next_variables.items():

                                next_block_color = next_variable[0][-1]


                                if color == next_block_color:
                                    #todo size need to be calculated-->
                                    next_possible_blocks.extend(next_variable[1][i+clue_size+1: ])
                                else:
                                    next_possible_blocks.extend(next_variable[1][i + clue_size:])
                                next_possible_blocks.insert(0, -variable)

                                self.cnf.append(next_possible_blocks)

                    elif clue_size>1:

                        for variable in starting_blocks[1][-(clue_size-1):]:
                            self.cnf.append([-variable])




    def create_indentifier(self):
        self.identifiers = [[[] for _ in range(self.column_size)] for _ in range(self.row_size)]
        n = 1
        ##print(self.identifiers)
        #print(self.row_size, self.column_size)
        for r in range(self.row_size):
            for c in range(self.column_size):
                self.identifiers[r][c] =  (n, n+1)
                n += 2
        self.current_v = n

    # def create_sat_file(self):
    #
    #     # Your CNF formula represented as a list of lists
    #
    #
    #     # Calculate the number of variables and clauses for the DIMACS header
    #     num_clauses = len(self.cnf)
    #
    #     # Open a file to write the CNF formula in DIMACS format
    #     filename = "/DIMACS/formula.sat"
    #     with open(filename, "w") as cnf_file:
    #         # Write the header
    #         cnf_file.write(f"p cnf {self.current_v-1} {num_clauses}\n")
    #
    #         # Write each clause
    #         for clause in self.cnf:
    #             # Each clause ends with a 0
    #             clause_line = " ".join(map(str, clause)) + " 0\n"
    #             cnf_file.write(clause_line)
    #
    #     print(f"The CNF formula has been saved to {filename} in DIMACS format.")

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


    def solver(self):

        # plue
        if self.parse_clues():
            self.convert_to_cnf()

            self.create_sat_file()

            self.check_satisfiability_from_file()






if __name__ == '__main__':
    directory = 'clues'

    # Loop through the directory
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):

            if filename == 'house.clues':
                e = Solution(filename)
                e.encode()
            else:
                s = SatSolver(filename)
                s.solver()
    print('All solutions have been written inside solutions directory')

    # if len(sys.argv) < 2:
    #     print("Please provide clue name parameter.")
    #     sys.exit(1)
    # else:




