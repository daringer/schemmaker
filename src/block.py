# -*- coding: utf-8 -*-

from pin import Pin

import copy

"""
--> representing an abstract block of a circuit
--> including max 4 connections

           (0)
        ____o____
       |    |    |
  (1)  |o___|____|o (3)
       |    |    |
       |____|____|
            o
           (2)
"""

class BlockException(Exception):
    def __init__(self, msg):
        self.message += "[EXC] {}: {}".\
            format(self.__class__.__name__, str(msg))

class BlockNoFieldAssigned(BlockException):
    pass


class Block(object):

    has_vdd = property(lambda s: any(p.supply for p in s.pins.values()))
    has_gnd = property(lambda s: any(p.gnd for p in s.pins.values()))
    is_biased = property(lambda s: any(p.biased for p in s.pins.values()))

    def __init__(self, b_type, pins=None, name=None, groups=None, size=(2, 2), parent=None):
        self.type = b_type
        self.name = name
        self.groups = groups

        self.pos = [-1, -1]

        # size-range: 2x2 to NxM, x and y must be even
        assert size[0] % 2 == 0 and size[1] % 2 == 0
        self.size = size

        # containing field
        self.field = parent

        # pin positions
        self.pins = {}

        # block is mirrored?
        self.mirrored = False

        # rotation: 0=0°, 1=-90°, 2=-180°, 3=-270°
        # rotation is COUNTER-CLOCK-WISE !!!
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


        # TODOOOOO!!!
        #rot, mir = self.get_prefered_orientation()
        #self.rotate((self.rotation - rot) % 4)
        #self.mirror(set_to=mir)

    def __contains__(self, pin):
        return pin in self.pins.values()

    def __pos_getter(self):
        """(internal) getter for .pos - ask for my position at parent"""
        if self.field is None:
            raise BlockNoFieldAssigned("cannot ask for global position")
        # if this rings, block is not owned by field or vice-versa
        assert self in self.field
        return self.field[self]

    def copy(self, parent):
        """Return real block copy"""
        out = Block(self.type)
        out.pins = dict((k, v.copy(out)) for k, v in self.pins.items())
        out.mirrored = self.mirrored
        out.rotation = self.rotation

        out.name = self.name
        out.groups = self.groups

        out.size = self.size
        out.field = parent or self

        return out

    def __rot_pos(self, pos, times, origin=(0,0)):
        """(internal) rotate 'pos' 'times' counter-clock-wise around 'origin'"""
        new_pos = pos
        for i in xrange(4 - times):
            # first move to origin
            o_x, o_y = new_pos[0] - origin[0], new_pos[1] - origin[1]
            # rotate 90° clock-wise
            r_x, r_y = (o_y, o_x*-1)
            # move back from origin
            new_pos = (r_x + origin[0], r_y + origin[1])
        return new_pos

    def rotate(self, count, force=False):
        """Rotate block counter-clock-wise 'count' times"""
        new_pins = {}
        rot = count % 4
        if rot == 0:
            return True

        targ_rot = (self.rotation + rot) % 4

        # validate new orientation
        if force and not self.is_orientation_legal(targ_rot, self.mirrored):
            return False

        self.rotation = targ_rot
        for pos, pin in self.pins.items():
            pin.pos = self.__rot_pos(pos, rot, self.__rot_origin)
            new_pins[pin.pos] = pin

        self.pins = new_pins

        # rot 1 or 3: (switch x and y size for 90° & 270°)
        # TODO: DO SOMETHING IF THIS LEADS TO A OVERLAP!!
        if rot % 2 == 1:
            self.size = (self.size[1], self.size[0])

        return True

    def mirror_v(self):
        """Mirror block vertically"""
        targ_rot = (self.rotation + 2) % 4
        targ_mir = not self.mirrored

        if not self.is_orientation_legal(targ_rot, targ_mir):
            return False

        return self.rotate(2) and self.mirror()

    def mirror(self, set_to=None):
        """
        Mirror block horizontally,
        or set 'set_to' mirror property and apply
        """
        if set_to is None:
            self.mirrored = not self.mirrored
        else:
            if self.mirrored == set_to:
                return True
            self.mirrored = set_to

        # FIXME: do this for any block size!!!
        # nothing to care for atm...
        if len(self.pins) == 2:
            return True

        for i, p in self.pins.items():
            if p.pos == (0, 1):
                p.pos = (2, 1)
                continue

            if p.pos == (2, 1):
                p.pos = (0, 1)
                continue
        return True

    # also derivation candidate!
    def is_orientation_legal(self, newrot, newmir):
        """Is the given 'newrot' and 'newmir' orientation legal"""
        if self.has_vdd and newrot != 0:
            return False
        if self.has_gnd and newrot != 2:
            return False
        return True

    def get_pin_direction(self, pin):
        """Return direction of pin:
            0 -> NORTH,
            1 -> WEST
            2 -> SOUTH,
            3 -> EAST,
        """
        if pin.pos[0] == 0:
            return 1    # left/west
        elif pin.pos[0] == self.size[0]:
            return 3    # right/east
        elif pin.pos[1] == 0:
            return 0    # top/north
        elif pin.pos[1] == self.size[1]:
            return 2    # bottom/south
        else:
            assert False, "No _inner_ pins allowed in block!"


    def get_pins_from_direction(self, i):
        """Return list of pins showing in the desired direction"""
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
