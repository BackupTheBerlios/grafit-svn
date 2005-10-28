import mingui as gui
import Image
from cElementTree import parse
from weakref import WeakValueDictionary
from commands import commands
from images import images

registry = {}

def _attr(attr):
    return eval(attr, {})

def merge(filename):
    root = parse(filename).getroot()
    for elem in root:
        if elem.tag == 'Commands':
            for e in elem:
                comm = _from_element(e)
                commands[comm.id] = comm
        elif elem.tag == 'Images':
            for e in elem:
                if e.tag == 'Image':
                    images.register(_attr(e.get('id')), Image.open(_attr(e.get('path'))))
                elif e.tag == 'DirImageProvider':
                    images.register_dir(_attr(e.get('path')))
        elif 'name' in elem.keys():
            registry[eval(elem.get('name'), {})] = elem
        else:
            print >>sys.stderr, "cannot use element", elem

def build(objname):
    return _from_element(registry[objname])

def _from_element(elem, parent=None, level=0):
    cls = getattr(gui, elem.tag)
    place = dict((k[1:], eval(v, {})) for k, v in elem.items() if k.startswith('_'))
    args = dict((k, eval(v, {})) for k, v in elem.items() if not k.startswith('_'))

    if parent is not None and hasattr(parent, '__call__'):
        widget = cls(parent(**place), **args)
    else:
        widget = cls(**args)

    #TODO remove
    if 'name' in args and args['name'] == 'mainwin':
        gui.app.mainwin = widget


    for child in elem:
        _from_element(child, widget, level+1)

    return widget

