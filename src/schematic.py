import re
from string import split
from os.path import join
from random import choice

from drawing_area import DrawingArea
from field import Field, FieldException
from block import Block
#from det_optimizer import Deterministic
#from genetic_optimizer import GeneticAlgorithm
#from base_optimizer import OptimizerError, FakeOptimizer

class Schematic:
    def __init__(self, canvas_backend_cls=None):
        # can be used instead of passing directly to generate_schematic
        self.cur_circ = None
        self.cur_circ_raw = None
        
        # canvas/drawing area
        self.draw_area_obj = None        

        # set canvas class
        if canvas_backend_cls is None:
            from matplotlib.backends.backend_pdf import FigureCanvasPdf
            canvas_backend_cls = FigureCanvasPdf
        self.canvas_backend_cls = canvas_backend_cls

    def plot(self, field, grid=None, net_names=False):
        # initializing drawing area for the schematics
        self.draw_area_obj = canvas = DrawingArea(field, self.canvas_backend_cls)

        # some abrevations/constants
        nx, ny = field.nx, field.ny    
        top_max, top_min = None, None
        bot_max, bot_min = None, None
        
        # block -> position mapping
        block2pos = field.block2xy 

        # draw each block at its position
        for blk, pos in block2pos.items():
            b_type, rot, mir, size  = blk.type, blk.rotation, blk.mirrored, blk.size
            bad_dir_top = (rot == 0 and not mir) or (rot == 2 and mir)
            add_max_top = size[0]/2 if not bad_dir_top else 0
            add_min_top = size[0]/2 if bad_dir_top else 0
            
            bad_dir_bot = (rot == 2 and not mir) or (rot == 0 and mir)
            add_max_bot = size[0]/2 if bad_dir_bot else 0
            add_min_bot = size[0]/2 if not bad_dir_bot else 0

            # find max x/y coors for wires, 
            # (only with vdd/vss connected devices)
            if blk.has_vdd:
                if top_max is None:
                    top_max = pos[0] + add_max_top
                else:
                    top_max = max(top_max, pos[0] + add_max_top)
                if top_min is None:
                    top_min = pos[0] + add_min_top
                else:
                    top_min = min(top_min, pos[0] + add_min_top)
            if blk.has_gnd:
                if bot_max is None:
                    bot_max = pos[0] + add_max_bot
                else:
                    bot_max = max(bot_max, pos[0] + add_max_bot) 
                if bot_min is None:
                    bot_min = pos[0] + add_min_bot
                else:
                    bot_min = min(bot_min, pos[0] + add_min_bot) 
            
            # device placement
            if b_type == "nmos":
                canvas.nmos(pos, mir, rot)
            elif b_type == "pmos":
                canvas.pmos(pos, mir, rot)
            elif b_type == "idc":
                canvas.i_const(pos, rot)
            elif b_type == "cap":
                canvas.c(pos, rot)
            elif b_type == "res":
                canvas.r(pos, rot)

            # pin naming
            if net_names:
                for pos, pin in blk.pins.items():
                    canvas.draw_text(pin.blk_pos, pin.net, fontsize=6, weight=200)
        
        # draw groups 
        if field.grp2pos is not None:
            txtposes = set()
            it = sorted(field.grp2pos.items(), key=lambda o: len(o[0].group_id))
            for grp, (x_pos, y_pos, x_size, y_size) in it: 
                lvl = len(grp.group_id)
                fill = True if lvl == 1 else False
                color = "0.77" if lvl == 1 else "0.00"
                shrink = lvl * 0.2
                gname = "({})".format(":".join( map(str, grp.group_id) ) \
                        if isinstance(grp.group_id, (tuple, list)) \
                        else str(grp.group_id))
                # calc box pos/size
                x_pos += shrink*0.8
                y_pos += shrink
                x_size -= shrink*2*0.8
                y_size -= shrink*2
                
                # calc unused text pos
                txt_pos = (x_pos+0.1, y_pos+0.5) if lvl == 2 else (x_pos+0.1, y_pos-0.2)
                while txt_pos in txtposes:
                    txt_pos = (txt_pos[0], txt_pos[1]+0.35)
                txtposes.add(txt_pos)

                canvas.draw_box_simple((x_pos, y_pos), x_size, y_size, fill=fill, color=color, zorder=-100)
                canvas.draw_text(txt_pos, gname, fontsize=6, weight=200*lvl**2)

        # drawing dots 
        for dot in field.wire_dots:
            canvas.filled_dot(dot)
            
        # draw vdd and gnd line
        vss_go, vss_end = (bot_min, ny), (bot_max, ny)
        vdd_go, vdd_end = (top_min, 0), (top_max, 0)

        if vdd_go is None or vdd_end is None or vss_go is None or vss_end is None:
            canvas.draw_line_simple(vdd_go, vdd_end)
            canvas.draw_line_simple(vss_go, vss_end)
        

        # draw open-input dots 
        for direction, pos, name in field.input_dots:
            canvas.open_dot(pos, direction)
            mod_x = (-0.13 if direction == 3 else (-0.1 - len(name) * 0.1))
            canvas.draw_text((pos[0]+mod_x, pos[1]-0.4), name, fontsize=8, weight=600)
        
        # draw output pin or not, if no output available
        if len(field.output_dots) > 0:
            for direction, pos, name in field.output_dots:
                outpos = pos
                ## draw filled (soldering) dot and a wire/line to the right 
                canvas.filled_dot(outpos)
                canvas.draw_line(outpos, (0, 0), (0.5, 0), 0)
                ## draw open (output pin) dot
                open_dot_point = (outpos[0] + 0.5, outpos[1])
                canvas.open_dot(open_dot_point, 1)
                ## draw label
                canvas.draw_text((open_dot_point[0]+0.3, open_dot_point[1]), name, fontsize=8, weight=600)
        
        # draw wires, if available
        for wire in field.wires:
            canvas.draw_line_simple(*wire)
                 
        # write id, if set
        if self.cur_circ is not None and len(self.cur_circ) != "":
            title_text = "Circuit: {}".format(self.cur_circ)
            canvas.draw_text((-2.2, -2.0), title_text, weight=600, fontsize=8)
        
        # draw grid 
        if grid is not None:

            # regular grid
            scaling = 2.0
            x_off, y_off = 0, 0
            width, height = 20*scaling, 20*scaling

            # custom grid set through 'grid' argument
            if len(grid) == 5:
                x_off, y_off = grid[2], grid[3]
                scaling = float(grid[4])
                width, height = int(grid[0]*scaling), int(grid[1]*scaling)

            # draw dots, 
            for x in xrange(x_off, width-x_off):
                for y in xrange(y_off, height-y_off):
                    canvas.dot((x/scaling + x_off, y/scaling + y_off), "black", 0.01, True)

    def save_all_to_file(self, c_data=None):
        """Pass multiple circuits as a list ('c_data') and generate their schematics
        
        c_data: list of (circuit_id, (raw) circuit blocks, output filename)
        """
        # check if result data and output dir is given
        if c_data is None:
            print "[E] no schematic(s) passed to save_all_to_file()!"
            return 
        
        for cid, circ_raw, outfn in c_data:
            if self.generate_schematic(circ_raw, cid):
                self.write_to_file(outfn)
            else:
                print "[E] Could not generate schematic for circuit id: {}".format(cid)
                
    # write schematic to file
    def write_to_file(self, fn, dpi=600):
        """Write this schematic to file at path 'fn' using a given 'dpi'"""
        if self.draw_area_obj:
            self.draw_area_obj.fig.savefig(fn, dpi=dpi)
            print "[+] saved schematic to " + fn
        
    # creates schematic of a single circuit
    def generate_schematic(self, circuit_raw=None, circuit_id=None, options=None):
        """
        Generate a schematic for the given raw circuit data.

        circuit_raw: list-dict like [{"name":.. ,"type":.. , "conns":.. , "groups":..}, ..]
        circuit_id: of the circuit as a tuple of strings ("foo", "bar")
        options: a {} to set various config options, see __init__()
        """
        # allow to pre-set target circuit as object-attr, 
        # instead of passing as argument
        self.cur_circ = circuit_id or self.cur_circ
        self.cur_circ_raw = circuit_raw or self.cur_circ_raw

        # make sure both contain something useful
        assert self.cur_circ
        assert self.cur_circ_raw
        
        # apply available OPTIONS here
        options = self.options = options or {}
        xsize = options.get("xsize") or 40
        ysize = options.get("ysize") or 40
        optimizer = "deterministic"
        if "optimizer" in options:
            optimizer = options["optimizer"]
        
        try:
            # max field size is critical...
            # DETERMINISTIC -> can be biiig, makes no difference
            # EVOLUTIONARY -> small approx 14x14 for 4block+bias 
            print "\n".join(str(x) for x in self.cur_circ_raw)
            field = Field(self.cur_circ, xsize, ysize)
            
            
            #if optimizer == "deterministic":
            #    o = Deterministic(field)
            #elif optimizer == "evolution":
            #    o = GeneticAlgorithm(field)
            #else:
            #    print "[ERR] Unknown optimizer!"
            #    sys.exit(1)
            
            o = FakeOptimizer(field, self.cur_circ_raw)
            
            field = o.run()        
            field.optimize_size()
            self.plot(field)
            return True
            
        except (OptimizerError, FieldException) as e:
            print "[-] failed to create schematic for circ {}".format(self.cur_circ)
            print e.message
            return False
            
        return None # never reached


def draw_field(field, fn, grid=None):
    """
    Simple wrapper to draw a Field() to a PDF.

    field: (with blocks filled) Field() to be drawn
    fn: write pdf to this filename
    grid: 'None'  -> no grid will be drawn
          'tuple' -> (<width>, <height>, <x_start>, <y_start>, <scaling>)
                     -> a grid with the given dimensions is drawn
          else    -> a default grid will be drawn -> (20, 20, 0, 0, 2)
    """
    s = Schematic()
    s.plot(field, grid=grid)
    s.write_to_file(fn)
    return fn


