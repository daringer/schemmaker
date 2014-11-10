import math

def start (forceOptimizer):

    print ""
    print "============="
    print "Main Phase"
    print "============="
    print ""

    calculate_zft_position(forceOptimizer)


def search_group(group_id, forceOptimizer):
    '''
    PARAMETER:  group_ids     is an array with the IDs of the parent Groups and the ID of the searched group
                return        the group if it exists, else None
    STATE:      not finish
    '''
    for group in forceOptimizer.groups:
        if group.group_id == group_id:
            return group
    return None

def search_neighbors(block, forceOptimizer):
    neighbors = {}
    for pin in block.pins.values():
        #print pin.net
        if pin.net in forceOptimizer.dictionary_net_blocks:
            for block_neighbor in forceOptimizer.dictionary_net_blocks[pin.net]:
                if block is not block_neighbor:# and block_neighbor.groups == block.groups:
                    if block_neighbor not in neighbors:
                        neighbors[block_neighbor] = 1
                    else:
                        value = neighbors[block_neighbor]
                        value += 1
                        neighbors[block_neighbor] = value
    for neighbor in neighbors:
        pass #print "Neighbor Block:", neighbor.name, "Group:", str(neighbor.groups)
    return neighbors

def calculate_zft_position(forceOptimizer):
    turn = 0
    while (turn != 18):
        print "TURN:", turn



        if turn % 3 == 0:
            # free block turn
            for block in forceOptimizer.blocks:
                group = search_group(block.groups, forceOptimizer)
                neighbors = search_neighbors(block, forceOptimizer)
                if block not in group.block_north and block not in group.block_south:
                    if block not in group.block_east and block not in group.block_west:
                        print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
                        block.pos = sum_calculate_free(block, neighbors, group)
                        print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]

        elif turn % 3 == 1:
            for block in forceOptimizer.blocks:
                group = search_group(block.groups, forceOptimizer)
                neighbors = search_neighbors(block, forceOptimizer)
                if (block in group.block_north or block in group.block_south) and (block not in group.block_east and block not in group.block_west):
                        print "N/S Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
                        block.pos = sum_calculate_north_south(block, neighbors, group)
                        print "N/S Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
                if (block in group.block_east or block in group.block_west) and (block not in group.block_north and block not in group.block_south):
                        print "E/W Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
                        block.pos = sum_calculate_east_west(block, neighbors, group)
                        print "E/W Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]

        elif turn % 3 == 2:

            for block in forceOptimizer.blocks:
                group = search_group(block.groups, forceOptimizer)

                print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]

                if (block in group.block_north) and (block not in group.block_east and block not in group.block_west):
                    block.pos[0] = calculate_border_north_south_position(block, group.block_north)
                if (block in group.block_south) and (block not in group.block_east and block not in group.block_west):
                    block.pos[0] = calculate_border_north_south_position(block, group.block_south)

                if (block in group.block_east) and (block not in group.block_north and block not in group.block_south):
                    block.pos[1] = calculate_border_east_west_position(block, group.block_east)
                if (block in group.block_west) and (block not in group.block_north and block not in group.block_south):
                    block.pos[1] = calculate_border_east_west_position(block, group.block_west)

                print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
        '''
        for group in forceOptimizer.groups:
            if turn%2 == 0:
                if group not in group.parent.child_east and group not in group.parent.child_west:
                    if group not in group.parent.child_south and group not in group.parent.child_north:
                        print "Group: ", group.group_id, " X:", group.position_x, " Y:", group.position_y
                        sum_calculate_free_group(group)
                        print "Group: ", group.group_id, " X:", group.position_x, " Y:", group.position_y
            else:
                if group in group.parent.child_south or group in group.parent.child_north:
                    if group not in group.parent.child_east and group not in group.parent.child_west:
                        print "Group: ", group.group_id, " X:", group.position_x, " Y:", group.position_y
                        sum_calculate_north_south_group(group)
                        print "Group: ", group.group_id, " X:", group.position_x, " Y:", group.position_y

                if group not in group.parent.child_south and group not in group.parent.child_north:
                    if group in group.parent.child_east or group in group.parent.child_west:
                        print "Group: ", group.group_id, " X:", group.position_x, " Y:", group.position_y
                        sum_calculate_east_west_group(group)
                        print "Group: ", group.group_id, " X:", group.position_x, " Y:", group.position_y
        '''
        turn += 1
def calculate_border_east_west_position(block,neighbors):
    top = 0
    for neighbor in neighbors:
        if neighbor.pos[1] < block.pos[1]:
            top = top + 1
    return top

def calculate_border_north_south_position(block,neighbors):
    left = 0
    for neighbor in neighbors:
        if neighbor.pos[0] < block.pos[0]:
            left = left + 1
    return left

def sum_calculate_north_south_group(group):
    '''
    weight =
    '''



    count_neighbors = len(group.neighbor_north) + len(group.neighbor_south) + len(group.neighbor_east) + len(group.neighbor_west)+ len(group.neighbor_unsorted)
    group_x = count_neighbors * group.position_x

    if count_neighbors > 1:

        for neighbor in group.neighbors:
            group_x += len(group.neighbors[neighbor]) * (neighbor.position_x )


        div = count_neighbors

        for neighbor in group.neighbors:
            print "Neighbor:", neighbor.group_id, "Weight:",len(group.neighbors[neighbor]), "PosX:", neighbor.position_x, "PosY:", neighbor.position_y
            div += len(group.neighbors[neighbor])

        group_x /= div


    else:
        group_x = group.position_x



    if group_x > group.parent.size_width - 1:
        group_x = group.parent.size_width - 1

    group.position_x = group_x

def sum_calculate_east_west_group(group):
    '''
    weight =
    '''



    count_neighbors = len(group.neighbor_north) + len(group.neighbor_south) + len(group.neighbor_east) + len(group.neighbor_west)+ len(group.neighbor_unsorted)
    group_y = count_neighbors * group.position_y

    if count_neighbors > 1:

        for neighbor in group.neighbors:
            group_y += len(group.neighbors[neighbor]) * (neighbor.position_y )


        div = count_neighbors

        for neighbor in group.neighbors:
            print "Neighbor:", neighbor.group_id, "Weight:",len(group.neighbors[neighbor]), "PosX:", neighbor.position_x, "PosY:", neighbor.position_y
            div += len(group.neighbors[neighbor])

        group_y /= div


    else:
        group_y = group.position_y



    if group_y > group.parent.size_height - 1:
        group_y = group.parent.size_height - 1

    group.position_y = group_y

def sum_calculate_free_group(group):
    '''
    weight =
    '''

    count_neighbors = len(group.neighbor_north) + len(group.neighbor_south) + len(group.neighbor_east) + len(group.neighbor_west)+ len(group.neighbor_unsorted)
    group_x = count_neighbors * group.position_x
    group_y = count_neighbors * group.position_y

    if count_neighbors > 1:

        for neighbor in group.neighbors:

            group_x += len(group.neighbors[neighbor]) * (neighbor.position_x )
            group_y += len(group.neighbors[neighbor]) * (neighbor.position_y )

        div = count_neighbors

        for neighbor in group.neighbors:
            print "Neighbor:", neighbor.group_id, "Weight:",len(group.neighbors[neighbor]), "PosX:", neighbor.position_x, "PosY:", neighbor.position_y
            div += len(group.neighbors[neighbor])

        group_x /= div
        group_y /= div

    else:
        group_x = group.position_x
        group_y = group.position_y

    if group_y > group.parent.size_height - 1:
        group_y = group.parent.size_height - 1
    if group_x > group.parent.size_width - 1:
        group_x = group.parent.size_width - 1

    group.position_x = group_x
    group.position_y = group_y



def sum_calculate_free(block, neighbors, group):
    '''
    weight =
    '''
    x = 0.0
    y = 0.0
    div = 0
    if len(neighbors) > 1:

        for neighbor in neighbors:

            if neighbor is not block:
                if neighbor.pos[0] < block.pos[0]:
                    x += neighbors[neighbor] * (neighbor.pos[0] + 1)
                else:
                    x += neighbors[neighbor] * (neighbor.pos[0] - 1)
                if neighbor.pos[1] < block.pos[1]:
                    y += neighbors[neighbor] * (neighbor.pos[1] - 1)
                else:
                    y += neighbors[neighbor] * (neighbor.pos[1] + 1)

            div += neighbors[neighbor]

        x /= div
        y /= div

    else:
        x = block.pos[0]
        y = block.pos[1]

    #x = math.ceil(x) # round to next int
    #y = math.ceil(y)

    if y > group.size_height - 1:
        y = group.size_height - 1
    if x > group.size_width - 1:
        x = group.size_width - 1
    if y < 0:
        y = 0
    if x < 0:
        x = 0

    if x <= 1 and group.size_width > 2:
        x =  1
    if y <= 1 and group.size_height > 2:
        y =  1
    if x >= group.size_width - 2 and group.size_width > 2:
        x = group.size_width - 2
    if y >= group.size_height - 2 and group.size_height > 2:
        y = group.size_height - 2

    return [x, y]


def sum_calculate_north_south(block, neighbors, group):
    '''
    weight = #same nets
    '''
    x = 0.0
    div = 0

    if len(neighbors) > 1:

        for neighbor in neighbors:

            if neighbor is not block:
                if neighbor.pos[0] < block.pos[0]:
                    x += neighbors[neighbor] * (neighbor.pos[0] + 1)
                else:
                    x += neighbors[neighbor] * (neighbor.pos[0] - 1)

            div += neighbors[neighbor]

        x /= div

    else:
        x = block.pos[0]

    #x = math.ceil(x) # round to next int

    if x > group.size_width - 1:
        x = group.size_width - 1

    if x < 0:
        x = 0

    return [x, block.pos[1]]


def sum_calculate_east_west(block, neighbors, group):
    '''
    weight =
    '''

    y = 0.0
    div = 0

    if len(neighbors) > 1:

        for neighbor in neighbors:

            if neighbor is not block:
                if neighbor.pos[1] < block.pos[1]:
                    y += neighbors[neighbor] * (neighbor.pos[1] - 1)
                else:
                    y += neighbors[neighbor] * (neighbor.pos[1] + 1)

            div += neighbors[neighbor]

        y /= div

    else:
        y = block.pos[1]

    #y = math.ceil(y)

    if y > group.size_height - 1:
        y = group.size_height - 1
    if y < 0:
        y = 0


    return [block.pos[0], y]


def calculate_pin_position(block, neighbor, pin):
    pos = []
    for pin1 in block.pins.values():
        for pin2 in neighbor.pins.values():
            #print "block.pins[pin].net:",block.pins[pin].net, "pin2.net:",pin2.net
            if pin1.net == pin2.net:# == block.pins[pin].net:
                pos.append(pin2.pos[0])
                pos.append(pin2.pos[1])
                pos[0] = pos[0]/2.0
                pos[1] = pos[1]/2.0
                return pos
    return -1
