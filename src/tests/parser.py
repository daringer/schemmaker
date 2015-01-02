import sys
import os
sys.path.append("..")

import unittest

from block import *
from field import *
from parsers.vhdl import parse_vhdl as parse

class VHDLParserTestSuite(unittest.TestCase):

    def setUp(self):
        self.test_data_dir = "../../testdata/"
        self.files = os.listdir(self.test_data_dir)

    def test_parse_all_testdata(self):
        for fn in self.files:
            path = os.path.join(self.test_data_dir, fn)
            output = parse(path)

            self.assertTrue( len(output) > 0 )
            for blk in output:
                self.assertTrue( "conns" in blk )
                self.assertTrue( "groups" in blk )
                self.assertTrue( "type" in blk )
                self.assertTrue( "name" in blk )

                self.assertTrue( len(blk["conns"]) > 0 )
                self.assertTrue( len(blk["groups"]) > 0 )
                self.assertTrue( len(blk["type"]) > 0 and 
                                 blk["type"] is not None )
                self.assertTrue( len(blk["name"]) > 0 and
                                 blk["type"] != blk["name"] )

    def test_net_parse_fail(self):
        path = os.path.join(self.test_data_dir, "circuit_op9.vhdl")
        out = parse(path)
        for blk in out:
            for c in blk["conns"]:
                self.assertTrue(c.startswith("net") or c.startswith("in") or
                        c.startswith("out") or c in ["gnd", "vdd", "vref"] or
                        c.startswith("vbias"), blk["conns"])

if __name__ == '__main__':
    unittest.main()
