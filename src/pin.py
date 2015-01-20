# -*- coding: utf-8 -*-

class PinNameDoesNotExist(Exception):
    def __init__(self, msg):
           self.message += "[EXC] " + self.__class__.__name__ + ": " + msg
   
class Pin(object):

    # absolute position 
    blk_pos = property(lambda s: (s.block.pos[0] + s.pos[0], s.block.pos[1] + s.pos[1]))

    def __init__(self, parent, net_name, pos, horizontal=False, vertical=False, is_output=None, is_input=None):
        self.net = net_name
        self.horizontal = horizontal
        self.vertical = vertical 
        self.output = net_name.startswith("out") if is_output is None else is_output
        self.input = net_name.startswith("in") if is_input is None else is_input
        
        self.supply = net_name.lower() == "vdd"
        self.gnd = net_name.lower() in ["gnd", "vss"]
        self.biased = net_name.startswith("vbias") and horizontal
        
        self.block = parent
        # relative position (inside block)
        self.pos = pos        
        
    def copy(self, parent):
        return Pin(parent, self.net, self.pos, self.horizontal, self.vertical, self.output, self.input)

    def __repr__(self):
        return "({0[0]},{0[1]} - {1})".format(self.pos, self.net)
