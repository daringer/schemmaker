# -*- coding: utf-8 -*-
from field import Field, FieldSpaceOccupied, FieldSameSourceTargetPos, FieldBlockPosNotValid, FieldBlockCouldNotBePlaced
from block import Block
from random import choice, random, randint
from print_block import bprint
from math import exp
from time import time
from itertools import permutations

from multiprocessing import Process, Queue, Pool


class OptimizerError(Exception):
    def __init__(self):
        self.message += "[EXC] " + self.__class__.__name__ + ": "
        

class NoBlockPairFoundError(OptimizerError):
    pass

class BaseOptimizer:
    def __init__(self, field, raw_blocks=None):
        # working on field
        self.field = field
        
        # show or hide console output
        self.console_show = True
        
        # copy of final field
        self.final_field = None
        
        if raw_blocks is not None:
            self.init_from_raw(raw_blocks)
    
    def init_from_raw(self, raw_blocks):
        for b_data in raw_blocks:
            b = Block(b_data["type"], b_data["conns"], b_data["name"], b_data["groups"])
            f.place_block(b)
                        
            ypos = choice(range(2, f.ny-4+1, 2))
                
            if not f.add_in_row(ypos, blk):
                raise FieldBlockCouldNotBePlaced((ypos, -1), blk)
        return f
    
    def shuffle_from_field(self, field):
        f = Field(field.circuit_id, field.nx, field.ny)
        
        blocks = field.get_blocks()
        shuffle(blocks)
        for blk in blocks:
            ypos = choice(range(2, f.ny-4+1, 2))
            if not f.add_in_row(ypos, blk):
                raise FieldBlockCouldNotBePlaced((ypos, -1), blk)
        
        return out
    
    def run(self):
        """Overload this to implement optimizer"""
        pass

class BaseRandomOptimizer(BaseOptimizer):
    def __init__(self, field):
        BaseOptimizer.__init__(self, field)
        # operations
        self.operations = [
            (self.random_swap, 50),
            (self.random_mirror, 20),
            (self.random_rotate, 20),
            (self.random_move, 130),
            (self.i_constant_move, 1),
            (self.dual_operation, 40),
            (self.swap_mirror, 20),
            (self.pair_move, 10),
        ]

        # list with multiples of the operations above to choice() from
        self.operations_weighted = []
        for op, weight in self.operations:
            for i in xrange(weight):
                self.operations_weighted.append(op)        
        
        # statistics about the executed operations 
        self.op_stats = dict((f[0].__name__, [0, 0]) for f in self.operations)
        
    def dual_operation(self, field):
        return self.get_random_operation()(field) and \
               self.get_random_operation()(field)

    def random_move(self, field):
        blk = self.get_random_block(field)
        x, y = field.get_block_pos(blk)
        new_x, new_y = self.get_random_position(field)

        if blk.has_vdd or blk.has_gnd:
            return field.move(blk, (new_x, y))
        else:
            return field.move(blk, (new_x, new_y))

    def random_swap(self, field):
        b1, b2 = None, None
        while b1 == b2:
            b1 = self.get_random_block(field)
            b2 = self.get_random_block(field)
        return field.swap(b1, b2)
        
    def random_mirror(self, field):
        blk = self.get_random_block(field)
        if blk.has_vdd or blk.has_gnd:
            return field.mirror_h(blk)        
        return choice([field.mirror_v, field.mirror_h])(blk)
            
    def random_rotate(self, field):
        blk = self.get_random_block(field)
        while blk.has_vdd or blk.has_gnd:
            blk = self.get_random_block(field)
        return field.rotate(blk, choice([0, 2]))   
    def handle_visualization(self, field):
        if self.console_show:
            self.show(field)
                    
    def get_random_block(self, field):
        return choice(field.get_blocks())
    
    def get_random_position(self, field):
        return choice(range(0, field.nx - 2 + 1, 2)), \
               choice(range(2, field.ny - 4 + 1, 2))        
    
    def get_random_operation(self):
        return choice(self.operations_weighted)
    
    def shuffle_field(self, field):
        for i in xrange(500):
            self.get_random_operation(field)
        return field
    
    def get_block_pair(self, field):
        stop = False
        blk1, blk2 = None, None
        tries_left = 10
        while blk1 is None or blk2 is None:
            blk = self.get_random_block(field)
            pos = field.block_pos[blk]
            
            if (pos[0]+2) < field.nx and field.is_occ((pos[0]+2, pos[1])):
                tmp = field.xy_pos_block[pos[0]+2, pos[1]]
                if tmp is not None and tmp != blk:
                    blk1 = blk
                    blk2 = tmp
                    break
            if (pos[0]-2) > -1 and field.is_occ((pos[0]-2, pos[1])):
                tmp = field.xy_pos_block[pos[0]-2, pos[1]]
                if tmp is not None and tmp != blk:
                    blk1 = blk
                    blk2 = tmp
                    break
            
            tries_left -= 1
            if tries_left < 0:
                raise NoBlockPairFoundError()
                
        return blk1, blk2

    def swap_mirror(self, field):
        try:
            blk1, blk2 = self.get_block_pair(field)
        except NoBlockPairFoundError as e:
            return False
        
        return field.swap(blk1, blk2) and field.mirror_h(blk1) and field.mirror_h(blk2)
    
    def pair_move(self, field):
        try:
            blk1, blk2 = self.get_block_pair(field)
        except NoBlockPairFoundError as e:
            return False
        
        new_x, new_y = self.get_random_position(field)
        x1, y1 = field.get_block_pos(blk1)
        x2, y2 = field.get_block_pos(blk2)
        move_x, move_y = new_x - x1, new_y - y1
        
        new_pos1 = (x1 + move_x, y1 + move_y)
        new_pos2 = (x2 + move_x, y2 + move_y)
        
        if field.is_block_free(new_pos1) and field.is_block_free(new_pos2):
            return field.move(blk1, new_pos1) and \
                   field.move(blk2, new_pos2)
        return False
    
    def i_constant_move(self, field):
        block = choice([b for b in field.get_blocks() if b.type == "i_constant"])
        x_pos, y_pos = field.get_block_pos(block)
        
        new_x = x_pos
        if block.has_gnd:
            new_y = (field.ny - 2) if y_pos == (field.ny - 4) else field.ny - 4
        elif block.has_vdd:
            new_y = 0 if y_pos == 2 else 2
                        
        return field.move(block, (new_x, new_y))
    


class FakeOptimizer(BaseOptimizer):
    def __init__(self, field):
        BaseOptimizer.__init__(self, field)
        
    def run(self):
        return self.field
        