import sys
import metakit
from giraffe.common.identity import register, lookup

class Project(object):
    def __init__(self, filename=None):
        self.filename = filename

        if self.filename is None:
            # We initially create an in-memory database.
            # When we save to a file, we will reopen the database from the file.
            self.db = metakit.storage()
        else:
            self.db = metakit.storage(self.filename, 1)

def wrap(name):
    def get_data(self):
        return getattr(self.row, name)
    def set_data(self, value):
        setattr(self.row, name, value)
    return property(get_data, set_data)


class Item(object):
    def __init__(self, project, id=None):
        self.project = project
        self.id = register(self, id)

        self._update_view()

    def _update_view(self):
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

    viewname = 'items'
    description = 'items[name:S,id:S]'
    name = wrap('name')

class Worksheet(Item):
    def __init__(self, project, name, id=None):
        Item.__init__(self, project, id)
        self.name = name

    def add_column(self, name):
        self.row.columns.append([name, ''])

    def get_column_names(self):
        return [c.name for c in self.row.columns]
    column_names = property(get_column_names)

    viewname = 'worksheets'
    description = 'worksheets[name:S,id:S,columns[name:S,data:B]]'
    
    name = wrap('name')

    


id = '34444444444'
        

p = Project('test.db')
i = Item(p, id)

w = Worksheet(p, "baka")
w.add_column('ass')
print w.column_names

print i.name
i.name  = 'square'
print i.name, i.id
p.db.commit()
        
"""
Project:
    container, encapsulates a metakit database
    has a flat structure, may contain several types of Items, each type corresponds to a view
"""

"""
Item:
    always associated with a Project
    data is stored in a row of a metakit view in a Project
    identified by uuid, (self.id)
"""
