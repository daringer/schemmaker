import sys
sys.path.append("..")

import unittest

from field import *
from block import Block

class FieldUnitTest(unittest.TestCase):
    def setUp(self):
        self.blk_vdd = Block("pmos", ["vdd", "n1", "n2"], "P1", (0,0))
        self.blk_gnd = Block("nmos", ["gnd", "n1", "n2"], "N1", (0,0))
        self.blk1 = Block("nmos", ["n3", "n4", "n2"], "N1", (0,1))
        self.blk2 = Block("nmos", ["n5", "n4", "n4"], "N1", (0,1))
        self.field = Field("t", 10, 10)

    def test_construct(self):
        self.assertTrue(isinstance(self.field, Field))

    def test_add_block(self):
        f, b = self.field, self.blk1
        f.add_block(b, (0,0))
        
        self.assertTrue(b in f)
        self.assertTrue((0, 0) in f)
        self.assertTrue((0, 1) in f)
        self.assertTrue((1, 0) in f)
        self.assertTrue((1, 1) in f)
        
        with self.assertRaises(FieldSpaceOccupied):
            f.add_block(self.blk2, (1, 1))
    
    def test_remove_block(self):
        f, b = self.field, self.blk1
        f.add_block(b, (0,0))
                
        self.assertTrue(b in f)
        
        f.remove_block(b)
        
        self.assertFalse(b in f)
        self.assertFalse((0, 0) in f)
        self.assertFalse((0, 1) in f)
        self.assertFalse((1, 0) in f)
        self.assertFalse((1, 1) in f)
        
        
    def test_clear(self):
        f, b1, b2 = self.field, self.blk1, self.blk2
        f.add_block(b1, (0, 0))
        f.add_block(b2, (2, 2))
        
        self.assertEqual(len(f), 2)
        
        f.clear()
        
        self.assertEqual(len(f), 0)
        
    def test_copy(self):
        f, b1, b2 = self.field, self.blk1, self.blk2
        f.add_block(b1, (0, 0))
        f.add_block(b2, (2, 2))
        
        f2 = f.copy()
        
        self.assertEqual(len(f2), len(f))
        
        

if __name__ == '__main__':
    unittest.main()