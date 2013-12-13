# -*- coding: utf-8 -*-

import copy

"""
--> representing an abstract block of a circuit
--> including max 4 connections

           (0)
        ____o____
       |    |    |
  (3)  |o___|____|o (1)  <-- not inverted
       |    |    |
       |____|____|
            o
           (2)
        
"""


class BlockException(Exception):
    def __init__(self, msg):
        self.message += "[EXC] " + self.__class__.__name__ + ": " + msg
          
class PinNameDoesNotExist(BlockException):
    pass

class Block:
    def __init__(self, b_type, con_list=None, name=None, groups=None):
        self.type = b_type
        self.name = name
        self.groups = groups       
        
        self.conns = {}
        if con_list is not None:
            self.conns[0] = con_list[0]
            if len(con_list) == 3:
                self.conns[1] = con_list[1]
                self.conns[2] = con_list[2]
            else:
                self.conns[2] = con_list[1]

        self.has_vdd = "vdd" in self.conns.values()
        self.has_gnd = "gnd" in self.conns.values()
        self.is_biased = self.conns[1].startswith("vbias") \
            if 1 in self.conns else False
            
        # block is mirrored?
        self.mirrored = False
        # rotation: 0=0°, 1=-90°, 2=-180°, 3=-270°
        self.rotation = 0      
    
    def copy(self):
        out = Block(self.type)
        out.conns = copy.deepcopy(self.conns)
        out.mirrored = self.mirrored
        out.rotation = self.rotation
        out.has_vdd = self.has_vdd
        out.has_gnd = self.has_gnd
        out.name = self.name
        out.groups = self.groups
        return out
        
    def is_rot(self):
        return True if self.rotation != 0 else False
    
    def rotate(self, count=1):
        self.rotation = (self.rotation + count) % 4
    
    def has_pin(self, names):
        if not isinstance(names, (list, tuple)):
            names = [names]
        return all(name in self.conns.values() for name in names)
    
    def get_pin_direction(self, i):
        return (i + self.rotation + (2 if self.mirrored and i in [1, 3] else 0)) % 4
    
    def get_pin_direction_from_name(self, name, only_horiz=False):
        if not self.has_pin(name):
            raise PinNameDoesNotExist(name)
        
        for i, conn in self.conns.items():
            if conn == name:
                d = self.get_pin_direction(i)
                if not only_horiz:
                    return d
                elif only_horiz and d in [1, 3]:
                    return d
                
        return False
                    
    def get_name_from_direction(self, i):
        for k, name in self.conns.items():
            if self.get_pin_direction(k) == i:
                return name
        return False
        
    def get_pin_position(self, i, blk_pos=(0,0)):
        direction = self.get_pin_direction(i)
        if direction == 0:
            return (blk_pos[0]+1, blk_pos[1])
        elif direction == 1:
            return (blk_pos[0]+2, blk_pos[1]+1)
        elif direction == 2:
            return (blk_pos[0]+1, blk_pos[1]+2)                    
        elif direction == 3:
            return (blk_pos[0], blk_pos[1]+1) 

    def set_pin_orientation(self, name, dir_i, only_mirror=False):
        ops = [(0, False), (0, True), (2, False), (2, True)] if not only_mirror else \
              [(self.rotation, False), (self.rotation, True)]
            
        for rot, mir in ops:
            self.rotation = rot
            self.mirrored = mir
            if self.get_pin_direction_from_name(name, only_horiz=only_mirror) == dir_i:
                return True
            
        return False

    #def get_pin_from_position(self, pos, blk_pos=(0,0)):
    #    inner_pos = (pos[0] - blk_pos[0], pos[1] - blk_pos[1])
    #    if inner_pos == (1, 0):
    #        return 
    #
    #def get_pin_from_direction(self, direction):
        

    def __str__(self):
        return "<Block {0:4}{1:5} rot={3:1} mir={4:5} conns={2:23} name={5:3} groups={6}>".format(
                self.type[:4], 
                ":vdd" if self.has_vdd else (":gnd" if self.has_gnd else ""), 
                ", ".join(str(x) for x in self.conns.values()), 
                self.rotation, 
                "true" if self.mirrored else "false",
                self.name, str(self.groups)
        )
    __repr__ = __str__