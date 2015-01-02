import sys
import os
sys.path.append("..")

import unittest

from block import *
from force_optimizer import *
from field import *
from parsers.vhdl import parse_vhdl as parse
from schematic import draw_field

class ForceAlgorithmUnitTest(unittest.TestCase):

    def setUp(self):
        self.test_data_dir = "../../testdata/"
        #self.fn = "circuit_op8.vhdl"
        #self.fn = "circuit_bi1_0op337_1.vhdl"        
        #self.fn = "circuit_bi1_0op324_0.vhdl"
        self.fn = "circuit_bi1_0op324_2.vhdl"
        
        self.files = os.listdir(self.test_data_dir)
        path = os.path.join(self.test_data_dir, self.fn)
        
        output = parse(path)

        self.blocks = []
        for i, b_data in enumerate(output):
            b = Block(b_data["type"], b_data["conns"], b_data["name"], b_data["groups"])
            self.blocks.append(b)

        self.field = Field("test_circ", 40, 40)
        self.pins = (['vdd'], ['gnd', 'vss'], ['out'], ['out2'])
        
        self.raw_data = [
            {'conns': ['net2', 'in1', 'net1'],       'type': 'pmos',       'name': 'm1',  'groups': [0, 0], 'pos': (4,4), 'rot': 2, 'mir': False},
            {'conns': ['out1', 'in2', 'net1'],       'type': 'pmos',       'name': 'm2',  'groups': [0, 0], 'pos': (6,4), 'rot': 2, 'mir': True},
            {'conns': ['vdd', 'vbias1', 'net1'],      'type': 'pmos',       'name': 'm3',  'groups': [0, 0], 'pos': (4,0), 'rot': 0, 'mir': True},
            {'conns': ['net2', 'net2', 'gnd'],        'type': 'nmos',       'name': 'm4',  'groups': [0, 1], 'pos': (4,8), 'rot': 0, 'mir': False},
            {'conns': ['out1', 'net2', 'gnd'],        'type': 'nmos',       'name': 'm5',  'groups': [0, 1], 'pos': (6,8), 'rot': 0, 'mir': True},

            {'conns': ['vbias1', 'vbias1', 'vdd'],    'type': 'pmos',       'name': 'm6',  'groups': [1, 0], 'pos': (2,0), 'rot': 2, 'mir': False},
            {'conns': ['vbias2', 'vbias2', 'vbias1'], 'type': 'pmos',       'name': 'm7',  'groups': [1, 0], 'pos': (2,2), 'rot': 2, 'mir': False},
            {'conns': ['vdd', 'vbias3'],              'type': 'idc',        'name': 'i2',  'groups': [1, 0], 'pos': (0,0), 'rot': 0, 'mir': False},
            {'conns': ['vbias3', 'vbias3', 'vbias4'], 'type': 'nmos',       'name': 'm8',  'groups': [1, 0], 'pos': (0,6), 'rot': 0, 'mir': True},
            {'conns': ['vbias2', 'vbias3', 'net3'],   'type': 'nmos',       'name': 'm9',  'groups': [1, 0], 'pos': (2,6), 'rot': 0, 'mir': False},
            {'conns': ['vbias4', 'vbias4', 'gnd'],    'type': 'nmos',       'name': 'm10', 'groups': [1, 0], 'pos': (0,8), 'rot': 0, 'mir': False},
            {'conns': ['net3', 'vbias4', 'gnd'],      'type': 'nmos',       'name': 'm11', 'groups': [1, 0], 'pos': (2,8), 'rot': 0, 'mir': True},
        ]

        self.raw_data_easy = [
            {'conns': ['gnd', 'in1', 'net1'],       'type': 'pmos',       'name': 'm1',  'groups': [0], 'pos': (4,4), 'rot': 2, 'mir': False},
            {'conns': ['out1', 'in2', 'net1'],       'type': 'pmos',       'name': 'm2',  'groups': [0], 'pos': (6,4), 'rot': 2, 'mir': True},
            {'conns': ['vdd', 'in2', 'net1'],      'type': 'pmos',       'name': 'm3',  'groups': [0], 'pos': (4,0), 'rot': 0, 'mir': True},
        ]


    def construct_force_algo_obj(self, field, blocks, pins):
        return ForceAlgorithm(field, blocks, *pins)

    #def xTODO_test_simple(self):
    #    
    #    self.blocks = []
    #    self.field = Field("test_circ", 40, 40)
    
    #    for i, b_data in enumerate(self.raw_data):
    #        b = Block(b_data["type"], b_data["conns"], b_data["name"], b_data["groups"])
    #        b.rotate(b_data["rot"])
    #        b.mirror(set_to=b_data["mir"])
    #        self.blocks.append(b)


    #    self.assertEqual(self.field.nx, 40)
    #    self.assertEqual(self.field.ny, 40)
    #    self.force_algo = ForceAlgorithm(self.field, self.blocks, ['vdd'], ['gnd', 'vss'], ['out'], [])

    #    for block in self.force_algo.blocks:
    #        self.field.add_block(block, block.pos)

    def test_create_groups(self):
        f = self.construct_force_algo_obj(self.field, self.blocks, self.pins)
        f.run()

        # Check if the main group containts only the two subgroups 0 and 1
        self.assertEqual(len(f.group_main.childs), 2)

    def test_check_neighbors(self):
        f = self.construct_force_algo_obj(self.field, self.blocks, self.pins)
        f.run()

        # Check that both subgroups of the main group are neighbor
        self.assertTrue(f.group_main.childs[0].are_neighbor(f.group_main.childs[1]))


    def test_import(self):
        f = self.construct_force_algo_obj(self.field, self.blocks, self.pins)

        f.step_build()
        f1 = f.get_debug_field()
        fn = draw_field(f1, "schematic_build.pdf")

        f.step_initial()
        f2 = f.get_debug_field()
        fn = draw_field(f2, "schematic_init.pdf")

        f.step_main()
        f3 = f.get_debug_field()
        fn = draw_field(f3, "schematic_main.pdf")

        f.step_last()
        f4 = f.get_debug_field()
        fn = draw_field(f4, "schematic_final.pdf")
        
        f4.show_blocks(sortkey="name")
        #f.debug_times()


if __name__ == '__main__':
    unittest.main()
