#!/usr/bin/env python

import nose
from nose.tools import assert_raises
import os
from goodruns import GRL


DIRNAME = os.path.dirname(__file__)
GRLA = os.path.join(DIRNAME, 'grlA.xml')
GRLB = os.path.join(DIRNAME, 'grlB.xml')


def grl_logic_test():

    a = GRL(GRLA)
    b = GRL(GRLB)

    assert a == a
    assert b == b
    assert a != b
    assert (a ^ b) == ((a | b) - (a & b))
    assert (a - b) == ((a + b) - b)
    assert (not (a - a)) == True
    assert (not (a ^ a)) == True

    a & b
    a ^ b
    a | b
    a + b
    a - b

    a &= b
    a ^= b
    a |= b
    a += b
    a -= b


def iter_test():

    grl = GRL(GRLA)
    for run in grl:
        lumiblocks = grl[run]


def str_init_test():

    grl = GRL(GRLA)

    assert (180225, 87) in grl
    assert (180225, 1) not in grl


def dict_init_test():

    a = {1234: [(1,2), (4,5)]}
    grl = GRL(a)
    assert (1234, 1) in grl


def file_init_test():

    with open(GRLA) as f:
        grl = GRL(f)
        assert (180225, 87) in grl


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

    assert grlb == grl


def test_read_yaml():

    grl = GRL(GRLA)
    grl.save('test.yml')
    grl2 = GRL('test.yml')
    assert grl == grl2
    os.unlink('test.yml')


def test_ROOT():

    import ROOT
    filename = os.path.join(DIRNAME, 'test.root')
    root_file = ROOT.TFile.Open(filename, 'recreate')
    root_file.Close()

    grl = GRL(GRLA)
    grl.save(filename + ':/lumi')
    grl2 = GRL(filename + ':/lumi')
    assert grl == grl2

    root_file = ROOT.TFile.Open(filename, 'recreate')
    root_file.mkdir('dir')
    root_file.Close()

    grl = GRL(GRLA)
    grl.save(filename + ':/dir/lumi')
    grl2 = GRL(filename + ':/dir/lumi')
    assert grl == grl2

    root_file = ROOT.TFile.Open(filename)
    tobj = root_file.Get('dir/lumi')
    assert isinstance(tobj, ROOT.TObjString)
    root_file.Close()
    os.unlink(filename)


if __name__ == '__main__':
    nose.runmodule()
