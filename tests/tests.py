#!/usr/bin/env python

import nose
import os
from goodruns import GRL

DIRNAME = os.path.dirname(__file__)

def str_init_test():

    grl = GRL(os.path.join(DIRNAME, 'grlA.xml'))

    assert (180225, 87) in grl
    assert (180225, 1) not in grl



def dict_init_test():

    a = {1234: [(1,2), (4,5)]}
    grl = GRL(a)
    assert (1234, 1) in grl


def file_init_test():

    with open(os.path.join(DIRNAME, 'grlA.xml')) as f:
        grl = GRL(f)
        assert (180225, 87) in grl


if __name__ == '__main__':
    nose.runmodule()
