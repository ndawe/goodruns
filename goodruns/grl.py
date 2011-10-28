# Author: E. Noel Dawe <Noel.Dawe@cern.ch>

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

import copy
import urllib2
from pprint import pprint
from operator import sub, or_, and_, xor, itemgetter
from .sorteddict import SortedDict
import bisect


def clipped(grl, startrun=None, startlb=None, endrun=None, endlb=None):
    """
    Clip a GRL between startrun, startlb and endrun, endlb (inclusive)
    """
    grl_copy = copy.deepcopy(grl)
    grl_copy.clip(startrun=startrun, startlb=startlb,
                  endrun=endrun, endlb=endlb)
    return grl_copy


def diffed(*args):
    """
    Return the difference of multiple GRLs: (((A-B)-C)-D)...)
    """
    return reduce(sub, args)


def ored(*args):
    """
    Return the OR of multiple GRLs: A | B | C...
    """
    return reduce(or_, args)


def anded(*args):
    """
    Return the AND of multiple GRLs: A & B & C...
    """
    return reduce(and_, args)


def xored(*args):
    """
    Return the XOR of multiple GRLs: A ^ B ^ C...
    """
    return reduce(xor, args)


def _lbrange_intersects(lbrange1, lbrange2):
    """
    Determine if two lumiblock ranges intersect
    """
    if lbrange1[0] >= lbrange2[0] and lbrange1[0] <= lbrange2[1]:
        return True
    if lbrange1[1] >= lbrange2[0] and lbrange1[1] <= lbrange2[1]:
        return True
    if lbrange2[0] >= lbrange1[0] and lbrange2[0] <= lbrange1[1]:
        return True
    if lbrange2[1] >= lbrange1[0] and lbrange2[1] <= lbrange1[1]:
        return True
    return False


def _lbrange_as_set(lbrange):
    """
    Convert lumiblock range to set of lumiblocks
    """
    return set(range(lbrange[0], lbrange[1] + 1))


def _dict_to_grl(d):
    """
    Convert tuples to LumiblockRanges
    """
    o = {}
    for run, lbranges in d.items():
        o[run] = [LumiblockRange(a) for a in lbranges]
    return o


def _grl_to_dict(g):
    """
    Convert tuples to LumiblockRanges
    """
    o = {}
    for run in g.iterruns():
        lbranges = g[run]
        o[run] = [(a[0], a[1]) for a in lbranges]
    return o


class LumiblockRange(tuple):
    """
    A 2-tuple consisting of the lower and upper
    bounds of a lumiblock range
    """
    def __new__(cls, args):

        if len(args) != 2:
            raise ValueError('lbrange must contain exactly 2 elements: %s' % \
                             (args,))
        for lumiblock in args:
            if not isinstance(lumiblock, int):
                raise TypeError('lbrange must contain integers only')
        if args[0] > args[1]:
            raise ValueError('lbrange in wrong order: %s' % (args,))

        return super(LumiblockRange, cls).__new__(cls, args)

    def __cmp__(self, lumiblock):

        if lumiblock < self[0]:
            return 1
        if lumiblock > self[1]:
            return -1
        return 0


class GRL(object):
    """
    The main GRL class holds a python dictionary
    mapping runs to a list of lumiblock ranges (2-tuples)
    """
    def __init__(self, grl=None):
        """
        grl may be a file name or URL of a valid GRL file, or None
        """
        self.__grl = SortedDict()
        if not grl:
            return
        if isinstance(grl, dict):
            self.__grl = SortedDict(_dict_to_grl(grl))
            return
        if type(grl) in [str, file]:
            filename = grl
            if type(grl) is str:
                if grl.startswith("http://"):
                    grl = urllib2.urlopen(grl)
            elif type(grl) is file:
                filename = grl.name
            if filename == "<stdin>" or filename.endswith('.xml') or \
                    filename.startswith("http://"):
                tree = ET.parse(grl)
                lbcols = tree.getroot().findall(
                    'NamedLumiRange/LumiBlockCollection')
                for lbcol in lbcols:
                    run = int(lbcol.find('Run').text)
                    lbs = lbcol.findall('LBRange')
                    for lumiblock in lbs:
                        self.insert(run,
                            LumiblockRange((int(lumiblock.attrib['Start']),
                                            int(lumiblock.attrib['End']))))
            elif filename.endswith('.yml'):
                if USE_YAML:
                    self.__grl = SortedDict(_dict_to_grl(grl))
                else:
                    raise ImportError("PyYAML module not found")
            else:
                raise ValueError(
                    "File %s is not recognized as a valid GRL format"
                    % filename)
            for run in self.iterruns():
                self.__grl[run].sort()
                self.__optimize(run)

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
        """
        return self.__grl[run]

    def __delitem__(self, run):
        """
        Remove run and associated lumiblock ranges from GRL
        """
        del self.__grl[run]

    def __contains__(self, runlb):
        """
        Pass the tuple (run, lbn)
        """
        run, lbn = runlb
        if run in self.__grl:
            lbranges = self.__grl[run]
            # Locate the LumiblockRange containing lbn
            i = bisect.bisect_left(lbranges, lbn)
            if i != len(lbranges) and lbranges[i] == lbn:
                return True
        return False

    def __iter__(self):
        """
        Iterate over runs in GRL
        """
        return iter(self.iterruns())

    def items(self):
        """
        Iterate over (run, lbranges) in GRL
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
        """
        return run in self.__grl

    def insert(self, run, lbrange):
        """
        Insert a lumiblock range into a run
        """
        if not isinstance(run, int):
            raise TypeError('run must be an integer')
        if not isinstance(lbrange, LumiblockRange):
            lbrange = LumiblockRange(lbrange)
        try:
            lbranges = self.__grl[run]
            i = bisect.bisect(lbranges, lbrange[0])
            lbranges.insert(i, lbrange)
            self.__optimize(run)
        except KeyError:
            self.__grl[run] = [lbrange]

    def remove(self, run, lbrange):
        """
        Remove a lumiblock range from a run
        """
        if run in self.__grl:
            if not isinstance(lbrange, LumiblockRange):
                lbrange = LumiblockRange(lbrange)
            lbranges = self.__grl[run]
            for mylbrange in lbranges[:]:
                if lbrange[1] < mylbrange[0]:
                    continue
                if lbrange == mylbrange:
                    lbranges.remove(mylbrange)
                    break
                elif lbrange[0] > mylbrange[0] and lbrange[1] < mylbrange[1]:
                    # embedded: must split
                    left_lbrange = LumiblockRange((mylbrange[0],
                                                   lbrange[0] - 1))
                    right_lbrange = LumiblockRange((lbrange[1] + 1,
                                                    mylbrange[1]))
                    index = lbranges.index(mylbrange)
                    lbranges[index] = left_lbrange
                    lbranges.insert(index + 1, right_lbrange)
                    break
                elif _lbrange_intersects(lbrange, mylbrange):
                    diff = _lbrange_as_set(mylbrange).difference(
                        _lbrange_as_set(lbrange))
                    if not diff:  # empty set
                        lbranges.remove(mylbrange)
                        if len(lbranges) == 0:
                            break
                        continue
                    newlbrange = LumiblockRange((min(diff), max(diff)))
                    lbranges[lbranges.index(mylbrange)] = newlbrange
                elif mylbrange[0] > lbrange[1]:
                    break
            if len(lbranges) == 0:
                del self.__grl[run]

    def clip(self, startrun=None, startlb=None, endrun=None, endlb=None):
        """
        Clip the GRL between startrun, startlb and endrun, endlb (inclusive)
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
                                    ] = LumiblockRange((startlb, lbrange[1]))
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
                                    ] = LumiblockRange((lbrange[0], endlb))
                        if len(self[run]) == 0:
                            del self[run]

    def __optimize(self, run):
        """
        Merge lumiblock ranges
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
                    lbranges[first] = LumiblockRange((lbranges[first][0],
                                                      lbranges[_next][1]))
                    for index in xrange(first + 1, _next + 1):
                        lbranges.pop(_next)
                    merged = True
                    break
                _next += 1
            last = len(lbranges) - 1
            if not merged:
                first += 1

    def __add__(self, other):

        grlcopy = copy.deepcopy(self)
        grlcopy += other
        return grlcopy

    def __iadd__(self, other):

        for run, lbrange in other.items():
            self.insert(run, lbrange)
        return self

    def __sub__(self, other):

        grlcopy = copy.deepcopy(self)
        grlcopy -= other
        return grlcopy

    def __isub__(self, other):

        for run, lbrange in other.items():
            self.remove(run, lbrange)
        return self

    def __and__(self, other):

        return self - (self - other)

    def __or__(self, other):

        return self + other

    def __xor__(self, other):

        return (self | other) - (self & other)

    def cut(self, runname='RunNumber', lbname='lbn'):
        """
        Convert this GRL into a TCut expression.
        This method is really meant to be a joke and should be of no use.
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

    formats = [
        'xml',
        'yml',
        'txt',
        'py',
        'cut'
    ]

    def write(self, filehandle, format='xml'):
        """
        Write the GRL in a specified format to the file object.
        """
        if format == 'xml':
            root = ET.Element('LumiRangeCollection')
            subroot = ET.SubElement(root, 'NamedLumiRange')
            for run in self.iterruns():
                lumiblocks = self.__grl[run]
                lbcol = ET.SubElement(subroot, 'LumiBlockCollection')
                runelement = ET.SubElement(lbcol, 'Run')
                runelement.text = str(run)
                for lumiblock in lumiblocks:
                    lbrange = ET.SubElement(lbcol, 'LBRange')
                    lbrange.set('Start', str(lumiblock[0]))
                    lbrange.set('End', str(lumiblock[1]))
            tree = ET.ElementTree(root)
            if USE_LXML:
                tree.write(filehandle, pretty_print=True)
            else:
                # get pretty XML from ElementTree
                xml = minidom.parseString(ET.tostring(tree.getroot()))
                filehandle.write(xml.toprettyxml(indent='   '))
        elif format in ('yml', 'yaml'):
            filehandle.write(yaml.dump(_grl_to_dict(self)))
        elif format == 'txt':
            filehandle.write(str(self) + '\n')
        elif format in ('py', 'python'):
            filehandle.write("grl = ")
            pprint(self.__grl, stream=filehandle)
        elif format == 'cut':
            filehandle.write(self.cut() + '\n')
        else:
            raise ValueError("Unrecognized grl format")
