import sys
import time, random, socket, md5

import metakit

from giraffe.base.mkarray import MkArray
from giraffe.common.commands import Command, command_list

def create_id(*args):
    """
    Generates a universally unique ID.
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


def wrap_attribute(name):
    def get_data(self):
        return getattr(self.data, name)
    def set_data(self, value):
        setattr(self.data, name, value)
    return property(get_data, set_data)


class Item(object):
    def __init__(self, project, id=None):
        self.project = project
        self.view, self.data, self.id = project.add(self)

    viewname = 'items'
    description = 'items[name:S,id:S]'
    name = wrap_attribute('name')


class Project(object):
    def __init__(self, filename=None):
        self.filename = filename

        if self.filename is None:
            # We initially create an in-memory database.
            # When we save to a file, we will reopen the database from the file.
            self.db = metakit.storage()
        else:
            self.db = metakit.storage(self.filename, 1)

        self.items = {}

    def add(self, item, id=None):
        # create or get the view
        if item.viewname in self.db.contents().properties().keys():
            view = self.db.view(item.viewname)
        else:
            view = self.db.getas(item.description)

        # get the row
        if id is None:
            id = create_id()
            view.append(id=id)
            data = view[view.find(id=id)]
        else:
            data = view[view.find(id=id)]

        self.items[id] = item
        return view, data, id

    def remove(self, id):
        obj = self.items[id]
        ind = obj.view.find(id=id)
        if ind == -1:
            raise NameError
        else:
#            obj.view.delete(ind)
            obj.data.id = obj.id = '-'+obj.id 
            del self.items[id]

    def dump(self):
        itemviews = [ 'worksheets', 'items' ]
        ids = []
        for n in itemviews:
           ids.append([r.id for r in self.db.view(n)])
