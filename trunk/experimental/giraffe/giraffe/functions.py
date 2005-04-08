import sys
import os
import gui
from signals import HasSignals

class FunctionsRegistry(HasSignals):
    def __init__(self, dir):
        """Create a new function registry from a directory"""
        self.functions = []
        self.dir = dir
        self.scan()

    def rescan(self):
        """Rescan the directory and check for changed functions"""
        dir = self.dir
        names = []
        for f in os.listdir(dir):
            try:
                func = Function()
                func.fromstring(open(dir+'/'+f).read())
                func.filename = dir + '/' + f
                names.append(func.name)
            except IOError, s:
                continue

            if func.name not in [f.name for f in self.functions]:
                self.functions.append(func)
                self.emit('added', func)
            else:
                for i, f in enumerate(self.functions):
                    if f.name == func.name:
                        self.functions[i] = func
                        self.emit('modified', func)

        for f in self:
            if f.name not in names:
                self.functions.remove(f)
                self.emit('removed', f)

#            self.functions.sort()

    def scan(self, dir=None):
        if dir == None:
            dir = self.dir
        self.functions = []

        for f in os.listdir(dir):
            try:
                func = Function()
                func.fromstring(open(dir+'/'+f).read())
                func.filename = dir + '/' + f
            except IOError, s:
                continue

            self.functions.append(func)
#        self.functions.sort()

    def __getitem__(self, name):
        return [f for f in self.functions if f.name == name][0]

    def __contains__(self, name):
        return name in [f.name for f in self.functions]

    def __len__(self):
        return len(self.functions)

    def __iter__(self):
        for f in self.functions:
            yield(f)

    """emits 'modified'(function) : a function definition has been modified"""

class RegModel(HasSignals):
    def __init__(self, registry):
        self.registry = registry
        self.registry.connect('modified', self.mod)
        self.registry.connect('added', self.mod)
        self.registry.connect('removed', self.mod)

    def mod(self, *args, **kwds):
        self.emit('modified')

    def __len__(self):
        return len(self.registry)

#    def get(self, row, column):
#        return self.registry.functions[row].name
#
    def __getitem__(self, item):
        return self.registry.functions[item]

functions = []

def mod_property(name):
    def mod_get(self):
        return getattr(self, '_'+name)
    def mod_set(self, value):
        old = mod_get(self)
        setattr(self, '_'+name, value)
#        self.emit('modified', name, value, old)
    return property(mod_get, mod_set)

class Function(HasSignals):
    def __init__(self, name='', parameters=[], text='', extra=''):
        self._name = name
        self._parameters = parameters
        self._text = text
        self._extra = extra

    extra = mod_property('extra')
    text = mod_property('text')
    name = mod_property('name')
    parameters = mod_property('parameters')

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Function %s(%s)>' % (self.name, ', '.join(self.parameters))

    def to_module(self):
        st = []
        st.append('from numarray import *\n')

        st.append('def func(x, '+', '.join(self.parameters)+'):\n')
        for line in self.text.splitlines():
            st.append('    '+line+'\n')
        st.append('    return y\n\n')
        st.append(self.extra+'\n')

        st = ''.join(st)
        exec st
        return func

    def save(self):
        file(self.filename, 'wb').write(self.tostring())

    def fromstring(self, s):
        self.name, param, self.text, self.extra = s.split('\n------\n')
        self.parameters = param.split(', ')

    def tostring(self):
        st = []
        st.append(self.name)
        st.append(', '.join(self.parameters))
        st.append(self.text)
        st.append(self.extra)
        st = '\n------\n'.join(st)
        return st

registry = FunctionsRegistry('functions')

class FunctionsWindow(gui.Window):
    def __init__(self):
        gui.Window.__init__(self, title='Functions', size=(300, 200))
        box = gui.Box(self, 'horizontal')

#        split = gui.Splitter(box, 'horizontal', stretch=1)
#        self.categories = gui.List(split)
        self.category = gui.List(box, model=RegModel(registry), stretch=1)
        self.category.connect('selection-changed', self.on_select_function)

        rbox = gui.Box(box, 'vertical', stretch=2)

        toolbar = gui.Toolbar(rbox, stretch=0)
        toolbar.append(gui.Action('New', '', self.on_new, 'new.png'))
        toolbar.append(gui.Action('Delete', '', self.on_remove, 'remove.png'))
        toolbar.append(gui.Action('Save', '', self.on_save, 'save.png'))

        book = gui.Notebook(rbox)

        edit = gui.Box(book, 'vertical', page_label='edit')
        g = gui.Grid(edit, 2, 2, stretch=0, expand=True)
        g.layout.AddGrowableCol(1)
        gui.Label(g, 'Name', pos=(0,0))
        gui.Label(g, 'Parameters', pos=(1,0))
        self.name = gui.Text(g, pos=(0,1), expand=True)
        self.params = gui.Text(g, pos=(1,1), expand=True)
        self.text = gui.Text(edit, multiline=True, stretch=1)

        extra = gui.Box(book, 'vertical', page_label='extra')
        self.extra = gui.Text(extra, multiline=True, stretch=1)

        self.functions = functions
        self.function = None

    def on_new(self):
        num = 0
        while 'function%d'%num in registry:
            num += 1
        self.function = Function('function%d'%num, [], 'y=f(x)', '')
        open('functions/function%d.function'%num, 'wb').write(self.function.tostring())
#        self.scan('functions')
        registry.rescan()
        self.update_gui()

    def on_remove(self):
        os.remove(self.function.filename)
        registry.rescan()

    def on_save(self):
        self.function.name = self.name.text
        self.function.parameters = [p.strip() for p in self.params.text.split(',')]
        self.function.extra = self.extra.text
        self.function.text = self.text.text

        self.function.save()
#        self.function.to_module()
        registry.rescan()

    def update_gui(self):
        self.name.text = self.function.name
        self.params.text = ', '.join(self.function.parameters)
        self.extra.text = self.function.extra
        self.text.text = self.function.text

    def on_select_function(self):
        try:
            self.function = self.category.model[self.category.selection[0]]
        except IndexError:
            return
#        if self.function is not None:
#            print 'are you sure?'
#        self.function = [f for f in self.functions if f.name == name][0]
        self.update_gui()


if __name__ == '__main__':
    gui.Application().run(FunctionsWindow)
