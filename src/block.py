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

class XYPoint:
    def __init__(self, pos_or_x, y=None):
        self.__xy = (0, 0)
        self.x = property(lambda s: s.__xy[0], self.__setterX)
        self.y = property(lambda s: s.__xy[1], self.__setterY)
        self.pos = property(lambda s: s.__xy, self.__setterXY)        
 
    def __setterX(self, val):
        assert val is not None
        self.__xy = self.__valid_pos((val, self.__xy[1]))
        
    def __setterXY(self, val):
        assert val is not None
        self.__xy = self.__valid_pos((self.__xy[0], val))
        
    def __setterXY(self, val):
        assert val is not None
        self.__xy = self.__validPos(val)
            
    def __valid_pos(self, pos):
        """Either enforce int() or float()"""
        #x = float(pos[0])
        #y = float(pos[1])
        x = int(pos[0])
        y = int(pos[1])
        return (x, y)


class Pos:
    def __init__(self, pos_or_x, y=None):
        pass
        #self.
        #if isinstance(pos_or_x, Pos):
        #    self.

class Area:
    pass


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


class Block:
    def __init__(self, b_type, pins=None, name=None, groups=None, size=(2,2), parent=None):
        self.type = b_type
        self.name = name
        self.groups = groups
        
        # size-range: 2x2 to NxM, x and y must be even
        assert size[0] % 2 == 0 and size[1] % 2 == 0
        self.size = size
        
        # containing field
        self.field = parent
        
        # get from parent, if available
        self.pos = property(self.__pos_getter)            
            
        # pin positions
        self.pins = {}
        
        # block is mirrored?
        self.mirrored = False
        
        # rotation: 0=0°, 1=-90°, 2=-180°, 3=-270°
        # rotation is clock-wise!
        self.rotation = 0
        self.__rot_origin = (self.size[0]/2, self.size[1]/2)
        
        if pins is not None:
            self.pins[(1, 0)] = Pin(self, pins[0], (1, 0), False, True)
            # mos-device
            if len(pins) == 3:
                self.pins[(2, 1)] = Pin(self, pins[1], (2, 1), True, False)
                self.pins[(1, 2)] = Pin(self, pins[2], (1, 2), False, True)
            # two-port device
            else:
                self.pins[(1, 2)] = Pin(self, pins[1], (1, 2), False, True)

        self.has_vdd = any(p.supply for p in self.pins.values())
        for i in xrange(3):
            if any(self.get_pin_direction(p) != 0 and p.vertical \
                   for p in self.pins.values() if p.supply):
                self.rotate(1)
            else:
                break
            
        self.has_gnd = any(p.gnd for p in self.pins.values())
        for i in xrange(3):
            if any(self.get_pin_direction(p) != 2 and p.vertical \
                   for p in self.pins.values() if p.gnd):
                self.rotate(1)
            else:
                break    
            
        self.is_biased = any(p.biased for p in self.pins.values())
        for i in xrange(3):
            if any(self.get_pin_direction(p) not in [1, 3] and p.horizontal \
                   for p in self.pins.values() if p.biased):
                self.rotate(1)
            else:
                break
        
        
    def __pos_getter(self):    
        # never call this before assigning block to a field
        assert self.field
        # if this rings, block is not owned by field or vice-versa                
        assert self in self.field
        return self.field[self]
    
    def copy(self, parent):
        out = Block(self.type)
        out.pins = [p.copy(out) for p in self.pins.values()]
        out.mirrored = self.mirrored
        out.rotation = self.rotation
        
        out.has_vdd = self.has_vdd
        out.is_biased = self.is_biased
        out.has_gnd = self.has_gnd
        
        out.name = self.name
        out.groups = self.groups
        
        out.size = self.size
        out.field = parent or self
        
        return out
        
    def is_rot(self):
        return True if self.rotation != 0 else False
    
    def __rot_pos(self, pos, times, origin=(0,0)):
        """clock-wise"""
        new_pos = pos
        # change idx from counter-clock-wise to clock-wise        
        for i in xrange(4 - times):
            # first move to origin
            o_x, o_y = new_pos[0] - origin[0], new_pos[1] - origin[1]
            # rotate 90° clock-wise
            r_x, r_y = (o_y, o_x*-1) 
            # move back from origin
            new_pos = (r_x + origin[0], r_y + origin[1])
        return new_pos
            
    
    def rotate(self, count=2):
        """rotate 'count' times CLOCK-WISE"""
        new_pins = {}
        rot = count % 4
        if rot == 0:
            return 
        
        self.rotation = (self.rotation + rot) % 4
        for pos, pin in self.pins.items():
            pin.pos = self.__rot_pos(pos, rot, self.__rot_origin)
            new_pins[pin.pos] = pin
        
        self.pins = new_pins
        
        # rot 1 or 3: (switch x and y size for 90° & 270°)
        if rot % 2 == 1:
            self.size = (self.size[1], self.size[0])

    def mirror(self, set_to=None):
        if set_to is None:
            self.mirrored = not self.mirrored
        else:
            if self.mirrored == set_to:
                return 
            self.mirrored = set_to
        
        # nothing to care for atm...
        if len(self.pins) == 2:
            return
        
        ilist = []
        for i, p in self.pins.items():
            if p.pos == (0, 1):
                p.pos = (2, 1)
                continue
            
            if p.pos == (2, 1):
                p.pos = (0, 1)
                continue

    def is_rot_legal(self, newrot):
        if self.has_vdd and newrot != 0:
            return False
        if self.has_gnd and newrot != 2:
            return False
        return True
        
        
    # AWAY WITH THIS!!!
    def set_rot_from_pin_dir(self, pin, d, only_mirror=None):
        reald = d % 4
        realpin = pin
        
        if not self.is_rot_legal(d % 4):
            return False
        
        for i in xrange(4):
            if self.get_pin_direction(realpin) != reald:
                self.rotate(1)
            else:
                break
        return True
    
    def has_pin(self, names):
        if not isinstance(names, (list, tuple)):
            names = [names]
        return all(name in [p.net for p in self.pins.values()] for name in names)
    
    def get_pin_direction(self, pin):
        if pin.pos[0] == 0:
            return 3 # left
        elif pin.pos[0] == self.size[0]:
            return 1 # right
        elif pin.pos[1] == 0:
            return 0 # top
        elif pin.pos[1] == self.size[1]:
            return 2 # bottom
        else:
            assert False, "No _inner_ pins allowed in block!"
            
            
    def get_pin_direction_from_name(self, name, only_horiz=False):
        if not self.has_pin(name):
            raise PinNameDoesNotExist(name)
        
        for i, conn in self.pins.items():
            if conn == name:
                d = self.get_pin_direction(i)
                if not only_horiz:
                    return d
                elif only_horiz and d in [1, 3]:
                    return d
                
        return False
    
                    
    def get_pins_from_direction(self, i):
        out = []
        for pos, pin in self.pins.items():
            if self.get_pin_direction(pin) == i:
                out.append(pin)
        return out

    def __str__(self):
        return "<Block {0:4}{1:5} rot={3:1} mir={4:5} conns=[{2:23}] name={5:3} groups={6} size={7[0]}x{7[1]}>".format(
                self.type[:4], 
                ":vdd" if self.has_vdd else (":gnd" if self.has_gnd else ""), 
                ", ".join(str(x) for x in self.pins.values()), 
                self.rotation, 
                "true" if self.mirrored else "false",
                self.name, str(self.groups), self.size
        )
    __repr__ = __str__