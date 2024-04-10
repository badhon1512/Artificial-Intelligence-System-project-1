def number_hexagonal_grid(size):

    identifiers = []
    n = 1
    row_per_direction = (2*size) - 1

    row_size = size
    is_upper = True
    for i in range(row_per_direction):
        row = [(i, i + 1) for i in range(n, (n+2*row_size), 2)]
        identifiers.append(row)
        n += 2*row_size

        if row_size >= row_per_direction:
            is_upper = False

        if is_upper:
            row_size += 1
        else:
            row_size -= 1

    # n_identity = []
    # row_size = size
    # is_upper = True
    # for i in range(row_per_direction):
    #
    #     for j in range(row_size):
    #     row = [(i, i + 1) for i in range(n, (n + 2 * row_size), 2)]
    #     n_identity.append(row)
    #
    #     if row_size >= row_per_direction:
    #         is_upper = False
    #
    #     if is_upper:
    #         row_size += 1
    #     else:
    #         row_size -= 1



    return identifiers







# Example usage:
size = 4  # Given the size of the hexagon
hex_grid = number_hexagonal_grid(size)

# Printing the grid
for row in hex_grid:
    print(row)

# Your original hexagonal grid structure
hex_grid = [
    [(1, 2), (3, 4), (5, 6)],
    [(7, 8), (9, 10), (11, 12), (13, 14)],
    [(15, 16), (17, 18), (19, 20), (21, 22), (23, 24)],
    [(25, 26), (27, 28), (29, 30), (31, 32)],
    [(33, 34), (35, 36), (37, 38)]
]



size = 3  # This is the "radius" of the hex grid

# Generate the coordinates for each direction
coordinates_1b = [(x, -x, 0) for x in range(-size + 1, size)]
coordinates_2b = [(0, -z, z) for z in range(-size + 1, size)]
coordinates_3a = [(y, 0, -y) for y in range(-size + 1, size)]

print("Coordinates for 1b (Horizontal):", coordinates_1b)
print("Coordinates for 2b (Downward-Right):", coordinates_2b)
print("Coordinates for 3a (Downward-Left):", coordinates_3a)

pllist = []
incmt = 0
startx = size - 1
starty = -(size - 1)
for r in range(2 * size - 1):
    collist = []
    for c in range(size + incmt):
        cell = f"X{startx - r}Y{starty + c}"
        print(c)


    if r >= size - 1:
        incmt -= 1
        starty += 1
    else:
        incmt += 1


def number_hexagonal_grid(size):

    identifiers = []
    identifiers_dict = {}
    starting_positions = {'dir-1':[], 'dir-2':[], 'dir-3':[]}
    outer_blocks = {'left':[], 'right':[], 'top':[], 'bottom':[]}
    n = 1
    row_per_direction = (2*size) - 1

    row_size = size
    is_upper = True
    x = - (size - 1)
    y = (size - 1)
    for i in range(row_per_direction):
        row = [(i, i + 1) for i in range(n, (n+2*row_size), 2)]
        x_prev = x

        for j, r in enumerate(row):
            identifiers_dict[(x,y)] = r


            #first direction
            if i == 0 :
                outer_blocks['top'].append((x, y))
            if i == row_per_direction - 1 :
                outer_blocks['bottom'].append((x, y))

            if j == 0:
                outer_blocks['left'].append((x,y))
                # first direction
            if j == len(row)-1:
                outer_blocks['right'].append((x,y))
            x += 1

            # storing starting pos


        y -= 1


        identifiers.append(row)
        n += 2*row_size

        if row_size >= row_per_direction:
            is_upper = False

        if is_upper:
            row_size += 1
            x = x_prev
        else:
            row_size -= 1
            x = x_prev + 1


    # create variable for each line in each directions

    outer_blocks = outer_blocks['left'] + outer_blocks['bottom'] + outer_blocks['right'][::-1] + outer_blocks['top'][::-1]
    # remove duplicate
    outer_blocks = list(dict.fromkeys(outer_blocks))

    # wow!!! now let's create variables _> there are three directions
    # first one start till size, 2nd one start from last one on previous and last one keep first cell also
    print('identifi', identifiers_dict)
    print('outer', outer_blocks)
    hexa_identifiers = []
    for i in range(3):



        if i == 0:
            starting_blocks = outer_blocks[0: row_per_direction]
        elif i == 1:
            starting_blocks = outer_blocks[row_per_direction-1: (2*row_per_direction-1)]
        else:
            starting_blocks = outer_blocks[(2*row_per_direction-1) -1: ]
            starting_blocks.append(outer_blocks[0])
        is_upper = True
        row_size = size
        for s_i, starting_block in enumerate(starting_blocks):

            tmp_identifiers = []
            x, y = starting_block
            tmp_identifiers.append(identifiers_dict[(x, y)])
            print('row', row_size, s_i)
            for k in range((row_size-1)):


                # first direction => x+1, y
                if i == 0:
                    x +=1
                    print('hold',(x,y), starting_block)
                    tmp_identifiers.append(identifiers_dict[(x,y)])
                elif i == 1:

                    x -= 1
                    y += 1
                    print('hold2',(x,y), starting_block)

                    tmp_identifiers.append(identifiers_dict[(x,y)])
                else:
                    y -= 1
                    print('hold23',(x,y), starting_block)

                    tmp_identifiers.append(identifiers_dict[(x,y)])
            hexa_identifiers.append(tmp_identifiers)

            if is_upper and  row_size >= row_per_direction:
                is_upper = False

            if is_upper:
                row_size += 1
            else:
                row_size -= 1






    print('ll', len(outer_blocks))




    return identifiers

# Example usage:
size = 7  # Given the size of the hexagon
hex_grid = number_hexagonal_grid(size)

# Printing the grid
for row in hex_grid:
    print(row)


