import mingui as gui
from cElementTree import parse

def attr_to_obj(attr):
    return eval(attr, {})

def from_element(elem, parent=None, level=0):
    cls = getattr(gui, elem.tag)
    place = dict((k[1:], attr_to_obj(v)) for k, v in elem.items() if k.startswith('_'))
    args = dict((k, attr_to_obj(v)) for k, v in elem.items() if not k.startswith('_'))
    print '  '*level, cls.__name__, place, args

    if parent is None:
        gui.app.mainwin = widget = cls(**args)
    else:
        widget = cls(parent(**place), **args)

    for child in elem:
        from_element(child, widget, level+1)

    return widget

class Resource(object):
    def __init__(self, filename):
        self.root = parse(filename).getroot()
        self.res = dict((attr_to_obj(elem.get('name')), elem) for elem in self.root)

    def build(self, name):
        return from_element(self.res[name]) 
