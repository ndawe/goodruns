#!/usr/bin/env python

import ROOT
ROOT.gSystem.Load('libGoodRunsLists.so')
from ROOT import Root
import random
from goodruns import GRL
from numpy import random
import time
import sys


reader = Root.TGoodRunsListReader('grl.xml')
reader.Interpret()
goodrunslist = reader.GetMergedGRLCollection()

grl = GRL('grl.xml')

size = 5000000
runs = [int(i) for i in random.randint(178000, 190500, size=size)]
lbs = [int(i) for i in random.randint(0, 1000, size=size)]


def GoodRunsLists():
    for i in xrange(size):
        goodrunslist.HasRunLumiBlock(runs[i], lbs[i])


def goodruns():
    for i in xrange(size):
        (runs[i], lbs[i]) in grl


print "Running over %i random (run, lumiblock) combinations..." % size

print "GoodRunsLists... ",
sys.stdout.flush()
t1 = time.time()
GoodRunsLists()
t2 = time.time()
print "%f [sec]" % (t2 - t1)

print "goodruns... ",
sys.stdout.flush()
t1 = time.time()
goodruns()
t2 = time.time()
print "%f [sec]" % (t2 - t1)
