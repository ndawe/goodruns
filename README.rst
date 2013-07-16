.. -*- mode: rst -*-

About
-----

goodruns provides an implementation of an ATLAS "good run list" (GRL)
reader/writer in Python, and collection of useful command-line tools.


Requirements
------------

goodruns requires at least Python 2.5.
Unlike the standard ATLAS GoodRunsLists package, goodruns does not depend on
`ROOT <http://root.cern.ch/>`_ for XML processing unless you are reading from
or writing to a ROOT file (see below). For better XML reading/writing goodruns
will optionally use `lxml <http://pypi.python.org/pypi/lxml/2.3>`_ if installed.
Install `PyYAML <http://pypi.python.org/pypi/PyYAML/>`_ if you would like to
convert GRLs into YAML format.

To enable the dependency on lxml and/or PyYAML change ``False`` to ``True`` on
the appropriate line(s) in `goodruns/info.py` and perform a manual installation
as described below.


Automatic Installation
----------------------

Automatically install the latest version of goodruns with
`pip <http://pypi.python.org/pypi/pip>`_::

    pip install --user goodruns

or with ``easy_install``::

    easy_install --user goodruns

Omit the ``--user`` for a system-wide installation (requires root privileges).
Add ``${HOME}/.local/bin`` to your ``${PATH}`` if using ``--user`` and if
it is not there already (put this in your .bashrc)::

   export PATH=${HOME}/.local/bin${PATH:+:$PATH}

To upgrade an existing installation use the ``-U``
option in the ``pip`` or ``easy_install`` commands above.


Manual Installation
-------------------

Get the latest tarball on `PyPI <http://pypi.python.org/pypi/goodruns/>`_

Untar and install (replace X appropriately)::

   tar -zxvf goodruns-X.tar.gz
   cd goodruns-X

To install goodruns into your home directory
if using at least Python 2.6::

   python setup.py install --user

or with older Python versions::

   python setup.py install --prefix=~/.local

Add ``${HOME}/.local/bin`` to your ``${PATH}`` if it is not there already
(put this in your .bashrc)::

   export PATH=${HOME}/.local/bin${PATH:+:$PATH}

To install the optional dependencies::

   pip install -U -r optional-requirements.txt


Usage
-----

An example of how to use goodruns::

   from goodruns import GRL

   grl = GRL('grl.xml')
   # or:
   grl = GRL('http://atlasdqm.web.cern.ch/atlasdqm/grlgen/path/to/grl.xml')
   # or (if '/path/to/grl' is a ROOT.TObjString in data.root):
   grl = GRL('data.root:/path/to/grl')

   # check if the GRL contains the lumiblock 231 in run 186356:
   if (186356, 231) in grl:
       # do something
       pass

The GRL is automatically optimized (lumiblocks are merged and sorted)::

   >>> from goodruns import GRL
   >>> a = GRL()
   >>> a.insert(1, (1,4))
   >>> a.insert(1, (7,10))
   >>> a
   ---------------
   RUN: 1
   LUMIBLOCKS:
     1 - 4
     7 - 10
   >>> a.insert(1, (6,7))
   >>> a
   ---------------
   RUN: 1
   LUMIBLOCKS:
     1 - 4
     6 - 10
   >>> a.insert(1, (5,5))
   >>> a
   ---------------
   RUN: 1
   LUMIBLOCKS:
     1 - 10


Command-line Tools
------------------

goodruns also provides a collection of command-line tools
for combining, manipulating, and inspecting GRLs. As above
GRLs may be XML files, URLs, or in ROOT files.


grl diff
~~~~~~~~

Use ``grl diff`` to determine the GRL containing the runs/lumiblocks in
``A.xml`` but not in ``B.xml``::
    
    grl diff A.xml B.xml

In other words, ``B.xml`` is subtracted from ``A.xml``.
All command-line tools print on stdout. Redirect stdout to a file to save
the result::

    grl diff A.xml B.xml > C.xml

You may supply more than two GRLs to ``grl diff``::

    grl diff A.xml B.xml C.xml D.xml > E.xml

which results in the GRL E=((A-B)-C)-D). This is equivalent to::

    grl diff A.xml B.xml | grl diff C.xml | grl diff D.xml > E.xml

The output of one command can be piped into any of the other commands
in goodruns.


grl and, grl or, grl xor
~~~~~~~~~~~~~~~~~~~~~~~~

These scripts implement logical combinations of GRLs. Logical AND::

    grl and A.xml B.xml > C.xml

OR::

    grl or A.xml B.xml > C.xml

and XOR (exclusive OR)::

    grl xor A.xml B.xml > C.xml

Again, these commands can be combined arbitrarily::

    grl and A.xml B.xml | grl or C.xml | grl xor D.xml > E.xml

and any GRL argument can also be a ROOT file or URL::

    grl and data.root:/path/to/grl http://atlasdqm.web.cern.ch/path/to/grl.xml


grl clip
~~~~~~~~

Use ``grl clip`` to truncate a GRL between a starting run/lumiblock and ending
run/lumiblock::

    grl clip --help
    usage: grl clip [-h] [-o OUTPUT] [-f FORMAT] [--startrun STARTRUN]
                    [--startlb STARTLB] [--endrun ENDRUN] [--endlb ENDLB]
                    [grl]

    positional arguments:
      grl

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            Output filename (optional)
      -f FORMAT, --format FORMAT
                            Output format: xml, yml, txt, py, cut
      --startrun STARTRUN   Start run
      --startlb STARTLB     Start lumiblock
      --endrun ENDRUN       End run
      --endlb ENDLB         End lumiblock 


grl convert
~~~~~~~~~~~

``grl convert`` can convert a GRL from XML format into YAML::

    grl convert -f yml A.xml
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

or plain text::

    grl convert -f txt A.xml
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

``grl convert`` will also convert a GRL into Python code (dict of lists of
tuples) or (as a joke) a ROOT TCut expression.


grl runs
~~~~~~~~

``grl runs`` simply prints the run numbers, one per line, contained
within a GRL::

    grl runs A.xml
    186178
    186179
    186180
    ...

Quickly print the runs contained in a GRL from a URL::

    grl runs http://atlasdqm.web.cern.ch/path/to/grl.xml


grl find
~~~~~~~~

``grl find`` prints the GRLs containing a run number and lumiblock number (if
any). The lumiblock number is optional, and if left unset all GRLs containing
the run will be printed. For example, you can determine which ROOT file contains
the run 215643 and lumiblock 400 with the following command::

    grl find --path Lumi/tau --pattern "*.root*" --run 215643 --lb 400 globbed*path*
