import sys, os
sys.path.append("..")

import unittest

from field import Field
from block import Block, Pin
from base_optimizer import FakeOptimizer
from routing import Routing

from force_optimizer import ForceAlgorithm
from schematic import Schematic, draw_field


class Regression(unittest.TestCase):
    """High-lvl tests, involving as much as possible"""
    def setUp(self):
        self.raw_data = [
            {'conns': ['net2', 'inp1', 'net1'], 'type': 'pmos', 'name': 'm1',  
                'groups': [0, 0], 'pos': (4,4), 'rot': 2, 'mir': False},
            {'conns': ['outp', 'inp2', 'net1'], 'type': 'pmos', 'name': 'm2',
                'groups': [0, 0], 'pos': (6,4), 'rot': 2, 'mir': True},
            {'conns': ['vdd', 'vbias1', 'net1'], 'type': 'pmos', 'name': 'm3',
                'groups': [0, 0], 'pos': (4,0), 'rot': 0, 'mir': True},
            {'conns': ['net2', 'net2', 'gnd'], 'type': 'nmos', 'name': 'm4',
                'groups': [0, 1], 'pos': (4,8), 'rot': 0, 'mir': False},
            {'conns': ['outp', 'net2', 'gnd'], 'type': 'nmos', 'name': 'm5',
                'groups': [0, 1], 'pos': (6,8), 'rot': 0, 'mir': True},
            {'conns': ['vbias1', 'vbias1', 'vdd'], 'type': 'pmos', 'name': 'm6',
                'groups': [1, 0], 'pos': (2,0), 'rot': 2, 'mir': False},
            {'conns': ['vbias2', 'vbias2', 'vbias1'], 'type': 'pmos', 'name': 'm7',
                'groups': [1, 0], 'pos': (2,2), 'rot': 2, 'mir': False},
            {'conns': ['vdd', 'vbias3'], 'type': 'idc', 'name': 'i2',
                'groups': [1, 0], 'pos': (0,0), 'rot': 0, 'mir': False},
            {'conns': ['vbias3', 'vbias3', 'vbias4'], 'type': 'nmos', 'name': 'm8', 
                'groups': [1, 0], 'pos': (0,6), 'rot': 0, 'mir': False},
            {'conns': ['vbias2', 'vbias3', 'net3'], 'type': 'nmos', 'name': 'm9',
                'groups': [1, 0], 'pos': (2,6), 'rot': 0, 'mir': True},
            {'conns': ['vbias4', 'vbias4', 'gnd'], 'type': 'nmos', 'name': 'm10', 
                'groups': [1, 0], 'pos': (0,8), 'rot': 0, 'mir': False},
            {'conns': ['net3', 'vbias4', 'gnd'], 'type': 'nmos', 'name': 'm11', 
                'groups': [1, 0], 'pos': (2,8), 'rot': 0, 'mir': True},
        ]

        self.field = None
        self.maxDiff = None


        self.pdf_path = "circuit_draw_test_file.pdf"
        self.tempfiles = []

        #print "cleaning up old test-pdfs:"
        #os.system("rm " + self.pdf_path[:-4] + "*")


    def tearDown(self):
        #for fn in self.tempfiles:
        #    if os.path.exists(fn):
        #        os.unlink(fn)
        pass


    def get_tempfile(self, num=None):
        suffix = num or self.tempfiles
        fn_parts = self.pdf_path.split(".")

        self.assertTrue(len(fn_parts) == 2)

        out = "{}_{}.{}".format(fn_parts[0], suffix, fn_parts[1])
        self.tempfiles.append(out)

        return out


    def test_init_field(self):
        self.field = Field("test_circ", 40, 40)

        self.assertEqual(self.field.nx, 40)
        self.assertEqual(self.field.ny, 40)

    def test_add_blocks(self):
        self.test_init_field()

        for i, b_data in enumerate(self.raw_data):
            b = Block(b_data["type"], b_data["conns"], b_data["name"], b_data["groups"])

            b.rotate(b_data["rot"])
            b.mirror(set_to=b_data["mir"])

            self.field.add_block(b, b_data["pos"])

        self.assertEqual(len(self.field), len(self.raw_data))


    def test_block_move(self):
        self.test_add_blocks()

        blk = filter(lambda a: a.name == "m3", self.field.get_blocks())

        self.assertEqual(len(blk), 1)
        blk = blk[0]
        pos = (6, 0)

        self.assertTrue(self.field.move(blk, pos))
        self.assertEqual(self.field.get_block_pos(blk), pos)

    def test_block_swap(self):
        self.test_add_blocks()

        name2blk = dict((b.name, b) for b in self.field.get_blocks())

        self.assertTrue(
            self.field.swap(name2blk["m1"], name2blk["m2"])
        )

    def test_field_copy_roundtrip(self):
        self.test_add_blocks()
        f1 = self.field.copy()

        self.test_add_blocks()
        f2 = self.field.copy()

        list_props = lambda blks, prop: tuple(sorted(getattr(blk, prop) for blk in blks))

        bl1 = f1.get_blocks()
        bl2 = f2.get_blocks()
        for pname in ["name", "groups", "type"]:
            self.assertSequenceEqual(list_props(bl1, pname), list_props(bl2, pname))

        self.assertEqual(f1.ny, f2.ny)
        self.assertEqual(f1.nx, f2.nx)

        self.assertEqual(len(f1.block2xy), len(f2.block2xy))
        self.assertEqual(len(f1.block2yx), len(f2.block2yx))
        self.assertEqual(len(f1.xy2block), len(f2.xy2block))
        self.assertEqual(len(f1.yx2block), len(f2.yx2block))

    def test_field_finalization(self):
        self.test_add_blocks()
        self.field.optimize_size()

        # no error is good at this point
        self.assertTrue(True)

    def test_expansion(self):
        self.test_field_finalization()

        nx, ny = self.field.nx, self.field.ny 
        self.field.expand_field(4)

        fn = draw_field(self.field, self.get_tempfile(4))
        
        self.assertTrue(nx < self.field.nx)
        self.assertTrue(ny < self.field.ny)

    def test_routing(self):
        self.test_field_finalization()

        r = Routing(self.field)
        ret = r.route(4)

        self.assertGreaterEqual(ret[0], 1)


    def test_draw_pdf(self):
        self.test_routing()

        fn = draw_field(self.field, self.get_tempfile(1))

        self.assertTrue( os.path.isfile(fn) )
        self.assertTrue( os.path.exists(fn) )
        self.assertTrue( len(file(fn).read()) > 10 )

    def test_draw_without_routing(self):
        self.test_field_finalization()

        fn = draw_field(self.field, self.get_tempfile(2))

        self.assertTrue( os.path.isfile(fn) )
        self.assertTrue( os.path.exists(fn) )
        self.assertTrue( len(file(fn).read()) > 10 )

    def test_draw_with_grid(self):
        self.test_field_finalization()

        fn = draw_field(self.field, self.get_tempfile(3), grid=(10, 10, 0, 0, 1))

        self.assertTrue( os.path.isfile(fn) )
        self.assertTrue( os.path.exists(fn) )
        self.assertTrue( len(file(fn).read()) > 10 )


if __name__ == "__main__":
    unittest.main()
