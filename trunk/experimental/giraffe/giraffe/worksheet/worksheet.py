from giraffe.common.signals import HasSignals
from giraffe.base.item import Item, NullFolder, wrap_attribute, register_class
from giraffe.worksheet.mkarray import MkArray

class Column(MkArray):
    def __init__(self, worksheet, ind):
        self.data = worksheet.data.columns[ind]
        self.worksheet = worksheet
        self.ind = ind
        MkArray.__init__(self, worksheet.data.columns, worksheet.data.columns.data, ind)

class Worksheet(Item, HasSignals):
    def __init__(self, project, name=None, parent=NullFolder, id=None):
        Item.__init__(self, project, id)

        self.columns = []
        if id is None:
            self.name = name
            self.parent = parent.id
        else:
            for i in range(len(self.data.columns)):
                self.columns.append(Column(self, i))

    def add_column(self, name):
        ind = self.data.columns.append([name, ''])
        self.columns.append(Column(self, ind))

    def get_ncolumns(self):
        return len(self.columns)
    ncolumns = property(get_ncolumns)

    def get_nrows(self):
        try:
            return max([len(c) for c in self.columns])
        except ValueError:
            return 0
    nrows = property(get_nrows)

    def remove_column(self, name):
        ind = self.data.columns.find(name=name)
        if ind == -1:
            raise NameError, "Worksheet does not have a column named %s" % name
        else:
            self.data.columns.delete(ind)

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
        

    def get_column_names(self):
        return [c.name for c in self.data.columns]
    column_names = property(get_column_names)

    name = wrap_attribute('name')
    parent = wrap_attribute('parent')

register_class(Worksheet, 'worksheets[name:S,id:S,parent:S,columns[name:S,data:B]]')
