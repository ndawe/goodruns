import lxml.etree as ET
import copy
import urllib2
from pprint import pprint
from operator import add, sub, or_, and_, xor, itemgetter

use_yaml = True
try:
    import yaml
except:
    use_yaml = False


def clipped(grl, startrun=None, startlb=None, endrun=None, endlb=None):

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
    Return the XOR of multuple GRLs: A ^ B ^ C...
    """
    return reduce(xor, args)


def _lbrange_intersects(lbrange1, lbrange2):

    if lbrange1[0] >= lbrange2[0] and lbrange1[0] <= lbrange2[1]:
        return True
    if lbrange1[1] >= lbrange2[0] and lbrange1[1] <= lbrange2[1]:
        return True
    return False


def _lbrange_as_set(lbrange):

    return set(range(lbrange[0], lbrange[1] + 1))


class GRL(object):

    def __init__(self, grl=None):

        self.__grl = {}
        if not grl:
            return
        if type(grl) is dict:
            self.__grl = grl
        elif type(grl) in [str, file]:
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
                    for lb in lbs:
                        self.insert(run,
                            (int(lb.attrib['Start']), int(lb.attrib['End'])))
            elif filename.endswith('.yml'):
                if use_yaml:
                    self.__grl = yaml.load(grl)
                else:
                    raise ImportError("PyYAML module not found")
            else:
                raise ValueError(
                    "File %s is not recognized as a valid GRL format"
                    % filename)
            for run in self.iterruns():
                self.__optimize(run)

    def __copy__(self):

        return copy.deepcopy(self)

    def __repr__(self):

        return self.__str__()

    def __str__(self):

        output = ""
        for run in sorted(self.iterruns()):
            lbranges = self.__grl[run]
            maxlength = max([len(str(lbrange[0])) for lbrange in lbranges])
            output += '-' * 15 + '\n'
            output += "RUN: %i\n" % run
            output += "LUMIBLOCKS:\n"
            for lbrange in lbranges:
                if lbrange[0] == lbrange[1]:
                    output += ("  %%-%ds" % maxlength + "\n") % lbrange[0]
                else:
                    output += ("  %%-%ds" % maxlength + " - %i\n") % lbrange
        return output

    def __getitem__(self, run):

        return self.__grl[run]

    def __delitem__(self, run):

        del self.__grl[run]

    def __contains__(self, runlb):
        """
        Pass the tuple (run, lbn)
        """
        if self.has_run(runlb[0]):
            lbranges = self[runlb[0]]
            for lbrange in lbranges:
                if runlb[1] >= lbrange[0] and runlb[1] <= lbrange[1]:
                    return True
        return False

    def __iter__(self):

        return iter(self.iterruns())

    def items(self):

        for run, lbranges in self.__grl.items():
            for lbrange in lbranges:
                yield (run, lbrange)

    def iterruns(self):

        for run in sorted(self.__grl.iterkeys()):
            yield run

    def has_run(self, run):

        return run in self.__grl

    def insert(self, run, lbrange):

        if self.has_run(run):
            if lbrange not in self[run]:
                self[run].append(lbrange)
            self.__optimize(run)
        else:
            self.__grl[run] = [lbrange]

    def remove(self, run, lbrange):

        if self.has_run(run):
            for mylbrange in self[run][:]:
                if lbrange[1] < mylbrange[0]:
                    continue
                if lbrange == mylbrange:
                    self[run].remove(mylbrange)
                    if len(self[run]) == 0:
                        del self[run]
                    break
                elif lbrange[0] > mylbrange[0] and lbrange[1] < mylbrange[1]:
                    # embedded: must split
                    left_lbrange = (mylbrange[0], lbrange[0] - 1)
                    right_lbrange = (lbrange[1] + 1, mylbrange[1])
                    index = self[run].index(mylbrange)
                    self[run][index] = left_lbrange
                    self[run].insert(index + 1, right_lbrange)
                elif _lbrange_intersects(lbrange, mylbrange):
                    diff = _lbrange_as_set(mylbrange).difference(
                        _lbrange_as_set(lbrange))
                    if not diff:  # empty set
                        self[run].remove(mylbrange)
                        if len(self[run]) == 0:
                            del self[run]
                            break
                        continue
                    newlbrange = (min(diff), max(diff))
                    self[run][self[run].index(mylbrange)] = newlbrange
                elif mylbrange[0] > lbrange[1]:
                    break

    def clip(self, startrun=None, startlb=None, endrun=None, endlb=None):

        for run in sorted(self.iterruns()):
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
                                    ] = (startlb, lbrange[1])
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
                                    ] = (lbrange[0], endlb)
                        if len(self[run]) == 0:
                            del self[run]

    def __optimize(self, run):
        """
        Sort and merge lumiblock ranges
        """
        if not self.has_run(run):
            return
        if len(self[run]) == 0:
            del self[run]
            return
        lbranges = sorted(self[run], key=itemgetter(0))
        if len(lbranges) > 1:
            first = 0
            last = len(lbranges) - 1
            while first != last:
                next = first + 1
                merged = False
                while next <= last:
                    if lbranges[first][1] >= lbranges[next][1]:
                        for index in range(first + 1, next + 1):
                            lbranges.pop(next)
                        merged = True
                        break
                    elif lbranges[first][1] + 1 >= lbranges[next][0]:
                        lbranges[first] = \
                            (lbranges[first][0], lbranges[next][1])
                        for index in range(first + 1, next + 1):
                            lbranges.pop(next)
                        merged = True
                        break
                    next += 1
                last = len(lbranges) - 1
                if not merged:
                    first += 1
            self.__grl[run] = lbranges

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

        try:
            cut = Cut()
            for run in self.iterruns():
                lbcut = Cut()
                for lbrange in self[run]:
                    lbcut |= (lbname + ">=%i&&" + lbname + "<=%i") % lbrange
                cut |= "(%s==%i)&&(%s)" % (runname, run, lbcut)
        except:
            cut = "install rootpy to enable conversion to a cut expression"
        return cut

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
                    lbrange.set("Start", str(lumiblock[0]))
                    lbrange.set("End", str(lumiblock[1]))
            tree = ET.ElementTree(root)
            tree.write(filehandle, pretty_print=True)
        elif format in ('yml', 'yaml'):
            filehandle.write(yaml.dump(self.__grl))
        elif format == 'txt':
            filehandle.write(str(self))
        elif format in ('py', 'python'):
            filehandle.write("grl = ")
            pprint(self.__grl, stream=filehandle)
        else:
            raise ValueError("Unrecognized grl format")