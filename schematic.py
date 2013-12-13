import re
from string import split
from os.path import join
from random import choice

from drawing_area import DrawingArea
from field import Field, FieldException
from block import Block
from det_optimizer import Deterministic
from genetic_optimizer import GeneticAlgorithm
from base_optimizer import OptimizerError

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

    def plot(self, field):
        # initializing drawing area for the schematics
        self.draw_area_obj = canvas = DrawingArea(field, self.canvas_backend_cls)

        # some abrevations/constants
        nx, ny = field.nx, field.ny    
        mid = nx/2.
        lu, ru, lb, rb = [mid]*4 
        blockToPos = field.block_pos
        pin_pos, pin_dir = {}, {}

        # draw each block at its position
        for item in blockToPos.keys():
            bType, pos = item.type, blockToPos[item]
            rot = item.rotation
            mir = item.mirrored
            if bType == "nmos":
                canvas.nmos(pos, mir, rot)
            elif bType == "pmos":
                canvas.pmos(pos, mir, rot)
            elif bType == "i_constant":
                canvas.i_const(pos, rot)
            elif bType == "cap":
                canvas.c(pos, rot)
                
        # drawing dots 
        for dot in field.wire_dots:
            canvas.filled_dot(dot)
            
        # draw vdd and gnd line
        lw = canvas.linewidth
        canvas.ax.plot([lu, ru], [0, 0], color='k', linewidth=lw)
        canvas.ax.plot([lb, rb], [ny, ny], color='k', linewidth=lw)
        
        # draw open-input dots
        for direction, pos, name in field.open_dots:
            canvas.open_dot(pos, direction)
            mod_x = (-0.13 if direction == 1 else (-0.1 - len(name) * 0.1))
            canvas.draw_text((pos[0]+mod_x, pos[1]-0.4), name, fontsize=8, weight=600)
        
        # draw output pin
        outpos, o_count = None, 0
        ## determine output start position
        out_x = max(x for x, y in field.output_dots)
        for p in field.output_dots:
            if out_x == p[0]:
                add_y = 0 if outpos is None else outpos[1]
                outpos = (p[0], p[1] + add_y) 
                o_count += 1
        outpos = (outpos[0], outpos[1]/o_count)
        ## draw filled (soldering) dot and a wire/line to the right
        canvas.filled_dot(outpos)
        canvas.draw_line(outpos, (0, 0), (0.5, 0), 0)
        ## draw open (output pin) dot
        open_dot_point = (outpos[0] + 0.5, outpos[1])
        canvas.open_dot(open_dot_point, 1)
        ## draw label
        canvas.draw_text((open_dot_point[0]+0.3, open_dot_point[1]), "out", fontsize=8, weight=600)
        
        # draw wires
        for wire in field.wires:
            canvas.draw_line_simple(*wire)
                 
        # write id
        title_text = "Circuit: {}".format(self.cur_circ)
        canvas.draw_text((-2.2, -2.0), title_text, weight=600, fontsize=8)
        
        #### FIXME: fully abondon specdata, this does not belong here!
        # write specs
        #if field.spec_data is not None:
        #    start, step = -0.5, 0.9
        #    for i, (k, v) in enumerate(sorted(field.spec_data.items())):
        #        canvas.draw_text((-3.0, start+i*step), k, fontsize=8, weight=600)
        #        canvas.draw_text((-3.0, start+0.4+i*step), "{0:.2e}".format(float(v)), fontsize=8)
        
        # draw grid
        #scaling = 4.0
        #for x, y in field.field_cost.graph:
        #    canvas.dot((x/scaling, y/scaling), "black", 0.02, False)

    def save_all_to_file(self, c_data=None, c_metadata=None):
        # check if result data and output dir is given
        if c_data is None:
            print "[E] no schematic(s) passed to save_all_to_file()!"
            return 
        
        c_metadata = c_metadata or {}
        
        for cid, circ_raw, outfn in c_data:
            if self.generate_schematic(circ_raw, cid, specdata=c_metadata.get(cid)):
                self.write_to_file(outfn)
            else:
                print "[E] Could not generate schematic for circuit id: {}".format(cid)
                
    # write schematic to file
    def write_to_file(self, fn, dpi=600):
        if self.draw_area_obj:
            self.draw_area_obj.fig.savefig(fn, dpi=dpi)
            print "[+] saved schematic to " + fn
        
    # creates schematic of a single circuit
    def generate_schematic(self, circuit_raw=None, circuit_id=None, specdata=None, options=None):
        """
        Generate a schematic for the given raw circuit data.

        @param circuit_raw list-dict like [{"name":.. ,"type":.. , "conns":.. , "groups":..}, ..]
        @param circuit_id of the circuit as a tuple of strings ("foo", "bar")
        @param specdata optional additional "specification" data 
        @param options a {} to set various config options, see __init__()
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
            
            field = Field(self.cur_circ, xsize, ysize, self.cur_circ_raw)
            
            if optimizer == "deterministic":
                o = Deterministic(field)
            elif optimizer == "evolution":
                o = GeneticAlgorithm(field)
            else:
                print "[ERR] Unknown optimizer!"
                sys.exit(1)
                
            field = o.run() 
            field.spec_data = specdata            
            field.optimize_size()
            self.plot(field)
            return True
            
        except (OptimizerError, FieldException) as e:
            print "[-] failed to create schematic for circ {}".format(self.cur_circ)
            print e.message
            print e.tb
            return False
            
        return None # never reached
