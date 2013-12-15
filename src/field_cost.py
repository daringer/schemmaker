# -*- coding: utf-8 -*-
from scipy import *
from print_block import *
from block import Block
from math import sqrt, factorial, pow
from random import choice, shuffle
import itertools
import heapq
import copy

from field import Field, FieldException

class FieldCostException(FieldException):
    def __init__(self, msg):
        FieldException.__init__(self)
        self.message += msg

class FieldCostRouteNotFoundException(FieldCostException):
    pass


class FieldNode:
    def __init__(self, name, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.names = name and [name]
    
class FieldCost:
    dirs = list(((0, -1), (0, 1), (-1, 0), (1, 0)))

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
        
    def scale_up(self, pos, scaling):
        x, y = pos
        return (x*scaling, y*scaling)
    
    def scale_down(self, pos, scaling):
        x, y = pos
        return (x/float(scaling), y/float(scaling))     

    def get_field_nodes(self, scaling):
        """Build and return a dict of {pos: FieldNode()} for all visitable nodes"""
        pos_map, net_map = {}, {}
        for blk_pos, block in self.field.iter_xy_pos_block(split=False, unique=True):
            for i, conn in block.conns.items():
                pos = self.scale_up(block.get_pin_position(i, blk_pos), scaling)
                direction = None
                # (transistor) pin position is also scaled a bit
                if len(block.conns) == 3: # and conn not in ["gnd", "vdd"]:
                    scaled_blk_pos = self.scale_up(blk_pos, scaling)
                    rel_pos = (pos[0]-scaled_blk_pos[0], pos[1]-scaled_blk_pos[1])
                    if rel_pos[0] == 0:
                        pos = (pos[0] + 1, pos[1])
                        direction = 3
                    elif rel_pos[1] == 0:
                        pos = (pos[0], pos[1] + 2)
                        direction = 0
                    elif rel_pos[0] > rel_pos[1]:
                        pos = (pos[0] - 1, pos[1])
                        direction = 1
                    else:
                        pos = (pos[0], pos[1] - 2)
                        direction = 2

                # conn is a input net, save position at field
                if conn.startswith("inp"):
                    self.field.open_dots += [(direction, self.scale_down(pos, scaling), conn)]                                        
                # conn is a output net, save position at field
                if conn.startswith("outp"):
                    self.field.output_dots += [self.scale_down(pos, scaling)]
                    
                if pos not in pos_map:
                    pos_map[pos] = FieldNode(conn, pos)
                else:
                    pos_map[pos].names.append(conn)
                poses = net_map.setdefault(conn, list()) #set()
                if pos not in poses:
                    poses.append(pos)
        
        if scaling == 1:
            hole_mask = ("XX",
                         "XX")
        elif scaling == 2:
            hole_mask = ("0000"
                         "0XX0"
                         "0XX0"
                         "0000")
        elif scaling == 4:
            hole_mask = ("00000000",
                         "00000000",
                         "00XXXXX0",
                         "00XXXXX0",
                         "00000000",
                         "00XXXXX0",
                         "00XXXXX0",
                         "00000000")
        else:
            hole_mask = ()
        
        holes = []
        for y, _inner in enumerate(hole_mask):
            holes += [(x, y) for x, val in enumerate(_inner) if val == "X"]
        
        all_holes = []
        for h_x, h_y in holes:
            all_holes += [(x*scaling+h_x, y*scaling+h_y) \
              for (x, y), b in self.field.iter_xy_pos_block(split=False, unique=True)]

        for pos in self.field.iter_wire(scaling):
            if pos not in pos_map and pos not in all_holes:
                pos_map[pos] = FieldNode(None, pos)
            
        return pos_map, net_map
    
    ### FIELD COST 
    def find_path(self, pos, to_pos, wire_pieces, bad_points, scaling):
        """A-star/Dijkstra path-finding for multiple targets"""
        from_pos = pos
        visited = set()
        heap = []
        path_matrix, cost_matrix = {}, {}
        
        max_x, min_x = self.field.nx*scaling, 0
        max_y, min_y = self.field.ny*scaling, 0
        
        
        cost_matrix[pos] = 0
        heapq.heappush(heap, (0, pos))
        
        #if from_pos not in self.graph:
        #    assert False, "find_path() called with target pos not inside graph"
        if from_pos not in self.graph:
            raise FieldCostRouteNotFoundException("from: ", from_pos, " was not found in graph")

        # Dijkstra -> try to visit all nodes    (len(graph) > len(visited) and len(heap) > 0)
        cost_fnc = lambda p1, p2: cost_matrix[p1] + 1
        while len(self.graph) > len(visited) and len(heap) > 0:
        # A-star -> take first found path       (pos != to_pos)
        #cost_fnc = lambda p1, p2: abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
        #while pos != to_pos:
            pos = heapq.heappop(heap)[1]
            
            visited.add(pos)
            
            for d in self.dirs:
                target = (d[0] + pos[0], d[1] + pos[1])

                if target in visited:
                    continue
                # only allow routes inside the field
                if target[0] < min_x or target[0] > max_x:
                    continue
                if target[1] < min_y or target[1] > max_y:
                    continue
                # is there such a point?
                if target not in self.graph:
                    continue
                # make sure no wire overlaps
                if (target, pos) in wire_pieces or (pos, target) in wire_pieces:
                    continue
                # points owned by other nets are not allowed
                if target in bad_points:
                    continue
                                
                new_cost = cost_matrix[pos] + 1
                if target not in cost_matrix or cost_matrix[target] > new_cost:
                    cost_matrix[target] = new_cost
                    path_matrix[target] = pos
                                                                
                    heapq.heappush(heap, (cost_fnc(target, to_pos), target))
        
        # determine the cheapest of the possible destinations 
        min_to_pos = None
        for p in to_pos:
            if p not in cost_matrix:
                continue
            
            if min_to_pos is None or cost_matrix[min_to_pos] > cost_matrix[p]:
                min_to_pos = p
        
        if min_to_pos is None:
            raise FieldCostRouteNotFoundException("from: " + str(from_pos) + " to: " + str(min_to_pos))
        
        # find path to cheapest destination
        to_pos = min_to_pos
        path = [to_pos]
        target_pos, pos = from_pos, to_pos
        direction, last_direction = None, None
        
        # make sure we can get there / don't we do this up there
        #if pos not in path_matrix:
        #    return (None, None)
        
        # start at destination and go bachward through the path_matrix
        while pos != target_pos:
            last_pos, pos = pos, path_matrix[pos]
            direction = (pos[0] - last_pos[0], pos[1] - last_pos[1])
            
            if (last_direction is not None and direction != last_direction):
                path += [last_pos]
                
            last_direction = direction
            
        path += [pos]
        return (path, cost_matrix[to_pos])


    def path_cost(self, path, dist=None, trivial=False):
        routing = 0
        corner_penalty = 0
        
        if trivial:
            routing = self.TRIVIAL_ROUTE_COST
        elif len(path) == 2:
            routing = dist * self.STRAIGHT_WIRE_FACTOR
        else:
            routing = (dist * self.ROUTING_PENALTY) ** self.ROUTING_EXPONENT
            corner_penalty = ((len(path)-2) ** self.CORNER_EXPONENT) * self.CORNER_PENALTY
            
        return routing, corner_penalty
    
    def expand_path_to_pieces(self, path):
        out = []
        for p1, p2 in self.field.iter_pairwise(path):
            i = 1 if p1[0] == p2[0] else 0
            start, end = min(p1[i], p2[i]), min(p1[i], p2[i]) + abs(p1[i] - p2[i]) + 1
                            
            # cut wires into smaller pieces to save them as obstacles
            for i1, i2 in self.field.iter_pairwise(range(start, end)):
                w_p1, w_p2 = ((i1, p1[1]), (i2, p2[1])) if p1[1] == p2[1] else \
                    ((p1[0], i1), (p2[0], i2))
                out.append((w_p1, w_p2))
        return out
    
    
    def calc_routes(self, open_pins, wire_pieces, bad_points, scaling):
        conns = {}
        
        initial_open = set(open_pins)
        
        available_targets = set()
        available_targets.add(initial_open.pop())
        
        remaining = initial_open - available_targets
        
        # find shortest full-route (pseudo-tsp!?)
        while len(remaining) > 0:
            # find all paths to targets
            min_cost, min_path, min_from, min_target = None, None, None, None
            #for to_pos in available_targets:
            for from_pos in remaining:                        
                path, dist = self.find_path(from_pos, list(available_targets), wire_pieces, bad_points, scaling)
                
                if path is None:
                    continue
                
                #cost = self.path_cost(path, dist)
                cost = (dist + len(path) - 2, 0)
                if min_cost is None or min_cost[0] > cost[0]:
                    min_cost = cost
                    min_path = path
                    min_target = path[0]
                    min_from = from_pos
                        
            if min_cost is None:
                raise FieldCostRouteNotFoundException("from: " + str(remaining) + " to: " + str(available_targets))
            
            # found shortest
            m_set = set()
            for p1, p2 in self.expand_path_to_pieces(min_path):
                m_set.add(p1)
                m_set.add(p2)
                
            available_targets = available_targets | m_set
            remaining = remaining - m_set
            
            #print min_path, min_cost
            conns[(min_from, min_target)] = (min_path, min_cost)
            
        return conns
               
    def calc_routing_cost(self, scaling):
        routing_cost, corner_cost, crossing_cost = 0, 0, 0
        wire_pieces = []
        
        self.graph, nets = self.get_field_nodes(scaling)
        self.field.wires = []
        self.field.wire_dots = []
        self.net_forbidden_pos = {}

        # setup a set of forbidden points for each net
        for net, poses in nets.items():
            self.net_forbidden_pos[net] = set()
            for other_net, other_poses in nets.items():
                if other_net != net:
                    self.net_forbidden_pos[net].update(other_poses)
        
        for net, poses in nets.items():
            if len(poses) < 2 and not net in ["vdd", "gnd"]: ### <- ???
                continue
            
            # add additional "fake" open nets to "vdd" and "gnd" to force the router
            # to connect vdd/gnd blocks, which are not placed on top/bottom of the circuit
            connect_poses = poses[:]
            if net in ["vdd", "gnd"]:
                target_y = 0 if net == "vdd" else self.field.ny*scaling
                for x, y in poses:
                    if y != target_y:
                        connect_poses.append((x, target_y))                        
            
            # init "wire-point" -count map with all pins as points (without the "virtual" pins)
            point_dot_map = pdm = dict((pin, 1) for pin in poses)
                        
            # actually calculate paths
            final_paths = self.calc_routes(sorted(connect_poses), wire_pieces, self.net_forbidden_pos[net], scaling=scaling)
            
            # go over all generated paths and add them to field and maintain "wire_pieces"
            for from_to, (paths, (path_cost, path_corner_cost)) in final_paths.items():
                routing_cost += path_cost
                corner_cost += path_corner_cost
                
                for w_p1, w_p2 in self.expand_path_to_pieces(paths):
                    # maintain a "wire-point" count ... count>2 <==> soldering-dot 
                    pdm.setdefault(w_p1, 0)
                    pdm.setdefault(w_p2, 0)                        
                    pdm[w_p1] += 1
                    pdm[w_p2] += 1
                    # keep full list of wire pieces, should be avoided by the other wires
                    wire_pieces += [(w_p1, w_p2)]
                
                for p1, p2 in self.field.iter_pairwise(paths):
                    # convention for wires: pos with smaller x, if equal y decides -> left 
                    _p1, _p2 = (p1, p2) if p1<=p2 else (p2, p1)
                    self.field.wires.append((self.scale_down(_p1, scaling), self.scale_down(_p2, scaling)))
            
            
            # add wire dots to forbidden points to other nets
            wire_dots = [self.scale_down(p, scaling) for p, num in pdm.items() if num > 2]
            self.field.wire_dots += wire_dots
            for t_net in self.net_forbidden_pos:
                if net != t_net:
                    self.net_forbidden_pos[net].update(wire_dots)
                
        # obsolete, due to dot counting?!     
        #crossing_cost += self.find_crossings(self.field.wires)
        return routing_cost, corner_cost, crossing_cost
        
    def calc_simple_routing(self):
        net_pos = {}
        blks = self.field.get_blocks()[:]
        for blk in blks:
            for net in blk.conns.values():
                if net not in ["vdd", "gnd"] and not net.startswith("vbias"):
                    b_pos = self.field.get_block_pos(blk)
                    net_pos.setdefault(net, set()).add((b_pos[0]+1, b_pos[1]+1))
                    
        cost = 0
        for net, posis in net_pos.items():
            net_cost = 0
            for pos in posis:
                for to_pos in posis:
                    if abs(to_pos[0] - pos[0]) <= 2:
                        net_cost += 1
                    else:
                        net_cost += 2
            cost += net_cost
        return cost
                


    def cost(self, simple=False, scaling=4):
        self.field.clean_up()
        
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
    