'''
Created on 23.03.2014

@author: Christian Auth
'''
import itertools
from base_optimizer import BaseOptimizer
from field import Field, FieldException
from operator import itemgetter, attrgetter
from group import Group
from block import Block


class ForceAlgorithm(BaseOptimizer):
    '''
    '''
    def __init__(self, field, blocks):
        '''
        '''

        print "init Force Algorithm"

        BaseOptimizer.__init__(self, field)

        self.groups = []
        self.blocks = blocks
        self.wide_search_index = 0
        self.wide_search_queue = []

        # dictionary with pin.net_name as key and a block list as value
        self.dictionary_net_blocks = {}
        self.dictionary_vdd_blocks = {}
        self.dictionary_out_blocks = {}
        self.dictionary_gnd_blocks = {}
        self.dictionary_inp_blocks = {}
        self.dictionary_bia_blocks = {}

        self.group_out = Group([-1])
        self.group_gnd = Group([-2])
        self.group_vcc = Group([-3])
        self.group_main = Group([-4])

        self.group_out.neighbor_west.append(self.group_main)
        self.group_main.neighbor_east.append(self.group_out)

        self.group_vcc.neighbor_south.append(self.group_main)
        self.group_main.neighbor_north.append(self.group_vcc)

        self.group_main.neighbor_south.append(self.group_gnd)
        self.group_gnd.neighbor_north.append(self.group_main)

        self.create_groups()

        for group in self.groups:
            group.to_string()

        self.find_neighbors()

        for group in self.groups:
            group.to_string()

        self.initial_phase()

    def create_groups(self):
        '''
        DESCRIPTION:   Create the groups and add them to the list: groups
        STATE:         finish
        '''
        print ""
        print "============="
        print "Create Groups"
        print "============="
        print ""

        #go through all blocks in circuit
        for block in self.blocks:

            group_id = block.groups  # the lowest group get all IDs
            print "Block: ", block.name, " Group ID", group_id
            group = self.search_group(group_id)  # check if the group allready exists

            if group is None:  # create a new group if needed
                print ("Create a new Group with ID", group_id)
                group = Group(group_id)
                self.groups.append(group)

            #check the connection to important pins
            for p in block.pins.values():
                if p.net.lower() in ["gnd", "vss"]:
                    group.connected_gnd += 1
                    group.block_south.append(block)
                if p.net.lower() in ["vdd"]:
                    group.connected_vcc += 1
                    group.block_north.append(block)
                if p.net.lower() == "outp":
                    group.connected_out += 1
                    group.block_east.append(block)
                if p.net.lower().startswith("inp"):
                    group.connected_inp

            if group.connected_out > 0:
                group.connected_parent_east += group.connected_out
            if group.connected_gnd > 0:
                group.connected_parent_south += group.connected_gnd
            if group.connected_vcc > 0:
                group.connected_parent_north += group.connected_vcc

            #add the block to the low level group
            group.add_block(block)

            #if group has parents create them
            if len(group_id) > 1:
                self.create_parent(group)
            #else add group to main group
            else:
                self.group_main.add_child(group)
                group.parent = self.group_main

    def search_group(self, group_id):
        '''
        PARAMETER:  group_ids     is an array with the IDs of the parent Groups and the ID of the searched group
                    return        the group if it exists, else None
        STATE:      not finish
        '''
        for group in self.groups:
            if group.group_id == group_id:
                return group
        return None

    def create_parent(self, child):
        '''
        DESCRIPTION:    builds recursive the parents of the groupe, which containts the block
                        when the algo reached the last parent, it will add them to the main group
        PARAMETER:      child        The group which need a parent
        STATE:          finish
        '''

        print "create parent for child:", child.group_id

        group_id = child.group_id[:len(child.group_id) - 1]  # remove the last ID

        print "parents ID:", group_id

        group = self.search_group(group_id)  # check if the group allready exists

        if group is None:  # create a new group if needed
            group = Group(group_id)
            self.groups.append(group)
            print "Parent not exist, create a new Group"

        group.add_child(child)
        child.parent = group

        #check the connection to important pins
        group.connected_gnd = 0
        group.connected_vcc = 0
        group.connected_out = 0
        group.connected_inp = 0


        for c in group.childs:
            group.connected_gnd += c.connected_gnd
            group.connected_vcc += c.connected_vcc
            group.connected_out += c.connected_out
            group.connected_inp += c.connected_inp

        group.connected_parent_east = group.connected_out
        group.connected_parent_south = group.connected_gnd
        group.connected_parent_north = group.connected_vcc

        #if group has parents create them
        if len(group_id) > 1:
            self.create_parent(group)
        #else add group to main group
        else:
            self.group_main.add_child(group)
            group.parent = self.group_main

    def find_neighbors(self):
        '''
        DESCRIPTION:    Looking for the neighbors of the groups via pins information of the blocks
        STATE:          not finish
        '''
        print ""
        print "=============="
        print "Find Neighbors"
        print "=============="
        print ""

        print "------"
        print "Step 1"
        print "------"

        # go through all blocks in the circuit
        for block in self.blocks:

            # check all pins in the block
            for pin in block.pins.values():
                # if pin is not connected to a special pin
                if pin.net not in["outp", "vdd", "gnd", "vss"] and not pin.net.startswith("inp"):
                    # add the block to block list in the dictionary
                    if pin.net in self.dictionary_net_blocks:
                        if block not in self.dictionary_net_blocks[pin.net]:
                            self.dictionary_net_blocks[pin.net].append(block)
                    # if the pin.net_name key does not exists in the dictionary,
                    # create a block list with one element
                    else:
                        self.dictionary_net_blocks[pin.net] = [block]

        print "------"
        print "Step 2"
        print "------"
        # go over all collected nets
        for key in self.dictionary_net_blocks.keys():

            # get the list with the blocks connected to the net
            block_list = self.dictionary_net_blocks[key]
            print key, "Count Blocks:", len(block_list)
            # comaper the blocks in the list

            for pair in itertools.combinations(block_list, 2):
                block_1 = pair[0]
                block_2 = pair[1]
                print "Block1:", block_1.name, "Block2:", block_2.name
                group_1_id = []
                group_2_id = []

                #start with the high level groups
                for i in range(len(block_1.groups)):
                    group_1_id.append(block_1.groups[i])
                    group_2_id.append(block_2.groups[i])
                    print "Group1ID:", group_1_id, "Group2ID", group_2_id
                    # compare the group IDs and when they are different
                    # then connect the groups with each other
                    if group_1_id != group_2_id:
                        group_1 = self.search_group(group_1_id)
                        group_2 = self.search_group(group_2_id)
                        # if the groups are already connected, increment the connection number
                        group_1.add_neighbor(group_2, block_1)
                        group_2.add_neighbor(group_1, block_2)


    def initial_phase(self):
        '''
        '''
        print ""
        print "============="
        print "Initial Phase"
        print "============="
        print ""

        # the main group is the only group on the highest level, so the queue starts with her
        self.wide_search_queue.append(self.group_main)
        self.wide_search()

        self.calculate_groups_frame()

        self.calculate_groups_position()

    def wide_search(self):
        '''
        Description:    Sorts the groups to the gnd / vcc / out list in their distance to out
        '''
        print "\nWide Search"
        print "Wide Search Queue count:", len(self.wide_search_queue)
        # get the first group of the queue to start a wide search on her over her subgroups
        group = self.wide_search_queue.pop(0)
        print "Group ID:", group.group_id, " Count Group Childs: ", len(group.childs)

        if len(group.childs) == 0:
            if len(self.wide_search_queue) > 0:
                self.wide_search()
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

                if visited_child not in self.wide_search_queue and visited_child not in group.childs_east_sorted:
                    self.wide_search_queue.append(visited_child)
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

            # when all children / subgroups are visited
            # then we can start to sort the neighborhood of these childs in the group
            self.sort_unsorted_neighbor(group.childs_east_sorted)

            # when the wide search is finish with one group and her subgroups,
            # then starts a wide search on a group in the same level
            # or when all groups on one level where visited, then go to the next lower level
            # the algorithm produce a sequence in the wide_search_queue,
            # where groups of a higher level are in the first positions
            # and the groups of a lower level comes in the last part
            if len(self.wide_search_queue) > 0:
                self.wide_search()

    def sort_unsorted_neighbor(self, east_list):
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

                    if neighbor.parent is group.parent:

                        #if the neighbor is connected to vcc and gnd
                        if neighbor.connected_parent_north and neighbor.connected_parent_south:
                            #then the only legal position for the neighbor is west
                            self.add_neighbor_east_west(group, neighbor)
                            #such a neighbor is dominant an the west list have to close
                            group.listfull_west = True
                        if neighbor.connected_parent_north and neighbor.connected_parent_south == 0 and group.connected_parent_north == 0:
                            self.add_neighbor_north_south(neighbor, group)

                    else:
                        group.neighbor_extern.append(neighbor)
                        group.neighbor_unsorted.remove(neighbor)

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

            group.to_string()

    def group_compare(self, x, y):
        '''
        Sort groups by their group_id
        groups on the low level with long IDs came first
        '''
        return len(y.group_id) - len(x.group_id)

    def group_compare_negative(self, x, y):
        '''
        Sort groups by their group_id
        groups on the high level with short IDs came first
        '''
        return len(x.group_id) - len(y.group_id)

    def calculate_groups_frame(self):
        '''
        '''
        print ""
        print "====================="
        print "Calculate Group Frame"
        print "====================="
        print ""

        for group in self.groups:
            print "Group:", group.group_id

        self.groups = sorted(self.groups, cmp=self.group_compare)

        for group in self.groups:
            print "SortedGroup:", group.group_id

        groups = self.groups[:]
        groups.append(self.group_main)

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

            group.to_string()

    def calculate_groups_position(self):
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

        for group in self.groups:
            print "Group:", group.group_id

        self.groups = sorted(self.groups, cmp=self.group_compare_negative)

        for group in self.groups:
            group.position_x = -1
            group.position_y = -1
            print "SortedGroup:", group.group_id

        groups = self.groups[:]
        groups.insert(0, self.group_main)

        #go through every group
        for group in groups:

            for block in group.blocks:
                if block in group.block_south:
                    block.position_y = group.size_height - 1
                elif block in group.block_north:
                    block.position_y = 0
                else:
                    block.position_y = group.size_height / 2

                if block in group.block_east:
                    block.position_x = group.size_width - 1
                elif block in group.block_west:
                    block.position_x = 0
                else:
                    block.position_x = group.size_width / 2
                print "Block:", block.name, " Group:", group.group_id, " X:", block.position_x, " Y:", block.position_y, "\n"

            for child in group.childs:
                #children connected to NORTH and SOUTH have position y = 0 and are tall as the group
                if child in group.child_north and child in group.child_south:
                    child.position_y = 0
                    child.size_height = group.size_height
                #children only connected to NORTH (not to SOUTH) have position y  = 0
                elif child in group.child_north:
                    child.position_y = 0
                #children only connected to SOUTH (not to NORTH) touching the lower bound of the group
                elif child in group.child_south:
                    child.position_y = group.size_height - child.size_height
                #children with no connection to NORTH or SOUTH are placed in the center
                #overlapping is allowed and will be fixed in the force algorithm
                else:
                    child.position_y = group.size_height/2 - child.size_height/2

                #children connected to WEST and EAST have position x = 0 and are wide as the group
                if child in group.child_west and child in group.child_east:
                    child.position_x = 0
                    child.size_width = group.size_width
                #children only connected to WEST (not to EAST) have position x  = 0
                elif child in group.child_west:
                    child.position_x = 0
                #children only connected to EAST (not to WEST) touching the right bound of the group
                elif child in group.child_east:
                    child.position_x = group.size_width - child.size_width
                #children with no connection to WEST or EAST are placed in the center
                #overlapping is allowed and will be fixed in the force algorithm
                else:
                    child.position_x = group.size_width/2 - child.size_width/2

        for group in groups:
            group.to_string()

    def add_neighbor_north_south(self, group_north, group_south):
        '''
        '''
        group_north.neighbor_south.append(group_south)
        group_north.neighbor_unsorted.remove(group_south)

        group_south.neighbor_north.append(group_north)
        group_south.neighbor_unsorted.remove(group_north)

        for child in group_north.childs:
            for child_neighbor in child.neighbors:
                if child_neighbor.parent is group_south:
                    child.connected_parent_south = child_neighbor.connected_parent_south + 1
                    child_neighbor.connected_parent_north = child_neighbor.connected_parent_north + 1

    def add_neighbor_east_west(self, group_east, group_west):
        '''
        '''
        group_east.neighbor_west.append(group_west)
        group_east.neighbor_unsorted.remove(group_west)

        group_west.neighbor_east.append(group_east)
        group_west.neighbor_unsorted.remove(group_east)

        for child in group_east.childs:
            for child_neighbor in child.neighbors:
                if child_neighbor.parent is group_west:
                    child.connected_parent_west = child_neighbor.connected_parent_west + 1
                    child_neighbor.connected_parent_east = child_neighbor.connected_parent_east + 1