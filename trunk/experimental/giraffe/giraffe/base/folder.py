from giraffe.base.item import Item, wrap_attribute, register_class

class Folder(Item):
    def __init__(self, project, name=None, parent=None, id=None):
        Item.__init__(self, project, id)

        if id is None: # new item
            self.name = name
        else: # existing item
            pass

    name = wrap_attribute('name')

register_class(Folder, 'folders[name:S,id:S,parent:S]')
