import weakref
import sys
import uuid

_objects = weakref.WeakValueDictionary()

def register(obj):
    if not hasattr(obj, 'uuid') or obj.uuid is None:
        try:
            obj.uuid = uuid.uuid(obj)
        except AttributeError:
            return None
    try:
        _objects[obj.uuid] = obj
    except TypeError:
        return None

    return obj.uuid


def get(key):
    return _objects[key]
