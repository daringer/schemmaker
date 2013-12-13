# -*- coding: utf-8 -*-
from sys import stdout
from random import choice, random, randint
from math import exp
from time import time
from itertools import permutations, cycle
from multiprocessing import Process, Queue, Pool


from base_optimizer import BaseOptimizer, OptimizerError
from field import Field
from block import Block
from print_block import bprint

class OptimizerNoColumnOrderFound(OptimizerError):
    def __init__(self, msg):
        OptimizerError.__init__(self)
        
        self.message += msg

class OptimizerBiasBlockPlacementError(OptimizerError):
    def __init__(self, blocks):
        OptimizerError.__init__(self)
        
        if not isinstance(blocks, (tuple, list, set)):
            blocks = [blocks]

        self.message += "could not be placed: \n"
        for b in blocks:
            self.message += "   " + str(b) + "\n"

class OptimizerHorizontalAlignError(OptimizerError):
    def __init__(self, blocks):
        OptimizerError.__init__(self)
        if not isinstance(blocks, (tuple, list, set)):
            blocks = [blocks]
            
        self.message += "Bias could not be placed: \n"
        for b in blocks:
            print "   " + str(b)

class OptimizerCannotSetPinOrientation(OptimizerError):
    def __init__(self, pin_name, orientation, blk):
        OptimizerError.__init__(self)
        
        self.message += "pin: {0} orientation: {1} blk: {2}". \
            format(pin_name, orientation, str(blk))
                
class OptimizerBlockDifferenceError(OptimizerError):
    def __init__(self, blks1=None, blks2=None, blks3=None):
        OptimizerError.__init__(self)
        if blks1:
            self.block_debug(blks1)
        if blks2:
            self.block_debug(blks2)
        if blks3:
            self.block_debug(blks3)
        
    def block_debug(self, blks):
        self.message += "\nStarting block debug, #blks: {0}\n".format(len(blks))
        for b in blks:
            self.message += str(b) + "\n"
	
	
	
class Deterministic(BaseOptimizer):
    def __init__(self, field):
        BaseOptimizer.__init__(self, field)


    def columnize(self, field, blks, net_blks):
        # only blocks with "vdd", each one spans one "column"
        vdd_blks = net_blks["vdd"]
        vdd_blks.sort(key=lambda o: o.name)

        # holds the results in form of a dict, with the parent-block as key -> holding a list of children:
        # the "None" key means there is no parent, thus block is a vdd-block
        # [child1, child2, ..., childN], if key(block) is ground block, replace list with "gnd"
        result = {None: vdd_blks[:]}
        
        # maintain queue of next blocks for each "column", start with "vdd"-block
        queue = dict( (k, [k.set_pin_orientation("vdd", 0) and k]) for k in vdd_blks)
        # check if all vdd blocks can be rotated, so that "vdd" points north
        if any(not x for x in queue.values()):
            raise OptimizerCannotSetPinOrientation("vdd", 0, [x for x in queue.values() if not x])
        
        # contains already added blocks                        
        added = [k for k in vdd_blks]

        # iterator to cycle through vdd blocks (keys of queue) endlessly
        q_iter = cycle(queue.keys())
        
        # keep adding blocks to result/added until all are added
        # cycle through columns to only add one block at once in each column
        while len(added) != len(blks):
            
            # get active block and queue
            q_blk = q_iter.next()
            active_q = queue[q_blk]
            
            # only add one block
            if len(active_q) > 0:
                blk = active_q.pop()
                net = blk.get_name_from_direction(2)                
                
                # for all candidates with the appropriate net turned north
                for b in sorted(net_blks[net], key=lambda o: o.name):
                    if b not in added and b.set_pin_orientation(net, 0):
                        south_net = b.get_name_from_direction(2)
                        # ignore if vdd
                        if south_net == "vdd":
                            continue
                        
                        # maintain result data
                        result.setdefault(blk, []).append(b)
                        added.append(b)
                        
                        # either add as ground block
                        if south_net == "gnd":
                            result[b] = "gnd"
                        # or regular
                        else:
                            result[b] = []
                            active_q.append(b)
                        
            # catch cornercase: only vdd block without children            
            else:
                result.setdefault(q_blk, [])
        
        # now insert the generated columns into field
        max_col = -2
        stack = [ ((-1, 0), blk) for blk in result[None] ]
        # stack-based means depth-first 
        while len(stack) > 0:
            (col, row), blk = stack.pop()
            
            # reset and columns set, if new column starts
            if blk.has_vdd:
                col = max_col + 2
                max_col = 0
            
            field[col, row] = blk
            
            max_col = max(max_col, col)
            row += 2
            
            # if "gnd" block don't touch the stack
            if result[blk] == "gnd":
                continue
            # add children to stack to be added next
            for i, child in enumerate(result[blk]):
                if result[child] == "gnd":
                    row = (field.ny - 2)
                    
                stack += [((col + i*2, row), child)]
        return field

    def reorder_cols(self, field):
        # find best permutation of columns
        _field = field.copy()
        _field.clear()
        best_p, best_c = None, None
        for i, p in enumerate(permutations(field.iter_cols())):

            # hard break after 1000 tries
            if i==1000:
                break

            autofail = False
            for x, cols in enumerate(p):
                for y, blk in cols:
                    ret = _field[x*2, y] = blk
                    
                    # EVIL HACK FOR BIAS-CIRCUIT # TODO / FIXME !!!!
                    if blk.groups[0] == 0 and x in [0, 1]:
                        autofail = True
                        break
                    
                    elif blk.groups[0] == 1 and blk.type == "i_constant" and x != 1:
                        autofail = True
                        break
      
                if autofail:
                    break
      
            if autofail:
                autofail = False
                _field.clear()
                continue

            simple_costs = _field.cost(simple=True)
            if best_p is None or best_c > simple_costs:
                best_p = p[:]
                best_c = simple_costs
            _field.clear()
        
        if best_p is None:
            raise OptimizerNoColumnOrderFound("WHYYYYYYYYYYYYYYY????!")
     
        field.clear()
        for i, col in enumerate(best_p):
            for y, blk in col:
                field[i*2, y] = blk        
        return field

    def expand_rows(self, field):
        row = 0
        
        add_vb_blks = {}
        vb_lines = {}
        
        _field = field.copy()
        _field.clear()
        
        # assign blocks to their appropriate line(-type)
        for y, cols in field.iter_yx_pos_block(split=True, unique=True):
            line_vb = None
            main_line, vb_line, vb_line2, inp_line = {}, {}, {}, {}
            need_split, need_inp_split = False, False
            for x, blk in cols:
                # extract blk-vb props
                vb = None
                _f = blk.get_name_from_direction
                left, right = _f(3), _f(1)
                if left and left.startswith("vbias"):
                    vb = int(left[-1])
                elif right and right.startswith("vbias"):
                    vb = int(right[-1])
                
                # blk has vb
                if vb is not None:
                    # first vb found in this line, define line as this vb
                    if line_vb is None:
                        line_vb = vb
                        
                    # add blk if vb matches line_vb - or save it for later use
                    if line_vb != vb:
                        add_vb_blks.setdefault(vb, []).append((x, blk))
                    elif x not in vb_line:
                        vb_line[x] = blk
                    else:
                        vb_line2[x] = blk
                        need_split = True
                        
                # regular non-vb blk
                else:
                    if left and left.startswith("inp"):
                        inp_line[x] = blk
                        need_inp_split = True
                    elif right and right.startswith("inp"):
                        inp_line[x] = blk
                        need_inp_split = True
                    else:
                        main_line[x] = blk

            # append previously appended vb-blks in line_vb matches
            if line_vb in add_vb_blks and len(add_vb_blks[line_vb]) > 0:
                for vb_x, vb_blk in add_vb_blks[line_vb]:
                    if vb_x in vb_line:
                        vb_line2[vb_x] = vb_blk
                    else:
                        vb_line[vb_x] = vb_blk
                del add_vb_blks[line_vb]            


            # when to split vb and main line:
            # [main] .. [main] [main] [vb] [vb] ... [vb]        = ok (never occurs)
            # [main] ... [main] [vb] ... [vb] [main] ... [main] = bad (split!) (not checked and never occurs)            
            # [vb] .. [vb] [vb] [main] [main] ... [main]        = ok
            # [vb] ... [vb] [main] ... [main] [vb] ... [vb]     = bad (split!)            
            if line_vb is not None and len(main_line) > 0 and len(vb_line) > 0:
                min_main_x = min(main_line.keys())
                min_vb_x, max_vb_x = min(vb_line.keys()), max(vb_line.keys())
                if min_main_x > min_vb_x and min_main_x < max_vb_x:
                    need_split = True
            #    for m_x in main_line.keys():
            #        lower, higher = False, False
            #        for vb_x in vb_line.keys():
            #            lower |= vb_x <= m_x
            #            higher |= vb_x >= m_x
            #            print lower, higher
            #        need_split |= lower and higher
            
            # those two lines should not be needed if everything works nicely   
            #if any(x in vb_line.keys() for x in main_line.keys()):
            #    need_split = True
                           
            # change vb and main order for upper/lower half of the field
            if not need_split and not need_inp_split:
                main_line.update(vb_line)
                lines = (vb_line2, main_line)
            elif need_inp_split:
                main_line.update(vb_line)
                lines = (vb_line2, main_line, inp_line)
            elif row < _field.ny//2:
                lines = (main_line, vb_line2, vb_line, inp_line)
            else:
                lines = (inp_line, vb_line2, vb_line, main_line)
            
            # fill main/vb_line into _field
            for line in lines:
                if len(line) > 0:
                    is_vb_line = False
                    for blk_x, blk in line.items():
                        _field[blk_x, row] = blk
                        is_vb_line |= blk.is_biased
                    # remember row for each bias level
                    if is_vb_line:
                        vb_lines[line_vb] = [row] + ([] if line_vb not in vb_lines else vb_lines[line_vb])
                    row += 2
            
        # still not inserted blocks available
        if len(add_vb_blks) > 0:
            added = []
            for vb, blks in add_vb_blks.items():
                if len(blks) < 1:
                    continue
                
                for x, blk in blks:
                    found_slot = False
                    tried_slots = []
                    # first: trying the original position
                    for y in vb_lines[vb]:
                        tried_slots += [(x, y)]
                        if (x, y) not in _field:
                            _field[x, y] = blk
                            added += [(vb, x, blk)]
                            found_slot = True
                            break
                    # next try: insert line above or below original position
                    # -> place block inside new line
                    if not found_slot:
                        tried_slots.sort()
                        top_blk, bottom_blk = \
                            _field[tried_slots[0]], \
                            _field[tried_slots[-1]]
                    
                        # looking for best match with net
                        top_net = top_blk.get_name_from_direction(0)
                        bottom_net = bottom_blk.get_name_from_direction(2)
                        
                        if top_net in blk.conns.values() and blk.set_pin_orientation(top_net, 2):
                            old_blk_pos = _field.get_block_pos(top_blk)
                            _field.insert_row(old_blk_pos[1], 2)
                            _field[old_blk_pos] = blk
                            added += [(vb, x, blk)]
                        elif bottom_net in blk.conns.values() and blk.set_pin_orientation(bottom_net, 0):
                            old_blk_pos = _field.get_block_pos(bottom_blk)
                            _field.insert_row(old_blk_pos[1] + 2, 2)
                            _field[old_blk_pos[0], old_blk_pos[1] + 2] = blk
                            added += [(vb, x, blk)]
                        
            # maintain add_vb_blks consistency
            for vb, x, blk in added:
                add_vb_blks[vb].remove((x, blk))
                if len(add_vb_blks[vb]) == 0:
                    del add_vb_blks[vb]
        
        # IF STILL ....
        if len(add_vb_blks) != 0:
            print _field.show_occ()
            raise OptimizerBiasBlockPlacementError(add_vb_blks)
        
        return _field
    
    def align_horizontal(self, field):
        # iterate colwise, if "netX" found, add to left, rotate/mirror and apply 
        inp_found = False
        left = {}
        max_x = max(x for x,y in field.iter_xy_pos_block())
        for (x, y), block in field.iter_xy_pos_block():
            _f = block.get_name_from_direction
            net = _f(3) or _f(1)
            if not net:
                continue
            
            _f = block.set_pin_orientation
            # handle input block, so they show in opposite dirs
            if net.startswith("inp"):
                if not inp_found:
                    ret = _f(net, 3, only_mirror=True)
                    inp_found = True
                else:
                    ret = _f(net, 1, only_mirror=True)
            # blocks inside the rightmost col: TURN LEFT
            elif x == max_x:
                ret = _f(net, 3, only_mirror=True)
            # net seen first or found straight over block: TURN RIGHT 
            elif net not in left or (net in left and left[net] == x):
                left[net] = x
                ret = _f(net, 1, only_mirror=True)
            # net already seen : TURN LEFT
            else:
                ret = _f(net, 3, only_mirror=True)
                
            if not ret:
                raise OptimizerHorizontalAlignError(blk)        
        return field

    def run(self):
        net_blks = {}
        blks = self.field.get_blocks()[:]
        
        org_block_count = len(blks)
        org_blocks = blks[:]
        
        for blk in blks:
            for net in blk.conns.values():
                net_blks.setdefault(net, []).append(blk)                
        
        field = self.field 
        field.clear()

        log = lambda m: (stdout.write(m), stdout.flush())

        log("[+] Starting {0} - columnize - ".format(field.circuit_id))

        # "columnize" the blocks and place them inside the field
        field = self.columnize(field, blks, net_blks)
        
        log("reorder columns - ")
        # find best column order
        field = self.reorder_cols(field)
        
        if org_block_count != len(field):
            raise OptimizerBlockDifferenceError(field.get_blocks(), org_blocks, \
                [blk for blk in org_blocks if blk not in field])        
        
        log("expanding rows - ")
        # expand rows to main/vb/special
        field = self.expand_rows(field)
        
        if org_block_count != len(field):
            print field.show_occ()
            raise OptimizerBlockDifferenceError(field.get_blocks(), org_blocks, \
                [blk for blk in org_blocks if blk not in field])        
        
      
        log("horizontal alignment - ")
        # mirror/rotate to get best horizontal alignment
        field = self.align_horizontal(field)
      
        if org_block_count != len(field):
            raise OptimizerBlockDifferenceError(field.get_blocks(), org_blocks, \
                            [blk for blk in org_blocks if blk not in field])        
       
        field.optimize_size()
        log("routing - ")
        #field.cost()
        field.route()
        
        log("finished!\n")
        if __debug__:
            print field.show_occ()
        
        self.field = field
        return field

