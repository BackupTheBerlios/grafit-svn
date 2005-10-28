import mingui as gui
from cElementTree import parse
from weakref import WeakValueDictionary

registry = {}

def merge(filename):
    res = Resource(filename)
    registry.update(res.res)

def build(objname):
    return from_element(registry[objname])

def from_element(elem, parent=None, level=0, base=None):
    if elem.tag == 'Commands':
        pass
    elif elem.tag == 'Images':
        pass
    else:
        cls = getattr(gui, elem.tag)
        place = dict((k[1:], eval(v, {})) for k, v in elem.items() if k.startswith('_'))
        args = dict((k, eval(v, {})) for k, v in elem.items() if not k.startswith('_'))

        if parent is None:
            gui.app.mainwin = widget = cls(**args)
        else:
            widget = cls(parent(**place), **args)

        if base is not None and 'name' in args:
            lookup[base][args['name']] = widget

        for child in elem:
            from_element(child, widget, level+1, base)

        return widget

class Resource(object):
    def __init__(self, filename):
        self.root = parse(filename).getroot()
        self.res = dict((eval(elem.get('name'), {}), elem) 
                        for elem in self.root if 'name' in elem.keys())
        self.lookup = dict((name, WeakValueDictionary()) for name in self.res)

#    def build(self, name):
#        return self.from_element(self.res[name], base=name) 

#    def find(self, base, locate):
#        return self.lookup[base][locate]
