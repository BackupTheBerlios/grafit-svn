import common.signals

class Item(common.signals.HasSignals):
    def __init__(self, name, parent):
        self.parent = parent
        self.name = name
        if self.parent is not None:
            parent.add_item(self)

    def to_element(self):
        """
        Convert the item to an Element. Must be overridden
        in subclasses.
        """
        raise NotImplementedError

    def from_element(cls, element):
        """
        Class method. Creates an object given its representation
        as an Element. Must be overridden in subclasses.
        """
        raise NotImplementedError
    from_element = classmethod(from_element)

    def load(element):
        """
        Static method. Item.load(element) creates an Item of the
        corresponding subclass.
        """
        lookup = dict([(i._element_name, i) for i in Item.__subclasses__() if hasattr(i, '_element_name')])
        print lookup['Folder']
        return lookup['Folder'].from_element(element)
    load = staticmethod(load)

    def _set_name(self, name):
        if self.parent is not None and not self.parent._is_name_ok(name):
            raise NameError
        self._name = name

    def _get_name(self):
        return self._name

    name = property(_get_name, _set_name)


class Folder(Item):
    """A folder. Folders contain items and subfolders"""
    def __init__(self, name, parent):
        Item.__init__(self, name, parent)
        self.items = []

    def from_element(cls, element):
        print 'fe_called'
        return Folder('new', None)
    from_element = classmethod(from_element)

    def add_item(self, item):
        """
        Add an item to the folder. Items are normally added by creating them
        with the folder as parent.
        """
        self.items.append(item)
        self.emit('add-item', item)
        item.connect('modified', self.on_child_modified)

    def remove_item(self, item):
        """
        Remove an item from the folder.
        """
        try:
            i = self.items.index(item)
        except ValueError: # item not in list
            return False
        
        item.disconnect('modified', self.on_child_modified)
        self.items.remove(i)

    def desc(self):
        r = "<Folder %s>" % self.name
        for i in self.items:
            r += "".join(["\n    " + l for l in repr(i).splitlines()])
        return r

    def on_child_modified(self):
        self.emit('modified')

    def _is_name_ok(self, name):
        """
        Check if `name` is ok for a child of this folder.
        `name` must not be the name of any existing child.
        """
        if name in [s.name for s in self.items]:
            return False
        return True

    def _get_subfolders(self):
        return [i for i in self.items if isinstance(i, Folder)]
    subfolders = property(_get_subfolders)

    def _get_objects(self):
        return [i for i in self.items if not isinstance(i, Folder)]
    objects = property(_get_objects)

    _element_name = 'Folder'

if __name__ == '__main__':
    f = Folder('root', None)
    f2 = Folder('child', f)
    f3 = Folder('child2', f)
    i = Item('item', f3)
    f3 = Folder('child5', f)
    i = Item('item', f3)
    i = Item('item3', f3)
    i = Item('item4', f3)
    i.emit('modified')
    print f.desc()
    print f3.objects
    print f.subfolders
    print f.load(None)
    print f3.load(None)
