from itertools import repeat

def start (forceOptimizer):

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

        print "columns of group:", group.group_id
        print columns





        for block in group.blocks:
            if block not in group.block_north and block not in group.block_south and block not in group.block_east and block not in group.block_west:
                inner_blocks.append(block)

        inner_blocks = sorted(inner_blocks, cmp=block_compare_y)

        for block in inner_blocks:

            new_y = round(block.pos[1])
            print "Block:", block.name, " y:",block.pos[1], "newY:", new_y

            if new_y > field_max_y:
                new_y = field_max_y
            if new_y < field_min_y:
                new_y = field_min_y

            no_position = True
            position = freeField_height-1
            while(no_position):
                if rows[position] < freeField_width:
                    rows[position] += 1
                    block.pos[1] = position
                    no_position = False
                else:
                    position -= 1

            print "Block:", block.name, " y:",block.pos[1]






        inner_blocks = sorted(inner_blocks, cmp=block_compare_x)

        for block in inner_blocks:

            new_x = round(block.pos[0])
            print "Block:", block.name, " x:",block.pos[0], "newX:", new_x

            if new_x > field_max_x:
                new_x = field_max_x
            if new_x < field_min_x:
                new_x = field_min_x

            no_position = True
            position = freeField_width-1
            while(no_position):
                if columns[position] < freeField_height:
                    columns[position] += 1
                    block.pos[0] = position
                    no_position = False
                else:
                    position -= 1

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