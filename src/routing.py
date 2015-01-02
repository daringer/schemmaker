"""

Keeps the routing/wiring algorithm 

"""
import heapq

from field import Field, FieldException, FieldNode

class RoutingException(FieldException):
    def __init__(self, msg):
        FieldException.__init__(self)
        self.message += msg


class Routing:
    dirs = list(((0, -1), (0, 1), (-1, 0), (1, 0)))
    
    def __init__(self, field, scaling=4):
        self.field = field
        self.net_forbidden_pos = {}
        self.scaling = scaling

    def scale_up(self, pos, scaling):
        x, y = pos
        return (x*scaling, y*scaling)
    
    def scale_down(self, pos, scaling):
        x, y = pos
        return (x/float(scaling), y/float(scaling))     

   
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
            
            print "ROUTING - from: ", from_pos , " to: ", to_pos

            #if from_pos not in self.graph:
            #    assert False, "find_path() called with target pos not inside graph"
            if from_pos not in self.graph:
                raise RoutingException("from: " + str(from_pos) + " was not found in graph")
    

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
                raise RoutingException("from: " + str(from_pos) + " to: " + str(min_to_pos))
                #return None, None
            
            # find path to cheapest destination
            to_pos = min_to_pos
            path = [to_pos]
            target_pos, pos = from_pos, to_pos
            direction, last_direction = None, None
            
            # make sure we can get there / don't we do this up there
            #if pos not in path_matrix:
            #    return (None, None)
            
            # start at destination and go backward through the path_matrix
            while pos != target_pos:
                last_pos, pos = pos, path_matrix[pos]
                direction = (pos[0] - last_pos[0], pos[1] - last_pos[1])
                
                if (last_direction is not None and direction != last_direction):
                    path += [last_pos]
                    
                last_direction = direction
                
            path += [pos]
            return (path, cost_matrix[to_pos])
    
    
    def path_cost(self, path, dist=None, trivial=False):
        """Calculate the costs (distance) of an path"""
        routing = 0
        corner_penalty = 0
        
        if trivial:
            routing = 1
        elif len(path) == 2:
            routing = dist * 1
        else:
            routing = dist * 1 
            corner_penalty = 0 # TODO
            
        return routing, corner_penalty
    
    def expand_path_to_pieces(self, path):
        """
        'path' contains 2-tuples ((x1, y1), ..., (xN, yN)), 
        which are expanded make sure each path component has the 
        length of 1
        """
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
        """
        Calculate Pseudo-Steiner-Tree for:
        'open_pins' the pins to be connected together
        'wire_pieces' existing wiring (which has to be avoided during routing)
        'bad_points' existing points (solder dots etc.) to be avoided
        """
        conns = {}
        
        initial_open = set(open_pins)
        
        available_targets = set()
        available_targets.add(initial_open.pop())
        
        remaining = initial_open - available_targets
        
        # find shortest full-route (pseudo-tsp!?)
        while len(remaining) > 0:
            # find all paths to targets
            min_cost, min_path, min_from, min_target = None, None, None, None
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
                raise RoutingException("from: " + str(remaining) + " to: " + str(available_targets))
                #continue
            
            # found shortest
            m_set = set()
            for p1, p2 in self.expand_path_to_pieces(min_path):
                m_set.add(p1)
                m_set.add(p2)
                
            available_targets = available_targets | m_set
            remaining = remaining - m_set
            
            conns[(min_from, min_target)] = (min_path, min_cost)
            
        return conns

    def get_field_nodes(self, scaling):
            """Build and return a dict of {pos: FieldNode()} for all visitable nodes"""
            pos_map, net_map = {}, {}
            for _blk_pos, block in self.field.iter_xy_pos_block(split=False, unique=True):
                print block
                blk_pos = self.scale_up(_blk_pos, scaling)
                for _pos, pin in block.pins.items():
                    
                    pos = self.scale_up(_pos, scaling)
                    
                    if len(block.pins) == 3:
                        if block.get_pin_direction(pin) == 0:
                            pos = (pos[0], pos[1]+1)
                        elif block.get_pin_direction(pin) == 1:
                            pos = (pos[0]+1, pos[1])
                        elif block.get_pin_direction(pin) == 2:
                            pos = (pos[0], pos[1]-1)
                        else:
                            pos = (pos[0]-0, pos[1])


                    if pos not in pos_map:
                        pos_map[pos] = FieldNode(pin.net, pos )
                    else:
                        pos_map[pos].names.append(pin.net)
                    poses = net_map.setdefault(pin.net, list()) #set()
                    if pos not in poses:
                        poses.append((pos[0]+blk_pos[0],pos[1]+blk_pos[1]))
            
            if scaling == 1:
               hole_mask = ("XX",
                            "XX")
            elif scaling == 2:
                hole_mask = ("00O0"
                             "0XX0"
                             "0XX0"
                             "00O0")
            elif scaling == 4:
                #hole_mask = ("00000000",
                #             "00000000",
                #             "00OOOOO0",
                #             "00OOOOO0",
                #             "00000000",
                #             "00OOOOO0",
                #             "00OOOOO0",
                #             "00000000")
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

    def route(self, scaling):
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
            final_paths = self.calc_routes(sorted(connect_poses), wire_pieces, self.net_forbidden_pos[net], scaling)
            
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
        
        
    # URGS ULTRAUGLY!
    def calc_simple_routing(self):
        net_pos = {}
        blks = self.field.get_blocks()[:]
        for blk in blks:
            for pin in blk.pins.values():
                if not pin.supply and not pin.gnd and not pin.biased:
                    b_pos = self.field.get_block_pos(blk)
                    net_pos.setdefault(pin.net, set()).add((b_pos[0]+1, b_pos[1]+1))
                    
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
                
