import sys

import metakit

from giraffe.common.identity import register
from giraffe.base.mkarray import MkArray

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

def wrap_mk_attribute(name):
    def get_data(self):
        return getattr(self.data, name)
    def set_data(self, value):
        setattr(self.data, name, value)
    return property(get_data, set_data)

class Item(object):
    def __init__(self, project, id=None):
        self.project = project
        self.id = register(self, id)

        # create or get the view
        if self.viewname in self.project.db.contents().properties().keys():
            self.view = self.project.db.view(self.viewname)
        else:
            self.view = self.project.db.getas(self.description)

        # get the row
        try:
            self.data = self.view.select(id=self.id)[0]
        except IndexError:
            self.view.append(id=self.id)
            self.data = self.view.select(id=self.id)[0]

        self.project.register(self)

    viewname = 'items'
    description = 'items[name:S,id:S]'
    name = wrap_mk_attribute('name')

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

    def register(self, item):
        self.items[item.id] = item

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
