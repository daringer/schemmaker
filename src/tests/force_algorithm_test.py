import sys
sys.path.append("..")

import unittest

from block import *
from force_optimizer import *
from field import *

class ForceAlgorithmUnitTest(unittest.TestCase):

    def setUp(self):
        self.raw_data = [
            {'conns': ['net2', 'inp1', 'net1'],       'type': 'pmos',       'name': 'm1',  'groups': [0, 0], 'pos': (4,4), 'rot': 2, 'mir': False},
            {'conns': ['outp', 'inp2', 'net1'],       'type': 'pmos',       'name': 'm2',  'groups': [0, 0], 'pos': (6,4), 'rot': 2, 'mir': True},
            {'conns': ['vdd', 'vbias1', 'net1'],      'type': 'pmos',       'name': 'm3',  'groups': [0, 0], 'pos': (4,0), 'rot': 0, 'mir': True},
            {'conns': ['net2', 'net2', 'gnd'],        'type': 'nmos',       'name': 'm4',  'groups': [0, 1], 'pos': (4,8), 'rot': 0, 'mir': False},
            {'conns': ['outp', 'net2', 'gnd'],        'type': 'nmos',       'name': 'm5',  'groups': [0, 1], 'pos': (6,8), 'rot': 0, 'mir': True},
            {'conns': ['vbias1', 'vbias1', 'vdd'],    'type': 'pmos',       'name': 'm6',  'groups': [1, 0], 'pos': (2,0), 'rot': 2, 'mir': False},
            {'conns': ['vbias2', 'vbias2', 'vbias1'], 'type': 'pmos',       'name': 'm7',  'groups': [1, 0], 'pos': (2,2), 'rot': 2, 'mir': False},
            {'conns': ['vdd', 'vbias3'],              'type': 'i_constant', 'name': 'i2',  'groups': [1, 0], 'pos': (0,0), 'rot': 0, 'mir': False},
            {'conns': ['vbias3', 'vbias3', 'vbias4'], 'type': 'nmos',       'name': 'm8',  'groups': [1, 0], 'pos': (0,6), 'rot': 0, 'mir': True},
            {'conns': ['vbias2', 'vbias3', 'net3'],   'type': 'nmos',       'name': 'm9',  'groups': [1, 0], 'pos': (2,6), 'rot': 0, 'mir': False},
            {'conns': ['vbias4', 'vbias4', 'gnd'],    'type': 'nmos',       'name': 'm10', 'groups': [1, 0], 'pos': (0,8), 'rot': 0, 'mir': False},
            {'conns': ['net3', 'vbias4', 'gnd'],      'type': 'nmos',       'name': 'm11', 'groups': [1, 0], 'pos': (2,8), 'rot': 0, 'mir': True},
        ]
        self.blocks = []
        for i, b_data in enumerate(self.raw_data):
            b = Block(b_data["type"], b_data["conns"], b_data["name"], b_data["groups"])

            b.rotate(b_data["rot"])
            b.mirror(set_to=b_data["mir"])

            self.blocks.append(b)
        self.field = Field("test_circ", 40, 40)

        self.assertEqual(self.field.nx, 40)
        self.assertEqual(self.field.ny, 40)
        self.force_algo = ForceAlgorithm(self.field, self.blocks, ['vdd'], ['gnd', 'vss'], ['outp'], [])

    def test_force_algo(self):
        print "test_create_groups"

        # Check if the main group containts only the two subgroups 0 and 1
        self.assertEqual(len(self.force_algo.group_main.childs), 2)

        print "test_check_neighbor"

        # Check that both subgroups of the main group are neighbor
        self.assertTrue(self.force_algo.group_main.childs[0].are_neighbor(self.force_algo.group_main.childs[1]))

if __name__ == '__main__':
    unittest.main()