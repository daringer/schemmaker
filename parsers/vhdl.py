# -*- coding: utf-8 -*-

import re

def parse_vhdl(data_path):
    block, blocks = (), []
    p = False
    pat = re.compile("([a-z]+[0-9]+)+")
    pat_type = re.compile("entity work\.([^\(]+)")
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
            if line.startswith('subnet'):
                left_res = pat.findall(line)
                right_res = pat_type.findall(line)
                name_res = pat_str_num.findall(left_res[-1])
                comp_counter.setdefault(name_res[0][0], 0)
                group_ids = [int(x[-1]) for x in left_res[:-1]]
                component_id = comp_counter[name_res[0][0]] = comp_counter[name_res[0][0]] + 1
                
                block = {'groups': group_ids,
                         'name': name_res[0][0] + str(component_id),
                         'type': right_res[0].replace("basic_", ""),
                         'conns': []}
                p = True
                
        final_blocks = []
        for blk in blocks:
            if blk["type"] == "i_constant":
                if any(net.startswith("vbias") for net in blk["conns"]):
                    break
                
                c_type = "vdd" if "vdd" in blk["conns"] else "gnd"
                t_type = "pmos" if c_type == "vdd" else "nmos"
                vb_type = "vbias1" if t_type == "pmos" else "vbias4"
                other_net = blk["conns"][1] if blk["conns"][0] in ["vdd", "gnd"] else blk["conns"][0]
                
                blk["type"] = t_type
                blk["conns"] = [c_type, vb_type, other_net]
                blk["name"] = "m(0)".format(len(blocks)+1)
            
            final_blocks.append(blk)
        
        return blocks
