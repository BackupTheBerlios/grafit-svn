from arrays import *

from items import Item, WithId

import common.commands
import common.signals

"""
A Worksheet contains Columns.

A Column is a VarArray which has a name, belongs to a Worksheet
and keeps track of changes to itself by registering Commands
and emitting signals.
"""

common.commands.Command.command_list = common.commands.CommandList()

class U(object):
    def __div__(self, other):
        return WithId.get(other)
U = U()

class worksheet_add_column(common.commands.Command):
    def __init__(self, worksheet, name):
        self.worksheet, self.name = worksheet, name

    def do(com):
        self = U/com.worksheet
        self.columns.append(Column(self, com.name))

    def undo(com):
        self = U/com.worksheet
        self.worksheet.remove_column(self, com.name)

class worksheet_remove_column(common.commands.Command):
    def __init__(self, worksheet, name):
        self.worksheet, self.name = worksheet, name

    def do(com):
        self = U/com.worksheet
        del self.columns[[c.name for c in self.columns].index(name)]

    def undo(com):
        self = U/com.worksheet

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

class Worksheet(Item, WithId):
    def __init__(self):
        Item.__init__(self, '', None)
        self.register()
        self.columns = []
    
    def get_ncolumns(self):
        return len(self.columns)
    ncolumns = property(get_ncolumns)

    def get_nrows(self):
        return max([len(c) for c in self.column])
    nrows = property(get_nrows)

    def add_column(self, name):
        worksheet_add_column(self.uuid, name).do_and_register()

    def remove_column(self, name):
        worksheet_add_column(self.uuid, name).do_and_register()

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
import pickle
print pickle.dumps(w.Star.data)
