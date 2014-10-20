
def start(forceOptimizer):


    print ""
    print "============="
    print "Initial Phase"
    print "============="
    print ""

    # the main group is the only group on the highest level, so the queue starts with her
    forceOptimizer.wide_search_queue.append(forceOptimizer.group_main)
    wide_search(forceOptimizer)

    calculate_groups_frame(forceOptimizer)

    calculate_groups_position(forceOptimizer)

def wide_search(forceOptimizer):
    '''
    Description:    Sorts the groups to the gnd / vcc / out list in their distance to out
    '''
    print "\nWide Search"
    print "Wide Search Queue count:", len(forceOptimizer.wide_search_queue)
    # get the first group of the queue to start a wide search on her over her subgroups
    group = forceOptimizer.wide_search_queue.pop(0)
    print "Group ID:", group.group_id, " Count Group Childs: ", len(group.childs)

    if len(group.childs) == 0:
        if len(forceOptimizer.wide_search_queue) > 0:
            wide_search(forceOptimizer)
    else:
        # looking for a start child with connection to the parents east neighbors
        start_child = None
        # a sub wide search queue to start a classic wide search on the actual group
        queue = []

        for child in group.childs:
            print str(child.group_id) + " Connected to parent's east neighbor:" + str(child.connected_parent_east)
            if child.connected_parent_east > 0:
                if start_child is None:
                    start_child = child
                    queue.insert(0, start_child)
                else:
                    queue.append(child)

        print "Start Child:", start_child.group_id

        # classic wide search
        start_child.wide_search_flag = 1

        while len(queue) > 0:

            visited_child = queue.pop(0)
            print "Visited Child:", visited_child.group_id

            if visited_child not in forceOptimizer.wide_search_queue and visited_child not in group.childs_east_sorted:
                forceOptimizer.wide_search_queue.append(visited_child)
                group.childs_east_sorted.append(visited_child)

            if visited_child.connected_parent_east and visited_child not in group.child_east:
                group.child_east.append(visited_child)
            if visited_child.connected_parent_north and visited_child not in group.child_north:
                group.child_north.append(visited_child)
            if visited_child.connected_parent_south and visited_child not in group.child_south:
                group.child_south.append(visited_child)
            if visited_child.connected_parent_west and visited_child not in group.child_west:
                group.child_west.append(visited_child)

            for neighbor in visited_child.neighbor_unsorted:

                print "Neighbor:", neighbor.group_id
                # only looking for neighbors in the same group and which are not allready discovered

                if neighbor.parent == visited_child.parent and neighbor.wide_search_flag == 0:
                    neighbor.wide_search_flag = 1
                    queue.append(neighbor)

            visited_child.wide_search_flag = 2

        # increment the number of connected to parent north/south/east/west
        sort_extern_neighbors(group.childs_east_sorted)

        # when all children / subgroups are visited
        # then we can start to sort the neighborhood of these childs in the group
        sort_unsorted_neighbor(group.childs_east_sorted)

        # when the wide search is finish with one group and her subgroups,
        # then starts a wide search on a group in the same level
        # or when all groups on one level where visited, then go to the next lower level
        # the algorithm produce a sequence in the wide_search_queue,
        # where groups of a higher level are in the first positions
        # and the groups of a lower level comes in the last part
        if len(forceOptimizer.wide_search_queue) > 0:
            wide_search(forceOptimizer)



def sort_extern_neighbors( east_list):

    for group in east_list:
        print "SORT EXTERN NEIGHBOR for:", str(group.group_id), "Neighbors count:", len(group.neighbor_extern)
        print "Group PArent Neighbor East count:", len(group.parent.neighbor_east)
        print "Group PArent Neighbor WEST count:", len(group.parent.neighbor_west)
        print "Group PArent Neighbor SOUTH count:", len(group.parent.neighbor_south)
        print "Group PArent Neighbor NORTH count:", len(group.parent.neighbor_north)
        if len(group.neighbor_extern):
            for neighbor in group.neighbor_extern:

                if neighbor.parent in group.parent.neighbor_east:
                    group.connected_parent_east += 1
                    neighbor.connected_parent_west += 1

                if neighbor.parent in group.parent.neighbor_west:
                    group.connected_parent_west += 1
                    neighbor.connected_parent_east += 1

                if neighbor.parent in group.parent.neighbor_north:
                    group.connected_parent_north += 1
                    neighbor.connected_parent_south += 1

                if neighbor.parent in group.parent.neighbor_south:
                    group.connected_parent_south += 1
                    neighbor.connected_parent_north += 1

        print "Group connected parent east:", group.connected_parent_east
        print "Group connected parent west:", group.connected_parent_west
        print "Group connected parent south:", group.connected_parent_south
        print "Group connected parent north:", group.connected_parent_north


def sort_unsorted_neighbor( east_list):
    '''
    '''
    groups = []

    for group in east_list:
        groups.append(group.group_id)

    print "Sort Unsorted Neighbor:", groups

    #go through all groups in their relative distance to out
    for group in east_list:
        print "Group in East List:", group.group_id

        #if the group has neighbor which are not sorted to north, south, east, west
        if len(group.neighbor_unsorted) > 0:

            print "Group connected to parent north:", group.connected_parent_north
            print "Group connected to parent south:", group.connected_parent_south
            print "Group connected to parent east:", group.connected_parent_east
            print "Group connected to parent west:", group.connected_parent_west

            #go through all unsorted neighbor
            for neighbor in group.neighbor_unsorted:

                #if the neighbor is connected to vcc and gnd
                if neighbor.connected_parent_north and neighbor.connected_parent_south:
                    #then the only legal position for the neighbor is west
                    add_neighbor_east_west(group, neighbor)
                    #such a neighbor is dominant an the west list have to close
                    group.listfull_west = True

                if neighbor.connected_parent_north and neighbor.connected_parent_south == 0 and group.connected_parent_north == 0:
                    # the neighbor has a parent NORTH connection but no parent SOUTH and the group herself have no connection to the parent NORTH
                    # than add the neighbor to the NORTH of the group
                    add_neighbor_north_south(neighbor, group)

                if neighbor.connected_parent_east and neighbor.connected_parent_west == 0 and group.connected_parent_east == 0:
                    # the neighbor has a parent EAST connection but no parent WEST connection and the group herself has no parent EAST connection
                    # than add
                    add_neighbor_east_west(neighbor, group)

                if neighbor.connected_parent_south and neighbor.connected_parent_north == 0 and group.connected_parent_south == 0:
                    # the neighbor has a parent SOUTH connection but no parent NORTH and the group herself have no connection to the parent SOUTH
                    # than add the neighbor to the SOUTH of the group
                    add_neighbor_north_south(group, neighbor)

                if neighbor.connected_parent_west and neighbor.connected_parent_east == 0 and group.connected_parent_west == 0:
                    # the neighbor has a parent WEST connection but no parent EAST connection and the group herself has no parent WEST connection
                    # than add
                    add_neighbor_east_west(group, neighbor)

                if neighbor.connected_parent_north and neighbor.connected_parent_south:
                    for block in group.neighbors[neighbor]:
                        group.block_west.append(block)

                    for block in neighbor.neighbors[group]:
                        neighbor.block_east.append(block)


                if neighbor.connected_parent_north and neighbor.connected_parent_south == 0 and group.connected_parent_north == 0:
                    for block in neighbor.neighbors[group]:
                        neighbor.block_south.append(block)

                    for block in group.neighbors[neighbor]:
                        group.block_north.append(block)

        print group

def group_compare(x, y):
    '''
    Sort groups by their group_id
    groups on the low level with long IDs came first
    '''
    return len(y.group_id) - len(x.group_id)

def group_compare_negative(x, y):
    '''
    Sort groups by their group_id
    groups on the high level with short IDs came first
    '''
    return len(x.group_id) - len(y.group_id)

def calculate_groups_frame(forceOptimizer):
    '''
    '''
    print ""
    print "====================="
    print "Calculate Group Frame"
    print "====================="
    print ""

    for group in forceOptimizer.groups:
        print "Group:", group.group_id

    forceOptimizer.groups = sorted(forceOptimizer.groups, cmp=group_compare)

    for group in forceOptimizer.groups:
        print "SortedGroup:", group.group_id

    groups = forceOptimizer.groups[:]
    groups.append(forceOptimizer.group_main)

    #go through every group
    for group in groups:

        width_south = 0
        width_north = 0
        height_east = 0
        height_west = 0

        if len(group.blocks) > 0:
            height_east = group.connected_out
            height_west = group.connected_inp
            width_south = group.connected_gnd
            width_north = group.connected_vcc

            for extern in group.neighbor_extern:
                if extern.parent in group.parent.neighbor_north:
                    width_north += len(group.neighbors[extern])
                if extern.parent in group.parent.neighbor_south:
                    width_south += len(group.neighbors[extern])
                if extern.parent in group.parent.neighbor_west:
                    height_west += len(group.neighbors[extern])
                if extern.parent in group.parent.neighbor_east:
                    height_east += len(group.neighbors[extern])

        if len(group.childs) > 0:
            for child in group.child_east:
                height_east += child.size_height
            for child in group.child_west:
                height_west += child.size_height
            for child in group.child_north:
                width_north += child.size_width
            for child in group.child_south:
                width_south += child.size_width

        print "Group:", group.group_id, "North:", width_north, "South:", width_south, "East:", height_east, "West:", height_west
        #the bigger width of north and south is the width for the group
        group.size_width = max({width_north, width_south})
        group.size_height = max({height_east, height_west})

        #if the group area is to small to place all blocks without overlapping
        while (group.size_height * group.size_width) < len(group.blocks):
            #increment the group width and height by 1
            group.size_width = group.size_width + 1
            group.size_height = group.size_height + 1

        print group

def calculate_groups_position(forceOptimizer):
    '''
    Only the position of the groups will be calculated
    starting with the high level group and set the positions of the childs
    position is relative to parent left upper corner
    '''
    print ""
    print "========================"
    print "Calculate Group Position"
    print "========================"
    print ""

    for group in forceOptimizer.groups:
        print "Group:", group.group_id

    forceOptimizer.groups = sorted(forceOptimizer.groups, cmp=group_compare_negative)

    for group in forceOptimizer.groups:
        group.position_x = -1
        group.position_y = -1
        print "SortedGroup:", group.group_id

    groups = forceOptimizer.groups[:]
    groups.insert(0, forceOptimizer.group_main)

    #go through every group
    for group in groups:

        for block in group.blocks:
            if block in group.block_south:
                block.pos[1] = group.size_height - 1
            elif block in group.block_north:
                block.pos[1] = 0
            else:
                block.pos[1] = group.size_height / 2

            if block in group.block_east:
                block.pos[0] = group.size_width - 1
            elif block in group.block_west:
                block.pos[0] = 0
            else:
                block.pos[0] = group.size_width / 2

            pins = ""
            for p in block.pins.values():
                pins += " " + p.net
            print "Block:", block.name, " Group:", group.group_id, " X:", block.pos[0], " Y:", block.pos[1], "Pins:", pins

        for child in group.childs:
            # children connected to NORTH and SOUTH have position y = 0 and are tall as the group
            if child in group.child_north and child in group.child_south:
                child.position_y = group.size_height / 2 - child.size_height / 2
                #child.size_height = group.size_height

            # children only connected to NORTH (not to SOUTH) have position y  = 0
            elif child in group.child_north:
                child.position_y = 0

            # children only connected to SOUTH (not to NORTH) touching the lower bound of the group
            elif child in group.child_south:
                child.position_y = group.size_height - child.size_height

            #children with no connection to NORTH or SOUTH
            else:
                #search for neighbors with north connection
                #find the highest and set the child under that neighbor
                max_height = 0
                for neighbor in child.neighbors:
                    if neighbor in group.child_north and max_height < neighbor.size_height:
                        max_height = 0 + neighbor.size_height
                if max_height:
                    child.position_y = max_height
                else:
                    #no neighbor in North, so check South
                    #search for neighbors with south connection
                    #find the highest and set the child over that neighbor
                    for neighbor in child.neighbors:
                        if neighbor in group.child_south and max_height < neighbor.size_height:
                            max_height = 0 + neighbor.size_height
                    if max_height:
                        child.position_y = group.size_height - max_height - child.size_height
                    else:
                        # placed child in the center
                        # overlapping is allowed and will be fixed in the force algorithm
                        child.position_y = group.size_height / 2 - child.size_height / 2

            # children connected to WEST and EAST have position x = 0 and are wide as the group
            if child in group.child_west and child in group.child_east:
                child.position_x = group.size_width / 2 - child.size_width / 2
                #child.size_width = group.size_width
            # children only connected to WEST (not to EAST) have position x  = 0
            elif child in group.child_west:
                child.position_x = 0
            # children only connected to EAST (not to WEST) touching the right bound of the group
            elif child in group.child_east:
                child.position_x = group.size_width - child.size_width
            #children with no connection to WEST or EAST
            else:
                #search for neighbors with west connection
                #find the biggest and set the child right to that neighbor
                max_width = 0
                for neighbor in child.neighbors:
                    if neighbor in group.child_west and max_width < neighbor.size_width:
                        max_width = 0 + neighbor.size_width
                if max_width:
                    child.position_x = max_width
                else:
                    #no neighbor in west, so check east
                    #search for neighbors with east connection
                    #find the biggest and set the child left to that neighbor
                    max_width = 0
                    for neighbor in child.neighbors:
                        if neighbor in group.child_east and max_width < neighbor.size_width:
                            max_width = 0 + neighbor.size_width
                    if max_width:
                        child.position_x = group.size_width - max_width - child.size_width
                    else:
                        # placed child in the center
                        # overlapping is allowed and will be fixed in the force algorithm
                        child.position_x = group.size_width / 2 - child.size_width / 2



    for group in groups:
        print group

def add_neighbor_north_south( group_north, group_south):
    '''
    '''
    group_north.neighbor_south.append(group_south)
    if group_south in group_north.neighbor_unsorted:
        group_north.neighbor_unsorted.remove(group_south)

    group_south.neighbor_north.append(group_north)
    if group_north in group_south.neighbor_unsorted:
        group_south.neighbor_unsorted.remove(group_north)

    for child in group_north.childs:
        for child_neighbor in child.neighbors:
            if child_neighbor.parent is group_south:
                child.connected_parent_south = child_neighbor.connected_parent_south + 1
                child_neighbor.connected_parent_north = child_neighbor.connected_parent_north + 1

def add_neighbor_east_west( group_east, group_west):
    '''
    '''
    group_east.neighbor_west.append(group_west)
    if group_west in group_east.neighbor_unsorted:
        group_east.neighbor_unsorted.remove(group_west)

    group_west.neighbor_east.append(group_east)
    if group_east in group_west.neighbor_unsorted:
        group_west.neighbor_unsorted.remove(group_east)

    for child in group_east.childs:
        for child_neighbor in child.neighbors:
            if child_neighbor.parent is group_west:
                child.connected_parent_west = child_neighbor.connected_parent_west + 1
                child_neighbor.connected_parent_east = child_neighbor.connected_parent_east + 1