import sys

import metakit

from giraffe.common.identity import register
from giraffe.base.mkarray import MkArray

def wrap_mk_attribute(name):
    def get_data(self):
        return getattr(self.row, name)
    def set_data(self, value):
        setattr(self.row, name, value)
    return property(get_data, set_data)


class Item(object):
    def __init__(self, project, id=None):
        self.project = project
        self.id = register(self, id)

        # create or get the view
        if self.viewname in self.project.db.contents().properties().keys():
            self.view = self.project.db.view(self.viewname)
        else:
            self.view = self.project.db.getas(self.description)

        # get the row
        try:
            self.row = self.view.select(id=self.id)[0]
        except IndexError:
            self.view.append(id=self.id)
            self.row = self.view.select(id=self.id)[0]

        self.project.register(self)

    viewname = 'items'
    description = 'items[name:S,id:S]'
    name = wrap_mk_attribute('name')


class Column(MkArray):
    def __init__(self, worksheet, ind):
        self.row = worksheet.row.columns[ind]
        self.worksheet = worksheet
        self.ind = ind
        MkArray.__init__(self, worksheet.row.columns, worksheet.row.columns.data, ind)


class Worksheet(Item):
    def __init__(self, project, name, id=None):
        Item.__init__(self, project, id)
        self.name = name
        self.columns = []

    def add_column(self, name):
        ind = self.row.columns.append([name, ''])
        self.columns.append(Column(self, ind))

    def remove_column(self, name):
        ind = self.row.columns.find(name=name)
        if ind == -1:
            raise NameError, "Worksheet does not have a column named %s" % name
        else:
            self.row.columns.delete(ind)

    def __getitem__(self, key):
        return self.columns[self.column_names.index(key)]

    def get_column_names(self):
        return [c.name for c in self.row.columns]
    column_names = property(get_column_names)

    viewname = 'worksheets'
    description = 'worksheets[name:S,id:S,columns[name:S,data:B]]'
    name = wrap_mk_attribute('name')


class Project(object):
    def __init__(self, filename=None):
        self.filename = filename

        if self.filename is None:
            # We initially create an in-memory database.
            # When we save to a file, we will reopen the database from the file.
            self.db = metakit.storage()
        else:
            self.db = metakit.storage(self.filename, 1)

        self.items = {}

    def register(self, item):
        self.items[item.id] = item

    def remove(self, id):
        obj = self.items[id]
        ind = obj.view.find(id=id)
        if ind == -1:
            raise NameError
        else:
#            obj.view.delete(ind)
            obj.row.id = obj.id = '-'+obj.id 
            del self.items[id]

    def dump(self):
        itemviews = [ 'worksheets', 'items' ]
        ids = []
        for n in itemviews:
           ids.append([r.id for r in self.db.view(n)])