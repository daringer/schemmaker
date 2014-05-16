# -*- coding: utf-8 -*-

"""
 ____________ ______ ______
|    n1      |      |      |
|            |      |      |
|Nmos      n1|______|______|  
|            |      |      |
|            |      |      |
|____n3______|______|______|

"""
def fprint():
    return ['      |', '______|']

def bprint(block, mir=False, rot=0):
    # block name
    name = "[{}]".format(block.name) #block.type[:2] + "(" + str(rot) + ("m" if mir else "") + ")"
    
    pins = block.pins.values()
    
    # 4 positions to write to (just take the one known by the block/pin)
    posi = {
        (1, 0): None, (0, 1): None, (1, 2): None, (2, 1): None
    }
    # get pin/net name by coord
    for p in pins:
        assert p.pos in posi
        posi[p.pos] = p.net.replace("vbias", "vb").\
                            replace("net", "n"). \
                            replace("inp", "in"). \
                            replace("outp", "out")
    
    # fill remaining slot with name
    placed = False
    for pos, who in posi.items():
        if who is None:
            if placed:
                posi[pos] = ""
            else:
                posi[pos] = name
                placed = True
        
    
            
    # string-formatting to get a box for each element ...
    # cols: 17 rows: 6
    spacer = "{0:>{1}} {0:>{1}}|".format(" ", 6)
    top = "{0:^{1}}|".format(posi[(1, 0)], 13)
    info = "{} {}{}".format(block.type[0].upper(), rot, (mir and "m") or "")
    info_spacer = "{0:^{1}}|".format(info, 13)
    mid = "{0}{1:>{2}}|".format(posi[(0, 1)], posi[(2, 1)], 13 - len(posi[(0, 1)]))
    bot = "{0:^{1}}|".format(posi[(1, 2)], 13).replace(" ", "_")

    block = [top, spacer, mid, info_spacer, spacer, bot]
    return block