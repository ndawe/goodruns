# Author: Noel Dawe <Noel.Dawe@cern.ch>

"""
This module provides the main GRL class and utility functions
"""

USE_LXML = True
try:
    import lxml.etree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    import xml.dom.minidom as minidom
    USE_LXML = False

USE_YAML = True
try:
    import yaml
except ImportError:
    USE_YAML = False

import os
import copy
import urllib2
from pprint import pprint
from operator import sub, or_, and_, xor, itemgetter
from .sorteddict import SortedDict
import bisect
import datetime
import cStringIO
import re


__all__ = [
    'clipped',
    'diffed',
    'ored',
    'anded',
    'xored',
    'LumiblockRange',
    'GRL',
]


def clipped(grl, startrun=None, startlb=None, endrun=None, endlb=None):
    """
    Return a clipped GRL between startrun, startlb and
    endrun, endlb (inclusive).

    *grl*: GRL

    *startrun*: [ int | None ]

    *startlb*: [ int | None ]

    *endrun*: [ int | None ]

    *endlb*: [ int | None ]
    """
    grl_copy = copy.deepcopy(grl)
    grl_copy.clip(startrun=startrun, startlb=startlb,
                  endrun=endrun, endlb=endlb)
    return grl_copy


def diffed(*args):
    """
    Return the difference of multiple GRLs: (((A-B)-C)-D)...)

    *args*: tuple of GRLs
    """
    return reduce(sub, args)


def ored(*args):
    """
    Return the OR of multiple GRLs: A | B | C...

    *args*: tuple of GRLs
    """
    return reduce(or_, args)


def anded(*args):
    """
    Return the AND of multiple GRLs: A & B & C...

    *args*: tuple of GRLs
    """
    return reduce(and_, args)


def xored(*args):
    """
    Return the XOR of multiple GRLs: A ^ B ^ C...

    *args*: tuple of GRLs
    """
    return reduce(xor, args)


class LumiblockRange(tuple):
    """
    A 2-tuple consisting of the lower and upper
    bounds of a lumiblock range
    """
    def __new__(cls, *args):
        """
        *args*: [ tuple | list ]
            2-tuple/list of lumiblock numbers in ascending order
        """
        if len(args) == 1 and isinstance(args[0], tuple):
            args = args[0]
        if len(args) != 2:
            raise ValueError('lbrange must contain exactly 2 elements: %s' % \
                             (args,))
        for lumiblock in args:
            if not isinstance(lumiblock, (int, long)):
                raise TypeError('lbrange must contain integers or longs only')
        if args[0] > args[1]:
            raise ValueError('lbrange in wrong order: %s' % (args,))
        return super(LumiblockRange, cls).__new__(cls, args)

    def __contains__(self, lbn):
        """
        Determine whether a lumiblock is contained by this
        lumiblock range

        *lbn*: int
        """
        return self[0] <= lbn <= self[1]

    def __cmp__(self, other):
        """
        Determine whether this lumiblock range should be placed
        to the right or left of another lumiblock number or range

        *other*: LumiblockRange
        """
        if isinstance(other, (int, long)):
            if other in self:
                return 0
            return cmp(self[0], other)
        return super(LumiblockRange, self).__cmp__(other)

    def intersects(self, lbrange):
        """
        Determine if self intersects with another lumiblock range

        *lbrange*: LumiblockRange
        """
        if lbrange[0] in self or lbrange[1] in self:
            return True
        if self[0] in lbrange or self[1] in lbrange:
            return True
        return False

    def as_set(self):
        """
        Convert self to set of lumiblocks
        """
        return set(range(self[0], self[1] + 1))


class GRL(object):
    """
    The main GRL class holds a python dictionary
    mapping runs to a list of lumiblock ranges (2-tuples)
    """
    formats = [
        'xml',
        'yml',
        'txt',
        'py',
        'cut'
    ]

    def __init__(self, grl=None, from_string=False):
        """
        *grl*: [ dict | str | None ]

        *from_string*: bool
            If True, interpret grl as xml string and not filename
        """
        self.name = 'GRL'
        self.version = '1.0'
        self.metadata = []
        self.__grl = SortedDict()
        if not grl:
            return
        if isinstance(grl, dict):
            self.from_dict(grl)
            return
        if isinstance(grl, basestring) and from_string:
            self.from_string(grl)
            return
        elif from_string:
            raise TypeError("grl is non-string type %s while "
                            "using from_string" % type(grl))
        elif isinstance(grl, (basestring, file)):
            filename = grl
            if isinstance(grl, basestring):
                # is grl a URL?
                if grl.startswith("http://"):
                    grl = urllib2.urlopen(grl)
                # is grl a ROOT file path?
                elif re.search('.root:/', grl):
                    # one place where goodruns requires ROOT
                    try:
                        import ROOT
                        ROOT.PyConfig.IgnoreCommandLineOptions = True
                    except ImportError:
                        raise ImportError('Specified GRL in ROOT file '
                                          'but cannot import ROOT. Are ROOT '
                                          'and PyROOT installed?')
                    cwd = ROOT.gDirectory
                    filename, _, path = grl.partition(':/')
                    root_file = ROOT.TFile.Open(filename)
                    if not root_file:
                        raise IOError('Could not open ROOT file: %s' %
                                      filename)
                    grl = root_file.Get(path)
                    if not grl:
                        raise ValueError('Path %s does not exist in '
                                         'ROOT file %s' % (path, filename))
                    if not isinstance(grl, ROOT.TObjString):
                        raise TypeError('Object at %s is not a '
                                        'ROOT.TObjString' % path)
                    self.from_string(str(grl.GetString()))
                    root_file.Close()
                    # return to previous directory
                    cwd.cd()
                    for run in self.iterruns():
                        self.__grl[run].sort()
                        self.__optimize(run)
                    return
            elif isinstance(grl, file):
                filename = grl.name
            name, ext = os.path.splitext(filename)
            if filename == "<stdin>" or ext == '.xml':
                tree = ET.parse(grl)
                self.from_xml(tree)
            elif ext == '.yml':
                if USE_YAML:
                    if isinstance(grl, file):
                        self.from_dict(yaml.load(grl))
                    else:
                        with open(grl) as grl_file:
                            self.from_dict(yaml.load(grl_file))
                else:
                    raise ImportError("PyYAML module not found")
            else:
                raise ValueError(
                    "File %s does not have valid GRL extension: %s"
                    % (filename, ext))
            for run in self.iterruns():
                self.__grl[run].sort()
                self.__optimize(run)
            return
        raise TypeError("Unable to initialize GRL from a %s" % type(grl))

    def from_string(self, string):
        """
        Insert runs and lumiblocks from XML string

        *string*: str
        """
        tree = ET.fromstring(string)
        self.from_xml(tree)

    def from_xml(self, tree):
        """
        Insert runs and lumiblocks from XML

        *tree*: ElementTree
        """
        name = tree.find('NamedLumiRange/Name')
        if name is not None:
            self.name = name.text
        version = tree.find('NamedLumiRange/Version')
        if version is not None:
            self.version = version.text
        metadata = tree.findall('NamedLumiRange/Metadata')
        if metadata is not None:
            self.metadata = metadata
        lbcols = tree.findall(
            'NamedLumiRange/LumiBlockCollection')
        if lbcols is None:
            return
        for lbcol in lbcols:
            run = int(lbcol.find('Run').text)
            lbs = lbcol.findall('LBRange')
            for lumiblock in lbs:
                self.insert(run,
                    LumiblockRange(int(lumiblock.attrib['Start']),
                                   int(lumiblock.attrib['End'])))

    def from_dict(self, d):
        """
        Convert dict to GRL

        *d*: dict
        """
        o = {}
        for run, lbranges in d.items():
            o[run] = [LumiblockRange(*a) for a in lbranges]
        self.__grl.update(o)

    def to_dict(self):
        """
        Convert self to dict
        """
        o = {}
        for run, lbranges in self.items():
            o[run] = [(a[0], a[1]) for a in lbranges]
        return o

    def __merge_metadata(self, other=None):

        # drop metadata for now
        self.metadata = []

    def __copy__(self):

        return copy.deepcopy(self)

    def __nonzero__(self):

        return bool(self.__grl)

    def __repr__(self):

        return self.__str__()

    def __str__(self):

        output = ''
        runs_end = len(self.__grl) - 1
        for i, run in enumerate(self.iterruns()):
            lbranges = self.__grl[run]
            maxlength = max([len(str(lbrange[0])) for lbrange in lbranges])
            output += '-' * 15 + '\n'
            output += 'RUN: %i\n' % run
            output += 'LUMIBLOCKS:\n'
            lbranges_end = len(lbranges) - 1
            for j, lbrange in enumerate(lbranges):
                if lbrange[0] == lbrange[1]:
                    output += ('  %%-%ds' % maxlength) % lbrange[0]
                else:
                    output += ('  %%-%ds' % maxlength + ' - %i') % lbrange
                if i != runs_end or j != lbranges_end:
                    output += '\n'
        return output

    def __getitem__(self, run):
        """
        Return list of lumiblock ranges for a run

        *run*: int
        """
        return self.__grl[run]

    def __delitem__(self, run):
        """
        Remove run and associated lumiblock ranges from GRL

        *run*: int
        """
        del self.__grl[run]

    def __contains__(self, runlb):
        """
        Returns True if this GRL contains a run and lumiblock

        *runlb*: tuple
            2-tuple of ints containing run number and lumiblock number
        """
        run, lbn = runlb
        if run in self.__grl:
            lbranges = self.__grl[run]
            # Locate the LumiblockRange containing lbn
            i = bisect.bisect_left(lbranges, lbn)
            if (i != len(lbranges)) and (lbn in lbranges[i]):
                return True
        return False

    def __iter__(self):
        """
        Iterate over runs in GRL
        """
        return self.iterruns()

    def items(self):
        """
        Iterate over (run, lbranges) in GRL
        """
        return self.__grl.items()

    def iterlbranges(self):
        """
        Iterate over (run, lbrange) in GRL
        """
        for run, lbranges in self.__grl.items():
            for lbrange in lbranges:
                yield (run, lbrange)

    def iterruns(self):
        """
        Iterate over runs in GRL
        """
        for run in self.__grl.iterkeys():
            yield run

    def runs(self):
        """
        Return list of runs in GRL
        """
        return self.__grl.keys()

    def has_run(self, run):
        """
        Returns True if run is in GRL, else False

        *run*: int
        """
        return run in self.__grl

    def insert(self, run, lbrange):
        """
        Insert a lumiblock range into a run

        *run*: int

        *lbrange*: [ LumiblockRange | tuple ]
        """
        if not isinstance(run, int):
            raise TypeError('run must be an integer')
        if not isinstance(lbrange, LumiblockRange):
            lbrange = LumiblockRange(*lbrange)
        try:
            lbranges = self.__grl[run]
            i = bisect.bisect(lbranges, lbrange)
            lbranges.insert(i, lbrange)
            self.__optimize(run)
        except KeyError:
            self.__grl[run] = [lbrange]

    def remove(self, run, lbrange):
        """
        Remove a lumiblock range from a run

        *run*: int

        *lbrange*: LumiblockRange
        """
        if run in self.__grl:
            if not isinstance(lbrange, LumiblockRange):
                lbrange = LumiblockRange(*lbrange)
            lbranges = self.__grl[run]
            for mylbrange in lbranges[:]:
                if lbrange[1] < mylbrange[0]:
                    continue
                if lbrange == mylbrange:
                    lbranges.remove(mylbrange)
                    break
                elif lbrange[0] > mylbrange[0] and lbrange[1] < mylbrange[1]:
                    # embedded: must split
                    left_lbrange = LumiblockRange(mylbrange[0],
                                                  lbrange[0] - 1)
                    right_lbrange = LumiblockRange(lbrange[1] + 1,
                                                   mylbrange[1])
                    index = lbranges.index(mylbrange)
                    lbranges[index] = left_lbrange
                    lbranges.insert(index + 1, right_lbrange)
                    break
                elif lbrange.intersects(mylbrange):
                    diff = mylbrange.as_set().difference(lbrange.as_set())
                    if not diff:  # empty set
                        lbranges.remove(mylbrange)
                        if len(lbranges) == 0:
                            break
                        continue
                    newlbrange = LumiblockRange(min(diff), max(diff))
                    lbranges[lbranges.index(mylbrange)] = newlbrange
                elif mylbrange[0] > lbrange[1]:
                    break
            if len(lbranges) == 0:
                del self.__grl[run]

    def clip(self, startrun=None, startlb=None, endrun=None, endlb=None):
        """
        Clip the GRL between startrun, startlb and endrun, endlb (inclusive)

        *startrun*: [ int | None ]

        *startlb*: [ int | None ]

        *endrun*: [ int | None ]

        *endlb*: [ int | None ]
        """
        for run in self.runs():
            if startrun is not None:
                if run < startrun:
                    del self.__grl[run]
                elif run == startrun:
                    if startlb is not None:
                        lbranges = self.__grl[run][:]
                        for lbrange in lbranges:
                            if lbrange[1] < startlb:
                                self.__grl[run].remove(lbrange)
                            elif startlb >= lbrange[0] and \
                                 startlb <= lbrange[1]:
                                self.__grl[run][
                                    self.__grl[run].index(lbrange)
                                    ] = LumiblockRange(startlb, lbrange[1])
                        if len(self.__grl[run]) == 0:
                            del self[run]
            if endrun is not None:
                if run > endrun:
                    del self.__grl[run]
                elif run == endrun:
                    if endlb is not None:
                        lbranges = self.__grl[run][:]
                        for lbrange in lbranges:
                            if lbrange[0] > endlb:
                                self[run].remove(lbrange)
                            elif endlb >= lbrange[0] and endlb <= lbrange[1]:
                                self[run][
                                    self[run].index(lbrange)
                                    ] = LumiblockRange(lbrange[0], endlb)
                        if len(self[run]) == 0:
                            del self[run]

    def __optimize(self, run):
        """
        Merge lumiblock ranges

        *run*: int
        """
        lbranges = self.__grl[run]
        if len(lbranges) == 0:
            del self.__grl[run]
            return
        first = 0
        last = len(lbranges) - 1
        while first != last:
            _next = first + 1
            merged = False
            while _next <= last:
                if lbranges[first][1] >= lbranges[_next][1]:
                    for index in xrange(first + 1, _next + 1):
                        lbranges.pop(_next)
                    merged = True
                    break
                elif lbranges[first][1] + 1 >= lbranges[_next][0]:
                    lbranges[first] = LumiblockRange(lbranges[first][0],
                                                     lbranges[_next][1])
                    for index in xrange(first + 1, _next + 1):
                        lbranges.pop(_next)
                    merged = True
                    break
                _next += 1
            last = len(lbranges) - 1
            if not merged:
                first += 1

    def __eq__(self, other):

        return self.__grl == other.__grl

    def __ne__(self, other):

        return not self.__eq__(other)

    def __add__(self, other):

        grlcopy = copy.deepcopy(self)
        grlcopy += other
        return grlcopy

    def __iadd__(self, other):

        if isinstance(other, basestring):
            other = GRL(other, from_string=True)
        for run, lbrange in other.iterlbranges():
            self.insert(run, LumiblockRange(lbrange))
        self.__merge_metadata(other)
        return self

    def __sub__(self, other):

        grlcopy = copy.deepcopy(self)
        grlcopy -= other
        return grlcopy

    def __isub__(self, other):

        if isinstance(other, basestring):
            other = GRL(other, from_string=True)
        for run, lbrange in other.iterlbranges():
            self.remove(run, lbrange)
        self.__merge_metadata(other)
        return self

    def __and__(self, other):

        return self - (self - other)

    def __iand__(self, other):

        self -= (self - other)
        return self

    def __or__(self, other):

        return self + other

    def __ior__(self, other):

        self += other
        return self

    def __xor__(self, other):

        return (self | other) - (self & other)

    def __ixor__(self, other):

        grlcopy = copy.deepcopy(self)
        self |= other
        self -= (grlcopy & other)
        return self

    def cut(self, runname='RunNumber', lbname='lbn'):
        """
        Convert this GRL into a TCut expression.
        This method is really meant to be a joke and should be of no use.

        *runname*: str

        *lbname*: str
        """
        cut = ''
        for run in self.iterruns():
            lbcut = ''
            for lbrange in self[run]:
                newcut = (lbname + '>=%i&&' + lbname + '<=%i') % lbrange
                if lbcut:
                    lbcut = '(%s)|(%s)' % (lbcut, newcut)
                else:
                    lbcut = newcut
            newcut = '(%s==%i)&&(%s)' % (runname, run, lbcut)
            if cut:
                cut = '(%s)|(%s)' % (cut, newcut)
            else:
                cut = newcut
        return cut

    def str(self, format='xml'):
        """
        Return string repr of self in the specified format

        *format*: str
        """
        str_io = cStringIO.StringIO()
        self.write(filehandle=str_io, format=format)
        return str_io.getvalue()

    def save(self, name):
        """
        Save GRL to file by name. Determine format from
        extension.

        *name*: str
        """
        # is name a ROOT file path?
        if re.search('.root:/', name):
            # one place where goodruns requires ROOT
            try:
                import ROOT
                ROOT.PyConfig.IgnoreCommandLineOptions = True
            except ImportError:
                raise ImportError('Attempting to save GRL in ROOT file '
                                  'but cannot import ROOT. Are ROOT and PyROOT '
                                  'installed?')
            cwd = ROOT.gDirectory
            filename, _, path = name.partition(':/')
            root_file = ROOT.TFile.Open(filename, 'UPDATE')
            if not root_file:
                raise IOError('Could not open ROOT file: %s' %
                              filename)
            head, tail = os.path.split(os.path.normpath(path))
            if head and not root_file.cd(head):
                raise ValueError('Path %s does not exist in file %s' %
                                 (head, filename))
            xml_string = ROOT.TObjString(self.str())
            xml_string.Write(tail)
            root_file.Close()
            # return to previous directory
            cwd.cd()
        else:
            _, ext = os.path.splitext(name)
            # ignore period
            ext = ext[1:]
            if ext not in GRL.formats:
                raise ValueError("Filename %s does not have "
                                 "a valid GRL extension." %
                                 name)
            with open(name, 'w') as filehandle:
                self.write(filehandle, format=ext)

    def write(self, filehandle, format='xml'):
        """
        Write the GRL in the specified format to the file object.

        *filehandle*: file

        *format*: str
        """
        if format == 'xml':
            root = ET.Element('LumiRangeCollection')
            subroot = ET.SubElement(root, 'NamedLumiRange')
            name = ET.SubElement(subroot, 'Name')
            name.text = self.name
            version = ET.SubElement(subroot, 'Version')
            version.text = self.version
            for meta in self.metadata:
                subroot.append(meta)
            for run in self.iterruns():
                lumiblocks = self.__grl[run]
                lbcol = ET.SubElement(subroot, 'LumiBlockCollection')
                runelement = ET.SubElement(lbcol, 'Run')
                runelement.text = str(run)
                for lumiblock in lumiblocks:
                    lbrange = ET.SubElement(lbcol, 'LBRange')
                    lbrange.set('Start', str(lumiblock[0]))
                    lbrange.set('End', str(lumiblock[1]))
            date = datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S")
            meta = (
            '''<!DOCTYPE LumiRangeCollection SYSTEM '''
            '''"http://atlas-runquery.cern.ch/LumiRangeCollection.dtd">\n'''
            '''<!-- This document was created by goodruns: '''
            '''http://pypi.python.org/pypi/goodruns/ on %s -->\n''' % date)
            tree = ET.ElementTree(root)
            if USE_LXML:
                filehandle.write('<?xml version="1.0"?>\n')
                filehandle.write(meta)
                tree.write(filehandle, pretty_print=True)
            else:
                # get pretty XML from ElementTree
                xml = minidom.parseString(meta +
                                          ET.tostring(tree.getroot(), 'utf-8'))
                filehandle.write(xml.toprettyxml(indent='   '))
        elif format in ('yml', 'yaml'):
            filehandle.write(yaml.dump(self.to_dict()))
        elif format == 'txt':
            filehandle.write(str(self) + '\n')
        elif format in ('py', 'python'):
            filehandle.write("grl = ")
            pprint(self.__grl, stream=filehandle)
        elif format == 'cut':
            filehandle.write(self.cut() + '\n')
        else:
            raise ValueError("Unrecognized grl format")
