#!/usr/bin/env python

import nose
from nose.tools import assert_raises, assert_equal, assert_true
from nose.exc import SkipTest
import os
from goodruns import GRL, LumiblockRange
from goodruns import info
info.USE_YAML = True
info.USE_LXML = True

DIRNAME = os.path.dirname(__file__)
GRLA = os.path.join(DIRNAME, 'grlA.xml')
GRLB = os.path.join(DIRNAME, 'grlB.xml')


def grl_logic_test():

    a = GRL(GRLA)
    b = GRL(GRLB)

    a & b
    a ^ b
    a | b
    a + b
    a - b

    assert_equal(a, a)
    assert_equal(b, b)
    assert_true(a != b)
    assert_equal((a ^ b), ((a | b) - (a & b)))
    assert_equal((a - b), ((a + b) - b))
    assert_true(not (a - a))
    assert_true(not (a ^ a))
    assert_equal(a & b, b & a)
    assert_equal(a | b, b | a)
    assert_equal(a ^ b, b ^ a)

    a &= b
    a ^= b
    a |= b
    a += b
    a -= b


def lumiblock_test():

    a = LumiblockRange(1, 10)
    b = LumiblockRange(5, 50)
    assert_true(b > a)
    assert_true(b.intersects(a))
    assert_true(a.intersects(b))


def iter_test():

    grl = GRL(GRLA)
    for run in grl:
        lumiblocks = grl[run]


def str_init_test():

    grl = GRL(GRLA)

    assert_true((180225, 87) in grl)
    assert_true((180225, 1) not in grl)


def dict_init_test():

    a = {1234: [(1,2), (4,5)]}
    grl = GRL(a)
    assert_true((1234, 1) in grl)


def file_init_test():

    with open(GRLA) as f:
        grl = GRL(f)
        assert_true((180225, 87) in grl)


def save_test():

    grl = GRL(GRLA)
    grl.save('testA.xml')
    os.unlink('testA.xml')
    assert_raises(ValueError, grl.save, 'testB.badext')


def from_string_test():

    with open(GRLA) as f:
        lines = f.readlines()
    grl_string = ''.join(lines)
    grl = GRL(grl_string, from_string=True)

    grl = GRL()
    grl.from_string(grl_string)

    grlb = GRL(grl.str(), from_string=True)

    assert_equal(grlb, grl)


def test_read_yaml():

    try:
        import yaml
    except ImportError:
        raise SkipTest

    grl = GRL(GRLA)
    grl.save('test.yml')
    grl2 = GRL('test.yml')
    assert_equal(grl, grl2)
    os.unlink('test.yml')


def test_ROOT():

    try:
        import ROOT
    except ImportError:
        raise SkipTest

    filename = os.path.join(DIRNAME, 'test.root')
    root_file = ROOT.TFile.Open(filename, 'recreate')
    root_file.Close()

    grl = GRL(GRLA)
    grl.save(filename + ':/lumi')
    grl2 = GRL(filename + ':/lumi')
    assert_equal(grl, grl2)

    root_file = ROOT.TFile.Open(filename, 'recreate')
    root_file.mkdir('dir')
    root_file.Close()

    grl = GRL(GRLA)
    grl.save(filename + ':/dir/lumi')
    grl2 = GRL(filename + ':/dir/lumi')
    assert_equal(grl, grl2)

    root_file = ROOT.TFile.Open(filename)
    tobj = root_file.Get('dir/lumi')
    assert_true(isinstance(tobj, ROOT.TObjString))
    root_file.Close()
    os.unlink(filename)


if __name__ == '__main__':
    nose.runmodule()
