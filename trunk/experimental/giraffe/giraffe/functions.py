import sys
import os
import gui
from signals import HasSignals
from ElementTree import Element, SubElement, ElementTree, parse
import StringIO

def mod_property(name):
    def mod_get(self):
        return getattr(self, '_'+name)
    def mod_set(self, value):
        old = mod_get(self)
        setattr(self, '_'+name, value)
        self.emit('modified', name, value, old)
    return property(mod_get, mod_set)

class Function(HasSignals):
    def __init__(self, name, parameters, text, extra):
        self._name = name
        self._parameters = parameters
        self._text = text
        self._extra = extra

    extra = mod_property('extra')
    text = mod_property('text')
    name = mod_property('name')
    parameters = mod_property('parameters')

    def to_xml(self, f):
        elem = Element('Function', name=self.name, text=repr(self.text), extra=repr(self.extra))
        for p in self.parameters:
            SubElement(elem, 'Parameter', name=p)
        ElementTree(elem).write(f)

    def __str__(self):
        return self.name

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
        print func

        print >>sys.stderr, st

class FunctionsWindow(gui.Window):
    def __init__(self):
        gui.Window.__init__(self, title='Functions')
        box = gui.Box(self, 'horizontal')

#        split = gui.Splitter(box, 'horizontal', stretch=1)
#        self.categories = gui.List(split)
        self.category = gui.List(box, stretch=1)
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

        self.functions = []
        self.function = None

#        self.function = Function('Dielectric/Havriliak-Negami', ['logf0', 'de', 'a', 'b'], 'y=hn(x)', 'import Numeric\ndef')

        self.scan('functions')

    def on_new(self):
        self.function = Function('new function', [], 'y=f(x)', '')
        self.function.to_xml(open('functions/function'+str(len(self.functions))+'.function', 'wb'))
        self.scan('functions')
        self.update_gui()

    def on_remove(self):
        os.remove(self.function.filename)
        self.scan('functions')

    def on_save(self):
        self.function.name = self.name.text
        self.function.parameters = [p.strip() for p in self.params.text.split(',')]
        self.function.extra = self.extra.text
        self.function.text = self.text.text

        self.function.to_xml(self.function.filename)
        self.function.to_module()
        self.scan('functions')

    def update_gui(self):
        self.name.text = self.function.name
        self.params.text = ', '.join(self.function.parameters)
        self.extra.text = self.function.extra
        self.text.text = self.function.text

    def add(self, function):
        self.functions.append(function)
        self.category.model.append(function)

    def scan(self, dir):
        self.functions = []
        sel = self.category.selection
        del self.category.model[:]
        for f in os.listdir(dir):
            try:
                e = parse(dir + '/' + f).getroot()
            except IOError:
                continue
            func = Function(e.get('name'),
                            [c.get('name') for c in e.getchildren()],
                            eval(e.get('text')),
                            eval(e.get('extra')))
            func.filename = dir + '/' + f
            self.add(func)
        print sel
        self.category.setsel(sel)

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
