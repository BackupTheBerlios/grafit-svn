import sys
import time, random, socket, md5

import metakit

from giraffe.common.commands import Command, command_list
from giraffe.common.signals import HasSignals
from giraffe.base.item import Item, Folder, storage_desc

# import only in order to register object types
import giraffe.worksheet


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


"""
Simplest case:
a command whose do() function calls a single method of an object
and the undo() another method:
"""

def command_from_methods(init, undo, redo, cleanup):
    def replace_init(selb, *args, **kwds):
        class CommandFromMethod(Command):
            def __init__(self):
                self.args, self.kwds = args, kwds
                self.__done = False

            def do(self):
                if not self.__done:
                    self.__state = init(selb, *self.args, **self.kwds)
                    self.__done = True
                else:
                    redo(selb, self.__state)
                return self.__state

            def undo(self):
                undo(selb, self.__state)

#            def __del__(self):
#                cleanup(selb, self.__state)
        com = CommandFromMethod()
        ret = com.do_and_register()
        return ret
    return replace_init

class Project(HasSignals):
    def __init__(self, filename=None):
        self.filename = filename

        if self.filename is None:
            # We initially create an in-memory database.
            # When we save to a file, we will reopen the database from the file.
            self.db = metakit.storage()
        else:
            self.db = metakit.storage(self.filename, 1)

        self.items = {}
        self.deleted = {}

        self._dict = {}

        try:
            id = self.db.getas(storage_desc[Folder]).select(name='top')[0].id
            self.top = self.items[id] = Folder(self, id=id, _isroot=True)
        except IndexError:
            self.top = Folder(self, 'top', _isroot=True)

        self.cleanup()

        self.this = self.top

        # create objects
        for cls, desc in storage_desc.iteritems():
            view = self.db.getas(desc)
            for i, row in enumerate(view):
                if row.id != self.top.id:
                    if not row.id.startswith('-'):
                        self.items[row.id] = cls(self, location=(view, i, row, row.id))
                    else:
                        self.deleted[row.id] = cls(self, location=(view, i, row, row.id))

    def set_dict(self, d):
        self._dict = d

    def cleanup(self):
        for cls, desc in storage_desc.iteritems():
            view = self.db.getas(desc)
            for i, row in enumerate(view):
                if row.id.startswith('-'):
                    view.delete(i)

    def create(self, cls):
        try:
            view = self.db.getas(storage_desc[cls])
        except KeyError:
            raise TypeError, "project cannot create an item of type '%s'" % cls

        id = create_id()
        row = view.append(id=id)
        data = view[row]

        return view, row, data, id


    def new(self, cls, *args, **kwds):
        obj = cls(self, *args, **kwds)
        self.items[obj.id] = obj
        if obj.parent is self.top:
            self._dict[obj.name] = obj

        return obj

    def new_undo(self, obj):
        del self.items[obj.id]
        self.deleted[obj.id] = obj
        obj.id = '-'+obj.id
        if obj.parent is self.top:
            del self._dict[obj.name] 

    def new_redo(self, obj):
        del self.deleted[obj.id]
        self.items[obj.id] = obj
        obj.id = obj.id[1:]
        if obj.parent is self.top:
            self._dict[obj.name] = obj

    def new_cleanup(self, obj):
        del self.deleted[obj.id]
        obj.view.remove(obj.row)

    new = command_from_methods(new, new_undo, new_redo, new_cleanup)


    def remove(self, id):
        obj = self.items[id]
        ind = obj.view.find(id=id)

        if obj.name in self._dict:
            del self._dict[obj.name]

        if ind == -1:
            raise NameError
        else:
            obj.data.id = obj.id = '-'+obj.id 
            del self.items[id]
            self.deleted[id] = obj
        
    def mkfolder(self, path):
        self.new(Folder, path)

    def rmfolder(self, path):
        if path in self.this:
            self.remove(self.this[path].id)
        else:
            raise NameError, "folder '%s' does not exist" % path

    def save(self):
        self.db.commit()

