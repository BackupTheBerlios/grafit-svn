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

    name = wrap('name')

    viewname = 'items'
    description = 'items[name:S,id:S]'

id = '34444444444'
        

p = Project('test.db')
i = Item(p, id)

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

"""
Folders and paths:
    Folders are implemented as a type of Item.
    folder[name:S,id:S,parent:S]
    item[name:S,id:S,parent:S,other_data...]

    Paths: project.get(path)
"""
