"""
Copied from:
    https://code.djangoproject.com/browser/django/
    trunk/django/utils/datastructures.py#L99
BSD license
"""

import copy
from types import GeneratorType
import bisect


class SortedDict(dict):
    """
    A dictionary that keeps its keys in the
    order in which they're inserted.
    """
    def __new__(cls, *args, **kwargs):

        instance = super(SortedDict, cls).__new__(cls, *args, **kwargs)
        instance.key_order = []
        return instance

    def __init__(self, data=None):

        if data is None:
            data = {}
        elif isinstance(data, GeneratorType):
            # Unfortunately we need to be able to read a generator twice.  Once
            # to get the data into self with our super().__init__ call and a
            # second time to setup key_order correctly
            data = list(data)
        super(SortedDict, self).__init__(data)
        if isinstance(data, dict):
            self.key_order = data.keys()
        else:
            self.key_order = []
            seen = set()
            for key, value in data:
                if key not in seen:
                    self.key_order.append(key)
                    seen.add(key)
        self.key_order.sort()

    def __deepcopy__(self, memo):

        return self.__class__([(key, copy.deepcopy(value, memo))
                               for key, value in self.iteritems()])

    def __setitem__(self, key, value):

        if key not in self:
            self.key_order.insert(bisect.bisect(self.key_order, key), key)
        super(SortedDict, self).__setitem__(key, value)

    def __delitem__(self, key):

        super(SortedDict, self).__delitem__(key)
        self.key_order.remove(key)

    def __iter__(self):

        return iter(self.key_order)

    def pop(self, k, *args):

        result = super(SortedDict, self).pop(k, *args)
        try:
            self.key_order.remove(k)
        except ValueError:
            # Key wasn't in the dictionary in the first place. No problem.
            pass
        return result

    def popitem(self):

        result = super(SortedDict, self).popitem()
        self.key_order.remove(result[0])
        return result

    def items(self):

        return zip(self.key_order, self.values())

    def iteritems(self):

        for key in self.key_order:
            yield key, self[key]

    def keys(self):

        return self.key_order[:]

    def iterkeys(self):

        return iter(self.key_order)

    def values(self):

        return map(self.__getitem__, self.key_order)

    def itervalues(self):

        for key in self.key_order:
            yield self[key]

    def update(self, dict_):

        for k, v in dict_.iteritems():
            self[k] = v

    def setdefault(self, key, default):

        if key not in self:
            self.key_order.append(key)
        return super(SortedDict, self).setdefault(key, default)

    def copy(self):

        """Returns a copy of this object."""
        # This way of initializing the copy means it works for subclasses, too.
        obj = self.__class__(self)
        obj.key_order = self.key_order[:]
        return obj

    def __repr__(self):
        """
        Replaces the normal dict.__repr__ with a version that returns the keys
        in their sorted order.
        """
        return '{%s}' % ', '.join(['%r: %r' % (k, v) for k, v in self.items()])

    def clear(self):

        super(SortedDict, self).clear()
        self.key_order = []
