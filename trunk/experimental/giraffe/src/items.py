import common.signals
import lib.ElementTree as et
import shelf

class Persistent(object):
    def to_element(self):
        """
        Convert the item to an Element. Must be overridden
        in subclasses.
        """
        raise NotImplementedError

    def from_element(element, parent):
        """
        Static method. Creates an object given its representation
        as an Element. Must be overridden in subclasses.
        """
        raise NotImplementedError
    from_element = staticmethod(from_element)

    def create(element, parent=None):
        """
        Static method. Persistent.create(element) creates an object of the
        corresponding subclass. Like __init__(), it has a `parent` argument.
        """
        lookup = dict([(i._element_name, i) for i in Persistent.__subclasses__() if hasattr(i, '_element_name')])
        obj = lookup[element.tag].from_element(element, parent)
        return obj
    create = staticmethod(create)


class Item(common.signals.HasSignals):
    def __init__(self, name, parent):
        self.parent = parent
        self.name = name
        if self.parent is not None:
            parent.add_item(self)

    def _set_name(self, name):
        if self.parent is not None and not self.parent._is_name_ok(name):
            raise NameError
        self._name = name

    def _get_name(self):
        return self._name

    name = property(_get_name, _set_name)


class Folder(Item, Persistent):
    """A folder. Folders contain items and subfolders"""
    def __init__(self, name, parent, uuid=None):
        Item.__init__(self, name, parent)
#        Persistent.__init__(self, uuid)
        self.items = []
        self.uuid = uuid
        shelf.register(self)

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
        self.items.remove(item)
        self.emit('remove-item', item)

    def _get_subfolders(self):
        return [i for i in self.items if isinstance(i, Folder)]
    subfolders = property(_get_subfolders)

    def _get_objects(self):
        return [i for i in self.items if not isinstance(i, Folder)]
    objects = property(_get_objects)

    def _is_name_ok(self, name):
        """
        Check if `name` is ok for a child of this folder.
        `name` must not be the name of any existing child.
        """
        if name in [s.name for s in self.items]:
            return False
        return True

    def desc(self):
        r = "<Folder %s>" % self.name
        for i in self.items:
            r += "".join(["\n    " + l for l in repr(i).splitlines()])
        return r

    def on_child_modified(self):
        self.emit('modified')

    def from_element(element, parent):
        folder = Folder(element.get('name'), parent, element.get('uuid'))

        # child items
        for eitem in element:
            item = Persistent.create(eitem, folder)
        return folder
    from_element = staticmethod(from_element)

    def to_element(self):
        elem = et.Element('Folder', name=self.name, uuid=self.uuid)

        for item in self.items:
            elem.append(item.to_element())

        return elem

    _element_name = 'Folder'


class TrivialItem(Item, Persistent):
    """An example: the simplest Item supporting the to_element/from_element protocol"""
    def to_element(self):
        return et.Element('TrivialItem', name=self.name)

    def from_element(element, parent):
        return TrivialItem(element.get('name'), parent)
    from_element = staticmethod(from_element)

    _element_name = 'TrivialItem'



if __name__ == '__main__':
    f = Folder('root', None)
    Folder('child', f)
    f3 = Folder('child2', f)
    i = TrivialItem('item', f3)
    f3 = Folder('child5', f)
    TrivialItem('item', f3)
    TrivialItem('item3', f3)
    i = TrivialItem('item4', f3)
    i.emit('modified')
    e = f3.to_element()

    print f3.desc()
    kaa = Persistent.create(e, f3)
    print f3.desc()
