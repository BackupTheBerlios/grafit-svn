from giraffe.base.item import Item, wrap_attribute, register_class
from giraffe.worksheet.mkarray import MkArray

class Column(MkArray):
    def __init__(self, worksheet, ind):
        self.data = worksheet.data.columns[ind]
        self.worksheet = worksheet
        self.ind = ind
        MkArray.__init__(self, worksheet.data.columns, worksheet.data.columns.data, ind)

class Worksheet(Item):
    def __init__(self, project, name=None, folder=None, id=None):
        Item.__init__(self, project, id)

        self.columns = []
        if id is None:
            self.name = name
            self.folder = folder
        else:
            for i in range(len(self.data.columns)):
                self.columns.append(Column(self, i))

    def add_column(self, name):
        ind = self.data.columns.append([name, ''])
        self.columns.append(Column(self, ind))

    def remove_column(self, name):
        ind = self.data.columns.find(name=name)
        if ind == -1:
            raise NameError, "Worksheet does not have a column named %s" % name
        else:
            self.data.columns.delete(ind)

    def __getitem__(self, key):
        return self.columns[self.column_names.index(key)]

    def __setitem__(self, key, value):
        self[key][:] = value

    def get_column_names(self):
        return [c.name for c in self.data.columns]
    column_names = property(get_column_names)

    name = wrap_attribute('name')
    folder = wrap_attribute('folder')

register_class(Worksheet, 'worksheets[name:S,id:S,folder:S,columns[name:S,data:B]]')
