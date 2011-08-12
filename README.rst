goodruns provides an implementation of an ATLAS "good runs list" (GRL) reader/writer in Python, and collection of useful command-line tools.

An example of how to use goodruns::

    from goodruns import GRL

    grl = GRL("some_grl.xml")
    
    # check if the GRL contains the lumiblock 231 in run 186356:
    if (186356, 231) in grl:
        # do something
        pass

Command-line Tools
------------------

grl-diff

grl-and
grl-or
grl-xor

grl-clip

grl-convert

grl-runs
