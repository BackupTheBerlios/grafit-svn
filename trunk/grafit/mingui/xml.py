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

def build(objname, parent=None, place=None, src={}, **extra):
    return _from_element(registry[objname], parent, place, src, extra)

def _from_element(elem, parent=None, place=None, src={}, extra={}):
    print elem.tag, parent, place

    if elem.tag == 'Commands':
        if not hasattr(parent, 'commands'):
            parent.commands = {}
        for e in elem:
            comm = _from_element(e)
            print comm.id
            parent.commands[comm.id] = comm
        return
    elif elem.tag in src:
        cls = src[elem.tag]
    else:
        cls = getattr(gui, elem.tag)
    plac = dict((k[1:], eval(v, {})) for k, v in elem.items() if k.startswith('_'))
    args = dict((k, eval(v, {})) for k, v in elem.items() if not k.startswith('_'))

    args.update(extra)
    print args

    if elem.tag == 'Command':
        return = cls(**args)
        if parent is not None:
            parent.commands[cmd.id] = cmd
        else:
            commands[cmd.id] = cmd
    elif parent is not None and hasattr(parent, '__call__'):
        widget = cls(parent(**plac), **args)
    elif place is not None:
        widget = cls(place, **args)
    else:
        widget = cls(**args)

    #TODO remove
    if 'name' in args and args['name'] == 'mainwin':
        gui.app.mainwin = widget


    for child in elem:
        _from_element(child, widget, src=src)

    if hasattr(widget, 'setup'):
        widget.setup()

    return widget

