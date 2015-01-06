from itertools import repeat

def start (forceOptimizer, debug=False):
    if debug:
        print ""
        print "============="
        print "Last Phase"
        print "============="
        print ""

    for group in forceOptimizer.groups:

        inner_blocks = []

        freeField_height = group.size_height
        freeField_width = group.size_width
        field_max_x = group.size_width
        field_min_x = 0
        field_max_y = group.size_height
        field_min_y = 0
        rows = list(repeat(0,freeField_height))
        columns = list(repeat(0,freeField_width))



        for block in group.block_north:
            rows[block.pos[1]] += 1

        for block in group.block_south:
            if block not in group.block_north:
                rows[block.pos[1]] += 1

        for block in group.block_east:
            if block not in group.block_north and block not in group.block_south:
                rows[block.pos[1]] += 1

        for block in group.block_west:
            if block not in group.block_north and block not in group.block_south:
                rows[block.pos[1]] += 1

        if debug:
            print "rows of group:", group.group_id
            for row in rows:
                print row

        for block in group.block_east:
            columns[block.pos[0]] += 1

        for block in group.block_west:
            if block not in group.block_east:
                columns[block.pos[0]] += 1

        for block in group.block_north:
            if block not in group.block_east and block not in group.block_west:
                columns[block.pos[0]] += 1

        for block in group.block_south:
            if block not in group.block_east and block not in group.block_west:
                columns[block.pos[0]] += 1

        if debug:
            print "columns of group:", group.group_id
            print columns

        for block in group.blocks:
            if block not in group.block_north and block not in group.block_south and block not in group.block_east and block not in group.block_west:
                inner_blocks.append(block)

        inner_blocks = sorted(inner_blocks, cmp=block_compare_y)

        for block in inner_blocks:

            new_y = int(round(block.pos[1]))
            if debug:
                print "Block:", block.name, " y:",block.pos[1], "newY:", new_y

            if new_y > field_max_y:
                new_y = field_max_y
            if new_y < field_min_y:
                new_y = field_min_y

            no_position = True
            max_position = 0
            if group.size_height > 2:
                max_position = freeField_height-2
            else:
                max_position = freeField_height-1



            if rows[new_y] < freeField_width:
                rows[new_y] += 1
                block.pos[1] = new_y

            elif rows[new_y-1] < freeField_width and new_y-1 > 0:
                rows[new_y-1] += 1
                block.pos[1] = new_y-1

            elif rows[new_y + 1] < freeField_width and new_y+1 < max_position:
                rows[new_y + 1] += 1
                block.pos[1] = new_y+1

            if debug:
                print "Block:", block.name, " y:",block.pos[1]

        inner_blocks = sorted(inner_blocks, cmp=block_compare_x)

        for block in inner_blocks:

            new_x = int(round(block.pos[0]))
            if debug:
                print "Block:", block.name, " x:",block.pos[0], "newX:", new_x

            if new_x > len(columns):
                new_x = len(columns)-1

            max_position = 0
            if group.size_width > 2:
                max_position = freeField_width-2
                if new_x < 1:
                    new_x = 1
            else:
                max_position = freeField_width-1
                if new_x < 0:
                    new_x = 0


            if columns[new_x] < freeField_height:
                columns[new_x] += 1
                block.pos[0] = new_x

            elif new_x-1 > 0 and columns[new_x-1] < freeField_height:
                columns[new_x-1] += 1
                block.pos[0] = new_x-1

            elif new_x+1 < max_position and columns[new_x+1] < freeField_height:
                columns[new_x+1] += 1
                block.pos[0] = new_x+1

            block_pos = []
            for neighbor in group.blocks:
                if neighbor is not block:
                    block_pos.append(neighbor.pos)
            j = -1
            i = -1
            c = 0
            r = 0

            while(block.pos in block_pos):
                if debug:
                    print "double position:",block.name, " Pos:",block.pos

                new_pos = [block.pos[0], block.pos[1]]
                pos_x = block.pos[0] + c * i
                pos_y = block.pos[1] + r * j

                if pos_x < 0 :
                    pos_x = 0
                if pos_x >= group.size_width:
                    pos_x = group.size_width - 1
                new_pos[0] = pos_x

                if pos_y < 0 :
                    pos_y = 0
                if pos_y >= group.size_height:
                    pos_y = group.size_height - 1
                new_pos[1] = pos_y

                if debug:
                    print "New Pos:", new_pos

                if j > 0:
                    c += 1
                j *= -1

                if i > 0:
                    r += 1
                i *= -1

                if new_pos not in block_pos:
                    block.pos = new_pos



            if debug:
                print "Block:", block.name, " x:",block.pos[0]

def block_compare_y(block_1, block_2):
    '''
    Sort groups by their group_id
    groups on the low level with long IDs came first
    '''
    if(block_1.pos[1] < block_2.pos[1]):
        return 1
    else:
        return -1

def block_compare_x(block_1, block_2):
    '''
    Sort groups by their group_id
    groups on the low level with long IDs came first
    '''
    if(block_1.pos[0] < block_2.pos[0]):
        return 1
    else:
        return -1
