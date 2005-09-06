import sys
#print >>sys.stderr, "import worksheet"

from giraffe.signals import HasSignals
from giraffe.commands import command_from_methods, command_from_methods2, StopCommand
from giraffe.project import Item, wrap_attribute, register_class, create_id

from giraffe.arrays import MkArray, transpose, array, asarray

import arrays

class Column(MkArray, HasSignals):
    def __init__(self, worksheet, ind):
        self.data = worksheet.data.columns[ind]
        self.worksheet = worksheet
        self.ind = ind
        MkArray.__init__(self, worksheet.data.columns, worksheet.data.columns.data, ind)
        self.dependencies = set()

    def set_name(self, name):
        self.data.name = name.encode('utf-8')
    def get_name(self):
        return self.data.name.decode('utf-8')
    name = property(get_name, set_name)

    def do_set_expr(self, state, expr, setstate=True):
        # find dependencies and error-check expression
        self.worksheet.record = set()
        try:
            data = asarray(self.worksheet.evaluate(expr))
        except Exception, ar:
            print >>sys.stderr, '*****************', ar
            raise StopCommand, False
        newdep = self.worksheet.record
        self.worksheet.record = None

        # set dependencies
        for column in newdep - self.dependencies:
            column.connect('data-changed', self.calculate)
        for column in self.dependencies - newdep:
            column.disconnect('data-changed', self.calculate)
        self.dependencies = newdep

        # command state
        if setstate:
            state['old'], state['new'] = self.expr, expr
            if self.expr == '':
                state['olddata'] = self[:]

        self.data.expr = expr.encode('utf-8')
        if expr != '':
            # set data without triggering a command
            MkArray.__setitem__(self, slice(None), data)
        self.worksheet.emit('data-changed')
        self.emit('data-changed')
        return True

    def undo_set_expr(self, state):
        self.do_set_expr(None, state['old'], setstate=False)
        if 'olddata' in state:
            MkArray.__setitem__(self, slice(None), state['olddata'])

    def redo_set_expr(self, state):
        self.do_set_expr(None, state['new'], setstate=False)

    set_expr = command_from_methods2('worksheet/column-expr', 
                                     do_set_expr, undo_set_expr, redo=redo_set_expr)

    def get_expr(self):
        return self.data.expr.decode('utf-8')

    expr = property(get_expr, set_expr)

    def calculate(self):
        self[:] = self.worksheet.evaluate(self.expr)

    def set_id(self, id):
        self.data.id = id
    def get_id(self):
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

    def __eq__(self, other):
        return self.id == other.id

    __setitem__ = command_from_methods('column_change_data', __setitem__, undo_setitem)


class Worksheet(Item, HasSignals):
    def __init__(self, project, name=None, parent=None, location=None):
        self.__attr = False

        Item.__init__(self, project, name, parent, location)

        self.columns = []

        if location is not None:
            for i in range(len(self.data.columns)):
                if not self.data.columns[i].name.startswith('-'):
                    self.columns.append(Column(self, i))

        self.__attr = True

    record = None

    def evaluate(self, expression):
        if expression == '':
            return []
        project = self.project
        worksheet = self

        class funnydict(dict):
            def __init__(self, recordkeys, *args, **kwds):
                dict.__init__(self, *args, **kwds)
                self.recordset = set()
                self.recordkeys = recordkeys

            def __getitem__(self, key):
                if key in self.recordkeys:
                    self.recordset.add(key)
                return dict.__getitem__(self, key)

        namespace = funnydict((c.name for c in worksheet.columns)) 

        namespace.update(arrays.__dict__)

        namespace['top'] = project.top
        namespace['here'] = project.this
        namespace['this'] = worksheet
        namespace['up'] = worksheet.parent.parent

        namespace.update(dict([(c.name, c) for c in worksheet.columns]))
        namespace.update(dict([(i.name, i) for i in worksheet.parent.contents()]))

        result = eval(expression, namespace)
        for name in namespace.recordset:
            self[name]
        return result

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
        return self.data.columns.select(*[{'name': n.encode('utf-8')} for n in self.column_names]).find(name=name.encode('utf-8'))

    def add_column(self, state, name):
        ind = self.data.columns.append(name=name, id=create_id(), data='')
        self.columns.append(Column(self, ind))
        self.emit('data-changed')
        state['obj'] = self.columns[-1]
        return name

    def add_column_undo(self, state):
        col = state['obj']
        col.id = '-'+col.id
        self.columns.remove(col)
        self.emit('data-changed')

    def add_column_redo(self, state):
        col = state['obj']
        col.id = col.id[1:]
        self.columns.append(col)
        self.emit('data-changed')

    add_column = command_from_methods2('worksheet/add_column', add_column, add_column_undo,
                                       redo=add_column_redo)

    def remove_column(self, state, name):
        ind = self.column_index(name)
        if ind == -1:
            raise NameError, "Worksheet does not have a column named %s" % name
        else:
            col = self.columns[ind]
            col.name = '-'+col.name
            del self.columns[ind]
            self.emit('data-changed')
            state['col'], state['ind'] = col, ind
            return (col, ind), None

    def undo_remove_column(self, state):
        col, ind = state['col'], state['ind']
        col.name = col.name[1:]
        self.columns.insert(ind, col)
        self.emit('data-changed')

    remove_column = command_from_methods2('worksheet_remove_column', remove_column, 
                                          undo_remove_column)

    def get_ncolumns(self):
        return len(self.columns)
    ncolumns = property(get_ncolumns)

    def get_nrows(self):
        try:
            return max([len(c) for c in self.columns])
        except ValueError:
            return 0
    nrows = property(get_nrows)

    def set_array(self, arr):
        if len(arr.shape) != 2:
            raise TypeError, "Array must be two-dimensional"

        for column in arr:
            name = self.suggest_column_name()
            self[name] = column

    def get_array(self):
        return array(self.columns)

    array = property(get_array, set_array)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.columns[key]
        elif isinstance(key, basestring) and key in self.column_names:
            column = self.columns[self.column_names.index(key)]
            if self.record is not None:
                self.record.add(column)
            return column
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

    def __iter__(self):
        for column in self.columns:
            yield column

    def set_name(self, n):
        self._name = n
        self.emit('rename', n, item=self)
    def get_name(self):
        return self._name
    name = property(get_name, set_name)

    def set_parent(self, state, parent):
        state['new'], state['old'] = parent, self._parent
        oldparent = self._parent
        self._parent = parent
        self.parent.emit('modified')
        if oldparent != '':
            oldparent.emit('modified')
        else:
            raise StopCommand
    def undo_set_parent(self, state):
        self._parent = state['old']
        if state['old'] != '':
            state['old'].emit('modified')
        state['new'].emit('modified')
    def redo_set_parent(self, state):
        self._parent = state['new']
        if state['old'] != '':
            state['old'].emit('modified')
        state['new'].emit('modified')
    set_parent = command_from_methods2('worksheet/set-parent', set_parent, undo_set_parent, redo=redo_set_parent)
    def get_parent(self):
        return self._parent
    parent = property(get_parent, set_parent)

    _name = wrap_attribute('name')
    _parent = wrap_attribute('parent')

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

    def export_ascii(self, f):
        for row in xrange(self.nrows):
            for col in xrange(self.ncolumns):
                f.write(str(self.columns[col][row]))
                f.write('\t')
            f.write('\n')

    default_name_prefix = 'sheet'

register_class(Worksheet, 'worksheets[name:S,id:S,parent:S,columns[name:S,id:S,data:B,expr:S]]')
