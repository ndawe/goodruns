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

grl-diff
^^^^^^^^

Use ``grl-diff`` to determine the GRL containing the runs/lumiblocks in ``A.xml`` but not in ``B.xml``::
    
    grl-diff A.xml B.xml

In other words, ``B.xml`` is subtracted from ``A.xml``.
All command-line tools print on stdout. Redirect stdout to a file to save the result::

    grl-diff A.xml B.xml > C.xml

You may supply more than two GRLs to ``grl-diff``::

    grl-diff A.xml B.xml C.xml D.xml > E.xml

which results in the GRL E=((A-B)-C)-D). This is equivalent to::

    grl-diff A.xml B.xml | grl-diff C.xml | grl-diff D.xml > E.xml

The output of one command can be piped into any of the other commands in goodruns.

grl-and grl-or grl-xor
^^^^^^^^^^^^^^^^^^^^^^

These scripts implement logical combinations of GRLs. Logical AND::

    grl-and A.xml B.xml > C.xml

OR::

    grl-or A.xml B.xml > C.xml

and XOR (exclusive OR)::

    grl-xor A.xml B.xml > C.xml

Again, these commands can be combined arbitrarily::

    grl-and A.xml B.xml | grl-or C.xml | grl-xor D.xml > E.xml

grl-clip
^^^^^^^^

grl-convert
^^^^^^^^^^^

grl-runs
^^^^^^^^
