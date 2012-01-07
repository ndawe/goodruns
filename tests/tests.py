#!/usr/bin/env python

import nose
from nose.tools import assert_raises
import os
from goodruns import GRL


DIRNAME = os.path.dirname(__file__)
grlA = os.path.join(DIRNAME, 'grlA.xml')
grlB = os.path.join(DIRNAME, 'grlB.xml')


def grl_logic_test():

    a = GRL(grlA)
    b = GRL(grlB)

    assert a ^ b == (a | b) - (a & b)

    assert a - b == (a + b) - b

    assert (not a - a) == True

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

    grl = GRL(grlA)
    for run in grl:
        lumiblocks = grl[run]


def str_init_test():

    grl = GRL(grlA)

    assert (180225, 87) in grl
    assert (180225, 1) not in grl


def dict_init_test():

    a = {1234: [(1,2), (4,5)]}
    grl = GRL(a)
    assert (1234, 1) in grl


def file_init_test():

    with open(grlA) as f:
        grl = GRL(f)
        assert (180225, 87) in grl


def save_test():

    grl = GRL(grlA)
    grl.save('testA.xml')
    os.unlink('testA.xml')
    assert_raises(NameError, grl.save, 'testB.badext')


def from_string_test():

    with open(grlA) as f:
        lines = f.readlines()
    grl_string = ''.join(lines)
    grl = GRL(grl_string, from_string=True)

    grl = GRL()
    grl.from_string(grl_string)

    grlb = GRL(grl.str(), from_string=True)

    assert grlb == grl


if __name__ == '__main__':
    nose.runmodule()
