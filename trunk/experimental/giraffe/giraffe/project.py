import metakit

from giraffe.commands import command_from_methods, command_list
from giraffe.signals import HasSignals
from giraffe.item import Item, Folder, storage_desc, create_id

# import only in order to register object types
import giraffe.worksheet
import giraffe.graph

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
        for cls, desc in storage_desc.iteritems():
            view = self.db.getas(desc)
            for i, row in enumerate(view):
                if row.id != self.top.id:
                    if not row.id.startswith('-'):
                        self.items[row.id] = cls(self, location=(view, row, row.id))
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
        """Create an entry for a new item of class `cls` in the database

        This method is called from the constructor of all `Item`-derived
        classes, if the item is not already in the database
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
        if obj.parent is self.top:
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

        if obj.name in self._dict:
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
