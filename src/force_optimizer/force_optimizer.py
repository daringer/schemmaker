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

        # flags
        self.group_connected_to_parent_neighbor_set_parent_size = False


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

        qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setBrush(QtGui.QColor(255, 255, 255))

        for group in self.forceOptimizer.groups:
            qp.drawRect(group.position_x, group.position_y, group.size_width * 50, group.size_height * 50)

        qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setBrush(QtGui.QColor(255, 255, 255))

        for group in self.forceOptimizer.groups:
            for block in group.blocks:

                qp.drawRect(block.pos[0] * 50 + group.position_x, block.pos[1] * 50 + group.position_y, 1 * 50, 1 * 50)
                label = QtGui.QLabel(block.name, self)

                label.setGeometry(block.pos[0] * 50 + group.position_x+5, block.pos[1] * 50 + group.position_y, 50, 50)
                label.show()
        '''
        for group in self.forceOptimizer.groups:
            print ""
            print "Group:", group.group_id, " POS_X:", group.position_x, " POS_Y:", group.position_y

            for block in group.blocks:
                b_x = block.pos[0] * 50 + group.position_x + 25
                b_y = block.pos[1] * 50 + group.position_y + 25
                print ""
                print "Block:", block.name, " POS_X:", b_x, " POS_Y:", b_y, "Pins:", block.pins.values()
                neighbors = search_neighbors(block, self.forceOptimizer)

                for neighbor in neighbors:

                    neighbor_group = search_group(neighbor.groups, self.forceOptimizer)


                    n_x = neighbor.pos[0] * 50 + neighbor_group.position_x + 25
                    n_y = neighbor.pos[1] * 50 + neighbor_group.position_x + 25

                    qp.drawLine(b_x, b_y, n_x, n_y)
                    print "Neighbor:",neighbor.name , " POS_X:", n_x, " POS_Y:", n_y
                    print "NeighborGroup:", neighbor_group.group_id, " POS_X:", neighbor_group.position_x, " POS_Y:", neighbor_group.position_y
        '''
def search_neighbors(block, forceOptimizer):
    neighbors = {}
    for pin in block.pins.values():
        #print pin.net
        if pin.net in forceOptimizer.dictionary_net_blocks:
            for block_neighbor in forceOptimizer.dictionary_net_blocks[pin.net]:
                if block is not block_neighbor:
                    if block_neighbor not in neighbors:
                        neighbors[block_neighbor] = 1
                    else:
                        value = neighbors[block_neighbor]
                        value += 1
                        neighbors[block_neighbor] = value
    for neighbor in neighbors:
        pass #print "Neighbor Block:", neighbor.name, "Group:", str(neighbor.groups)
    return neighbors





def search_group(group_id, forceOptimizer):
    '''
    PARAMETER:  group_ids     is an array with the IDs of the parent Groups and the ID of the searched group
                return        the group if it exists, else None
    STATE:      not finish
    '''
    for group in forceOptimizer.groups:
        if group.group_id == group_id:
            return group
    return None