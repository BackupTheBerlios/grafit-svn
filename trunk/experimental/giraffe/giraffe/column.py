from arrays import *

import common.commands
import common.signals

"""
A Worksheet contains Columns.

A Column is a VarArray which has a name, belongs to a Worksheet
and keeps track of changes to itself by registering Commands
and emitting signals.
"""

class Column(VarArray, common.signals.HasSignals):
    def __init__(self, worksheet, name):
        VarArray.__init__(self)
        self.worksheet = worksheet
        self.name = name

    def set_name(self, name):
        self._name = name
    def get_name(self):
        return self._name
    name = property(get_name, set_name)

    def __repr__(self):
        return VarArray.__repr__(self)

class Worksheet(object):
    def __init__(self):
        self.columns = []
    
    def get_ncolumns(self):
        return len(self.columns)
    ncolumns = property(get_ncolumns)

    def get_nrows(self):
        return max([len(c) for c in self.column])
    nrows = property(get_nrows)

    def add_column(self, name):
        self.columns.append(Column(self, name))

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        elif name in [c.name for c in self.columns]:
            return self.columns[[c.name for c in self.columns].index(name)]

    def __str__(self):
        s = "Worksheet:"
        for c in self.columns:
            s += '\n   ' + c.name + ": " + str(c)
        return s


w = Worksheet()
w.add_column('A')
w.add_column('V')
w.add_column('Star')

s = w.Star
s[4] = 13
w.A[4] = 23
print w.Star + array([1,2,3,4,5,6,7,])
print sin(w.Star) + sin(array([1,2,3,4,5,6,7,]))
print w.A[1333]
print w
