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
        
        #TODO: How to get the OUT group?
        self.group_out = Group()
        self.group_gnd = Group()
        self.group_vcc = Group()
        
        self.gnd_list = list()
        self.vcc_list = list()
        self.out_list = list()
        
        
        self.create_groups(self)
        self.find_neighbors(self)
        self.initial_phase(self)
        

    '''
    
    Parameter group_ids: is an array with the IDs of the parent Groups and the ID of the searched group
    '''    
    def search_group(self,group_id, group_list):
        for group in group_list:
            if group.id == group_id:
                return group
        return None
                        
    '''
    Create the groups and add them to the list: groups
    '''
    def create_groups(self):
        
        #go through all blocks in circuit
        for block in self.blocks:

            group_parent = Group()
            group_list = self.groups
            g_id = []
            #go through all id fields in the block.groups list
            for group_id in block.groups:
                g_id.append(group_id)
                group = self.search_group(g_id,group_list)
               
                if group == None:
                    group = Group(g_id,group_parent)
                    group_list.append(group)
                    group_parent.sub_groups.append(group)
                
                group.add_blocks(block)
                group_list = group.sub_groups
                group_parent = group

                 
          
    '''
    Looking for the neighbors of the groups via pins information of blocks
    '''
    def find_neighbors(self):
       
        dictionary_net = {}
       
        for block in self.blocks:
            
            group = self.search_group(block.groups, self.groups)
            
            for pin in block.pins:
                if pin == "outp":
                    group.connected_out = True
                elif pin == "vdd":
                    group.connected_vcc = True
                elif pin == "gnd":
                    group.connected_gnd = True
                elif pin.containts("inp"):
                    group.connected_input = True    
                else:
                    if pin in dictionary_net:
                        group_list = dictionary_net[pin]
                        
                        group_list.append(group)
                    else:
                        dictionary_net[pin]=[group]
                
       
        for key in dictionary_net.keys():
            neighbor_list = dictionary_net[key]
            #connect each group in neighbor to each other
            for neighbor in neighbor_list:
                for group in neighbor_list:
                    if group is not neighbor:
                        group.add_neighbor(neighbor)
                
        

                            
   
    
    
    '''
    find the neighbors of the group via the pins of the block, 
    which are connected to pins from blocks in other groups
    '''        
    def get_groups_of_neighbor(self, group,block,pins):
        neighbors = []
        #go through all pins in the block
        for pin in pins:
            #TODO: Here I need a function to find the connection between to blocks
            #and to compare the groups 
            neighbor = pin.net 
            if neighbor is not group:
                neighbors.append(neighbor)
        return neighbors
    
    
    
    '''
    
    '''
    def initial_phase(self):
        #TODO: NOT FINISHED
        self.wide_search(self.group_out)
        #TODO: NOT FINISHED
        self.find_unsorted_neighbor()
        #TODO: FINISHED
        self.calculate_groups_frame()
        #TODO: NOT FINISHED
        self.calculate_groups_position()            
    
    
    '''
    Sorts the groups to the gnd / vcc / out list in their distance to out 
    and saved the distance in the distance_to_out variable of the groups
    '''
    def wide_search(self,group):
        
        #if the group is not in one of the lists 
        if group not in self.out_list: 
            self.out_list.append(group)
        if group.connected_vcc and group not in self.vcc_list:
            self.vcc_list.append(group)
        if group.connected_gnd and group not in self.gnd_list:
            self.gnd_list.append(group)    
        
        for neighbor in group.neighbors.keys():
          
            #if the algorithm finds a shorter way, update the distance
            if neighbor.distance_to_out > group.distance_to_out+1:
                neighbor.distance_to_out = group.distance_to_out +1 
            
            if neighbor not in self.out_list:
                self.wide_search(neighbor)
           
        #TODO: Wide Search 

                
        
    '''
    
    '''        
    def find_unsorted_neighbor(self):
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
                        if neighbor.connected_vcc & neighbor.connected_gnd:
                            #then the only legal position for the neighbor is west
                            self.add_neighbor_east_west(group, neighbor) 
                            #such a neighbor is dominant an the west list have to close
                            group.listfull_west = True  
                                    
    
    '''
    
    '''
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
            group.size_width =  max({width_north, width_south})
           
            height_east = 0
            height_west = 0
           
            for neighbor in group.neighbor_east:
                height_east += group.neighbors[neighbor]
            for neighbor in group.neighbor_west:
                height_west += group.neighbors[neighbor]  
            
            group.size_height =  max({height_east, height_west})
            
            #if the group area is to small to place all blocks without overlapping
            while (group.size_height * group.size_width) < len(group.blocks):
                #increment the group width and height by 1
                group.size_width += 1
                group.size_height += 1
            
                
        
    def add_neighbor_north_south(self,group_north,group_south):
        group_north.neighbor_south.append(group_south)
        group_north.neighbor_unsorted.remove(group_south)
        
        group_south.neighbor_north.append(group_north)
        group_south.neighbor_unsorted.remove(group_north)
        
    
        
    def add_neighbor_east_west(self,group_east,group_west):
        group_east.neighbor_west.append(group_west)
        group_east.neighbor_unsorted.remove(group_west)
        
        group_west.neighbor_east.append(group_east)
        group_west.neighbor_unsorted.remove(group_east)