'''
Created on 23.08.2014

@author: christian auth

'''

from block import Block

class Group:

    def __init__(self, group_id):

        #set the ID of the group
        self.group_id = group_id

        #set the parent group
        self.parent = None
        self.childs = []

        #Frame size and origin
        self.size_width = 0
        self.size_height = 0
        self.position_x = 0
        self.position_y = 0

        #Lists includes the groups in the neighborhood relative to their position
        self.neighbor_north = []
        self.neighbor_south = []
        self.neighbor_west = []
        self.neighbor_east = []
        #List with all neighbor-groups, which are not sorted in a list from above
        self.neighbor_unsorted = []

        #Lists includes the neighbors which are not in the parent group
        self.neighbor_north_extern = []
        self.neighbor_south_extern = []
        self.neighbor_west_extern = []
        self.neighbor_east_extern = []
        self.neighbor_extern = []

        # Lists includes childs with connection to the neighbor of the group
        self.child_north = []
        self.child_south = []
        self.child_west = []
        self.child_east = []
        self.childs_east_sorted = []

        #Dictionary to count the connections between the groups
        self.neighbors = {}

        #List with all elements in this group
        self.blocks = []

        #
        self.distance_to_out = 0

        #flags
        self.connected_vcc = 0
        self.connected_gnd = 0
        self.connected_out = 0
        self.connected_inp = 0

        self.wide_search_flag = 0  # 0:not discover, 1: discover, 2: visited

        self.connected_parent_east = 0
        self.connected_parent_north = 0
        self.connected_parent_south = 0
        self.connected_parent_west = 0

        self.listfull_north = False
        self.listfull_south = False
        self.listfull_east = False
        self.listfull_west = False

    def add_neighbor(self,neighbor):

        if neighbor in self.neighbors.keys():
            value = self.neighbors[neighbor]
            value += 1
            self.neighbors[neighbor] = value
        else:
            self.neighbors[neighbor] = 1
            self.neighbor_unsorted.append(neighbor)

    def add_block(self,block):
        self.blocks.append(block)

    def add_child(self, child):
        if self.childs.count(child) == 0:
            self.childs.append(child)

    def to_string(self):
        print ""
        print "+------------------------------------------"
        print "| Group:", self.group_id
        print "+------------------------------------------"
        if self.parent is not None:
            print "|    Parent:", self.parent.group_id

        children = []
        for child in self.childs:
            children.append(child.group_id)
        print "|    Children:", children

        blocks = []
        for block in self.blocks:
            blocks.append(block.name)
        print "|    Blocks:", blocks

        print "|    Connected to:", ("OUT:"+ str( self.connected_out)) if self.connected_out else '', ("VDD:"+ str( self.connected_vcc)) if self.connected_vcc else '', ("GND:"+ str( self.connected_gnd)) if self.connected_gnd else ''
        s = ""

        for key, value in self.neighbors.items():
            s = s + str(value) + "x " + str(key.group_id) + ", "
        print "|    Neighbors:"
        print "|        ", s
        neighbors = []
        for neighbor in self.neighbor_east:
            neighbors.append(neighbor.group_id)
        print "|        EAST:", neighbors
        neighbors = []
        for neighbor in self.neighbor_west:
            neighbors.append(neighbor.group_id)
        print "|        WEST:", neighbors
        neighbors = []
        for neighbor in self.neighbor_north:
            neighbors.append(neighbor.group_id)
        print "|        NORTH:", neighbors
        neighbors = []
        for neighbor in self.neighbor_south:
            neighbors.append(neighbor.group_id)
        print "|        SOUTH:", neighbors

        print "|    Connected to parent's neighbor:", "EAST" if self.connected_parent_east else '', "NORTH" if self.connected_parent_north else '', "SOUTH" if self.connected_parent_south else '', "WEST" if self.connected_parent_west else ''


        print "|    Frame:"
        print "|        width:", self.size_width
        print "|        height:",self.size_height
        print "|        x:",self.position_x
        print "|        y:",self.position_y
        print "+------------------------------------------"
        print ""

    def are_neighbor(self, group):
        '''
        function searches if an other group is the neighbor of this group
        Parameter return:   0: NORTH
                            1: SOUTH
                            2: EAST
                            3: WEST
                            4: Unsorted
                           -1: NO neighbor
        '''
        for neighbor in self.neighbor_north:
            if neighbor == group:
                return 0  # means NORTH

        for neighbor in self.neighbor_south:
            if neighbor == group:
                return 1  # means SOUTH

        for neighbor in self.neighbor_east:
            if neighbor == group:
                return 2  # means EAST

        for neighbor in self.neighbor_west:
            if neighbor == group:
                return 3  # means WEST

        for neighbor in self.neigbor_unsorted:
            if neighbor == group:
                return 4  # means Unsorted

        return -1
