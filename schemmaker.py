#!/usr/bin/python 
# -*- coding: utf-8 -*-

import sys
from random import choice
from os import path

from schematic import Schematic
from parsers import parse_vhdl as parse
        
entryfile = "schemmaker.py"

if len(sys.argv) < 2:
    print "[i] Usage: {} <vhdl_path> [output_filename]".format(entryfile)
    sys.exit(1)

s = Schematic()

# input filename, derive circuit name from it
fn = sys.argv[1]
name = path.basename(fn).replace("circuit_", "").replace(".vhdl", "")

# set output filename
output_fn = "schematic.pdf"
if len(sys.argv) > 2:
    output_fn = sys.argv[2]
if not output_fn.endswith(".pdf"):
    output_fn += ".pdf"

# parse file for raw_circ data:
# [{"conns": ["n1", "n2", "inp], "type": "nmos", "groups": (0, 4), "name": "TN1"}, ...]
raw_circ = parse(fn)

# execute generation
if s.generate_schematic(circuit_raw=raw_circ, circuit_id=name):
    s.write_to_file(output_fn)
else:
    print "[E] failed drawing schematic from file: {}".format(fn)


# TODOOOOS: 
#  - names, sizing next to device
#  - soldering dots (recheck placement)
#  - conditional edges (ask FieldNode instead of checking for existance
#  - try all possible routing starts (find_path)
#  - use groups provided inside circuit_raw
#    - e.g., colors on transistors


