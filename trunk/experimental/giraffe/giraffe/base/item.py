from giraffe.common.commands import Command, command_list

storage_desc = {}

def register_class(cls, description):
    storage_desc[cls] = description

def wrap_attribute(name):
    def get_data(self):
        return getattr(self.data, name)
    def set_data(self, value):
        setattr(self.data, name, value)
    return property(get_data, set_data)

class NullFolder(object):
    id = None
    def contents(self):
        return iter([])
NullFolder = NullFolder()


class Item(object):
    def __init__(self, project, id=None):
        self.project = project
        self._update(id)

        # We have to emit the signal after calling _update()
        # so the signal handlers can access wrapped attributes.
        # We can't emit in project.add()
        self.project.emit('add-item', self)

    def _update(self, id):
        self.view, self.data, self.id = self.project.add(self, id)

class Folder(Item):
    def __init__(self, project, name=None, parent=None, id=None):
        Item.__init__(self, project, id=id)
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

    def on_add(self, item):
        if self.project.this is self:
            self.project._dict[item.name] = item

    name = wrap_attribute('name')
    parent = wrap_attribute('parent')

register_class(Folder, 'folders[name:S,id:S,parent:S]')
