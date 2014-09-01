'''
Created on 23.08.2014

@author: christian auth

'''

from block import Block

class Group:
    
    def __init__(self, group_id, parent):
       
        #set the ID of the group
        self.group_id = group_id
        
        #set the parent group
        self.parent = parent
        
       
        #Frame size and origin
        self.size_width = 0
        self.size_height = 0
        self.position_x = 0
        self.position_y = 0
       
        #Lists includes the groups in the neighborhood relative to their position
        self.neighbor_north = list()
        self.neighbor_south = list()
        self.neighbor_west = list()
        self.neighbor_east = list()
       
        #List with all neighbor-groups, which are not sorted in a list from above
        self.neigbor_unsorted = list()
       
        #Dictionary to count the connections between the groups
        self.neighbors = {}
        
        #List with all elements in this group
        self.blocks = list()
        
        #
        self.distance_to_out = 0
        
        #flags
        self.connected_vcc = False
        self.connected_gnd = False
        self.connected_out = False
        self.connected_input = False
        
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
            self.neigbor_unsorted.append(neighbor)
        
        
                                          
           
    def add_block(self,block):
      
        self.blocks.append(block)     
       
    
    
    '''
    function searches if an other group is the neighbor of this group
    Parameter return:   0: NORTH
                        1: SOUTH
                        2: EAST
                        3: WEST
                        4: Unsorted
                       -1: NO neighbor 
    '''
    def are_neighbor(self,group):
        
        for neighbor in self.neighbor_north:
            if neighbor == group:
                return 0 # means NORTH
        
        for neighbor in self.neighbor_south:
            if neighbor == group:
                return 1 # means SOUTH
            
        for neighbor in self.neighbor_east:
            if neighbor == group:
                return 2 # means EAST
        
        for neighbor in self.neighbor_west:
            if neighbor == group:
                return 3 # means WEST
        
        for neighbor in self.neigbor_unsorted:
            if neighbor == group:
                return 4 # means Unsorted
        
        return -1
    