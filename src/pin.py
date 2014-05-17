# -*- coding: utf-8 -*-

class PinNameDoesNotExist(Exception):
    def __init__(self, msg):
           self.message += "[EXC] " + self.__class__.__name__ + ": " + msg
   
class Pin:
    def __init__(self, parent, net_name, pos, horizontal=False, vertical=False):
        self.net = net_name
        self.horizontal = horizontal
        self.vertical = vertical
        
        self.supply = net_name.lower() == "vdd"
        self.gnd = net_name.lower() in ["gnd", "vss"]
        self.biased = net_name.startswith("vbias") and horizontal
        
        self.block = parent
        # relative position (inside block)
        self.pos = pos        
        # absolute position 
        self.blk_pos = property(lambda s: (s.block.pos[0] + s.pos[0], s.block.pos[1] + s.pos[1]))
        
    def copy(self, parent):
        return Pin(self, self.net, self.pos, self.horizontal, self.vertical)

    def __repr__(self):
        return "({0[0]},{0[1]} - {1})".format(self.pos, self.net)
