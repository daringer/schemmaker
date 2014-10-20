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


def calculate_zft_position(forceOptimizer):
    turn = 0
    while (turn != 6):
        print "TURN:", turn
        for net in forceOptimizer.dictionary_net_blocks:
            print "Net:", net
            for block in forceOptimizer.dictionary_net_blocks[net]:
                group = search_group(block.groups, forceOptimizer)
                if block not in group.block_north or block not in group.block_south:
                    if block not in group.block_east or block not in group.block_west:
                        print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
                        block.pos = sum_calculate_free(block, forceOptimizer.dictionary_net_blocks[net])
                        print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
                    else:
                        print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
                        block.pos[1] = sum_calculate_west_east(block, forceOptimizer.dictionary_net_blocks[net])
                        print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
                else:
                    print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
                    block.pos[0] = sum_calculate_north_south(block, forceOptimizer.dictionary_net_blocks[net])
                    print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
        turn += 1


def sum_calculate_free(block, neighbors):
    '''
    weight = 1
    '''

    x = 0.0
    y = 0.0

    for neighbor in neighbors:
        if neighbor is not block:
            x += neighbor.pos[0]
            y += neighbor.pos[1]

    x /= len(neighbors)
    y /= len(neighbors)

    return [x, y]

def sum_calculate_north_south(block, neighbors):
    '''
    weight = 1
    '''

    x = 0.0

    for neighbor in neighbors:
        if neighbor is not block:
            x += neighbor.pos[0]

    x /= len(neighbors)

    return x

def sum_calculate_west_east(block, neighbors):
    '''
    weight = 1
    '''

    y = 0.0

    for neighbor in neighbors:
        if neighbor is not block:
            y += neighbor.pos[1]

    y /= len(neighbors)

    return y