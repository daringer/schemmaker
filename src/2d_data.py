# -*- coding: utf-8 -*-

class XYPoint:
    def __init__(self, pos_or_x=None, y=None):
        self.__xy = (0, 0)
        self.x = property(lambda s: s.__xy[0], self.__setterX)
        self.y = property(lambda s: s.__xy[1], self.__setterY)
        self.pos = property(lambda s: s.__xy, self.__setterXY)
        
        if isinstance(pos_or_x, (tuple, list)) and len(pos_or_x) == 2:
            self.__xy = self.__valid_pos(pos_or_x)
        elif y is not None:
            self.__xy = self.__valid_pos((pos_or_x, y))
        
    def copy(self):
        return XYPoint(self.__xy)
 
    def __setterX(self, val):
        assert val is not None
        self.__xy = self.__valid_pos((val, self.__xy[1]))
        
    def __setterY(self, val):
        assert val is not None
        self.__xy = self.__valid_pos((self.__xy[0], val))
        
    def __setterXY(self, val):
        assert val is not None
        self.__xy = self.__valid_pos(val)
            
    def __valid_pos(self, pos):
        """Either enforce int() or float()"""
        #x = float(pos[0])
        #y = float(pos[1])
        x = int(pos[0])
        y = int(pos[1])
        return (x, y)


class Pos(XYPoint):
    pass
    
class Size(XYPoint):
    pass

class Area(XYPoint):
    def __init__(self, from_pos, to_pos):
        pass
