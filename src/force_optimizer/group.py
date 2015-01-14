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

        self.is_bias = False
        self.is_bias_connected = False
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
        self.blocks = set()
        self.block_north = set()
        self.block_south = set()
        self.block_west = set()
        self.block_east = set()

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

    def add_neighbor(self,neighbor,block):

        if neighbor in self.neighbors.keys():
            self.neighbors[neighbor].append(block)
        else:
            self.neighbors[neighbor] = [block]
            if neighbor.parent is self.parent:
                self.neighbor_unsorted.append(neighbor)
            else:
                self.neighbor_extern.append(neighbor)

    def add_block(self,block):
        self.blocks.add(block)

    def add_child(self, child):
        if self.childs.count(child) == 0:
            self.childs.append(child)

    def __str__(self):
        nl = "\n"
        less_padding = 16
        padding = 20
        more_padding = 24

        # header (group_id + size + pos)
        o = "" + nl
        o += "+------------------------------------------" + nl
        o += "| {}: {} - Size: {}x{} - Pos: {}x{}{}".format("Group", self.group_id,
                self.size_width, self.size_height,
                self.position_x, self.position_y, nl, pad=less_padding)
        o += "+------------------------------------------" + nl

        #show is bias
        if self.is_bias:
            o += "|{:>{pad}} {}".format("BIAS", nl, pad=padding)
        # show parent
        if self.parent is not None:
            o += "|{:>{pad}}: {}{}".format("Parent", self.parent.group_id, nl, pad=padding)

        # list children
        children = []
        for child in self.childs:
            children.append(child.group_id)
        o += "|{:>{pad}}: {}{}".format("Children", children, nl, pad=padding)

        o += "|{:>{pad}}: {}{}".format("Blocks", ", ".join(b.name for b in self.blocks), nl, pad=padding)
        # list all blocks
        n_types = (("EAST", self.block_east),
                   ("WEST", self.block_west),
                   ("NORTH", self.block_north),
                   ("SOUTH", self.block_south))
        for direction, data in n_types:
            if len(data) > 0:
                o += "|{:>{pad}}: {}{}".format(
                        direction, ", ".join(str(n.name) for n in data), nl, pad=more_padding)
        # connected to which ports
        c_types = (("OUT", self.connected_out),
                   ("VDD", self.connected_vcc),
                   ("GND", self.connected_gnd))
        _c = ["{}: {}".format(name, num) for name, num in c_types if num]
        o += "|{:>{pad}}: {} {}".format("Connected to", ", ".join(_c), nl, pad=padding)

        # neighbor count
        o += "|{:>{pad}}: ".format("Neighbors", pad=padding)
        if len(self.neighbors) > 0:
            o += ", ".join(("{}x {}".format(len(v), k.group_id)) for k, v in self.neighbors.items())
        o += nl

        # list all neighbors
        n_types = (("EAST", self.neighbor_east),
                   ("WEST", self.neighbor_west),
                   ("NORTH", self.neighbor_north),
                   ("SOUTH", self.neighbor_south))
        for direction, data in n_types:
            if len(data) > 0:
                o += "|{:>{pad}}: {}{}".format(
                        direction, ", ".join(str(n.group_id) for n in data), nl, pad=more_padding)

        # show unsorted neighbors
        o += "|{:>{pad}}: ".format("Unsorted Neighbors", pad=padding)
        o += "{}{}".format("", ", ".join(str(n.group_id) for n in self.neighbor_unsorted ), nl, pad=padding)
        o +=  nl

        # show extern neighbors
        o += "|{:>{pad}}: ".format("Extern Neighbors", pad=padding)
        o += "{}{}".format("", ", ".join(str(n.group_id) for n in self.neighbor_extern ), nl, pad=padding)
        o +=  nl

        # show parent's neighbor conns
        p_con_type = (("EAST", self.connected_parent_east),
                      ("WEST", self.connected_parent_west),
                      ("NORTH", self.connected_parent_north),
                      ("SOUTH", self.connected_parent_south))
        o += "|{:>{pad}}  {}".format("Parent's neighbor", nl, pad=padding)
        o += "|{:>{pad}}: {}{}".format("connections",
                ", ".join(("{}:{}".format(key, data)) \
                          for key, data in p_con_type if data), nl, pad=padding)

        # footer
        o += "+------------------------------------------" + nl
        o +=  nl
        return o

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
