import sys
import time, random, socket, md5

from giraffe.signals import HasSignals

# by (Carl Free Jr. http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/213761)
def create_id(*args):
    """Generates a universally unique ID.
    Any arguments only create more randomness.
    """
    t = long(time.time() * 1000)
    r = long(random.random()*100000000000000000L)
    try:
        a = socket.gethostbyname(socket.gethostname())
    except:
        # if we can't get a network address, just imagine one
        a = random.random()*100000000000000000L
    data = str(t)+' '+str(r)+' '+str(a)+' '+str(args)
    data = md5.md5(data).hexdigest()
    return data

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
    """Base class for all items in a Project"""
    def __init__(self, project, name=None, parent=None, location=None):
        self.project = project

        if location is None:
            # this is a new item, not present in the database 
            # create an entry for it
            self.view, self.data, self.id = project._create(type(self))

            # we have to handle creation of the top folder as a special case
            # we cannot specify its parent when we create it!
            if hasattr(self, '_isroot') and self._isroot:
                parent = self

            # parent defaults to top-level folder
            # (XXX: should this be the current folder?)
            if parent is None:
                parent = self.project.top

            # initialize
            self.name = name
            self.parent = parent.id
        else:
            # this is an item already present in the database
            self.view, self.data, self.id = location

        # enter ourselves in the project dictionary
        self.project.items[self.id] = self

        # We have to emit the signal at the end
        # so the signal handlers can access wrapped attributes.
        # We can't emit in project.add()
        self.project.emit('add-item', self)


class Folder(Item, HasSignals):
    def __init__(self, project, name=None, parent=None, location=None, _isroot=False):
        # we have to handle creation of the top folder as a special case
        # since we cannot specify its parent when we create it. 
        # see Item.__init__
        self._isroot = _isroot
        self.project = project
        Item.__init__(self, project, name, parent, location)

    def contents(self):
        for desc in storage_desc.values():
            for row in self.project.db.getas(desc):
                if row.parent == self.id and row.id in self.project.items and row.id != self.id:
                    yield self.project.items[row.id]

    name = wrap_attribute('name')
    parent = wrap_attribute('parent')

    up = property(lambda self: self.parent)

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

register_class(Folder, 'folders[name:S,id:S,parent:S]')
