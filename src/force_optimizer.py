'''
Created on 23.03.2014

@author: Christian Auth
'''

from field import Field, FieldException

from base_optimizer import BaseOptimizer

class ForceAlgorithm(BaseOptimizer):
    
    def __init__(self, field):
        BaseOptimizer.__init__(self, field)
        
        