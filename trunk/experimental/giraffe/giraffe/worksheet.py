import sys

from giraffe.signals import HasSignals
from giraffe.commands import command_from_methods
from giraffe.item import Item, wrap_attribute, register_class, create_id

import arrays
from giraffe.arrays import MkArray

def evaluate_expression(expression, project, worksheet):
    namespace = {}

    namespace.update(arrays.__dict__)

    namespace['top'] = project.top
    namespace['here'] = project.this
    namespace['this'] = worksheet
    namespace['up'] = worksheet.parent.parent

    namespace.update(dict([(c.name, c) for c in worksheet.columns]))
    namespace.update(dict([(i.name, i) for i in worksheet.parent.contents()]))

    return eval(expression, namespace)


class Column(MkArray, HasSignals):
    def __init__(self, worksheet, ind):
        self.data = worksheet.data.columns[ind]
        self.worksheet = worksheet
        self.ind = ind
        MkArray.__init__(self, worksheet.data.columns, worksheet.data.columns.data, ind)

    def set_name(self, name):
        self.data.name = name
    def get_name(self):
        return self.data.name
    name = property(get_name, set_name)

    def set_id(self, id):
        self.data.id = id
    def get_id(self, id):
        return self.data.id
    id = property(get_id, set_id)

    def __setitem__(self, key, value):
        prev = self[key]
        MkArray.__setitem__(self, key, value)
        self.worksheet.emit('data-changed')
        self.emit('data-changed')
        return [key, value, prev]

    def undo_setitem(self, state):
        key, value, prev = state
        self[key] = prev

    __setitem__ = command_from_methods('column_change_data', __setitem__, undo_setitem)



class Worksheet(Item, HasSignals):
    def __init__(self, project, name=None, parent=None, location=None):
        self.__attr = False
        Item.__init__(self, project, name, parent, location)

        self.columns = []

        if location is not None:
            for i in range(len(self.data.columns)):
                if not i.name.startswith('-'):
                    self.columns.append(Column(self, i))

        self.__attr = True


    def __getattr__(self, name):
        if name in self.column_names:
            return self[name]
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name.startswith('_') or hasattr(self.__class__, name) \
                                or name in self.__dict__ or not self.__attr:
            return object.__setattr__(self, name, value)
        else:
            if name not in self.column_names:
                self.add_column(name)
            self[name] = value

    def __delattr__(self, name):
        if name in self.column_names:
            self.remove_column(name)
        else:
            object.__delattr__(self, name)

    def column_index(self, name):
        return self.data.columns.select(*[{'name': n} for n in self.column_names]).find(name=name)

    def add_column(self, name):
        ind = self.data.columns.append(name=name, id=create_id(), data='')
#        print >>sys.stderr, 'appended', ind
        self.columns.append(Column(self, ind))
        self.emit('data-changed')
        return name

    def add_column_undo(self, name):
        ind = self.column_index(name=name)
#        print >>sys.stderr, 'found', ind
        self.data.columns.delete(ind)
        del self.columns[ind]
        self.emit('data-changed')

    add_column = command_from_methods('worksheet_add_column', add_column, add_column_undo)


    def remove_column(self, name):
        ind = self.column_index(name)
        if ind == -1:
            raise NameError, "Worksheet does not have a column named %s" % name
        else:
            col = self.columns[ind]
            col.name = '-'+col.name
            del self.columns[ind]
            self.emit('data-changed')
            return (col, ind), None

    def undo_remove_column(self, c):
#        print >>sys.stderr, c
        col, ind = c
        col.name = col.name[1:]
        self.columns.insert(ind, col)
        self.emit('data-changed')

    remove_column = command_from_methods('worksheet_remove_column', remove_column, undo_remove_column)


    def get_ncolumns(self):
        return len(self.columns)
    ncolumns = property(get_ncolumns)

    def get_nrows(self):
        try:
            return max([len(c) for c in self.columns])
        except ValueError:
            return 0
    nrows = property(get_nrows)


    def __getitem__(self, key):
        if isinstance(key, int):
            return self.columns[key]
        elif isinstance(key, basestring) and key in self.column_names:
            return self.columns[self.column_names.index(key)]
        else:
            raise IndexError

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.columns[key][:] = value
        elif isinstance(key, basestring):
            if key not in self.column_names:
                self.add_column(key)
            self.columns[self.column_names.index(key)][:] = value
        else:
            raise IndexError
        self.emit('data-changed')

    def __repr__(self):
        return '<Worksheet %s%s>' % (self.name, '(deleted)'*self.id.startswith('-'))


    def get_column_names(self):
        return [c.name for c in self.columns]
    column_names = property(get_column_names)

    def set_name(self, n):
        self._name = n
        self.emit('rename', n, item=self)
    def get_name(self):
        return self._name
    name = property(get_name, set_name)

    _name = wrap_attribute('name')
    parent = wrap_attribute('parent')

    def suggest_column_name(self):
        def num_to_alpha(n):
            alphabet = 'abcdefghijklmnopqrstuvwxyz'
            name = ''
            n, ypol = n//len(alphabet), n%len(alphabet)
            if n == 0:
                return alphabet[ypol]
            name = num_to_alpha(n) + alphabet[ypol]
            return name

        i = 0
        while num_to_alpha(i) in self.column_names:
            i+=1
        return num_to_alpha(i)

register_class(Worksheet, 'worksheets[name:S,id:S,parent:S,columns[name:S,id:S,data:B,expr:S]]')
