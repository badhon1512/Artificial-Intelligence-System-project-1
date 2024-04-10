import re
from pysat.formula import CNF
from pysat.solvers import Solver
from itertools import combinations
import subprocess


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
            clue = f"{length}{color}"
            #clue = clue.replace(match, replacement, 1)  # Replace only the first occurrence

        return clue

    def get_variables(self, size):

        variable = []

        for i in range(size):
            variable.append([self.current_v, self.current_v+1])
            self.current_v += 2
        return variable

    def parse_clues(self):
        # with open(self.clue_file, 'r') as file:
        #     lines = file.readlines()
        #     print(len(lines), 'linejgdj')

        lines = []
        with open(self.clue_file, 'r') as file:
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
        self.create_indentifier()
        print(self.identifiers)



        serial = 0
        for i, line in enumerate(lines[2:]):
            # print('line', line)
            # print(i,'kshdkhfd', self.rows)

            line = line.strip()


            # create size based on number of cell

            if self.type == RECT and i < self.row_size:
                variables = self.identifiers[i]
            elif self.type == RECT:
                variables = [row[i-self.row_size] for row in self.identifiers]
            else:
                size = 0

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
        print(self.clues_info)




    def convert_to_cnf(self):

        starting_variables = {}

        # for each clue
        for key, clue_info in self.clues_info.items():


            # if there is +, there could be multiple combination of clues possible
            for clue in clue_info['clues']:
                clue = clue.split()

                starting_variables = {}
                print(clue_info)
                # assign starting variable for each block i-clue { 0-1a:[9(A1) 10(A) 11(B1).... ] }
                for i, c in enumerate(clue):
                    starts = [i for i in range(self.current_v, (self.current_v + int(clue_info['size'])))]
                    self.current_v += clue_info['size']
                    starting_variables[str(i)+'-'+c] = starts

                # step-1 create cnf for position rule

                possible_blocks = {}
                cell_combinations = {}

                # create dict for each cell color
                for sublist in clue_info['variables']:
                    #cell_combinations[sublist[0]] = []
                    for pair in sublist:
                        cell_combinations[pair] = []


                #loop over starting variables for ecah block
                for k, starting_blocks in starting_variables.items():


                    clue_size, color = int(k.split('-')[1][:-1]), k.split('-')[1][-1]
                    print('hold on', k, clue_size)

                    # loop over all starting variable for a single block
                    for block_index, block in enumerate(starting_blocks):

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
                            #print(color)
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

                # print('cc', cell_combinations)
                # break


                #setp 2 -> exclusive or (⊕) to make sure that each block has exactly one start: --> done
                #
                for k, variables in starting_variables.items():
                    self.cnf += [[-x for x in combo] for combo in combinations(variables, 2)]

                    self.cnf.append(variables)
                    # print([[-x for x in combo] for combo in combinations(variables, 2)])
                    # return


                '''setp -3 , cnf---> if one block starts at a particular position, the next block
                            will start sufficiently late:  '''

                # Convert dictionary items to a list of items
                items = list(starting_variables.items())

                for i, (k, variables) in enumerate(items):
                    clue_size, color = int(k.split('-')[1][:-1]), k.split('-')[1][-1]

                    # Check if there is a next item
                    if i + 1 < len(items):
                        next_k, next_variables = items[i + 1]
                        next_block_color = next_k.split('-')[1][-1]

                        for i, variable in enumerate(variables):

                            if color == next_block_color:
                                #todo size need to be calculated-->
                                next_possible_blocks = next_variables[i+clue_size+1: ]
                            else:
                                next_possible_blocks = next_variables[i + clue_size:]
                            next_possible_blocks.insert(0, -variable)

                            self.cnf.append(next_possible_blocks)

                    elif clue_size>1:

                        for variable in variables[-(clue_size-1):]:
                            self.cnf.append([-variable])









    # define unique variable colors for each cell

    def create_indentifier(self):
        self.identifiers = [[[] for _ in range(self.column_size)] for _ in range(self.row_size)]
        n = 1
        #print(self.identifiers)
        print(self.row_size, self.column_size)
        for r in range(self.row_size):
            for c in range(self.column_size):
                self.identifiers[r][c] =  (n, n+1)
                n += 2
        self.current_v = n
        print(self.current_v)

    def create_sat_file(self):

        # Your CNF formula represented as a list of lists


        # Calculate the number of variables and clauses for the DIMACS header
        num_clauses = len(self.cnf)

        # Open a file to write the CNF formula in DIMACS format
        filename = "formula.sat"
        with open(filename, "w") as cnf_file:
            # Write the header
            cnf_file.write(f"p cnf {self.current_v-1} {num_clauses}\n")

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
        grid = [['-' for _ in range(self.column_size)] for _ in range(self.row_size)]

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
        filename = 'grid_output.solution'
        with open(filename, 'w') as file:
            for row in grid:
                line = ''.join(row) + '\n'
                file.write(line)

        print(f'Grid has been written to {filename}.')

    def check_satisfiability_from_file(self):
        # Load the CNF formula from a DIMACS format file
        filename = 'formula.sat'
        cnf = CNF(from_file=filename)

        # Use a SAT solver to solve the CNF formula
        with Solver(bootstrap_with=cnf) as solver:
            is_satisfiable = solver.solve()

            # Print the result
            if is_satisfiable:
                print(f"The formula in {filename} is satisfiable.")
                # Get and print a satisfying model
                self.sat_assignments = solver.get_model()
                #print("A satisfying assignment is:", self.sat_assignments)
                self.create_sol_file()
            else:
                print(f"The formula in {filename} is unsatisfiable.")

    # def check_satisfiability_from_file(self):
    #     # Path to the Kissat executable
    #     kissat_path = r"kissat\build\kissat.exe"
    #
    #     # Path to the CNF file
    #     cnf_file = 'formula.sat'
    #
    #     # Run Kissat with the CNF file as input
    #     result = subprocess.run([kissat_path, cnf_file], capture_output=True, text=True)
    #
    #     # Process the output
    #     if 's SATISFIABLE' in result.stdout:
    #         print(f"The formula in {cnf_file} is satisfiable.")
    #         # Extract the satisfying assignment
    #         assignment_lines = [line for line in result.stdout.splitlines() if line.startswith('v')]
    #         assignment_str = ' '.join(assignment_lines).replace('v', '').strip()
    #         self.sat_assignments = [int(var) for var in assignment_str.split() if int(var) > 0]
    #         print("A satisfying assignment is:", self.sat_assignments)
    #     elif 's UNSATISFIABLE' in result.stdout:
    #         print(f"The formula in {cnf_file} is unsatisfiable.")
    #     else:
    #         print("Error: Could not determine satisfiability.")

    def encode(self):

        # plue
        self.parse_clues()
        self.convert_to_cnf()

        self.create_sat_file()

        self.check_satisfiability_from_file()






if __name__ == '__main__':
    #print('styart')

    file_name = './clues/test2.clues'
    e = Solution(file_name)
    e.encode()
    # print(len(e.cnf), e.cnf)
    print(e.clues_info)



