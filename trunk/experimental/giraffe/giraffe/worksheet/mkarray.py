import sys
import time
import struct

import metakit
from numarray import *
from numarray.ieeespecial import nan

class MkArray(object):
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

        # adjust size
        if start > self.length:
            buf = array([nan]*(start-self.length), type=Float64).tostring()
            self.view.modify(self.prop, self.row, buf, self.length*8)
        
        arr = asarray(value, typecode=Float64)
        if arr.shape == ():
            arr = asarray([value]*length, typecode=Float64)
        buf = arr.tostring()

        if isinstance(key, slice) and key.start is None and key.stop is None:
            setattr(self.view[self.row], self.prop.name, buf)
        else:
            self.view.modify(self.prop, self.row, buf, start * 8)


    def get_length(self):
        return self.view.itemsize(self.prop, self.row)/8
    length = property(get_length)

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        # integer and (non-extended) slice keys supported
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


