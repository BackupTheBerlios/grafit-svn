"""
Shelf for global object access
"""

import weakref

def uuid( *args ):
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

_objects = weakref.WeakValueDictionary()

def register(obj):
    if not hasattr(obj, 'uuid') or obj.uuid is None:
        try:
            obj.uuid = uuid(obj)
        except AttributeError:
            return None
    try:
        _objects[obj.uuid] = obj
    except TypeError:
        return None

    return obj.uuid

def get(key):
    return _objects[key]
