import sys
sys.path.append("..")

import unittest

from field import *
from block import Block

class BlockUnitTest(unittest.TestCase):
    def setUp(self):
        self.blk = None
        self.pin_posi = [(1, 0), (0, 1), (1, 2), (2, 1)]
        self.pin_dirs = [  0   ,   1   ,   2   ,   3   ]

    def test_construct_block(self):
        self.blk = Block("nmos", ["n1", "n2", "n3"], "N1", (0, 1), (2, 2), None)


    def test_rotate_ccw(self):
        self.test_construct_block()

        get_pins = self.blk.get_pins_from_direction
        get_dir = self.blk.get_pin_direction

        for d in self.pin_dirs:
            pins = get_pins(self.pin_dirs[d])
            self.assertEqual(len(pins), 1)
            pin = pins[0]
            self.assertEqual(get_dir(pin), self.pin_dirs[d])
            self.assertEqual(pin.pos, self.pin_posi[d])
            self.blk.rotate(1)

        #self.assertEqual(len(pins), 1)
        #self.assertEqual(get_dir(pin), 0)







if __name__ == '__main__':
    unittest.main()
