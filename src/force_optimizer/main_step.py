import math

def start (forceOptimizer, debug=False):
    if debug:
        print ""
        print "============="
        print "Main Phase"
        print "============="
        print ""

    calculate_zft_position(forceOptimizer, debug)


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
    return neighbors

def calculate_zft_position(forceOptimizer, debug):
    turn = 0
    while (turn != 18):

        if debug:
            print "TURN:", turn

        # zero-force-stuff: blocks not assigned to any direction
        if turn % 3 == 0:
            for block in forceOptimizer.blocks:
                group = search_group(block.groups, forceOptimizer)
                neighbors = search_neighbors(block, forceOptimizer)
                if block not in group.block_north and block not in group.block_south:
                    if block not in group.block_east and block not in group.block_west:
                        if debug:
                            print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]

                        block.pos = sum_calculate_free(block, neighbors, group)

                        if debug:
                            print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]

        # zero-force-stuff: 
        #    blocks in north||south  -> sum_calc_north_south
        #    blocks in east||west    -> sum_calc_east_west
        elif turn % 3 == 1:
            for block in forceOptimizer.blocks:
                group = search_group(block.groups, forceOptimizer)
                neighbors = search_neighbors(block, forceOptimizer)
                if (block in group.block_north or block in group.block_south) and (block not in group.block_east and block not in group.block_west):
                        if debug:
                            print "N/S Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
                        block.pos = sum_calculate_north_south(block, neighbors, group)
                        if debug:
                            print "N/S Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
                if (block in group.block_east or block in group.block_west) and (block not in group.block_north and block not in group.block_south):
                        if debug:
                            print "E/W Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
                        block.pos = sum_calculate_east_west(block, neighbors, group)
                        if debug:
                            print "E/W Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]

        # set blocks.pos based on the group the block is assigned to 
        elif turn % 3 == 2:
            if debug:
                print "---------"
                print "TURN: Border Blocks"
                print "---------"

            for group in forceOptimizer.groups:

                # why aren't the already existing sets used inside group... ?
                # try using the existing ones and remove these here if there is no change....a 
                ##### quite sure these are never used afterwards, so using group directly should make no difference
                ##### moreover the only thing that happens here is an pos assignment based on the group's direction (N,NE,...)
                blocks_SE = set()
                blocks_SW = set()
                blocks_S = set()
                blocks_NE = set()
                blocks_NW = set()
                blocks_N = set()
                blocks_E = set()
                blocks_W = set()
                
                # has no use, checking for a size of a container > 1 before , why?
                #number_of_east_north = len(group.block_north & group.block_east)
                #number_of_west_north = len(group.block_north & group.block_west)
                #number_of_east_south = len(group.block_south & group.block_east)
                #number_of_west_south = len(group.block_south & group.block_west)
                
                # handling of static block positions here TODO
                #for blk in group.blocks:
                #    if blk.name.startswith('ff'):
                #        blocks_NW.add(blk)
                #
                # does this even have _any_ effect? isn't the "static block" already 
                # assigned to a set previously?!?!
                for blk, orientation in forceOptimizer.static_blocks.items():
                    # ugly, need block sets inside dict(), stupid to have 8 identical datastructures
                    if orientation == "N": blocks_N.add(blk)
                    elif orientation == "NE": blocks_NE.add(blk)
                    elif orientation == "E": blocks_E.add(blk)
                    elif orientation == "SE": blocks_SE.add(blk)
                    elif orientation == "S": blocks_S.add(blk)
                    elif orientation == "SW": blocks_SW.add(blk)
                    elif orientation == "W": blocks_W.add(blk)
                    elif orientation == "NW": blocks_NW.add(blk)

                # check north assigned blocks, reassign to new sets 
                # (why not simple copy the groups directly: blocksNW = group.block_north & group.block_west
                #for block in group.block_north:
                #    if block in group.block_east:
                #        blocks_NE.add(block)
                #    elif block in group.block_west:
                #        blocks_NW.add(block)
                #    elif block not in group.block_east and block not in group.block_west:
                #        blocks_N.add(block)
                blocks_NE |= group.block_north & group.block_east
                blocks_NW |= group.block_north & group.block_west
                blocks_N  |= group.block_north - (group.block_east | group.block_west)

                ### assign designated pos for blks, based on group size/pos
                #if number_of_east_north > 1:
                #    position = group.size_width - 1
                #    for block in blocks_NE:
                #        if debug:
                #            print "Group:", group.group_id, " Block_NE"
                #            print block, block.pos
                #        block.pos[0] = position
                #        if debug:
                #            print block, block.pos
                #        position -= 1
                
                # place NE blocks at right border of group
                x_pos = group.size_width - 1
                for blk in blocks_NE:
                    blk.pos[0] = x_pos
                    x_pos -= 1

                #if number_of_west_north > 1:
                #    position = 0
                #    for block in blocks_NW:
                #        if debug:
                #            print "Group:", group.group_id, " Block_NW"
                #            print block, block.pos
                #        block.pos[0] = position
                #
                #        if debug:
                #            print block, block.pos
                #        position += 1
                
                # place NW blocks at left border of group
                x_pos = 0
                for blk in blocks_NW:
                    blk.pos[0] = x_pos
                    x_pos += 1

                # ok, blocks_N is a copy of group.block_north!
                # then one block from blocks_N is moved in its position according to the 
                # number of blocks in group.block_north - wh00000t!
                #
                ### actually leaving it out, changes nothing .... :/ 
                # in fact it is just a sorted list with key == blk.pos[0] 
                # and changing the pos[0] to the idx inside the sorted list 
                for block in blocks_N:
                    if debug:
                        print "Group:", group.group_id, " Block_North"
                        print block, block.pos
                    block.pos[0] = calculate_border_north_south_position(block, group.block_north)
                    if debug:
                        print block, block.pos
                
                # sorting by x-pos, replace x-pos with index in sorted-list
                #for i, blk in enumerate(sorted(blocks_N, key=lambda b:b.pos[0])):
                #    blk.pos[0] = i
                
                ############################################

                #SOUTH
                #for block in group.block_south:
                #    if block in group.block_east:
                #        blocks_SE.add(block)
                #    elif block in group.block_west:
                #        blocks_SW.add(block)
                #    elif block not in group.block_east and block not in group.block_west:
                #        blocks_S.add(block)

                blocks_SE |= group.block_south & group.block_east
                blocks_SW |= group.block_south & group.block_west
                blocks_S  |= group.block_south - (group.block_east | group.block_west)

                #### this is the identical operation as for north!?
                #### looks like.... ok first do it like it's done above
                #if number_of_east_south > 1:
                #    position = group.size_width - 1
                #    for block in blocks_SE:
                #        if debug:
                #            print "Group:", group.group_id, " Block_SE"
                #            print block, block.pos
                #        block.pos[0] = position
                #        if debug:
                #            print block, block.pos
                #        position -= 1
                
                x_pos = group.size_width - 1
                for blk in blocks_SE:
                    blk.pos[0] = x_pos
                    x_pos -= 1
                
                #### see above..
                #if number_of_west_south > 1:
                #    position = 0
                #    for block in blocks_SW:
                #        if debug:
                #            print "Group:", group.group_id, " Block_SW"
                #            print block, block.pos
                #        block.pos[0] = position
                #        if debug:
                #            print block, block.pos
                #        position += 1
                x_pos = 0
                for blk in blocks_SW:
                    blk.pos[0] = x_pos
                    x_pos += 1

                #### see above, keeping it first, later replace with sort-based implemenation
                for block in blocks_S:
                    if debug:
                        print "Group:", group.group_id, " Block_South"
                        print block, block.pos
                    block.pos[0] = calculate_border_north_south_position(block, group.block_south)
                    if debug:
                        print block, block.pos
                # sorting by x-pos, replace x-pos with index in sorted-list
                #for i, blk in enumerate(sorted(blocks_S, key=lambda b:b.pos[0])):
                #    blk.pos[0] = i


                ############ these both also just sort by y-pos and 
                ############ assign their position inside the sorted list to the y-pos 
                #EAST
                for block in group.block_east:
                    if debug:
                        print "Group:", group.group_id, " Block_East"
                    if block not in group.block_north and block not in group.block_south:
                        if debug:
                            print block, block.pos
                        block.pos[1] = calculate_border_east_west_position(block, group.block_east)
                        if debug:
                            print block, block.pos
                # sorting by y-pos, replace y-pos with index in sorted-list
                #for i, blk in enumerate(sorted(blocks_W, key=lambda b:b.pos[1])):
                #    blk.pos[1] = i


                #WEST
                for block in group.block_west:
                    if debug:
                        print "Group:", group.group_id, " Block_West"
                    if block not in group.block_north and block not in group.block_south:
                        if debug:
                            print block, block.pos
                        block.pos[1] = calculate_border_east_west_position(block, group.block_west)
                        if debug:
                            print block, block.pos
                # sorting by y-pos, replace y-pos with index in sorted-list
                #for i, blk in enumerate(sorted(blocks_W, key=lambda b:b.pos[1])):
                #    blk.pos[1] = i

            '''
            for block in forceOptimizer.blocks:
                group = search_group(block.groups, forceOptimizer)
                number_of_east_north = len(group.block_north & group.block_east)
                number_of_west_north = len(group.block_north & group.block_west)
                number_of_east_south = len(group.block_south & group.block_east)
                number_of_west_south = len(group.block_south & group.block_west)
                print "Group:", group.group_id, " NW:",number_of_west_north, " NE:", number_of_east_north, " SW:", number_of_west_south, " SE:", number_of_east_south
                print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]

                if(block in group.block_north):
                    if block in group.block_east:

                        pass
                    elif block in group.block_west:
                        pass
                    elif (block not in group.block_east and block not in group.block_west):



                if (block in group.block_south) and (block not in group.block_east and block not in group.block_west):
                    block.pos[0] = calculate_border_north_south_position(block, group.block_south)

                if (block in group.block_east) and (block not in group.block_north and block not in group.block_south):
                    block.pos[1] = calculate_border_east_west_position(block, group.block_east)
                if (block in group.block_west) and (block not in group.block_north and block not in group.block_south):
                    block.pos[1] = calculate_border_east_west_position(block, group.block_west)

                print "Block: ", block.name, " Group:", block.groups, " X:", block.pos[0], " Y:", block.pos[1]
            '''
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

#### obsolete once the sorting based y-pos assignment is active
def calculate_border_east_west_position(block,neighbors):
    top = 0
    for neighbor in neighbors:
        if neighbor.pos[1] < block.pos[1]:
            top = top + 1
    return top
#### obsolete once the sorting based x-pos assignment is active
def calculate_border_north_south_position(block,neighbors):
    left = 0
    for neighbor in neighbors:
        if neighbor.pos[0] < block.pos[0]:
            left = left + 1
    return left

def sum_calculate_north_south_group(group, debug):
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
            if debug:
                print "Neighbor:", neighbor.group_id, "Weight:",len(group.neighbors[neighbor]), "PosX:", neighbor.position_x, "PosY:", neighbor.position_y
            div += len(group.neighbors[neighbor])

        group_x /= div


    else:
        group_x = group.position_x



    if group_x > group.parent.size_width - 1:
        group_x = group.parent.size_width - 1

    group.position_x = group_x

def sum_calculate_east_west_group(group, debug):
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
            if debug:
                print "Neighbor:", neighbor.group_id, "Weight:",len(group.neighbors[neighbor]), "PosX:", neighbor.position_x, "PosY:", neighbor.position_y
            div += len(group.neighbors[neighbor])

        group_y /= div


    else:
        group_y = group.position_y



    if group_y > group.parent.size_height - 1:
        group_y = group.parent.size_height - 1

    group.position_y = group_y

def sum_calculate_free_group(group, debug):
    '''
    weight  = 1 between free blocks
            = 3 between border blocks
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
            if debug:
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
            if block.name == "m7":
                print "m7 Neighbor:", neighbor.name, " pos:",neighbor.pos
            #weight = neighbors[neighbor]
            weight = 1
            if neighbor in group.block_east or neighbor in group.block_west or neighbor in group.block_south or neighbor in group.block_north:
                weight = weight*1
            if neighbor is not block:
                if neighbor.pos[0] < block.pos[0]:
                    x += weight * (neighbor.pos[0] + 1)
                else:
                    x += weight * (neighbor.pos[0] - 1)
                if neighbor.pos[1] < block.pos[1]:
                    y += weight * (neighbor.pos[1] - 1)
                else:
                    y += weight * (neighbor.pos[1] + 1)

            div += weight

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


def calculate_pin_position(block, neighbor, pin, debug):
    pos = []
    for pin1 in block.pins.values():
        for pin2 in neighbor.pins.values():
            if debug:
                print "block.pins[pin].net:",block.pins[pin].net, "pin2.net:",pin2.net
            if pin1.net == pin2.net:# == block.pins[pin].net:
                pos.append(pin2.pos[0])
                pos.append(pin2.pos[1])
                pos[0] = pos[0]/2.0
                pos[1] = pos[1]/2.0
                return pos
    return -1
