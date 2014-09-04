'''
Created on 23.03.2014

@author: Christian Auth
'''

from base_optimizer import BaseOptimizer
from field import Field, FieldException

from group import Group
from block import Block


class ForceAlgorithm(BaseOptimizer):

    def __init__(self, field, blocks):

        BaseOptimizer.__init__(self, field)

        self.groups = list()
        self.blocks = blocks
        self.wide_search_index = 0

        # dictionary with pin.net_name as key and a block list as value
        self.dictionary_net_blocks = {}

        self.group_out = Group([-1])
        self.group_gnd = Group([-2])
        self.group_vcc = Group([-3])
        self.group_main = Group([-4])

        self.add_neighbor_east_west(self.group_out, self.group_main)
        self.add_neighbor_north_south(self.group_vcc, self.group_main)
        self.add_neighbor_north_south(self.group_main, self.connected_gnd)

        self.create_groups(self)

        self.find_neighbors(self)

        self.initial_phase(self)


    def create_groups(self):
        '''
        DESCRIPTION:   Create the groups and add them to the list: groups
        STATE:         finish
        '''
        #go through all blocks in circuit
        for block in self.blocks:

            group_id = block.groups  # the lowest group get all IDs
            #TODO: invalid syntax???
            Group group = self.search_group(group_id)  # check if the group allready exists

            if group is None:  # create a new group if needed
                Group group = Group(group_id)
                self.groups.append(group)

            #check the connection to important pins
            group.connected_gnd = any(p.net.lower() in ["gnd", "vss"] for p in block.pins.values())
            group.connected_vcc = any(p.net.lower() == "vdd" for p in block.pins.values())
            group.connected_out = any(p.net.lower() == "outp" for p in block.pins.values())
            group.connected_inp = any(p.net.lower().startswith("inp") for p in block.pins.values())

            #add the block to the low level group
            group.add_block(block)

            #if group has parents create them
            if len(group_id) > 1:
                self.create_parent(group)
            #else add group to main group
            else:
                self.group_main.add_child(group)


    def search_group(self, group_id):
        '''
        PARAMETER:  group_ids     is an array with the IDs of the parent Groups and the ID of the searched group
                    return        the group if it exists, else None
        STATE:      not finish
        '''
        #TODO: better with exception handling
        #TODO: this returns a boolean not a groop
        return any(group.id == group_id for group in self.groups)


    def create_parent(self, child):
        '''
        DESCRIPTION:    builds recursive the parents of the groupe, which containts the block
                        when the algo reached the last parent, it will add them to the main group
        PARAMETER:      child        The group which need a parent
        STATE:          finish
        '''
        group_id = child.group_id[:len(child.group_id) - 1]  # remove the last ID
        Group group = self.search_group(group_id)  # check if the group allready exists

        if group is None:  # create a new group if needed
            Group group = Group(group_id)
            self.groups.append(group)

        group.add_child(child)

        #check the connection to important pins
        group.connected_gnd = any(c.connected_gnd for c in group.childs)
        group.connected_vcc = any(c.connected_vcc for c in group.childs)
        group.connected_out = any(c.connected_out for c in group.childs)
        group.connected_inp = any(c.connected_inp for c in group.childs)

        if group.connected_out:
            group.connected_parent_east = True

        #if group has parents create them
        if len(group_id) > 1:
            self.create_parent(group)
        #else add group to main group
        else:
            self.group_main.add_child(group)


    def find_neighbors(self):
        '''
        DESCRIPTION:    Looking for the neighbors of the groups via pins information of the blocks
        STATE:          not finish
        '''
        # go through all blocks in the circuit
        for block in self.blocks:

            # check all pins in the block
            for pin in block.pins:
                # if pin is not connected to a special pin
                if pin.net_name not in["outp", "vdd", "gnd", "inp", "vss"]:
                    # add the block to block list in the dictionary
                    if pin in dictionary_net:
                        block_list = self.dictionary_net_blocks[pin.net_name]
                        block_list.append(block)
                    # if the pin.net_name key does not exists in the dictionary,
                    # create a block list with one element
                    else:
                        self.dictionary_net_blocks[pin.net_name] = [block]

        # go over all collected nets
        for key in dictionary_net.keys():

            # get the list with the blocks connected to the net
            block_list = dictionary_net[key]

            # comaper the blocks in the list
            #TODO: bad style, too many loops
            for block_1 in block_list:
                for block_2 in block_list:
                    group_1_id = []
                    group_2_id = []
                    #start with the high level groups
                    for i, j in block_1.groups, block_2.groups:
                        group_1_id.append(i)
                        group_2_id.append(j)
                        # compare the group IDs and when they are different
                        # then connect the groups with each other
                        if group_1_id not group_2_id:
                            group_1 = self.search_group(group_1_id)
                            group_2 = self.search_group(group_2_id)
                            # if the groups are already connected, increment the connection number
                            group_1.add_neighbor(group_2)
                            group_2.add_neighbor(group_1)


    def initial_phase(self):
        '''
        '''
        # looking for a child with connection to the parents east neighbors
        start = Group()
        for child in self.group_main.childs:
            if child.connected_parent_east is True:
                start = child
                break
        self.group_main.childs_east_sorted.append(start)
        self.wide_search(self.group_main, start)

        self.sort_unsorted_neighbor()

        self.calculate_groups_frame()

        self.calculate_groups_position()


    #TODO: This is a one level version
    def wide_search(self, group, child):
        '''
        Description:    Sorts the groups to the gnd / vcc / out list in their distance to out
        '''
        neighbors = child.neigbor_unsorted

        while len(neighbors) > 0:
            neighbor = neighbors.pop()

            # check if the neighbor has the same parent like the child
            if neighbor in group.childs:

                if neighbor not in group.childs_east_sorted:
                    group.childs_east_sorted.append(neighbor)

                    # check neighbor has connection to group.neighbor_east and then add child to group.child_east
                    self.search_extern_neighbors(neighbor, group.neighbor_east, group.child_east)
                    # check neighbor has connection to group.neighbor_west and then add child to group.child_west
                    self.search_extern_neighbors(neighbor, group.neighbor_west, group.child_west)
                    # check neighbor has connection to group.neighbor_north and then add child to group.child_north
                    self.search_extern_neighbors(neighbor, group.neighbor_north, group.child_north)
                    # check neighbor has connection to group.neighbor_south and then add child to group.child_south
                    self.search_extern_neighbors(neighbor, group.neighbor_south, group.child_south)

        # till every child was visited
        if len(group.childs) is not len(group.childs_east_sorted):
            self.wide_search_index += 1
            child_new = group.childs_east_sorted[self.wide_search_index]
            self.wide_search(group, child_new)
        # jump to next lower level (deep search)
        else:
            for parent in group.childs_east_sorted:
                self.wide_search_index = 0
                # looking for a child with connection to the parents east neighbors
                start = Group()
                for child_new in parent.childs:
                    if child_new.connected_parent_east is True:
                        start = child_new
                        break
                parent.childs_east_sorted.append(start)
                self.wide_search(parent, start)

    def search_extern_neighbors(self, neighbor, neighbor_list, child_list):
        for parent_neighbor in neighbor_list:
            for neighb in neighbor.neigbor_unsorted:
                if parent_neighbor is neighb.parent:
                    if neigbhor not in child_list
                        child_list.append(neighbor)
                        child_list.append(neighbor)


    def sort_unsorted_neighbor(self):
        #go through all groups in their relative distance to out
        for group in self.out_list:
            #if the group has neighbor which are not sorted to north, south, east, west
            if len(group.neigbor_unsorted) > 0:

                #if north and south is full, then the only legal position for the not sorted neighbor is west
                if group.listfull_north and group.listfull_south and not group.listfull_east:
                    for neighbor in group.neigbor_unsorted:
                        self.add_neighbor_east_west(group, neighbor)

                #if north and west is full, then the only legal position for the not sorted neighbor is south
                elif group.listfull_north and group.listfull_west and not group.listfull_south:
                    for neighbor in group.neigbor_unsorted:
                        self.add_neighbor_north_south(group, neighbor)

                #if south and west is full, then the only legal position for the not sorted neighbor is north
                elif group.listfull_south and group.listfull_west and not group.listfull_north:
                    for neighbor in group.neigbor_unsorted:
                        self.add_neighbor_north_south(neighbor, group)

                else:
                    #go through all unsorted neighbor
                    for neighbor in group.neigbor_unsorted:
                        #if the neighbor is connected to vcc and gnd
                        if neighbor.connected_vcc and neighbor.connected_gnd:
                            #then the only legal position for the neighbor is west
                            self.add_neighbor_east_west(group, neighbor)
                            #such a neighbor is dominant an the west list have to close
                            group.listfull_west = True


    def calculate_group_frame(self):
        #go through every group
        for group in self.groups:

            width_south = 0
            width_north = 0

            #the width_south is the number of blocks which are connected with neighbors in the south
            for neighbor in group.neighbor_south:
                width_south += group.neighbors[neighbor]
            for neighbor in group.neighbor_north:
                width_north += group.neighbors[neighbor]

            #the bigger width of north and south is the width for the group
            group.size_width = max({width_north, width_south})

            height_east = 0
            height_west = 0

            for neighbor in group.neighbor_east:
                height_east += group.neighbors[neighbor]
            for neighbor in group.neighbor_west:
                height_west += group.neighbors[neighbor]

            group.size_height = max({height_east, height_west})

            #if the group area is to small to place all blocks without overlapping
            while (group.size_height * group.size_width) < len(group.blocks):
                #increment the group width and height by 1
                group.size_width += 1
                group.size_height += 1

    def add_neighbor_north_south(self, group_north, group_south):
        group_north.neighbor_south.append(group_south)
        group_north.neighbor_unsorted.remove(group_south)

        group_south.neighbor_north.append(group_north)
        group_south.neighbor_unsorted.remove(group_north)

    def add_neighbor_east_west(self, group_east, group_west):
        group_east.neighbor_west.append(group_west)
        group_east.neighbor_unsorted.remove(group_west)

        group_west.neighbor_east.append(group_east)
        group_west.neighbor_unsorted.remove(group_east)
