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
    name = block.type[:2] + "(" + str(rot) + ("m" if mir else "") + ")"
    name = name + ' ' if len(name)%2==1 else name
    ln = len(name)
    c1 = block.conns[0] if len(block.conns) > 0 else ''
    c2 = block.conns[1] if len(block.conns) > 2 else ''
    c3 = block.conns[2] if len(block.conns) > 2 else block.conns[2]

    if c1.startswith("vbias"): c1 = "vb" + c1[-1:]
    if c2.startswith("vbias"): c2 = "vb" + c2[-1:]
    if c3.startswith("vbias"): c3 = "vb" + c3[-1:]
    
    if c1.startswith("net"): c1 = "ne" + c1[-2:]
    if c2.startswith("net"): c2 = "ne" + c2[-2:]
    if c3.startswith("net"): c3 = "ne" + c3[-2:]
    
    c1 = c1 + ' ' if len(c1)%2==1 else c1
    c2 = c2 + ' ' if len(c2)%2==1 else c2
    c3 = c3 + ' ' if len(c3)%2==1 else c3

    l1, l2, l3 = len(c1), len(c2), len(c3)
    desc = name 
    # no rotation
    if rot==0:
        s1 = int((13 - l1)/2.)
        s2 = int(13 - l2) - ln
        s3 = int((13 - l3)/2.)
        u = ' ' + ' ' * s1 + c1 + ' ' * s1 + '|'
        m = '' + desc + ' ' * s2 + c2 + '|' if not mir else \
            '' + c2 + ' ' * s2 + desc + '|'
        d = '_' + '_' * s3 + c3 + '_' * s3 + '|'
    # rotation: -90°
    elif rot==1:
        s1 = int((13 - l3)/2.)
        s2 = int(13 - l1 - l2)
        s3 = int((13 - ln)/2.)
        u = ' ' + ' ' * s3 + desc + ' ' * s3 + '|'
        m = '' + c1 + ' ' * s2 + c2 + '|' if not mir else \
            '' + c2 + ' ' * s2 + c1 + '|'
        d = '_' + '_' * s1 + c3  + '_' * s1 + '|'
    elif rot==2:
        s1 = int((13 - l2)/2.)
        s2 = int(13 - l3) - ln
        s3 = int((13 - l1)/2.)
        u = ' ' + ' ' * s1 + c3 + ' ' * s1 + '|'
        m = '' + c2 + ' ' * s2 + desc + '|' if not mir else \
            '' + desc + ' ' * s2 + c2 + '|'
        d = '_' + '_' * s3 + c1 + '_' * s3 + '|'
    elif rot==3:
        s1 = int((13 -ln)/2.)  
        s2 = int(13 - l1 - l3)
        s3 = int((13 - l2)/2.)
        u = ' ' + ' ' * s1 + desc + ' ' * s1 + '|'
        m = '' + c3 + ' ' * s2 + c1 + '|' if not mir else \
            '' + c1 + ' ' * s2 + c3 + '|'
        d = '_' + '_' * s3 + c2 + '_' * s3 + '|'
    else:
        return None

    block = [ u, '' + ' ' * 13 + '|', 
              m, '' + ' ' * 13 + '|',
              '' + ' ' * 13 + '|', d ]

    return block
