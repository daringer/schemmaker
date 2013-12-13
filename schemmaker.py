#!/usr/bin/python 
# -*- coding: utf-8 -*-

import sys
from random import choice
from os import path

from schematic import Schematic
from parsers import parse_vhdl as parse
        
entryfile = "schemmaker.py"

if len(sys.argv) < 2:
    print "[i] Usage: {} <vhdl_path>".format(entryfile)
    sys.exit(1)

s = Schematic()
fn = sys.argv[1]
name = path.basename(fn).replace("circuit_", "").replace(".vhdl", "")

# :: Generate schematic for one specific vhdl netlist
raw_circ = parse(fn)

if s.generate_schematic(circuit_raw=raw_circ, circuit_id=name):
    s.write_to_file("schematic.pdf")
else:
    print "[E] failed drawing schematic from file: {}".format(fn)


# TODOOOOS: 
#  - colors on transistors
#  - names on transistors
#  - soldering dots (recheck placement)
#  - conditional edges (ask FieldNode instead of checking for existance
#  - try all possible routing starts (find_path)

