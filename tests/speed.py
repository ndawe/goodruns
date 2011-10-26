#!/usr/bin/env python

import ROOT
ROOT.gSystem.Load('libGoodRunsLists.so')
from ROOT import Root
import random
from goodruns import GRL
from numpy import random

reader = Root.TGoodRunsListReader('grl.xml')
reader.Interpret()
goodrunslist = reader.GetMergedGRLCollection()

grl = GRL('grl.xml')

size = 1000000
runs = [int(i) for i in random.randint(178000, 190500, size=size)]
lbs = [int(i) for i in random.randint(0, 1000, size=size)]

def GoodRunsLists():
    for i in xrange(size):
        goodrunslist.HasRunLumiBlock(runs[i], lbs[i])

def goodruns():
    for i in xrange(size):
        (runs[i], lbs[i]) in grl

import time
t1 = time.time()
GoodRunsLists()
print time.time() - t1
t1 = time.time()
goodruns()
print time.time() - t1
