# -*- coding: utf-8 -*-

from random import choice, random, randint

from math import exp
from time import time
from itertools import permutations

from multiprocessing import Process, Queue, Pool


from base_optimizer import BaseRandomOptimizer

from print_block import bprint
from field import Field, FieldException
from block import Block

class GeneticAlgorithm(BaseRandomOptimizer):
    def __init__(self, field):
        BaseRandomOptimizer.__init__(self, field)

        self.max_pop = 14
        self.keep_best = 3
        self.pop = []

        self.pop.append( (field.cost(simple=True), field) )
        for i in xrange(self.max_pop-1):
            new_field = field.shuffle_copy()
            self.pop.append( (new_field.cost(simple=True), new_field) )
    
        self.proc_pool = Pool(processes=20)

            
    def mutation(self, field):
        try:
            while not self.get_random_operation()(field):
                pass
        except FieldException as e:
            pass
        return field
    
    def selection(self):
        self.pop.sort()
        
        #print [c for c, f in self.pop]
        # keep best 3
        new_pop = self.pop[0:self.keep_best]
        #print "best 3"
        #print [c for c, f in new_pop]
        
        # choose remaining with propability scaled with rank
        for i, (c, f) in enumerate(self.pop[self.keep_best:]):
            r = random()
            if r <= 1.0/(1+i):
                new_pop.append( (c, f) )
                
            if len(new_pop) == self.max_pop:
                break
        #print "after random choosing"
        #print [c for c, f in new_pop]
        # drop fields with same costs
        #costs = {}
        #for c, f in new_pop:
        #    costs[c] = costs.get(c, 0) + 1
        unique_new_pop = []
        for cost, field in new_pop:
            if cost not in [c for c, f in unique_new_pop]:
                unique_new_pop.append((cost,field))
        new_pop = unique_new_pop
        
        #print "after drop"
        #print [c for c, f in new_pop]
        # fill remaining pop-places with random ones
        for i in xrange(self.max_pop - len(new_pop)):
            new_field = new_pop[-1][1].shuffle_copy()
            new_pop.append( (new_field.cost(simple=True), new_field) )
        #print "after random append"
        #print [c for c, f in new_pop]
        self.pop = new_pop 
        
    def recombination(self):
        pass

    def step(self):
        # queues... :(
        #i_q, o_q = Queue.Queue(), Queue.Queue()
        #for cost, field in self.pop:
        #    new_field = self.mutation(field.copy())
        #    i_q.put(new_field)
        func = lambda (c, f): (f.cost(simple=True), f)
        new = [(c, self.mutation(f.copy())) for c,f in self.pop]
        
        #o = self.proc_pool.map(func, new)
        map(func, new)
        
        
        #self.proc_pool.close()
        #self.proc_pool.join()        
        
        self.pop += new
        self.selection()
        
    def run(self):
        start = time()
        for i in xrange(1000):
            self.step()
            
            if i % 100 == 0:
                end = time()
                print "avg time per iteration", (end - start) / (i+1)
                self.show(*self.pop[0])
            print "rank: ", [c for c, f in self.pop]
    
        # return best
        ret = self.pop[0][1]
        ret.optimize_size()
        ret.show_occ()
        self.show(*self.pop[0])
        ret.route()
        return ret

    def show(self, cost, field):
        cs = dict((k, v) for k, v in field.field_cost.costs.items() if v > 0 )
        print "[i] overview - [costs] {0:d} ".format(sum(cs.values()))
        
        print "[i] cost stats - {0}".format("  ".join("[{0}] {1:d}".format(k, v) \
                                                      for k, v in cs.items()[:5]))
        if len(cs) > 5:
            print "               - {0}".format("  ".join("[{0}] {1:d}".format(k, v) \
                                                          for k, v in cs.items()[5:]))
        if len(cs) > 10:
                    print "               - {0}".format("  ".join("[{0}] {1:d}".format(k, v) \
                                                                  for k, v in cs.items()[10:]))
        #t = field.copy()
        #t.optimize_size()
        #print f.show_occ()
            
