"""
The identity module provides a way to get a reference to an object
which is not guranteed to stay the *same* object, but can be deleted
and re-created. For example, it may be loaded and saved, or it may
be deleted and the deletion undone.

When creating the object, use something like:

    def __init__(self, id=None):
        self.id = identity.register(self, id)

If __init__ is called with the `id` parameter, the object assumes
the identity `id`, otherwise a new identity is created for it.

We can get a reference to the object with

    ref = obj.id

and retrieve the object with

    obj = identity.lookup(ref)

Identity uses weak references, so the object can be deleted, in which
case the reference disappears.
"""

import weakref
import time
import random
import socket
import md5

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

_objects = weakref.WeakValueDictionary()

def register(obj, key=None):
    """
    """
    if key is None:
        key = create_id(obj)
    _objects[key] = obj
    return key

def lookup(key):
    return _objects[key]
