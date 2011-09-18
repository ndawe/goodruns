import nose
import os
from goodruns import GRL

def test():
    
    dirname = os.path.dirname(__file__)
    grl = GRL(os.path.join(dirname, "grl.xml"))

    assert (180225, 87) in grl

if __name__ == '__main__':
    nose.runmodule()
