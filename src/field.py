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

class FieldColumnNotEmpty(FieldPosException):
    pass
class FieldRowNotEmpty(FieldPosException):
    pass




class FieldNode(object):
    def __init__(self, name, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.names = name and [name]
 

class DebugField(object):
    def __init__(self, nx, ny, blocks=None):
        self.nx = nx 
        self.ny = ny 

        self.block2xy = {}

        # keep group pos and size data 
        self.grp2pos = {}

        # fake container
        self.wire_dots = []
        self.input_dots = []
        self.output_dots = []
        self.wires = []

        if blocks is not None:
            for blk, pos in blocks:
                self.add_block(blk, pos[0], pos[1])

    def add_block(self, blk, x, y):
        self.block2xy[blk] = (x, y)
        blk.pos = (x, y)

    def copy(self):
        out = DebugField(self.nx, self.ny)
        for blk, (x, y) in self.block2xy.items():
            out.add_block(blk.copy(), x, y)

    def show_blocks(self, sortkey=None):
        """
        sortkey: key(s) to use for sorting
                 -> tuple, list : sort fields in given order 
                 -> string : sort only based on this field
        """
        pad = 10
        tmpl = "{:<{pad}}"
        headers = ["name", "type", "grp", "grp-pos", "grp-size", "blk-pos", "nets"]
        print (tmpl*len(headers)).format(*headers, pad=pad)

        objs = self.block2xy.items()

        if sortkey is not None:
            if not isinstance(sortkey, (tuple, list)):
                sortkey = [sortkey]
            objs.sort( key=lambda o: tuple(getattr(o[0], skey) for skey in sortkey) )

        grpid2pos = {}
        for grp, data in sorted(self.grp2pos.items(), key=lambda x: x[1][0]):
            grpid2pos[tuple(grp.group_id)] = data

        for blk, (x, y) in objs:
            g_pos = grpid2pos[tuple(blk.groups)][:2] 
            g_size = grpid2pos[tuple(blk.groups)][2:]
            print (tmpl*6).format(
                    blk.name, blk.type, blk.groups, 
                    g_pos, g_size, blk.pos, blk.pins.values(), 
                    pad=pad)

    def has_overlapping_blocks(self):
        # haha just brute-force this ! ;(
        f = Field("test_circuit_id", self.nx, self.ny)
        try:
            for blk, (x, y) in self.block2xy.items():
                f.add_block(blk, (x, y))
        except FieldSpaceOccupied as e:
            # exception thrown -> overlapping blocks!
            print e
            return True

        # no exception - no overlaps!
        return False

    def to_field(self, cid=None):
        out = Field(cid or "<no name>", self.nx, self.ny)

        for blk, (x, y) in self.block2xy.items():
            out.add_block(blk, (x, y))

        out.grp2pos = self.grp2pos

        return out

    def trim_size(self):
        max_x = max( (pos[0] + blk.size[0]) for blk, pos in self.block2xy.items() )
        max_y = max( (pos[1] + blk.size[1]) for blk, pos in self.block2xy.items() )
        self.nx = max_x
        self.ny = max_y

class Field(object):
    def __init__(self, cid, nx, ny):
        # circuit id
        self.circuit_id = cid
        
        # dimensions (wires go up to s.nx+1 and s.ny+1
        self.nx = nx
        self.ny = ny

        # block-to-position map (only one pos for each block)
        self.block2xy = {}
        self.block2yx = {}
        
        # position-to-block map (all occupied pos as keys)
        self.xy2block = {}
        self.yx2block = {}
        
        # keep group pos and size data 
        self.grp2pos = {}
    
        # wiring related datastructures
        self.clear_wires() 

    ############################################################################
    ### Cleanup/copy and clear Field
    ############################################################################        
    def clear_wires(self):
        """Clear field from wires and related"""
        self.wires = []
        self.wire_dots = []
        self.input_dots = set()
        self.input_nets = set()
        self.output_dots = set()
        self.output_nets = set()
        self.net_forbidden_pos = {}

    def clear(self):
        """Clear field from any blocks and wires"""
        blks = self.get_blocks()[:]
        for blk in blks:
            self.remove_block(blk)
            
        self.clear_wires()

    def copy(self):
        """Return true copy (clone) of instance"""
        # copy only blocks - no wires!?
        out = Field(self.circuit_id, self.nx, self.ny)
        for k, v in self.block2xy.items():
            out.add_block(k.copy(out), v)
        return out

    ############################################################################
    ### various iterators for a fancier traversal
    ############################################################################
    def iter_pairwise(self, iterable):
        """Iterate over pairs of items in iterables"""
        a, b = itertools.tee(iterable)
        next(b, None)
        return itertools.izip(a, b)

    def iter_xy_pos_block(self, split=False, unique=True):
        """
        (x, y)-based iteration over occupied positions
          split: see Field::__generic_iter() for info
          unique: True  -> only iterates over the blocks' start positions
                  False -> iterates over all positions occupied by blocks
        """
        it = self.__generic_iter(
            sorted(self.block2xy.values() if unique else self.xy2block.keys()),
            self.xy2block,
            split
        )
        for item in it:
            yield item
 
    def iter_yx_pos_block(self, split=False, unique=True):
        """
        (y, x)-based iteration over occupied positions
          split: see Field::__generic_iter() for info
          unique: True  -> only iterates over the blocks' start positions
                  False -> iterates over all positions occupied by blocks
        """
        it = self.__generic_iter(
            sorted(self.block2yx.values() if unique else self.xy2block.keys()),
            self.yx2block,
            split
        )
        for item in it:
            yield item
    
    def iter_rows(self):
        """Iterate over all occupied rows"""
        for y, row in self.iter_yx_pos_block(split=True):
            yield row
            
    def iter_cols(self):
        """Iterate over all occupied columns"""
        for x, col in self.iter_xy_pos_block(split=True):
            yield col
            
    def __generic_iter(self, idx, data, split):
        """
        (internal) - Generic iterator factory
          idx: iterable of keys if type tuple with two items (a, b)
          data: dict-able with idx \subset data.keys()
          split: False -> [(a_1, [data[(a_1, b_1)], data[(a_1, b_2)], data[(a_1, b_y)], ...,], ... ]
                 True  -> [(a_1, b_1), (a_1, b_2), ... , (a_2, b_1), (a_2, b_2), ... ]
        """
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
        """Iterate over all 'wire-dots'"""
        for x in xrange(self.nx*scaling + 1):
            for y in xrange(self.ny*scaling + 1):
                yield (x, y)

    def iter_area_pos(self, pos=(0, 0), size=(2, 2)):
        """
        Iterate all points for given area
          pos: position to start iteration from
          size: size of area to iterate
        """
        for add_x in xrange(size[0]):
            for add_y in xrange(size[1]):
                yield (pos[0] + add_x, pos[1] + add_y)
        
    def iter_area_block(self, block):
        """Iterate over all occupied positions from a given block"""
        if not block in self:
            raise FieldBlockNotFound(block)
        
        pos = self.block2xy[block]
        for x, y in self.iter_area_pos(pos, block.size):
            yield x, y

    ############################################################################
    ### Item datastructure inspection/manipulation/search
    ############################################################################
    def get_blocks(self):
        """Return all blocks inside field"""
        return self.block2xy.keys()
    
    def get_nets(self):
        """Return all nets inside field"""
        out = set()
        for blk in self.get_blocks():
            out.update(p.name for p in blk.pins.values())
        return out
   
    def get_block_pos(self, block):
        """Return position of block inside field"""
        if not block in self:
            raise FieldBlockNotFound(block)
        return self.block2xy[block]    
    
    def add_block(self, block, pos):
        """Add block at given position"""
        x, y = pos
        if not self.validate_block_pos(pos):
            raise FieldBlockPosNotValid(pos)
        elif not self.is_block_free(pos):
            raise FieldSpaceOccupied(pos)
        
        block.pos = pos

        for x, y in self.iter_area_pos(pos, block.size):
            self.xy2block[(x, y)] = block
            self.yx2block[(y, x)] = block

        self.block2xy[block] = pos
        self.block2yx[block] = (pos[1], pos[0])

        #self.output_nets.update(block.output_nets)
        #for 

        #self.input_nets.update(block.input_nets)

        # calc x: max(x-values) y: (sum of all y) / (num items)
        if len(self.output_nets) > 0:
            pos = ((max(self.output_nets, key=lambda x: x[0])[0], 
                    sum([x[1] for x in self.output_nets]) / len(self.output_nets)))
            self.output_dots.clear()
            self.output_dots.add( (3, pos, "OUT") )

        assert all(len(x) == 3 for x in self.output_dots)

        if len(self.input_nets) > 0:
            for pos in self.input_nets:
                self.input_dots.add( (-1, pos, "IN?") )

        assert all(len(x) == 3 for x in self.input_dots)

        return True
    
    def remove_pos(self, pos):
        """Remove any block at given position"""
        if not self.validate_pos(pos):
            raise FieldPosNotValid(pos)
        elif not self.is_occ(pos):
            raise FieldNoBlockAtPos(pos)
        
        return self.__remove_block(self.xy_pos_block[pos])

    def remove_block(self, block):
        """Remove block from field"""
        if not block in self:
            raise FieldBlockNotFound(block)
        return self.__remove_block(block)

    def __remove_block(self, block):
        """(internal) helper to remove block and maintain datastructures"""
        for x, y in self.iter_area_block(block):
            del self.xy2block[x, y]
            
            del self.yx2block[y, x]
            
        x, y = self.block2xy[block]
        del self.block2xy[block]
        del self.block2yx[block]
        
        return True
    
    def move(self, block, pos, force=False):
        """Move given block to new position"""
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
        
        # TODO, FIXME ??? yes this is a important 
        # detail for this specific block type !!!!!
        # ultimately -> derive NMOSBlock, PMOSBlock, ResBlock, CapBlock, IDCBlock, ...
        ##### mmmh
        #if block.type == "i_constant":
        #    if (block.has_gnd and y not in [self.ny-2, self.ny-4] or \
        #        block.has_vdd and y not in [0, 2]) and not force:
        #        return False
        #else:
        #    if (block.has_gnd and y != (self.ny - 2) or \
        #        block.has_vdd and y != 0) and not force:
        #        return False
        ###### mmmh - end
        
        if not self.remove_block(block):
            raise FieldCriticalError("Remove Block Failed -> " + str(block))
            
        ret = self.add_block(block, pos)
        if not ret:
            # rewind last operation -> remove_block -> re-add_block at pos_old
            self.add_block(block, pos_old)
            raise FieldCriticalError("Add Block Failed -> " + str(block))
        
        return True        
        
    def remove_col(self, which_x, width=2):
        """
        Remove (empty) column from field.
        moving all blocks right of it to the left by width
        """
        move_from_x = which_x + 2
        if not self.is_col_empty(which_x, width):
            raise FieldColumnNotEmpty(which_x)
    
        start = (move_from_x, 0)
        end = (move_from_x + width - 1, self.ny)
        good = True
        for pos in self.iter_area_pos(start, end):
            if self.is_occ(pos):
                good &= self.move(self[pos], (pos[0] - width, pos[1]))
        
        self.nx -= width
        return good        
    
    def insert_col(self, which_x, width=2):
        """
        Insert column into field.
        moving all blocks right of it to the right by width
        """
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
        """
        Insert column into field.
        moving all blocks below it down by height
        """        
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
    
    # seems not to work!????? or just badly, need to recalculated output/input-dots
    def expand_field(self, amount, stepping=2, offset=(0,0)):
        for xidx in xrange(self.nx, offset[0], -stepping):
            assert self.insert_col(xidx, amount)
        for yidx in xrange(self.ny, offset[1], -stepping):
            assert self.insert_row(yidx, amount)

    def remove_row(self, which_y, height=2):
        """
        Remove row from field
        moving all blocks below it up by height
        """
        move_from_y = which_y + 2
        if not self.is_row_empty(which_y, height):
            raise FieldRowNotEmpty(which_y)
        
        good = True
        for pos in self.iter_area_pos((0, move_from_y), (self.nx, move_from_y+height-1)):
            if self.is_occ(pos):
                good &= self.move(self[pos], (pos[0], pos[1] - 2))
        self.ny -= height
        return good 
        
    ############################################################################
    ### Checkers and Validators
    ############################################################################
    def validate_block_pos(self, pos, blk_size=(2, 2)):
        """A 'pos' is valid - the field is big enough for the block with 'blk_size'"""
        x, y = pos
        return (x >= 0 and x <= self.nx - blk_size[0]) and \
               (y >= 0 and y <= self.ny - blk_size[1])
    
    def validate_pos(self, pos):
        """A 'pos' is valid - the field contains this position"""
        x, y = pos
        return (x >= 0 and x <= self.nx) and \
               (y >= 0 and y <= self.ny)
    
    def is_occ(self, pos):
        """Is the given 'pos' occupied?"""
        return pos in self.xy2block
    
    def is_free(self, pos):
        """Is the given 'pos' free?"""
        return pos not in self.xy2block
    
    def is_block_free(self, pos, size=(2, 2)):
        """Is the given 'pos' free for a block with 'size'?"""
        return all([self.is_free(p) for p in self.iter_area_pos(pos, size)])
    
    def is_row_empty(self, which_y, height=2):
        """Is the given row 'which_y' with 'height' empty?"""
        all_free = True
        for pos in self.iter_area_pos((0, which_y), (self.nx, which_y+height-1)):
            all_free &= self.is_free(pos)
        return all_free
    
    def is_col_empty(self, which_x, width=2):
        """Is the given column 'which_x' with 'width' empty?"""
        all_free = True
        for pos in self.iter_area_pos((which_x, 0), (which_x+width-1, self.ny)):
            all_free &= self.is_free(pos)
        return all_free

    ############################################################################
    ### Overloaded container methods
    ############################################################################
    def __contains__(self, item):
        # position
        if isinstance(item, (tuple, list)) and len(item) == 2:
            return item in self.xy2block
        # block
        elif isinstance(item, Block): 
            return item in self.block2xy
        else:
            print "'in' operator on Field only for position-tuple or Block instances"
            return False

    def __setitem__(self, pos, block):
        self.add_block(block, pos)
        
    def __getitem__(self, pos):
        if pos not in self.xy2block:
            raise FieldNoBlockAtPos(pos)     
        return self.xy2block[pos]

    def __len__(self):
        return len(self.block2xy)
    
    ############################################################################
    ### Block operations
    ############################################################################    
    def rotate(self, block, i):
        """Rotate block (clock-wise) by 'i'"""
        # TODO: handle changed size due to rotation (NxM -> MxN)
        return block.rotate(i)

    def mirror_h(self, block):
        """Mirror block horizontally"""
        if block not in self:
            raise FieldBlockNotFound(block)
        return block.mirror()

    def mirror_v(self, block):
        """Mirror block vertically"""
        if block not in self:
            raise FieldBlockNotFound(block)
        return block.mirror_v()
               
    def swap(self, block1, block2):
        """Swap positions between 'block1' and 'block2'"""
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
        """Add given 'blk' in row 'ypos' with a 'x_offset'"""
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
        """Remove all empty rows and columns"""
        for x in xrange(0, self.nx - 1, 2):
            if self.is_col_empty(x):
                self.remove_col(x)

        for y in xrange(0, self.ny - 1, 2):
            if self.is_row_empty(y):
                self.remove_row(y)

    def optimize_block_dirs(self):
        pos2pin = {}
        for b, (x, y) in self.block2xy.items():
            if b.type == "pmos":
                b.rotate(2)

            blk_nets = [p.net for p in b.pins.values()]
            if "in2" in blk_nets:
                b.mirror()

            # all nmos, without 2 conns to the same net, mirror!
            if len(set(blk_nets)) == len(blk_nets) and b.type == "nmos":
                b.mirror()

            for p_pos, p in b.pins.items():
                pos2pin.setdefault(p_pos, []).append((p.net, p.blk_pos))
        print pos2pin

    def show_occ(self):
        """Show ascii art schematic, occupation based"""
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
                            space = True
                        else:
                            row += fprint()[0] if k!=2 else fprint()[1]
                    else:
                        space = False
                print row
