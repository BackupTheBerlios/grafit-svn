import items
from common import identity
import lib.ElementTree as et

class Project(items.Folder, items.Persistent):
    """
    """
    def __init__(self):
        items.Folder.__init__(self, 'Project', None)
        self._filename = None
        self._modified = False
        self.connect('modified', self.on_modified)
    
    def _set_filename(self, fn):
        self._filename = fn
    def _get_filename(self):
        return self._filename
    filename = property(_get_filename, _set_filename)

    def _set_modified(self, fn):
        if fn and not self._modified:
            self.emit('status-changed', True)
        elif not fn and self._modified:
            self.emit('status-changed', False)
        self._modified = fn
    def _get_modified(self):
        return self._modified
    modified = property(_get_modified, _set_modified)

    def load(self, filename):
        """Load the project from a file."""
        self.new()
        element = et.parse(filename).getroot()
        for child in element:
            items.Persistent.create(child, self)
        
    def save(self):
        """
        Save the project.
        Returns
        - True: project saved succesfully
        - False: no file name. Set a file name, and call save again.
        """
        if self.filename is None:
            return False
        else:
            self.saveas(self.filename)
            self.modified = False
            return True

    def saveas(self, filename):
        """Save the project to a file."""
        et.ElementTree(self.to_element()).write(file(filename, 'wb'))

    def new(self):
        """Clear the project."""
        for i in self.items[:]:
            self.remove_item(i)
        self.modified = False
        self.filename = None

    def on_modified(self):
        self.modified = True

    def to_element(self):
        e = items.Folder.to_element(self)
        e.tag = 'Project'
        return e    

    _element_name = 'Project'

import sys

def test():
    p= Project()
    f = items.Folder('Trivial', p)
    i = items.TrivialItem('opikou', f)
    i.emit('modified')

    p.filename = 'test.xml'
    p.save()
    p.new()

    p2 = Project()
#    f = items.Folder('Trivial', p2)
    items.TrivialItem('opikou', p2)
    items.TrivialItem('opi3ou', p2)
    items.TrivialItem('op2kou', p2)
    items.TrivialItem('oooooo', p2)
    def funq(self):
        pass

    print sys.getrefcount(p2)
    import gc
    print gc.get_referrers(p2)
    p2.new()
    print sys.getrefcount(p2)
    print gc.get_referrers(p2)
    p2.connect('modified', funq)
    del funq
    p2.emit('modified')

    del p2

    import gc

    
#    p2.new()

    print p.desc()
    print p.uuid
    p.load('test.xml')
    print p.desc()
    print p.uuid
    print identity.lookup(p.uuid), p

    p3 = items.Persistent.create(et.parse('test.xml').getroot())
    print p3.uuid
    print identity.lookup(p.uuid), p3, p


if __name__== '__main__':
    test()
