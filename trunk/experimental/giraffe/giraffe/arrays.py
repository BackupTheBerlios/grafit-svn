"""
VarArray framework.

All simple operations in giraffe are done on these VarArrays,
which are 1-d arrays of floats with undefined length.

For anything more complicated, we can interface to Numarray
usings VarArray.data
"""

from numarray import *
from numarray.ieeespecial import nan

class VarOperation(object):
    def __init__(self, oper):
        self.oper = oper

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.oper, attr)

    def __call__(self, a, b=None):
        if self.oper.arity == 1:
            try:
                length = len(a)
            except TypeError:
                return self.oper(a)
            else:
                r = VarArray()
                r[:length] = self.oper(a)
                return r
        elif self.oper.arity == 2:
            try:
                length = min(len(a), len(b))
            except TypeError:
                return self.oper(a, b)
            else:
                return self.oper(a[:length], b[:length])

mod_ufuncs = dict([(k, VarOperation(v)) for k, v in ufunc._UFuncs.iteritems() if v.arity in (1,2)])
globals().update(mod_ufuncs)

class VarArray(object):
    def __init__(self):
        self.data = array(shape=(0,), type=Float64)

    def __setitem__(self, key, value):
        """
        Works like regular __setitem__ for arrays but
        grows the array for out-of-bounds indices.
        """
        if type(key) is int:
            length = key+1
        elif type(key) is slice:
            length = max(key.start, key.stop)
        elif hasattr(key, '__len__'):
            length = max(key)+1
        self._extend(length)
        self.data[key] = value
        
    def __getitem__(self, key):
        """
        Works like regular __getitem__ for arrays but
        substitutes nan for out-of-bounds indices.
        Supports integer and slice keys.
        """
        if type(key) is int:
            try:
                return self.data[key]
            except IndexError:
                return nan
        elif type(key) is slice:
            if key.start is None: start = 0
            else: start = key.start

            if key.stop is None: stop = len(self.data)
            else: stop = key.stop

            fr = min(start, stop)
            to = max(start, stop)
            l  = len(self.data)

            if to <= l and fr <= l:
                return self.data[key]
            else:
                val = array(shape=(to-fr,), type=Float64)
                val[:l-fr] = self.data[fr:]
                val[l-fr:] = nan
                return val[start-fr:stop-start:key.step]

    def _extend(self, length):
        oldlen = len(self.data)
        self.data.resize(length)
        self.data.shape = (length,)
        self.data[oldlen:] = nan

    def __add__(self, other): return add(self, other)
    def __sub__(self, other): return subtract(self, other)

    def __len__(self):
        return len(self.data)

c = VarArray()
c[10:15] = 244
c[[1,2,5]] = [1,2,5]
#c[115] = 2
c2 = VarArray()
c2[0:4] = [1,2,3,4]
print sin(c)+sin(c2)
print c-c2
