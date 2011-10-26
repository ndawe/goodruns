#!/usr/bin/env python

import ROOT
ROOT.gSystem.Load('libGoodRunsLists.so')
from ROOT import Root
import random
from goodruns import GRL
from numpy import random
import time
import sys

ROOT.gErrorIgnoreLevel = ROOT.kFatal

print "Initializing GRL readers... ",
sys.stdout.flush()
reader = Root.TGoodRunsListReader('grl.xml')
reader.Interpret()
goodrunslist = reader.GetMergedGRLCollection()

grl = GRL('grl.xml')
print "done"

size = 5000000
print "Generating list of %i random (run, lumiblock) combinations... " % size,
sys.stdout.flush()
runs = [int(i) for i in random.randint(178000, 190500, size=size)]
lbs = [int(i) for i in random.randint(0, 1000, size=size)]
print "done"


def GoodRunsLists():
    for i in xrange(size):
        goodrunslist.HasRunLumiBlock(runs[i], lbs[i])


def goodruns():
    for i in xrange(size):
        (runs[i], lbs[i]) in grl


def compare_response():

    for i in xrange(size):
        run = runs[i]
        lb = lbs[i]
        if ((run, lb) in grl) != goodrunslist.HasRunLumiBlock(run, lb):
            raise ValueError('conflicting response for (%i, %i)' % (run, lb))


print "Comparing responses from GoodRunsLists and goodruns... ",
sys.stdout.flush()
try:
    compare_response()
except ValueError, e:
    print "Failed: %s" % e
    sys.exit(1)
print "OK"

print "Running speed test on %i (run, lumiblock) combinations..." % size

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


