# -*- coding: utf-8 -*-

import sys, os
import re

def parse_vhdl(data_path):

    if not os.path.exists(data_path):
        print "FAIL: {} <- not found!".format(data_path)
        self.assertTrue(False)

    block, blocks = (), []
    p = False
    pat = re.compile("([a-z]+[0-9]+)+")
    pat_type = re.compile("entity\w*([^\(]+)")
    pat_str_num = re.compile("([a-zA-Z]+)([0-9]+)")
 
    inside_generic_map = False

    with open(data_path) as fp:
        comp_counter = {}
        for line in iter(fp.readline, ''):
            if "generic" in line:
                inside_generic_map = True
            
            if inside_generic_map and ")" in line:
                inside_generic_map = False
                continue
            
            if inside_generic_map:
                continue

            if p and line.startswith(');'):
                blocks.append(block)
                p = False            

            if p and not line.startswith('port') and line.strip() != "" and line.strip() != ")":
                con = re.split('=> ', line)[1][:-1]
                if con[-1] == ',':
                    con = con[:-1]
                block["conns"].append(con)
            
        return blocks


if __name__ == "__main__":
    fn = "../../testdata/circuit_op8.vhdl"
    for i in parse_vhdl(fn):
        print i
