from arrays import *

from items import Item, WithId, Persistent
from common.commands import Command, CommandList
from common.signals import HasSignals
from lib.ElementTree import Element

Command.command_list = CommandList()

class U(object):
    def __div__(self, other):
        return WithId.get(other)
U = U()

class worksheet_add_column(Command):
    def __init__(self, worksheet, name):
        self.worksheet, self.name = worksheet, name

    def do(com):
        self = U/com.worksheet
        self.columns.append(Column(self, com.name))

    def undo(com):
        self = U/com.worksheet
        self.remove_column(com.name)

class worksheet_remove_column(Command):
    def __init__(self, worksheet, name):
        self.worksheet, self.name = worksheet, name

    def do(com):
        self = U/com.worksheet
        ind = [c.name for c in self.columns].index(com.name)
        com.column = self.columns[ind].to_element()
        del self.columns[ind]

    def undo(com):
        self = U/com.worksheet
        c = Persistent.create(com.column)
        self.columns.append(c)

class column_change_data(Command):
    def __init__(self, worksheet, name, key, value):
        self.worksheet, self.name, self.key, self.value = worksheet, name, key, value

    def do(com):
        self = getattr(U/com.worksheet, com.name)
        com.old_value = self[com.key]
        VarArray.__setitem__(self, com.key, com.value)

    def undo(com):
        self = getattr(U/com.worksheet, com.name)
        self[com.key] = com.old_value



class Column(VarArray, HasSignals, Persistent):
    def __init__(self, worksheet, name):
        VarArray.__init__(self)
        self.worksheet = worksheet
        self.name = name

    def set_name(self, name):
        self._name = name
    def get_name(self):
        return self._name
    name = property(get_name, set_name)

    def to_element(self):
        e = Element('Column', name=self.name)
        e.text = self.data.tostring()
        return e

    def from_element(element, parent):
        c = Column(parent, element.get('name'))
        c.data = fromstring(element.text, Float64)
        return c
    from_element = staticmethod(from_element)

    def __setitem__(self, key, value):
        column_change_data(self.worksheet.uuid, self.name, key, value).do_and_register()

    def __repr__(self):
        return VarArray.__repr__(self)

    _element_name = 'Column'

class Worksheet(Item, WithId, Persistent):
    def __init__(self, name, parent):
        Item.__init__(self, name, parent)
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
        worksheet_remove_column(self.uuid, name).do_and_register()

    def __getattr__(self, name):
        if 'columns' in self.__dict__ and name in [c.name for c in self.columns]:
            return self.columns[[c.name for c in self.columns].index(name)]
        else:
#           return __getattr__(self, name)
            return self.__dict__[name]

    def __setattr__(self, name, value):
        if 'columns' in self.__dict__ and name in [c.name for c in self.columns]:
            getattr(self, name)[:] = value
        else:
            return object.__setattr__(self, name, value)

    def __getitem__(self, key):
        return self.columns[self.column_names.index(key)] 

    def __setitem__(self, key, value):
        if key in self.column_names:
            self.columns[self.column_names.index(key)][:] = value
        
    def get_column_names(self):
        return [c.name for c in self.columns]
    column_names = property(get_column_names)
        
    def __str__(self):
        s = "Worksheet:"
        for c in self.columns:
            s += '\n   ' + c.name + ": " + str(c)
        return s

    def to_element(self):
        elem = Element('Worksheet', name=self.name, uuid=self.uuid)
        return elem

    def from_element(element, parent):
        w = Worksheet(element.get('name'), parent)
        w.uuid = element.get('uuid')
        return w
    from_element = staticmethod(from_element)

if __name__ == '__main__':
    w = Worksheet('test', None)
    w.add_column('A')
    w.add_column('Star')
    w.Star[4] = 13
    w.A[4] = 23
    w.Star = [1,2,4,5,5,5,6,7]
    print w
    Command.command_list.undo()
    print w
