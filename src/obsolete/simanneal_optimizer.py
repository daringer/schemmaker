# -*- coding: utf-8 -*-
from random import choice, random, randint
from math import exp
from time import time
from itertools import permutations

from multiprocessing import Process, Queue, Pool

from base_optimizer import BaseRandomOptimizer

from print_block import bprint
from field import Field
from block import Block

class SimulatedAnnealing(BaseRandomOptimizer):
    reduce_temp = 0.8
    step_reduce_temp = 3000
    
    def __init__(self, field):
        BaseRandomOptimizer.__init__(self, field)

        # initial temp defined by 1st cost val
        self.temp = field.cost() / 100.0
        
        # to keep the "last" field configuration
        self.last_cost = 0
        self.last_new_cost = 0
        self.last_field = None
        
        # represents the cost direction [reduce: -1, keep: 0, up: +1]
        self.last_decision = None   
        # counters for the different decisions beeing made
        self.last_positive_decisions = 0
        self.last_reduced_decisions = 0
        self.last_failed_operations = 0
        
        # holds all timing related stuff
        self.times = {}        

    #def __debug_cost_details(self, field1, field2):
    #    print "[D] Showing cost details (comparing old and new field) [last decision]: {0}".format(self.last_decision)
    #    a, b = field1.cost(), field2.cost()
    #    print a, b
    #    print a == b
    #    if field1.cost() != field2.cost():
    #        for k in field1.costs.keys():
    #            print "[{0:>20}] old: {1:10d} new: {2:10d}". \
    #                  format(k.upper(), field2.costs[k], field1.costs[k]),
    #            print "<---- {0:d}".format(field2.costs[k] - field1.costs[k], ) \
    #                  if abs(field2.costs[k] - field1.costs[k]) > 0.01 else ""
    #        print "[D] left field: {0:d} right field: {1:d}". \
    #              format(field1.cost(), field2.cost())
    #        
    #          
    #        print self.show(field1)
    #        print self.show(field2)
    #        
    #        for l, r in zip(field1.wires, field2.wires):
    #            print "l: {0:25} r: {1:25}".format(str(l), str(r))
    #        
    #    else:
    #        print "[D] The passed fields do absolutly match in costs!"
                              
    def step(self, iteration):
        step_start_time = time()
                  
        #self.last_field = self.field.copy()
        
        # to verify/debug the cost-function stability only react, if costs haven't decided to be changed,
        # but still there is a noticable change between the costs of the old and new field
        #if __debug__ and self.last_decision == 0 and (self.last_field.cost() != self.field.cost()):
        #    self.__debug_cost_details(self.last_field, self.field)
        #    assert self.last_field.cost() == self.field.cost()                      
            
        #old_cost = self.last_cost = self.last_field.cost()
        
        #if __debug__: # check cost-stability assert
        #    f1 = self.last_field
        #    f2 = self.last_field.copy()
        #    assert old_cost == f1.cost()
        #    assert old_cost == f2.cost()
        #    assert f1.cost() == f2.cost()
            
            #assert old_cost == self.last_field.cost()
            #assert old_cost == self.last_field.copy().cost()
            #assert self.last_field.cost() == self.last_field.copy().cost()
        
        old_cost = self.field.cost()
        new_field = self.field.copy()
        
        
        end_time = time()
        self.times["prepare"] += (end_time - step_start_time)
        
        # executing operation (get -> count -> exec -> save stats)
        start_time = time()
        func = self.get_random_operation()
        op_desc, op_result = func.__name__, True
        self.op_stats[op_desc][1] += 1
        if not func(new_field):
            op_result = False
            self.last_failed_operations += 1
            self.op_stats[op_desc][0] += 1                                
        end_time = time()
        self.times["operation"] += (end_time - start_time)
        
        # calc cost of new field
        start_time = time()
        #self.last_new_cost = new_cost = self.field.cost()
        new_field.clear_wires()
        self.last_new_cost = new_cost = new_field.cost()
        #print new_cost
        end_time = time()
        self.times["new_cost"] += (end_time - start_time)

        
        #if __debug__:
        #    # again stability debugging / also checking for negative costs -> evil!
        #    for f_new, f_old in zip(self.field.costs.items(), self.last_field.costs.items()):
        #        (new_desc, new_val), (old_desc, old_val) = f_new, f_old
        #        assert new_cost >= 0 and old_cost >= 0, new_desc + " : " + old_desc
        #    
        #    try:
        #        f1 = self.field
        #        f2 = self.field.copy()
        #        assert new_cost == f1.cost(), "Sucks I"
        #        assert new_cost == f2.cost(), "Sucks II"
        #        assert f1.cost() == f2.cost(), "Sucks III"
        #    except AssertionError as e:
        #        print e
        #        self.__debug_cost_details(self.field, self.field.copy())
        #        print "##################"                
        #        for p1, p2 in zip(f1.all_paths, f2.all_paths):
        #            print p1
        #            print p2
        #            print "----"
        #        import sys
        #        sys.exit(1)

        # decide on the new calculated costs
        start_time = time()

        # print all necassary information about each step in __debug__ mode
        #if __debug__:
        #    print "[COST] new: {0:8d} old: {1:8d} [OP] {3}{2:15}". \
        #          format(new_cost, old_cost, op_desc, "+" if op_result else "-"),
        #    out = "{0:30s}"
        #    msg = None
        
        if new_cost == old_cost:
            #if __debug__:
            #    msg = "|KEEP| COST UNCHANGED!" + (" "*18)
            self.last_decision = 0
            #self.field = self.last_field #.copy()
            
        elif new_cost < old_cost:
            #if __debug__:
            #    msg = "|DOWN| COST DOWN! - YES!!!" + (" "*14)
                
            self.last_reduced_decisions += 1
            self.last_decision = -1            
            self.field = new_field
        else:
            p_continue = exp(- (new_cost - old_cost) / self.temp) 
            randomno = random()
            
            #if __debug__:
            #    chance = "p(UP) = {0:.3f} X: {1:.3f}".format(p_continue, randomno)
            
            if randomno <= p_continue:                
                self.last_positive_decisions += 1
                self.last_decision = 1
                #if __debug__:
                #    msg = "|UP|   COST UP!   " + chance
                self.field = new_field
            else:
                #if __debug__:
                #    msg = "|KEEP| COST KEEP! " + chance
                self.last_decision = 0
        #       self.field = self.last_field #.copy()
            
        step_end_time = time()
        
        #if __debug__:
        #    assert old_cost == self.last_field.cost() == self.last_field.copy().cost()
        #    if self.last_decision == -1:
        #        assert self.field.cost() <= self.last_cost <= self.last_field.cost()
        #    elif self.last_decision == 1:
        #        assert self.field.cost() >= self.last_cost >= self.last_field.cost()
        #    elif self.last_decision == 0:
        #        assert old_cost == self.field.cost() == self.last_field.cost()
        #        
        #    print out.format(msg) ,             
        #    print "[ANNEALING] temp: {0:7.4f} iter: {1:5d}".format(self.temp, iteration)
                        
        self.times["decision"] += (step_end_time - start_time)
        self.times["step"] += (step_end_time - step_start_time)
        
    def run(self):
        start_time = time()
        
        last_costs_maxlen = 12
        last_costs = range(last_costs_maxlen)
        
        i = 0
        start = True
        while len(set(last_costs)) > 1:
            i += 1
            self.last_positive_decisions = 0
            self.last_failed_operations = 0
            self.last_reduced_decisions = 0
            
            for desc in ["operation", "new_cost", "prepare", "decision", "step"]:
                self.times[desc] = 0
            
            for opname in self.op_stats:
                self.op_stats[opname] = [0, 0]
            
            if start:
                self.step(0)
                self.show()
                start = False
            
            for i in xrange(self.step_reduce_temp):
                self.step(i)
                
            self.temp *= self.reduce_temp

            last_costs += [self.last_cost]
            if len(last_costs) > last_costs_maxlen:
                last_costs.pop(0)
            
            self.handle_visualization(self.field)
            
        print "[i] The last {0} temperature reductions have not changed the costs.".format(last_costs_maxlen)
        print "[+] Supposing we have reached the end - exiting..." 
               
        end_time = time()
        print "[i] The full optimization process took: {0:.2f} secs".format(end_time - start_time)
        print "[i] Showing final Schematic now!"
        
        return self.field
    
    
    def show(self, field=None):
        if field is None:
            field = self.field
        print "##############################################################################"
        
        cs = dict((k, v) for k, v in field.costs.items() if v > 0)
        print "[i] overview - [costs] {0:d}  [temp] {1:.2f} [time for temp-step] {2:.2f}secs [per iteration]: {3:.3f}ms". \
              format(sum(cs.values()), self.temp, \
                     sum(self.times.values()), 1000 * sum(self.times.values()) / self.step_reduce_temp)
        
        print "[i] cost stats - {0}".format("  ".join("[{0}] {1:d}".format(k, v) \
                                                      for k, v in cs.items()[:5]))
        if len(cs) > 5:
            print "               - {0}".format("  ".join("[{0}] {1:d}".format(k, v) \
                                                          for k, v in cs.items()[5:]))
        if len(cs) > 10:
                    print "               - {0}".format("  ".join("[{0}] {1:d}".format(k, v) \
                                                                  for k, v in cs.items()[10:]))
                                                        
        print "[i] average times - {0}".format("  ".join("[{0}] {1:.2f}ms".format(k, (v / self.step_reduce_temp) * 1000) \
                                            for k, v in self.times.items()))
        
        print "[i] operations stats - {0} ".format("  ".join("[{0}] {1}/{2}".format(k, v[0], v[1]) \
                                               for k, v in self.op_stats.items()[:4]) )
        print "    (fail/all)       - {0} ".format("  ".join("[{0}] {1}/{2}".format(k, v[0], v[1]) \
                                                       for k, v in self.op_stats.items()[4:]) )        
        div = self.step_reduce_temp / 100.0
        print "[i] positive decisions: {0} ({3:.1f}%) reducing costs: {5} ({6:.1f}%) failed ops: {1} ({4:.1f}%) during {2} steps". \
              format(self.last_positive_decisions, self.last_failed_operations, self.step_reduce_temp,
                     self.last_positive_decisions / div, self.last_failed_operations / div,
                     self.last_reduced_decisions, self.last_reduced_decisions / div)
        #f.optimize_size()
        field.show_occ()
        
        #for p1, v in field.all_paths.items():
        #    print "----------", p1, v[0][0]
        #    for key, (path, cost) in v[1].items():
        #        print "path: ", path
        #        print "cost: ", cost
        #        #print cost
        
        print "##############################################################################"


