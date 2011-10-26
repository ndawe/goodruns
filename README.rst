.. -*- mode: rst -*-

About
-----

goodruns provides an implementation of an ATLAS "good run list" (GRL)
reader/writer in Python, and collection of useful command-line tools.


Requirements
------------

goodruns requires at least Python 2.5 and only depends on modules in the standard library.
For improved performance goodruns will optionally use `lxml <http://pypi.python.org/pypi/lxml/2.3>`_
if installed. Install `PyYAML <http://pypi.python.org/pypi/PyYAML/>`_ if you would
like to convert GRLs into YAML format.


Installation
------------

The easiest way to install goodruns is with ``pip``.
To install for all users::

    sudo pip install goodruns

To install in your home directory::

    pip install --user goodruns

If you have obtained a copy of goodruns yourself use the ``setup.py``
script to install. To install for all users::

    sudo python setup.py install

To install in your home directory::

    python setup.py install --user

To install the optional dependencies
(first download a source distribution if you haven't already)::

    pip install -U -r optional-requirements.txt


Usage
-----

An example of how to use goodruns::

    from goodruns import GRL

    grl = GRL('grl.xml')
    
    # check if the GRL contains the lumiblock 231 in run 186356:
    if (186356, 231) in grl:
        # do something
        pass


Command-line Tools
------------------

goodruns also provides a collection of command-line tools
for combining, manipulating, and inspecting GRLs.

grl-diff
~~~~~~~~

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

grl-and, grl-or, grl-xor
~~~~~~~~~~~~~~~~~~~~~~~~

These scripts implement logical combinations of GRLs. Logical AND::

    grl-and A.xml B.xml > C.xml

OR::

    grl-or A.xml B.xml > C.xml

and XOR (exclusive OR)::

    grl-xor A.xml B.xml > C.xml

Again, these commands can be combined arbitrarily::

    grl-and A.xml B.xml | grl-or C.xml | grl-xor D.xml > E.xml

grl-clip
~~~~~~~~

Use ``grl-clip`` to truncate a GRL between a starting run/lumiblock and ending run/lumiblock::

    > grl-clip --help
    Usage: grl-clip [options] [file]

    Options:
      -h, --help            show this help message and exit
      -o OUTPUT, --output=OUTPUT
                            Output filename
      --startrun=STARTRUN   Start run
      --startlb=STARTLB     Start lumiblock
      --endrun=ENDRUN       End run
      --endlb=ENDLB         End lumiblock

grl-convert
~~~~~~~~~~~

``grl-convert`` can convert a GRL from XML format into YAML::

    > grl-convert -f yml A.xml
    186178:
    - !!python/tuple [125, 156]
    - !!python/tuple [158, 161]
    186179:
    - !!python/tuple [382, 388]
    - !!python/tuple [390, 390]
    - !!python/tuple [396, 396]
    - !!python/tuple [398, 415]
    - !!python/tuple [417, 431]
    - !!python/tuple [433, 453]
    - !!python/tuple [455, 469]
    - !!python/tuple [471, 474]
    - !!python/tuple [476, 479]
    186180:
    - !!python/tuple [114, 116]
    - !!python/tuple [118, 124]
    - !!python/tuple [126, 140]
    - !!python/tuple [144, 149]
    - !!python/tuple [151, 170]
    - !!python/tuple [173, 176]
    ...

or plain text format::

    > grl-convert -f txt A.xml
    ---------------
    RUN: 186178
    LUMIBLOCKS:
      125 - 156
      158 - 161
    ---------------
    RUN: 186179
    LUMIBLOCKS:
      382 - 388
      390
      396
      398 - 415
      417 - 431
      433 - 453
      455 - 469
      471 - 474
      476 - 479
    ---------------
    RUN: 186180
    LUMIBLOCKS:
      114 - 116
      118 - 124
      126 - 140
      144 - 149
      151 - 170
      173 - 176
    ...

grl-runs
~~~~~~~~

``grl-runs`` simply prints the run numbers, one per line, contained within a GRL::

    > grl-runs A.xml
    186178
    186179
    186180
    ...
