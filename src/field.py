# -*- coding: utf-8 -*-
from scipy import *
from math import sqrt, factorial, pow
from random import choice, shuffle
import itertools
import heapq
import copy

from block import Block
from print_block import *

"""
-> representing a field of the dimension nx*ny
-> blocks added to the field have the size 2*2
-> position of the blocks is given by the coordinate of the left upper edge

     _ -nx-> _
    |x|x|_|_|_|
   ||x|x|_|_|_|
  ny|_|_|_|_|_|
   V|_|_|_|_|_|
    |_|_|_|_|_|

"""

class IncorrectDirectionError(Exception):
    pass

class FieldException(Exception):
    def __init__(self):
        import traceback as t
        self.tb  = "########################## STACKTRACE\n"
        self.tb += "".join(t.format_stack()) + "\n"
        self.tb += "##########################"
        
        self.message += "[EXC] " + self.__class__.__name__ + ": "
        
class FieldCriticalError(FieldException):
    def __init__(self, msg=""):
        FieldException.__init__(self)    
        self.message += msg
            
class FieldPosException(FieldException):
    def __init__(self, pos):
        FieldException.__init__(self)
        self.message += str(pos)
        
class FieldBlockException(FieldException):
    def __init__(self, block):
        FieldException.__init__(self)
        self.message += str(block)
        
class FieldBlockPosException(FieldException):
    def __init__(self, pos, block):
        FieldException.__init__(self)
        self.message += str(pos) + " " + str(block)
        
class FieldBlockPosNotValid(FieldPosException):
    pass
class FieldPosNotValid(FieldPosException):
    pass
class FieldSpaceOccupied(FieldPosException):
    pass
class FieldNoBlockAtPos(FieldPosException):
    pass
class FieldSameSourceTargetPos(FieldPosException):
    pass

class FieldBlockNotFound(FieldBlockException):
    pass
class FieldBlockBadOrientation(FieldBlockException):
    pass

class FieldBlockCouldNotBePlaced(FieldBlockPosException):
    pass


class FieldNode:
    def __init__(self, name, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.names = name and [name]
    

class Field:
    def __init__(self, cid, nx, ny, raw_blocks=None):
        # circuit id
        self.circuit_id = cid
        
        # dimensions (wires go up to s.nx+1 and s.ny+1
        self.nx = nx
        self.ny = ny

        # block to (x,y) pos map
        self.block_pos = {}
        
        # (x,y)/(y,x) to block map (all occupied pos as keys)
        self.xy_pos_block = {}
        self.yx_pos_block = {}
        # (x,y)/(y,x) always sorted index-list
        self.xy_index = []
        self.yx_index = []
        # (x,y)/(y,x) always sorted (only unique blocks) index-list
        self.xy_unique_index = []
        self.yx_unique_index = []        
        
        self.wires = []
        self.wire_dots = []
        self.open_dots = []
        self.output_dots = []
        self.net_forbidden_pos = {}
        #self.net_wires = {}
        
        self.field_cost = None
        
        # UUUGLYYYY
        self.spec_data = {}
        
        if raw_blocks is not None:
            self.initial_placement(raw_blocks)
        
    ############################################################################
    ### Cleanup/copy and clear Field
    ############################################################################        
    def clear_wires(self):
        self.wires = []

    def clear(self):
        blks = self.get_blocks()[:]
        for blk in blks:
            self.remove_block(blk)
            
        self.clear_wires()

    def copy(self):
        # copy only blocks - no wires!?
        out = Field(self.circuit_id, self.nx, self.ny)
        for k, v in self.block_pos.items():
            out.add_block(k.copy(out), v) #copy.deepcopy(v))
        return out

    def shuffle_copy(self):
        out = Field(self.circuit_id, self.nx, self.ny)
        
        blocks = self.block_pos.keys()
        shuffle(blocks)
        for b in blocks:
            out.place_block(b)        
        
        return out
   
    ############################################################################
    ### various iterators for a fancier traversal
    ############################################################################
    def iter_pairwise(self, iterable):
        a, b = itertools.tee(iterable)
        next(b, None)
        return itertools.izip(a, b)

    def iter_xy_pos_block(self, split=False, unique=True):
        it = self.__generic_iter(
            self.xy_unique_index if unique else self.xy_index,
            self.xy_pos_block,
            split
        )
        for item in it:
            yield item
 
    def iter_yx_pos_block(self, split=False, unique=True):
        it = self.__generic_iter(
            self.yx_unique_index if unique else self.yx_index,
            self.yx_pos_block,
            split
        )
        for item in it:
            yield item
    
    def iter_rows(self):
        for y, row in self.iter_yx_pos_block(split=True):
            yield row
            
    def iter_cols(self):
        for x, col in self.iter_xy_pos_block(split=True):
            yield col
            
    def __generic_iter(self, idx, data, split):
        if not split:
            for pos in idx:
                yield pos, data[pos]
        else:
            out = []
            active_one = None
            for one, two in idx:
                if active_one is None:
                    active_one = one
                  
                if active_one != one:
                    yield one, out
                    out = []
                    active_one = one
                    
                out.append( (two, data[one, two]) )
            if len(out) > 0:
                yield active_one, out
                
    def iter_wire(self, scaling=1):
        for x in xrange((self.nx+1)*scaling):
            for y in xrange((self.ny+1)*scaling):
                yield (x, y)

    def iter_area_pos(self, pos=(0,0), size=(2,2)): #, reverse=False):
        #endpos = (pos[0]+size[0], pos[1]+size[1])
        #if reverse:
        #    size = size[0]+1, size[1]+1
        for add_x in xrange(size[0]):
            for add_y in xrange(size[1]):
        #        if not reverse:
                yield (pos[0] + add_x, pos[1] + add_y)
        #        else:
        #            yield (endpos[0] - add_x, endpos[1] - add_y)
    
    def iter_area_block(self, block):
        if not block in self:
            raise FieldBlockNotFound(block)
        
        pos = self.block_pos[block]
        for x, y in self.iter_area_pos(pos):
            yield x, y

    ############################################################################
    ### Item datastructure inspection/manipulation/search
    ############################################################################
    def get_blocks(self):
        return self.block_pos.keys()
    
    def get_nets(self):
        out = set()
        for blk in self.get_blocks():
            out.update(blk.conns.values())
        return out
   
    def get_block_pos(self, block):
        if not block in self:
            raise FieldBlockNotFound(block)
        return self.block_pos[block]    
    
    def add_block(self, block, pos, idx_sort=True):
        x, y = pos
        if not self.validate_block_pos(pos):
            raise FieldBlockPosNotValid(pos)
        elif not self.is_block_free(pos):
            raise FieldSpaceOccupied(pos)
        
        for x, y in self.iter_area_pos(pos):
            self.xy_pos_block[x, y] = block
            self.xy_index.append((x, y))
            
            self.yx_pos_block[y, x] = block
            self.yx_index.append((y, x))
        
        self.xy_unique_index.append(pos)
        self.yx_unique_index.append((pos[1], pos[0]))
        
        if idx_sort:
            self.xy_index.sort()
            self.yx_index.sort()
            self.xy_unique_index.sort()
            self.yx_unique_index.sort()
        
        self.block_pos[block] = pos
        return True
    
    def remove_pos(self, pos):
        if not self.validate_pos(pos):
            raise FieldPosNotValid(pos)
        elif not self.is_occ(pos):
            raise FieldNoBlockAtPos(pos)
        
        return self.__remove_block(self.xy_pos_block[pos])

    def remove_block(self, block):
        if not block in self:
            raise FieldBlockNotFound(block)
        return self.__remove_block(block)

    def __remove_block(self, block):
        for x, y in self.iter_area_block(block):
            del self.xy_pos_block[x, y]
            self.xy_index.remove((x, y))
            
            del self.yx_pos_block[y, x]
            self.yx_index.remove((y, x))
            
        x, y = self.block_pos[block]
        self.xy_unique_index.remove((x, y))
        self.yx_unique_index.remove((y, x))
        del self.block_pos[block]
        
        return True
    
    def move(self, block, pos, force=False):
        x, y = pos
        pos_old = self.get_block_pos(block)
        
        if not self.validate_block_pos(pos):
            raise FieldBlockPosNotValid(pos)
        elif pos == pos_old:
            raise FieldSameSourceTargetPos(pos)
        elif block not in self:
            raise FieldBlockNotFound(block)
        elif not self.is_block_free(pos):
            raise FieldSpaceOccupied(pos)
        
        ##### mmmh
        if block.type == "i_constant":
            if (block.has_gnd and y not in [self.ny-2, self.ny-4] or \
                block.has_vdd and y not in [0, 2]) and not force:
                return False
        else:
            if (block.has_gnd and y != (self.ny - 2) or \
                block.has_vdd and y != 0) and not force:
                return False
        ##### mmmh - end
        
        if not self.remove_block(block):
            raise FieldCriticalError("Remove Block Failed!!!" + str(block))
            
        if not self.add_block(block, pos):
            raise FieldCriticalError("Add Block Failed!!!" + str(block))
        
        return True        
        
    def remove_col(self, which_x, width=2):
        move_from_x = which_x + 2
        good = False
        if self.is_col_empty(which_x, width):
            good = True
            for pos in self.iter_area_pos((move_from_x, 0), (move_from_x+width-1, self.ny)):
                if self.is_occ(pos):
                    good &= self.move(self[pos], (pos[0] - width, pos[1]))
            self.nx -= width
        return good        
    
    def insert_col(self, which_x, width=2):
        self.nx += width
        
        good = True
        to_add = []
        for blk in self.get_blocks():
            b_pos = self.get_block_pos(blk)
            if b_pos[0] >= which_x:
                self.remove_block(blk)
                to_add += [(blk, (b_pos[0]+width, b_pos[1]))]
        for blk, pos in to_add:
            self[pos] = blk
            
        return good     

    def insert_row(self, which_y, height=2):
        self.ny += height
        
        good = True
        to_add = []
        for blk in self.get_blocks():
            b_pos = self.get_block_pos(blk)
            if b_pos[1] >= which_y:
                self.remove_block(blk)
                to_add += [(blk, (b_pos[0], b_pos[1]+height))]
        for blk, pos in to_add:
            self[pos] = blk
            
        return good
    
    def remove_row(self, which_y, height=2):
        move_from_y = which_y + 2
        good = False
        if self.is_row_empty(which_y, height):
            good = True
            for pos in self.iter_area_pos((0, move_from_y), (self.nx, move_from_y+height-1)):
                if self.is_occ(pos):
                    good &= self.move(self[pos], (pos[0], pos[1] - 2))
            self.ny -= height
        return good 
        
    ############################################################################
    ### Checkers and Validators
    ############################################################################
    def validate_block_pos(self, pos):
        x, y = pos
        return (x >= 0 and x <= self.nx - 2) and \
               (y >= 0 and y <= self.ny - 2)
    
    def validate_pos(self, pos):
        x, y = pos
        return (x >= 0 and x <= self.nx) and \
               (y >= 0 and y <= self.ny)
    
    def is_occ(self, pos):
        return pos in self.xy_pos_block
    
    def is_free(self, pos):
        return not self.is_occ(pos)
    
    def is_block_free(self, pos):
        return all([self.is_free(p) for p in self.iter_area_pos(pos)])
    
    def is_row_empty(self, which_y, height=2):
        all_free = True
        for pos in self.iter_area_pos((0, which_y), (self.nx, which_y+height-1)):
            all_free &= self.is_free(pos)
        return all_free
    
    def is_col_empty(self, which_x, width=2):
        all_free = True
        for pos in self.iter_area_pos((which_x, 0), (which_x+width-1, self.ny)):
            all_free &= self.is_free(pos)
        return all_free

    ############################################################################
    ### Overloaded container methods
    ############################################################################
    def __contains__(self, item):
        if isinstance(item, (tuple, list)): # position
            
            return item in self.xy_pos_block
        elif isinstance(item, Block):       # block
            return item in self.block_pos
        else:
            print "'in' operator on Field only for position-tuple or Block instances"
            return False

    def __setitem__(self, pos, block):
        self.add_block(block, pos)
        
    def __getitem__(self, pos):
        if pos not in self.xy_pos_block:
            raise FieldNoBlockAtPos(pos)     
        return self.xy_pos_block[pos]

    def __len__(self):
        return len(self.block_pos)
    
    ############################################################################
    ### Block operations
    ############################################################################    
    def initial_placement(self, raw_blocks):
        for b_data in raw_blocks:
            b = Block(b_data["type"], b_data["conns"], b_data["name"], b_data["groups"])
            self.place_block(b)
                
    def place_block(self, blk):
        ypos = choice(range(2, self.ny-4+1, 2))
        
        if not self.add_in_row(ypos, blk):
            raise FieldBlockCouldNotBePlaced((ypos, -1), blk)
        
    def rotate(self, block, i):
        if block not in self:
            return False
        elif block.has_vdd or block.has_gnd:
            return False
        else:            
            block.rotate(i)
            return True

    def mirror_h(self, block):
        if block not in self.block_pos.keys():
            return False
        else:            
            block.mirrored = not block.mirrored
            return True

    def mirror_v(self, block):
        if block not in self.block_pos.keys():
            return False
        elif block.has_vdd or block.has_gnd:
            return False
        else:
            block.rotation = (block.rotation + 2) % 4
            self.mirror_h(block)
            return True
                
    def swap(self, block1, block2):
        pos1 = self.get_block_pos(block1)
        pos2 = self.get_block_pos(block2)
        
        if block1 not in self:
            raise FieldBlockNotFound(block1)
        elif block2 not in self:
            raise FieldBlockNotFound(block2)
 
        if (block1.has_vdd ^ block2.has_vdd or block1.has_gnd ^ block2.has_gnd):
            return False
        
        if any((block1.has_vdd, block1.has_gnd, block2.has_gnd, block2.has_vdd)) and \
           not pos1[1] == pos2[1]:
            return False
       
        self.remove_block(block1)
        self.remove_block(block2)
        self.add_block(block1, pos2)
        self.add_block(block2, pos1)
        return True
        
    def add_in_row(self, ypos, blk, x_offset=0, from_behind=False):
        if from_behind:
            xpos = self.nx - x_offset - 2
            step = -2
        else:
            xpos = x_offset
            step = 2
        
        is_placed = False
        while (not is_placed):
            pos = (xpos, ypos)
            if self.is_block_free(pos):
                is_placed = self.add_block(blk, pos)
            
            # iter over slots linewise
            xpos += step
            if xpos >= self.nx:
                xpos = 0
                ypos += step
            if ypos >= self.ny:
                ypos = step
                
        return is_placed    

    ############################################################################
    ### Wrappers and misc
    ############################################################################    
    
    def optimize_size(self):
        for x in xrange(0, self.nx - 1, 2):
            self.remove_col(x)

        for y in xrange(0, self.ny - 1, 2):
            self.remove_row(y)

    def show_occ(self):
        space = False
        blk_list = {}
        print ' ______' * self.nx
        for ypos in xrange(self.ny):
            for k in xrange(3):
                row = '|'
                for xpos in xrange(self.nx):
                    pos = (xpos, ypos)
                    if not space:
                        if self.is_occ(pos):
                            blk = self[pos]
                            im = blk.mirrored
                            rot = blk.rotation
                            if blk_list.get(blk) is None:
                                blk_list[blk] = 0
                            z = blk_list[blk]
                            
                            row += bprint(blk, im, rot)[z]
                            blk_list[blk] += 1
                            #blk_list[blk] = min(blk_list[blk], 5)
                            space = True
                        else:
                            row += fprint()[0] if k!=2 else fprint()[1]
                    else:
                        space = False
                print row
