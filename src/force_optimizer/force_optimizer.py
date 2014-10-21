'''
Created on 23.03.2014

@author: Christian Auth
'''


from base_optimizer import BaseOptimizer
from field import Field, FieldException
from operator import itemgetter, attrgetter
from group import Group
from block import Block
from PyQt4 import QtGui
from PyQt4 import QtCore

import sys
import build_step
import initial_step
import main_step
import time

MAIN_GRP = -4
OUT_GRP = -1
VCC_GRP = -3
GND_GRP = -2

class ForceAlgorithm(BaseOptimizer):
    '''
    '''
    def __init__(self, field, blocks, north_pins, south_pins, east_pins, west_pins):
        '''
        '''

        print "init Force Algorithm"

        BaseOptimizer.__init__(self, field)

        self.groups = []
        self.blocks = blocks
        self.wide_search_index = 0
        self.wide_search_queue = []

        self.pins_east = east_pins
        self.pins_west = west_pins
        self.pins_north = north_pins
        self.pins_south = south_pins

        # dictionary with pin.net_name as key and a block list as value
        self.dictionary_net_blocks = {}
        self.dictionary_vdd_blocks = {}
        self.dictionary_out_blocks = {}
        self.dictionary_gnd_blocks = {}
        self.dictionary_inp_blocks = {}
        self.dictionary_bia_blocks = {}

        self.group_east = Group([OUT_GRP])
        self.group_south = Group([GND_GRP])
        self.group_north = Group([VCC_GRP])
        self.group_west = Group([-5])
        self.group_main = Group([MAIN_GRP])

        self.group_east.neighbor_west.append(self.group_main)
        self.group_main.neighbor_east.append(self.group_east)

        self.group_west.neighbor_east.append(self.group_main)
        self.group_main.neighbor_west.append(self.group_west)

        self.group_north.neighbor_south.append(self.group_main)
        self.group_main.neighbor_north.append(self.group_north)

        self.group_main.neighbor_south.append(self.group_south)
        self.group_south.neighbor_north.append(self.group_main)


        start = time.time()
        build_step.start(self)
        end = time.time()
        interval_build_step = end - start


        start = time.time()
        initial_step.start(self)
        end = time.time()
        interval_initial_step = end - start

        app1 = QtGui.QApplication(sys.argv)
        ex1 = Example([self.group_main.position_x, self.group_main.position_y, self.group_main.size_width, self.group_main.size_height], "Main Step", self)
        app1.exec_()
        

        start = time.time()
        main_step.start(self)
        end = time.time()
        interval_main_step = end - start

        print "============================================"
        print('build_step took %.03f sec.' % interval_build_step)
        print "============================================"
        print "============================================"
        print('initial_step took %.03f sec.' % interval_initial_step)
        print "============================================"
        print "============================================"
        print('main_step took %.03f sec.' % interval_main_step)
        print "============================================"

        

class Example(QtGui.QMainWindow):

    def __init__(self, frame, group_id, forceOptimizer):
        '''
        '''
        super(Example, self).__init__()
        self.labels = []
        self.x = frame[0]
        self.y = frame[1]
        self.width = frame[2]
        self.height = frame[3]
        self.title = group_id
        self.forceOptimizer = forceOptimizer
        self.initUI()

    def initUI(self):
        '''
        '''
        self.setGeometry(self.x * 50, self.y * 50, self.width * 50, self.height * 50)
        self.setWindowTitle(self.title)

        for group in self.forceOptimizer.groups:

            pos_x = group.position_x * 50 + group.parent.position_x
            pos_y = group.position_y * 50 + group.parent.position_y
            group.position_x = pos_x
            group.position_y = pos_y

            for block in group.blocks:

                label = QtGui.QLabel(block.name, self)
                label.setGeometry(block.pos[0] * 50 + pos_x, block.pos[1] * 50 + pos_y, 50, 50)

        self.show()

    def paintEvent(self, e):
        '''
        '''
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawRectangles(qp)
        qp.end()



    def drawRectangles(self, qp):
        '''
        '''
        color = QtGui.QColor(0, 0, 0)
        qp.setPen(color)

        for group in self.forceOptimizer.groups:

            red = 255
            green = 255
            blue = 255
            '''
            if len(group.group_id) < 2:
                red = (group.group_id[0] * 30) % 256
            elif len(group.group_id) < 3:
                red = (group.group_id[0] * 30) % 256
                green = (group.group_id[1] * 30) % 256

            else:
                red = (group.group_id[0] * 10) % 256
                green = (group.group_id[1] * 10) % 256
                blue = (group.group_id[2] * 10) % 256
            '''
            qp.setBrush(QtGui.QColor(red, green, blue))

            qp.drawRect(group.position_x, group.position_y, group.size_width * 50, group.size_height * 50)

            for block in group.blocks:

                qp.setBrush(QtGui.QColor(255, 255, 255))
                qp.drawRect(block.pos[0] * 50 + group.position_x, block.pos[1] * 50 + group.position_y, 1 * 50, 1 * 50)





