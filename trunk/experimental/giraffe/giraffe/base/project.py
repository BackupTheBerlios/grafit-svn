import metakit

from giraffe.base.commands import Command, command_from_methods
from giraffe.base.signals import HasSignals
from giraffe.base.item import Item, Folder, storage_desc, create_id

# import only in order to register object types
import giraffe.worksheet

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

        self.items = {}
        self.deleted = {}
        self._dict = {}

        # Create top folder.
        # - it must be created before all other items
        # - it must be created with _isroot=True, to set itself as its parent folder
        try:
            fv = self.db.getas(storage_desc[Folder])
            row = fv.select(name='top')[0]
            self.top = self.items[id] = Folder(self, location=(fv, row, row.id), _isroot=True)
        except IndexError:
            # can't find it in the database, create a new one.
            self.top = Folder(self, 'top', _isroot=True)

        self.this = self.top

        # create objects
        for cls, desc in storage_desc.iteritems():
            view = self.db.getas(desc)
            for i, row in enumerate(view):
                if row.id != self.top.id:
                    if not row.id.startswith('-'):
                        self.items[row.id] = cls(self, location=(view, row, row.id))
                    else:
                        self.deleted[row.id] = cls(self, location=(view, row, row.id))

    def set_dict(self, d):
        self._dict = d

    def cleanup(self):
        """Purge all deleted items from the database"""
        for cls, desc in storage_desc.iteritems():
            view = self.db.getas(desc)
            for i, row in enumerate(view):
                if row.id.startswith('-'):
                    view.delete(i)

    def create(self, cls):
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
        return obj, obj

    def new_undo(self, obj):
        del self.items[obj.id]
        obj.id = '-'+obj.id
        self.deleted[obj.id] = obj
        if obj.parent is self.top:
            del self._dict[obj.name] 

    def new_redo(self, obj):
        del self.deleted[obj.id]
        obj.id = obj.id[1:]
        self.items[obj.id] = obj
        if obj.parent is self.top:
            self._dict[obj.name] = obj

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
        return id

    def remove_undo(self, id):
        obj = self.deleted['-'+id]
        ind = obj.view.find(id=obj.id)

        del self.deleted[obj.id]
        obj.id = obj.id[1:]
        self.items[obj.id] = obj

        if obj.parent is self.top:
            self._dict[obj.name] = obj

    remove = command_from_methods('project_remove', remove, remove_undo)


    # Shortcuts for creating and removing folders
        
    def mkfolder(self, path):
        self.new(Folder, path)

    def rmfolder(self, path):
        if path in self.this:
            self.remove(self.this[path].id)
        else:
            raise NameError, "folder '%s' does not exist" % path

    def save(self):
        self.db.commit()

