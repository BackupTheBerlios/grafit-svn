from giraffe.common.commands import Command, command_list
import sys

# The layout of the metakit project database.
# For each type of object (worksheet, graph etc) we call
# register_class(class, metakit_desc)
storage_desc = {}

def register_class(cls, description):
    storage_desc[cls] = description

def wrap_attribute(name):
    """Wrap a metakit column in a class attribute.
    
    If the wrapped attribute is an id of an object in project.items,
    it is wrapped with an attribute referencing the object.
    """
    def get_data(self):
        value = getattr(self.data, name)
        if value in self.project.items:
            value = self.project.items[value]
        return value

    def set_data(self, value):
        if hasattr(value, 'id') and value in self.project.items.values():
            value = value.id
        setattr(self.data, name, value)
    return property(get_data, set_data)


class Item(object):
    def __init__(self, project, name=None, parent=None, location=None):
        self.project = project

        if location is None:
            self.view, self.row, self.data, self.id = project.create(type(self))
        else:
            self.view, self.row, self.data, self.id = location

        self.project.items[self.id] = self

        if location is None:
            if hasattr(self, '_isroot') and self._isroot:
                folder = self
            elif parent is None:
                folder = self.project.top

            self.name = name
            self.parent = folder

        if (not (hasattr(self, '_isroot') and self._isroot)) and self.parent is self.project.top:
            self.project._dict[self.name] = self

        # We have to emit the signal after calling _update()
        # so the signal handlers can access wrapped attributes.
        # We can't emit in project.add()
        self.project.emit('add-item', self)

#    def _update(self, id):
#        self.view, self.data, self.id = self.project.add(self, id)


class Folder(Item):
    def __init__(self, project, name=None, parent=None, id=None, _isroot=False, location=None):
        self._isroot = _isroot
        Item.__init__(self, project, name, parent, id)
        self.project = project

    def contents(self):
        for desc in storage_desc.values():
            for row in self.project.db.getas(desc):
                if row.parent == self.id and not row.id.startswith('-'):
                    yield self.project.items[row.id]

    def __getitem__(self, key):
        cn = [i.name for i in self.contents()]
        ci = [i.id for i in self.contents()]

        if key in cn:
            return self.project.items[ci[cn.index(key)]]
        else:
            raise KeyError, "item '%s' does not exist" % key

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __repr__(self):
        return '<Folder %s>' % self.name

    name = wrap_attribute('name')
    parent = wrap_attribute('parent')

register_class(Folder, 'folders[name:S,id:S,parent:S]')
