import sys
print >>sys.stderr, 'starting...',

import metakit
import time
import struct
from numarray import *
from numarray.ieeespecial import nan

print >>sys.stderr, 'ok'

class MkArray(object):
    def __init__(self, view, prop, row, start=None, end=None):
        self.view, self.prop, self.row = view, prop, row
        self.start, self.end = start, end

    def __setitem__(self, key, value):
        """Set the column data.

        `key` can be:
            - an integer: change a single value
            - a slice: arr[i:j] change a range of values.
        `value` can be a scalar or a sequence.
        """

        if isinstance(key, int):
            start = key
            length = 1
        elif isinstance(key, slice):
            if key.start is None:
                start = 0
            else:
                start = key.start
            if key.stop is None:
                try:
                    length = len(value)
                except TypeError:
                    length = 1
            else:
                length = abs(key.start - key.stop)

        self.length = len(self.view.access(self.prop, self.row, 0))/8
        if start > self.length:
            buf = array([nan]*(start-self.length), type=Float64).tostring()
            self.view.modify(self.prop, self.row, buf, self.length*8)
        
        arr = asarray(value, typecode=Float64)
        if arr.shape == ():
            arr = asarray([value]*length, typecode=Float64)

        buf = arr.tostring()

        self.view.modify(self.prop, self.row, buf, start * 8)

    def __getitem__(self, key):
        self.length = len(self.view.access(self.prop, self.row, 0))/8
        if isinstance(key, int):
            if key >= self.length:
                return nan
            buf = self.view.access(self.prop, self.row, key*8, 8)
            value = struct.unpack('d', buf)[0]
        elif isinstance(key, slice):
            if key.start is None:
                start = 0
            else:
                start = key.start
            if key.stop is None:
                stop = start+self.length
            else:
                stop = key.stop
            buf = self.view.access(self.prop, self.row, start*8, (stop-start)*8)
            value = fromstring(buf, type=Float64)
        return value

    def __repr__(self):
        data = self[:]
        return repr(data).replace('nan', '--')


"""
a = MkArray(view, prop, col)

Supports at least:

a[n] = 134
a[n:m] = 2
a[n:m] = [3,4,5]    # sequence must have correct size

a[n]      # if n is out of range, returns nan
a[n:m]    # padded with nan's if out of range

slices have n < m, no extended slices. Missing values (a[:n]) allowed.
"""


db = metakit.storage('asshole', 1)
#v = db.getas('test[ass:B]')
#v.append(ass='')

v = db.view('test')

a = MkArray(v, v.ass, 0)

a[10000:10005] = 3.33
#a[0] = 13
#a[24]  = 5
#a[30:35] = arange(5)
print a
print a[31]

db.commit()
