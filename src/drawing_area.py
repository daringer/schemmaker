from math import sin, cos, pi

import matplotlib.pyplot as plt
#import pylab
from matplotlib.ticker import NullLocator

class DrawingArea:
    def __init__(self, field, canvas_backend_cls):
        """
        Construct drawing area for schematic plotting.

        field: the (schematic-)field to be plotted
        canvas_backend_cls: canvas class to create as drawing object, examples:
            gtk: from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg
            pdf: from matplotlib.backends.backend_pdf import FigureCanvasPdf
        """

        # adjust figure properties
        self.fig = fig = plt.figure()
        fig.subplots_adjust(bottom=0.005)
        fig.subplots_adjust(top=1)
        fig.subplots_adjust(left=0.000)
        fig.subplots_adjust(right=0.995)
        self.ax = fig.add_subplot(1,1,1)
        
        # determine axis-dimensions and set
        self.xy_max = max(field.nx+4.0, field.ny+4.0)
        self.xy_range = 4.0 + self.xy_max
        self.ax.axis([-4.0, self.xy_max, -4.0, self.xy_max])
        
        # ???
        self.ax.xaxis.set_major_locator(NullLocator())
        self.ax.yaxis.set_major_locator(NullLocator())

        # invert_yaxis (positive y means down)
        self.ax.invert_yaxis()

        # init canvas with figure
        self.plt_fig = canvas_backend_cls(fig)
        
        # constants
        self.angles = {0: 0, 1: -pi/2., 2: -pi, 3: -3*pi/2.}
        self.linewidth = 1.5
        
        # draw gnd and vdd
        self.gnd((field.nx/2. - 1, field.ny-0.25), 0)
        self.vdd((field.nx/2. - 1, -1.75), 0)  

    def _get_device_draw_pos(self, pos, rot):
        """
        Move position into middle of device and 
        translate rotation idx to radiant
        """
        # get radiant from rotation index
        r = self.angles.get(rot)
        if r is None:
            print "[E] rotation index not legal: {0}".format()
            print "[i] setting to 0"
            r = self.angles.get(0)
        
        # translate the root to the middle of the box
        x, y = pos[0] + 1, pos[1] + 1

        return (x, y), r

    def get_canvas(self):
        """Return figure to plot in"""
        return self.plt_fig
    
    def filled_dot(self, pos):
        """Draw a filled dot (soldering dot)"""
        self.dot(pos, 'k', 0.07, True)
 
    def draw_text(self, pos, s, **kwargs):
        """Draw text"""
        rel_pos = (4.0+pos[0])/float(self.xy_range), 1-(4.0+pos[1])/float(self.xy_range)
        plt.figtext(rel_pos[0], rel_pos[1], s, **kwargs)
        
    def open_dot(self, pos, cdir):
        """Draw open dot used for pins"""
        cor = 0.1
        if cdir == 0:
            pos = (pos[0], pos[1]-cor)
        elif cdir == 1:
            pos = (pos[0]+cor, pos[1])  
        elif cdir == 2:
            pos = (pos[0], pos[1]+cor)         
        elif cdir == 3:
            pos = (pos[0]-cor, pos[1])         
        self.dot(pos, 'k', 0.12, False)
    
    def dot(self, pos, col, rad, fil):
        """Draw a dot"""
        dot = plt.Circle(pos, radius=rad, color=col, fill=fil, linewidth=self.linewidth)
        self.ax.add_patch(dot)

    def draw_circle(self, root, p, r, w):
        """Draw circle"""
        x,y = root
        p = self.rotate(p, w)
        x0, y0 = x+p[0], y+p[1]
        self.ax.add_patch(
            plt.Circle((x0, y0), radius=r, color='k', fill=False, linewidth=self.linewidth)
        )
        
    def draw_box_simple(self, root, width, height, **kwargs):
        """Draw a rectangle"""
        self.ax.add_patch(
                plt.Rectangle(root, width=width, height=height, **kwargs)
        ) 

    def draw_line_simple(self, p1, p2):
        """Draw simple line (without rotation)"""
        root = p1
        p2 = [p2[0]-p1[0], p2[1]-p1[1]]
        p1 = [0,0]
        self.draw_line(root, p1, p2, 0)

    def draw_line(self, root, p1, p2, alpha):
        """Draw single line"""
        x, y = root
        p1 = self.rotate(p1, alpha)
        p2 = self.rotate(p2, alpha)
        x0, y0 = x+p1[0], y+p1[1]
        x1, y1 = x+p2[0], y+p2[1]
        self.ax.plot([x0, x1], [y0, y1], 'k', linewidth=self.linewidth)

    def draw_lines(self, root, point_pairs, alpha):
        """Draw multiple lines"""
        for (p1, p2) in point_pairs:
            self.draw_line(root, p1, p2, alpha)

    def rotate(self, xy, alpha):
        """Rotate coordinates according to angle given by 'alpha' (in rad)"""
        s, c = sin(alpha), cos(alpha)
        x0, y0 = xy
        x = round(c*x0 - s*y0, 2)
        y = round(s*x0 + c*y0, 2)
        return x, y

    #####
    #### Drawing methods for the various devices!
    #####
    def pmos(self, xy, mir=False, rot=0):
        """Draw PMOS device"""
        self._mos(xy, mir, rot, mtype="p")
    
    def nmos(self, xy, mir=False, rot=0):
        """Draw NMOS device"""
        self._mos(xy, mir, rot, mtype="n")    

    def _mos(self, xy, mir=False, rot=0, mtype=None):
        """
        Actual drawing method for mos devices.

        xy: position to be drawn at
        mir: is device mirrored
        rot: rotation of the device
        mtype: either "p" for PMOS or "n" for NMOS
        """
        pos, alpha = self._get_device_draw_pos(xy, rot)

        # mirror independent
        ## drawing pre-calculations
        sig = lambda x: x if not mir else -x
        height = h = 0.25
        width = w = 0.35
        gate = g = h + 0.1
        
        ## upper(pmos) wire
        self.draw_line(pos, (0, h+0.15), (0, 0.7), alpha) 
        ## lower(pmos) wire
        self.draw_line(pos, (0, -h-0.15), (0, -0.7), alpha) 
        
        # mirror dependent
        ## upper line
        self.draw_line(pos, (0, h+0.1), (sig(h), h+0.1), alpha)
        ## lower line
        self.draw_line(pos, (0, -h-0.1), (sig(h), -h-0.1), alpha)
        ## bottom gate
        self.draw_line(pos, (sig(h), w), (sig(h), -w), alpha)
        ## gate
        self.draw_line(pos, (sig(g), w), (sig(g), -w), alpha)

        ## wire to gate: PMOS -> shorter, NMOS -> longer
        longer_gate = 0.0
        if mtype == "p":
            ### p-mos dot
            self.draw_circle(pos, (sig(g+0.12), 0), 0.1, alpha)
        else:    
            longer_gate = 0.15
        ## gate-wire
        self.draw_line(pos, (sig(g+0.4), 0), (sig(g+0.2-longer_gate), 0), alpha)

    def r(self, xy, rot):
        """Draw resistor device"""
        pos, alpha = self._get_device_draw_pos(xy, rot)

        points = [
            ((0, 1/2.), (0, 1.0)),           ((0, -1/2.), (0, -1.0)),
            ((-2/7., 1/2.), (2/7., 1/2.)),   ((-2/7., -1/2.), (2/7., -1/2.)),
            ((-2/7., 1/2.), (-2/7., -1/2.)), ((2/7., 1/2.), (2/7., -1/2.)) 
        ]

        self.draw_lines(pos, points, alpha)

    def c(self, xy, rot):
        """Draw capacitor device"""
        pos, alpha = self._get_device_draw_pos(xy, rot)

        points = [
            ((0, 1/7.), (0, 1.0)),         ((0, -1/7.), (0, -1.0)),
            ((-1/3., 1/7.), (1/3., 1/7.)), ((-1/3., -1/7.), (1/3., -1/7.))
        ]
        self.draw_lines(pos, points, alpha)

    def i_const(self, xy, rot):
        """Draw constant current source"""
        pos, alpha = self._get_device_draw_pos(xy, rot)

        points = [
            ((0, 2/7.),   (0, 1.0)), 
            ((0, -2/7.), (0, -1.0+(2/7.))),
            ((-2/7., 0), (2/7., 0))
        ]
        self.draw_lines(pos, points, alpha)
        self.draw_circle(pos, (0, 0), 2/7., alpha)

    def gnd(self, xy, rot):
        """Draw ground symbol"""
        pos, alpha = self._get_device_draw_pos(xy, rot)

        points = [
            ((0, -1/7.), (0, -1.0)), ((-1/3., -1/7.), (1/3., -1/7.))
        ]
        self.draw_lines(pos, points, alpha)
        self.filled_dot((pos[0], pos[1]-1))

    def vdd(self, xy, rot):
        """Draw supply voltage symbol"""
        pos, alpha = self._get_device_draw_pos(xy, rot)

        points = [
            ((0, 1/7.), (0, 1.0)),       ((-1/5., 1/7.), (1/5., 1/7.)),
            ((-1/5., 1/7.), (0, -1/7.)), ((1/5., 1/7.), (0, -1/7.))
        ]
        self.draw_lines(pos, points, alpha)
        self.filled_dot((pos[0], pos[1]+1))
