from giraffe.base.item import Item, wrap_attribute, register_class, storage_desc

class Folder(Item):
    def __init__(self, project, name=None, parent=None, id=None):
        Item.__init__(self, project, id)
        self.project = project

        if id is None: # new item
            self.name = name
        else: # existing item
            pass

    def contents(self):
        for desc in storage_desc.values():
            for row in self.project.db.getas(desc):
                if row.parent == self.id and not row.id.startswith('-'):
                    yield self.project.items[row.id]

    name = wrap_attribute('name')

register_class(Folder, 'folders[name:S,id:S,parent:S]')
