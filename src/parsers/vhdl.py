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
            
            if inside_generic_map and ")" in line and not "(" in line:
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
             
            if line.startswith('subnet'):
                left_res = pat.findall(line)
                right_res = pat_type.findall(line) 
                if right_res:
                    right_res = map(lambda s: s.strip(), right_res)
                name_res = pat_str_num.findall(left_res[-1])
                comp_counter.setdefault(name_res[0][0], 0)
                group_ids = [int(x[-1]) for x in left_res[:-1]]
                component_id = comp_counter[name_res[0][0]] = comp_counter[name_res[0][0]] + 1
                
                block = {'groups': group_ids,
                         'name': name_res[0][0] + str(component_id),
                         'type': right_res[0],
                         'conns': []}
                p = True
                
           
        return blocks


if __name__ == "__main__":
    fn = "../../testdata/circuit_op8.vhdl"
    for i in parse_vhdl(fn):
        print i
