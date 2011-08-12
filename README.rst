.. -*- mode: rst -*-

About
=====

goodruns provides an implementation of an ATLAS "good runs list" (GRL)
reader/writer in Python, and collection of useful command-line tools.

Installation
============

To install in your home directory, use::

  python setup.py install --home

To install for all users::

  sudo python setup.py install

Usage
=====

An example of how to use goodruns in a Python application::

    from goodruns import GRL

    grl = GRL("some_grl.xml")
    
    # check if the GRL contains the lumiblock 231 in run 186356:
    if (186356, 231) in grl:
        # do something
        pass

Command-line Tools
==================

goodruns also provides a collection of command-line tools
for combining, manipulating, and inspecting GRLs.

Use ``grl-diff`` determine the GRL containing the runs/lumiblocks in ``A.xml`` but not in ``B.xml``::
    
    grl-diff A.xml B.xml

All command-line tools print on stdout. Redirect stdout to a file to save the result::

    grl-diff A.xml B.xml > C.xml

grl-and grl-or grl-xor
^^^^^^^^^^^^^^^^^^^^^^

grl-clip
^^^^^^^^

grl-convert
^^^^^^^^^^^

grl-runs
^^^^^^^^
