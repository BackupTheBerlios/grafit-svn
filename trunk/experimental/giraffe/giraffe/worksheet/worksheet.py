import sys

from giraffe.common.signals import HasSignals
from giraffe.common.commands import command_from_methods
from giraffe.base.item import Item, wrap_attribute, register_class
from giraffe.worksheet.mkarray import MkArray

class Column(MkArray):
    def __init__(self, worksheet, ind):
        self.data = worksheet.data.columns[ind]
        self.worksheet = worksheet
        self.ind = ind
        MkArray.__init__(self, worksheet.data.columns, worksheet.data.columns.data, ind)

    def set_name(self, name):
        self.data.name = name
    def get_name(self):
        return self.data.name
    name = property(get_name, set_name)

    def __coerce__(self, other):
        print >>sys.stderr, self, other

class Worksheet(Item, HasSignals):
    def __init__(self, project, name=None, parent=None, location=None):
        Item.__init__(self, project, name, parent, location)

        self.columns = []

        if location is not None:
            for i in range(len(self.data.columns)):
                self.columns.append(Column(self, i))

    def add_column(self, name):
        ind = self.data.columns.append([name, ''])
        self.columns.append(Column(self, ind))
        return name

    def add_column_undo(self, name):
        ind = self.data.columns.find(name=name)
        self.data.columns.delete(ind)
        del self.columns[ind]

    add_column = command_from_methods('worksheet_add_column', add_column, add_column_undo)


    def remove_column(self, name):
        ind = self.data.columns.find(name=name)
        if ind == -1:
            raise NameError, "Worksheet does not have a column named %s" % name
        else:
            col = self.columns[ind]
            del self.columns[ind]
            return (col, ind), None

    def undo_remove_column(self, c):
        print >>sys.stderr, c
        col, ind = c
        self.columns.insert(ind, col)

    remove_column = command_from_methods('worksheet_remove_column', remove_column, undo_remove_column)


    def get_ncolumns(self):
        return len(self.columns)
    ncolumns = property(get_ncolumns)

    def get_nrows(self):
        try:
            return max([len(c) for c in self.columns])
        except ValueError:
            return 0
    nrows = property(get_nrows)


    def __getitem__(self, key):
        if isinstance(key, int):
            return self.columns[key]
        elif isinstance(key, basestring) and key in self.column_names:
            return self.columns[self.column_names.index(key)] 
        else:
            raise IndexError

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.columns[key][:] = value
        elif isinstance(key, basestring) and key in self.column_names:
            self.columns[self.column_names.index(key)][:] = value
        else:
            raise IndexError

    def __repr__(self):
        return '<Worksheet %s%s>' % (self.name, '(deleted)'*self.id.startswith('-'))
        

    def get_column_names(self):
        return [c.name for c in self.columns]
    column_names = property(get_column_names)

    def set_name(self, n):
        self._name = n
        self.emit('rename', n, item=self)
    def get_name(self):
        return self._name
    name = property(get_name, set_name)

    _name = wrap_attribute('name')
    parent = wrap_attribute('parent')

register_class(Worksheet, 'worksheets[name:S,id:S,parent:S,columns[name:S,data:B]]')
