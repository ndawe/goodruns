import nose
import os
from goodruns import GRL

def test_read():
    
    dirname = os.path.dirname(__file__)
    grl = GRL(os.path.join(dirname, "grl.xml"))

if __name__ == '__main__':
    node.runmodule()
