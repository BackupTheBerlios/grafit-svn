import sys
import re
import time, random, socket, md5

import metakit

from giraffe.commands import command_from_methods, command_list
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

            if name is None:
                name = self.create_name(parent)
            if not self.check_name(name, parent):
                raise NameError
 
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

    def check_name(self, name, parent):
        if not re.match('^[a-zA-Z]\w*$', name):
            return False
        if name in [i.name for i in parent.contents()]:
            return False
        return True

    def create_name(self, parent):
        for i in xrange(sys.maxint):
            name = self.default_name_prefix+str(i)
            if self.check_name(name, parent):
                return name

    default_name_prefix = 'item'


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

    default_name_prefix = 'folder'

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

class Project(HasSignals):
    def __init__(self, filename=None):
        self.filename = filename

        if self.filename is None:
            # We initially create an in-memory database.
            # When we save to a file, we will reopen the database from the file.
            self.db = metakit.storage()
        else:
            self.db = metakit.storage(self.filename, 1)

        self.cleanup()

        self._modified = False

        command_list.connect('added', self.on_command_added)

        self.items = {}
        self.deleted = {}
        self._dict = {}
        self.save_dict = {}

        # Create top folder.
        # - it must be created before all other items
        # - it must be created with _isroot=True, to set itself as its parent folder
        try:
            fv = self.db.getas(storage_desc[Folder])
            row = fv.select(name='top')[0]
            self.top = self.items[row.id] = Folder(self, location=(fv, row, row.id), _isroot=True)
        except IndexError:
            # can't find it in the database, create a new one.
            self.top = Folder(self, 'top', _isroot=True)

        self.here = self.top
        self.this = None

        # create objects
        for cls, desc in [(i, storage_desc[i]) for i in (Folder, giraffe.worksheet.Worksheet, giraffe.graph.Graph)]:
            view = self.db.getas(desc)
            for i, row in enumerate(view):
                if row.id != self.top.id:
                    if not row.id.startswith('-'):
                        print 'loading', cls, row.id,
                        self.items[row.id] = cls(self, location=(view, row, row.id))
                        print 'end'
                    else:
                        self.deleted[row.id] = cls(self, location=(view, row, row.id))


    def on_command_added(self, command=None):
        self.modified = True

    def cd(self, folder):
        # restore dictionary
        for o in self.here.contents():
            try:
                del self._dict[o.name]
            except KeyError:
                pass
        self._dict.update(self.save_dict)
        self._save_dict = {}
        
        self.here = folder

        # update dictionary
        self._dict['here'] = self.here
        self._dict['up'] = self.here.up
        for o in self.here.contents():
            if o.name in self._dict:
                self._save_dict[o.name] = self._dict[o.name]
            self._dict[o.name] = o

        self.emit('change-current-folder', folder)

    def set_current(self, obj):
        if obj not in list(self.here.contents()):
            raise NotImplementedError
        self.this = obj
        self._dict['this'] = self.this
        self.emit('set-current-object', obj)

    def set_dict(self, d):
        self._dict = d

        self._dict['top'] = self.top
        self._dict['this'] = self.this
        self.cd(self.here)

    def unset_dict(self):
        for o in self.here.contents():
            if o.name in self._dict:
                self._save_dict[o.name] = self._dict[o.name]
            self._dict[o.name] = o

    def cleanup(self):
        """Purge all deleted items from the database"""
        for cls, desc in storage_desc.iteritems():
            view = self.db.getas(desc)
            for i, row in enumerate(view):
                if row.id.startswith('-'):
                    view.delete(i)

    def _create(self, cls):
        """Create a new entry a new item of class `cls` in the database

        This method is called from the constructor of all `Item`-derived
        classes, if the item is not already in the database.
        Returns the view, row and id of the new item.
        """
        try:
            view = self.db.getas(storage_desc[cls])
        except KeyError:
            raise TypeError, "project cannot create an item of type '%s'" % cls

        id = create_id()
        row = view.append(id=id)
        data = view[row]

        return view, data, id

    # new ##################################

    def new(self, cls, *args, **kwds):
        obj = cls(self, *args, **kwds)
        self.items[obj.id] = obj
        if obj.parent is self.top:
            self._dict[obj.name] = obj
        # don't emit 'add-item' because it is emitted by Item.__init__
        return obj, obj

    def new_undo(self, obj):
        del self.items[obj.id]
        obj.id = '-'+obj.id
        self.deleted[obj.id] = obj
        if obj.parent is self.top and obj.name in self._dict:
            del self._dict[obj.name] 
        self.emit('remove-item', obj)

    def new_redo(self, obj):
        del self.deleted[obj.id]
        obj.id = obj.id[1:]
        self.items[obj.id] = obj
        if obj.parent is self.top:
            self._dict[obj.name] = obj
        self.emit('add-item', obj)

    def new_cleanup(self, obj):
        if obj.id in self.deleted:
            del self.deleted[obj.id]
        obj.view.remove(obj.view.select(id=obj.id))

    new = command_from_methods('project_new', new, new_undo, new_redo, new_cleanup)

    # remove ###############################

    def remove(self, id):
        obj = self.items[id]
        ind = obj.view.find(id=id)

        if obj.name in self._dict and obj.name in self._dict:
            del self._dict[obj.name]

        if ind == -1:
            raise NameError
        else:
            del self.items[id]
            obj.id = '-'+obj.id 
            self.deleted[obj.id] = obj

        self.emit('remove-item', obj)
        return id

    def remove_undo(self, id):
        obj = self.deleted['-'+id]
        ind = obj.view.find(id=obj.id)

        del self.deleted[obj.id]
        obj.id = obj.id[1:]
        self.items[obj.id] = obj

        if obj.parent is self.top:
            self._dict[obj.name] = obj
        self.emit('add-item', obj)

    remove = command_from_methods('project_remove', remove, remove_undo)


    # Shortcuts for creating and removing folders
        
    def mkfolder(self, path, parent=None):
        self.new(Folder, path, parent)

    def rmfolder(self, path):
        if path in self.here:
            self.remove(self.here[path].id)
        else:
            raise NameError, "folder '%s' does not exist" % path

    def commit(self):
        self.db.commit()
        self.modified = False

    def saveto(self, filename):
        try:
            f = open(filename, 'wb')
            self.db.save(f)
        finally:
            f.close()
            self.modified = False

    def get_modified(self):
        return self._modified
    def set_modified(self, value):
        if value and not self._modified:
            self.emit('modified')
        elif self._modified and not value:
            self.emit('not-modified')
        self._modified = value
    modified = property(get_modified, set_modified)

# import only in order to register object types
import giraffe.worksheet
import giraffe.graph
