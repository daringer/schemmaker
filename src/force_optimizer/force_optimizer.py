'''
Created on 23.03.2014

@author: Christian Auth
'''


from base_optimizer import BaseOptimizer
from field import Field, DebugField, FieldException
from operator import itemgetter, attrgetter
from group import Group
from block import Block

import sys
import build_step
import initial_step
import main_step
import time
import last_step

MAIN_GRP = -4
OUT_GRP = -1
VCC_GRP = -3
GND_GRP = -2

class ForceAlgorithm(BaseOptimizer):
    def __init__(self, field, blocks, north_pins, south_pins, east_pins, west_pins):

        BaseOptimizer.__init__(self, field)

        # flags
        self.group_connected_to_parent_neighbor_set_parent_size = True

        self.groups = []
        self.blocks = blocks
        self.wide_search_index = 0
        self.wide_search_queue = []

        self.pins_east = east_pins
        self.pins_west = west_pins
        self.pins_north = north_pins
        self.pins_south = south_pins

        # dictionary with pin.net_name as key and a block list as value
        self.dictionary_net_blocks = {}
        self.dictionary_vdd_blocks = {}
        self.dictionary_out_blocks = {}
        self.dictionary_gnd_blocks = {}
        self.dictionary_inp_blocks = {}
        self.dictionary_bia_blocks = {}

        self.group_east = Group([OUT_GRP])
        self.group_south = Group([GND_GRP])
        self.group_north = Group([VCC_GRP])
        self.group_west = Group([-5])
        self.group_main = Group([MAIN_GRP])

        self.group_east.neighbor_west.append(self.group_main)
        self.group_main.neighbor_east.append(self.group_east)

        self.group_west.neighbor_east.append(self.group_main)
        self.group_main.neighbor_west.append(self.group_west)

        self.group_north.neighbor_south.append(self.group_main)
        self.group_main.neighbor_north.append(self.group_north)

        self.group_main.neighbor_south.append(self.group_south)
        self.group_south.neighbor_north.append(self.group_main)

        # static block positions
        self.static_blocks = {}

    def set_static_block(self, block, orientation):
        assert orientation in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        self.static_blocks[block] = orientation

    def _timeit(self, func, *v, **kw):
        s = time.time()
        func(*v, **kw)
        e = time.time()
        return e - s

    def run(self, debug=True):
        self.step_build(debug)
        self.step_initial(debug)
        self.step_main(debug)
        self.step_last(debug)

    def step_build(self, debug=True):
        self.interval_build_step = \
            self._timeit(build_step.start, self, debug)

    def step_initial(self, debug=True):
        self.interval_initial_step = \
            self._timeit(initial_step.start, self, debug)

    def step_main(self, debug=True):
        self.interval_main_step = \
            self._timeit(main_step.start, self, debug)

    def step_last(self, debug=True):
        self.interval_last_step = \
            self._timeit(last_step.start, self, debug)

    def get_debug_field(self):
        # HELP ME, UUGLYYY :)))) but works!
        blksize = 2

        # calc grp positions // kinda ugly ;D
        # feels like I need to do a breadth-first search to correctly
        # inherit from top-lvl-grp downwards!
        grp2pos = {}
        next_grp = None
        next_stack = [-4]
        while len(grp2pos) < len(self.groups):
            next_grp = next_stack.pop(0)
            for g in self.groups:
                if next_grp == g.parent.group_id[0]:
                    grp2pos[g] = (
                        g.position_x * g.size_width + g.parent.position_x * blksize,
                        g.position_y * g.size_height + g.parent.position_y * blksize
                    )
                    next_stack.extend(grp.group_id[0] for grp in g.childs)

        # actually calc block positions
        out = DebugField(self.field.nx, self.field.ny)
        for g in self.groups:
            grp_x, grp_y = grp2pos[g]
            for b in g.blocks:
                x = b.pos[0] * b.size[0] + grp_x
                y = b.pos[1] * b.size[1] + grp_y
                out.add_block(b.copy(out), x, y)
        return out

    def debug_times(self):
        print "## build_step took {:.3f} sec.".format(self.interval_build_step)
        print "## initial_step took {:.3f} sec.".format(self.interval_initial_step)
        print "## main_step took {:.3f} sec.".format(self.interval_main_step)
        print "## last_step took {:.3f} sec.".format(self.interval_last_step)

def search_group(group_id, forceOptimizer):
    '''
    PARAMETER:  group_ids     is an array with the IDs of the parent Groups and the ID of the searched group
                return        the group if it exists, else None
    STATE:      not finish
    '''
    for group in forceOptimizer.groups:
        if group.group_id == group_id:
            return group
    return None
