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

        self.this = self.top

        # create objects
        for cls, desc in storage_desc.iteritems():
            for row in self.db.getas(desc):
                if row.id != self.top.id:
                    if not row.id.startswith('-'):
                        self.items[row.id] = cls(self, id=row.id)
                    else:
                        self.deleted[row.id] = cls(self, id=row.id)


    def add(self, item, id=None):
        view = self.db.getas(storage_desc[type(item)])

        # get the row
        if id is None:
            id = create_id()
            row = view.append(id=id)
            data = view[row]
        else:
            data = view[view.find(id=id)]

        self.items[id] = item

        return view, data, id

    def set_dict(self, d):
        self._dict = d

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
        Folder(self, path)

    def rmfolder(self, path):
        if path in self.this:
            self.remove(self.this[path].id)
        else:
            raise NameError, "folder '%s' does not exist" % path


    def save(self):
        self.db.commit()
