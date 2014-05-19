# -*- coding: utf-8 -*-
from scipy import *
from math import sqrt, factorial, pow
from random import choice, shuffle
import itertools
import heapq
import copy

from print_block import *
from block import Block
from field import Field, FieldException, FieldNode

class FieldCostException(FieldException):
    def __init__(self, msg):
        FieldException.__init__(self)
        self.message += msg

class FieldCostRouteNotFoundException(FieldCostException):
    pass



"""
     OBSOOOOLEEEETE only thing that's useful here,
     is the cost calculation maybe
"""


class FieldCost:
    
    INPUT_WRONG_PENALTY = 200		
    VBIAS_PENALTY = 50
    IN_OUT_PLACEMENT_PENALTY = 400
    WRONG_DIRECTION_PENALTY = 3
    CROSSING_PENALTY = 100
    CORNER_PENALTY = 50
    ROUTING_PENALTY = 12
    AREA_PENALTY = 10
    
    STRAIGHT_WIRE_FACTOR = 1
    TRIVIAL_ROUTE_COST = 1
    
    ROUTING_EXPONENT = 2
    CORNER_EXPONENT = 2
    
    def __init__(self, field):
        self.field = field

        self.costs = dict((key, 0) for key in \
                    ["routing", "corner_penalty", "wire_crossings", "wire_direction", 
                     "input_neighbours", "input_dist", "bias_place_1", "bias_place_2", 
                     "bias_place_3", "bias_place_4", "bias_row_1", "bias_row_2", 
                     "bias_row_3", "bias_row_4", "input_row", "input_direction", 
                     "input_place", "output_place", "wrong_dir_vbias", "area"] 
                )        

    def cost(self, simple=False, scaling=4):
        self.field.clear_wires()
        
        netlist, netdirs, netpos_dir = {}, {}, {}
        inp_rows, outp_cols = [], []
        inp_blk_pos, inp_dir = [], []
        blk_max_x, blk_min_x, blk_max_y, blk_min_y = 0, self.field.nx, 0, self.field.ny
        pin_max_x, pin_min_x, pin_max_y, pin_min_y = 0, self.field.nx, 0, self.field.ny
        vbias_rows, vbias_pos = {}, {}
        
        self.pos_net = {}
        #self.trivial_paths = {}
                                
        for (xpos, ypos), block in self.field.iter_xy_pos_block():
            #blk_pos = (xpos, ypos)
            blk_max_x, blk_min_x = max(blk_max_x, xpos), min(blk_min_x, xpos)
            blk_max_y, blk_min_y = max(blk_max_y, ypos), min(blk_min_y, ypos)
            blocknets = {}
            for i, conn in block.conns.items():
                net = netlist.setdefault(conn, [])
                netdir = netdirs.setdefault(conn, [])
                direction = block.get_pin_direction(i)
                pos = block.get_pin_position(i, (xpos, ypos))
 
                #blocknets.setdefault(conn, set()).add(pos)
                bn = blocknets.setdefault(conn, [])
                if pos not in bn:
                    bn.append((pos, (xpos+1, ypos+2)))
               
                #self.pos_block.setdefault(pos, set()).add(block)
                #self.pos_net.setdefault(pos, set()).add(conn)
                
                pin_max_x, pin_min_x = max(pin_max_x, pos[0]), min(pin_min_x, pos[0])
                pin_max_y, pin_min_y = max(pin_max_y, pos[1]), min(pin_min_y, pos[1])
                                                            
                if direction == 0:
                    if conn.startswith("vbias"):
                        self.costs["wrong_dir_vbias"] += self.WRONG_DIRECTION_PENALTY
                elif direction == 1:
                    if conn.startswith("vbias"):
                        self.costs["wrong_dir_vbias"] += self.WRONG_DIRECTION_PENALTY
                elif direction == 2:
                    if conn.startswith("vbias"):
                        self.costs["wrong_dir_vbias"] += self.WRONG_DIRECTION_PENALTY
                elif direction == 3:
                    pass
                
                net.append(pos)
                netdir.append(direction)

                if conn.startswith("inp"):
                    inp_rows.append(pos)
                    inp_dir.append(direction)
                    inp_blk_pos.append((xpos, ypos))
                elif conn == "outp":
                    outp_cols.append(pos)
                elif conn.startswith("vbias"):
                    vbias_rows.setdefault(conn[-1], set()).add(pos[1])
                    vbias_pos.setdefault(conn, []).append(pos)
            
            # generating trivial paths            
            #for net, posis in blocknets.items():
                #triv_map = self.trivial_paths.setdefault(net, {})
                #if len(posis) == 2:
                    #(pin_pos1, blk_pos1), (pin_pos2, blk_pos2) = posis
                    
                    #if pin_pos1[0] < blk_pos1[0]: # left
                        #if ((pin_pos1[0] + 1, pin_pos1[1] - 1) == pin_pos2): # left 2 top
                            #triv_map[pin_pos1] = triv_map[pin_pos2] = \
                                #(pin_pos1, (pin_pos1[0], pin_pos1[1] - 1), pin_pos2)
                        #elif ((pin_pos1[0] + 1, pin_pos1[1] + 1) == pin_pos2): # left 2 bottom
                            #triv_map[pin_pos1] = triv_map[pin_pos2] = \
                                #(pin_pos1, (pin_pos1[0], pin_pos1[1] + 1), pin_pos2)                        
                    #elif pin_pos1[0] > blk_pos1[0]: # right
                        #if ((pin_pos1[0] - 1, pin_pos1[1] - 1) == pin_pos2): # right 2 top
                            #triv_map[pin_pos1] = triv_map[pin_pos2] = \
                                #(pin_pos1, (pin_pos1[0], pin_pos1[1] - 1), pin_pos2)
                        #elif ((pin_pos1[0], pin_pos1[1] - 1) == pin_pos2):     # right 2 bottom                        
                            #triv_map[pin_pos1] = triv_map[pin_pos2] = \
                                #(pin_pos1, (pin_pos1[0], pin_pos1[1] - 1), pin_pos2)                        
                    #elif pin_pos1[1] < blk_pos1[1]: # top
                        #if ((pin_pos1[0] + 1, pin_pos1[1] + 1) == pin_pos2):  # top 2 right
                            #triv_map[pin_pos1] = triv_map[pin_pos2] = \
                                #(pin_pos1, (pin_pos1[0] + 1, pin_pos1[1]), pin_pos2)
                        #elif ((pin_pos1[0] - 1, pin_pos1[1] + 1) == pin_pos2): # top 2 left
                            #triv_map[pin_pos1] = triv_map[pin_pos2] = \
                                #(pin_pos1, (pin_pos1[0] - 1, pin_pos1[1]), pin_pos2)
                    #else:
                        #if ((pin_pos1[0] - 1, pin_pos1[1] - 1) == pin_pos2): # bottom 2 left
                            #triv_map[pin_pos1] = triv_map[pin_pos2] = \
                                #(pin_pos1, (pin_pos1[0] - 1, pin_pos1[1]), pin_pos2)
                        #elif ((pin_pos1[0] + 1, pin_pos1[1] - 1) == pin_pos2): # bottom 2 right
                            #triv_map[pin_pos1] = triv_map[pin_pos2] = \
                                #(pin_pos1, (pin_pos1[0] + 1, pin_pos1[1]), pin_pos2)
                    
        # all vbias from one class should be on one row
        for vb, rows in vbias_rows.items():
            if len(rows) > 1:
                self.costs["bias_row_" + vb[-1]] += len(rows) * self.VBIAS_PENALTY
                
        # vbias1+2 should be in the upper half and
        # vbias3+4 should be in the lower half
        for vb, poses in vbias_pos.items():
            vb_nr = int(vb[-1])
            if vb_nr in [1, 2]:
                for pos in poses:
                    if pos[1] > self.field.ny / 2:
                        self.costs["bias_place_" + vb[-1]] += self.VBIAS_PENALTY
            else:
                for pos in poses:
                    if pos[1] <= self.field.ny / 2:
                        self.costs["bias_place_" + vb[-1]] += self.VBIAS_PENALTY
                                
        # if input blocks are not neighbors
        if abs(inp_blk_pos[0][0] - inp_blk_pos[1][0]) != 2:
            self.costs["input_neighbours"] += self.INPUT_WRONG_PENALTY  * 5

        # calc euler-dist for inpX ports and penalize for not beeing exactly 4
        dist_inp = abs(inp_rows[0][0] - inp_rows[1][0]) + \
                   abs(inp_rows[0][1] - inp_rows[1][1])
        if dist_inp != 4:
            self.costs["input_dist"] += self.INPUT_WRONG_PENALTY * abs(dist_inp - 4)
            
        # penalize if inpX ports are not in the same row
        if inp_rows[0][1] != inp_rows[1][1]:
            self.costs["input_row"] += self.INPUT_WRONG_PENALTY * abs(inp_rows[0][1] - inp_rows[1][1]) * 5
            
        # penalize if inpX ports are not oriented in opposite directions
        if not(inp_dir == [1, 3] or inp_dir == [3, 1]):
            self.costs["input_direction"] += self.INPUT_WRONG_PENALTY
            
        # inputs should be in the middle of the field
        if not simple:
            for x, y in inp_rows:
                middle = round(abs(pin_max_x - pin_min_x) / 2, 0) + pin_min_x
                self.costs["input_place"] += \
                    max(0, int(abs(middle - x - 1))) * self.IN_OUT_PLACEMENT_PENALTY

        # outputs should be on the right side of the field
        for x, y in outp_cols:
            self.costs["output_place"] += \
                max(0, (pin_max_x - x)) * self.IN_OUT_PLACEMENT_PENALTY

        # the area should be minimized
        self.costs["area"] += \
            (blk_max_x+2 - blk_min_x) * (blk_max_y+2 - blk_min_y) * self.AREA_PENALTY
            
        # get routing costs
        if not simple:
            self.costs["routing"], self.costs["corner_penalty"], self.costs["wire_crossings"] = \
                self.calc_routing_cost(scaling=scaling)
        else:
            self.costs["routing"], self.costs["corner_penalty"], self.costs["wire_crossings"] = \
                self.calc_simple_routing(), 0, 0

        # return plain integer costs
        return int(sum(self.costs.values()))
    