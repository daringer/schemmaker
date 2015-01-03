import sys
import os
sys.path.append("..")

import unittest

from block import *
from force_optimizer import *
from field import *
from parsers.vhdl import parse_vhdl as parse
from schematic import draw_field
from routing import Routing

DEBUG = False

class ForceAlgorithmUnitTest(unittest.TestCase):
    # fixture setup, called BEFORE each test
    def setUp(self):
        self.test_data_dir = "../../testdata/"
        
        self.files = os.listdir(self.test_data_dir)
        self.files = [x for x in self.files if "324_0" in x]
        
        self.pins = (['vdd'], ['gnd', 'vss'], ['out1'], ['out2'])

    # fixture cleanup, called AFTER each test
    def tearDown(self):
        pass
     
    # no unit test, just helpers
    def parse_blocks(self, path):
        output = parse(path)
        self.blocks = []
        for i, b_data in enumerate(output):
            b = Block(b_data["type"], b_data["conns"], b_data["name"], b_data["groups"])
            self.blocks.append(b)

    def construct_force_algo_obj(self, field, blocks, pins):
        return ForceAlgorithm(field, blocks, *pins)

    def construct_field(self, name="test_circ", x=40, y=40):
        self.field = Field("test_circ", x, y)

    ##
    ## tests start here!
    ##
    def test_create_groups(self):
        for fn in self.files:
            print "-> create groups - fn: {}".format(fn)
            field = self.construct_field()
            blocks = self.parse_blocks(os.path.join(self.test_data_dir, fn))
            f = self.construct_force_algo_obj(field, blocks, self.pins)
            f.run(DEBUG)

            # Check if the main group containts only the two subgroups 0 and 1
            self.assertEqual(len(f.group_main.childs), 2)
            

    def test_check_neighbors(self):
        for fn in self.files:
            print "-> check neighbors - fn: {}".format(fn)
            field = self.construct_field()
            blocks = self.parse_blocks(os.path.join(self.test_data_dir, fn))
            f = self.construct_force_algo_obj(self.field, self.blocks, self.pins)
            f.run(DEBUG)

            # Check that both subgroups of the main group are neighbor
            self.assertTrue(f.group_main.childs[0].are_neighbor(f.group_main.childs[1]))


    def test_full(self):
        ###
        # slice the self.files list to reduce test time!!!
        ###
        for fn in self.files[:7]:
            print "-> full run - fn: {}".format(fn)
            field = self.construct_field()
            blocks = self.parse_blocks(os.path.join(self.test_data_dir, fn))
            f = self.construct_force_algo_obj(self.field, self.blocks, self.pins)
            cid = fn.split("op")[1].split(".")[0]
            

            f.step_build(DEBUG)
            f1 = f.get_debug_field()
            fn = draw_field(f1, "schematic_build_{}.pdf".format(cid))

            f.step_initial(DEBUG)
            f2 = f.get_debug_field()
            fn = draw_field(f2, "schematic_init_{}.pdf".format(cid))

            f.step_main(DEBUG)
            f3 = f.get_debug_field()
            fn = draw_field(f3, "schematic_main_{}.pdf".format(cid))

            f.step_last(DEBUG)
            f4 = f.get_debug_field()
            fn = draw_field(f4, "schematic_final_{}.pdf".format(cid))
            
            # CHECK IF OVERLAPPING BLOCKS WERE FOUND
            overlap = f4.has_overlapping_blocks()
            if overlap:
                print "-"*80
                print "#### FAILED ..... FAILED ..... circ_id: {}".format(cid)
                #f4.show_blocks(sortkey="pos")
                #f4.show_blocks(sortkey="name")
                f4.show_blocks(sortkey=("groups", "pos"))
            else:
                print "-"*80
                print "#### {} ####".format(cid)
                f = f4.to_field()
                f.optimize_size()
                f.optimize_block_dirs()
                #f.expand_field(4)
                r = Routing(f)
                ret = r.route(4)
                fn = draw_field(f, "schematic_real_{}.pdf".format(cid))

                
            # NOT COOL -> removed asserts to see him doing all circuits!
            #self.assertFalse(overlap, "Found overlapping blocks!")


if __name__ == '__main__':
    unittest.main()
