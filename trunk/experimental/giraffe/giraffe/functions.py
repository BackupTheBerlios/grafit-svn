import sys
import os
import gui

import odr

from signals import HasSignals
from giraffe.arrays import zeros, nan
from giraffe.commands import command_from_methods, StopCommand, command_from_methods2

def gen_flatten(s):
    try:
        iter(s)
    except TypeError:
        yield s
    else:
        for elem in s:
            for subelem in flatten(elem):
                yield subelem

def flatten(l):
    return list(gen_flatten(l))

def splitlist(seq, sizes):
    "Split list into list of lists with specified sizes"
    sumsizes = [sum(sizes[:i]) for i in range(len(sizes)+1)]
    slices = [sumsizes[i:i+2] for i in range(len(sizes))]
    return [list(seq)[s[0]:s[1]] for s in slices]



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

class FunctionInstance(HasSignals):
    def __init__(self, function, name):
        self.name = name
        self.function = function
        self.callable = self.function.to_module()
        self._parameters = [1.]*len(function.parameters)
        self.reg = True
        self._old = None
        self.__old = None

    def update(self):
        self.emit('modified')

    def move(self, x, y):
        if not hasattr(self.function, 'move'):
            return
        self.parameters = self.function.move(x, y, *self.parameters)
        self.emit('modified')

    def __call__(self, arg):
        try:
            return self.callable(arg, *self.parameters)
        except (ValueError, OverflowError):
            # If we don't catch these errors here,
            # odr segfaults on us!
            if hasattr(arg, '__len__'):
                return array([nan]*len(arg))
            else:
                return nan

    def set_reg(self, on):
        if self.reg == on:
            return
        elif on:
            self._old = self.__old 
        else:
            self.__old = self._parameters
        self.reg = on

    def set_parameters(self, p):
#        print >>sys.stderr, self, self._parameters, p
        if self._old is not None:
            old = self._old
            self._old = None
        else:
            old = self._parameters
        self._parameters = p
        if not self.reg:
            raise StopCommand
        if old == p:
            # if the values haven't changed, don't bother
            raise StopCommand
        return [old, p]
    def get_parameters(self):
        return self._parameters

    def redo_set_parameters(self, state):
        old, p = state
        self._parameters = p
        self.emit('modified')

    def undo_set_parameters(self, state):
        old, p = state
        self._parameters = old
        self.emit('modified')

    def combine_set_parameters(self, state, other):
#        print state, other
#        print 'attempt to combine', state, other
        return False

    set_parameters = command_from_methods('function-change-parameters', set_parameters, 
                                        undo_set_parameters, redo_set_parameters, combine=combine_set_parameters)
    parameters = property(get_parameters, set_parameters)


class FunctionSum(HasSignals):
    def __init__(self):
        self.terms = []

    def add(self, func, name):
        self.terms.append(FunctionInstance(registry[func], name))
        self.emit('add-term', self.terms[-1])
        self.terms[-1].connect('modified', lambda: self.emit('modified'), True)
        self.terms[-1].enabled = True

    def remove(self, ind):
        t = self.terms[ind]
        self.emit('remove-term', t)
        del self.terms[ind]

    def __getitem__(self, key):
        return self.terms[key]

    def __call__(self, arg):
        try:
            res = zeros(len(arg), 'd')
        except TypeError:
            res = 0.
        for func in self.terms:
            if func.enabled:
                res += func(arg)
        return res

    def fit(self, x, y, lock, maxiter):
        def __fitfunction(*args):
            if len(args) == 3:
                niter, actred, wss = args
                message  = 'Fitting: Iteration %d, xsqr=%g, reduced xsqr=%g' % (niter, wss, actred)
                self.emit('status-message', message)
                return
            else:
                params, x = args

            params = splitlist(params, [len(t.parameters) for t in self.terms])

            for p, t in zip(params, self.terms):
                t.parameters = p

            return self(x)
                
        model = odr.Model(__fitfunction)
        data = odr.RealData(x, y)
        initial = flatten(t.parameters for t in self.terms)

        odrobj = odr.ODR(data, model, beta0=initial,  ifixb=[not k for k in lock], 
                         partol=1e-100, sstol=1e-100, maxit=maxiter)
        odrobj.set_job (fit_type=2)
        odrobj.set_iprint (iter=3, iter_step=1)
        for term in self.terms:
            term.set_reg(False)
        try:
            output = odrobj.run()
        finally:
            for term in self.terms:
                term.set_reg(True)

#        except:
#            raise
#            print >>sys.stderr, 'Fit den Vogel (but no problem)'
            

"""
    functions [
        id:S,
        func:S,
        name:S,
        params:S,
        lock:S,
        use:I
    ]
]
"""

from giraffe.project import create_id

class MFunctionSum(FunctionSum):
    def __init__(self, data):
        FunctionSum.__init__(self)
        self.data = data
        for f in self.data:
            if f.func in registry and not f.id.startswith('-'):
                self.add(f.func, f.name)
                self.terms[-1].data = f
            else:
                print >>sys.stderr, "function '%s' not found." %f.func
        self.connect('add-term', self.on_add_term)
        self.connect('remove-term', self.on_remove_term)

    def on_add_term(self, state, term):
        if hasattr(term, 'data') and term.data.id.startswith('-'):
            raise StopCommand
        row = self.data.append(id=create_id(), func=term.function.name, name=term.name)
        term.data = self.data[row]
        state['term'] = term
    def undo_add_term(self, state):
        term = state['term']
        term.data.id = '-'+term.data.id
        self.terms.remove(term)
        self.emit('remove-term', term)
    def redo_add_term(self, state):
        term = state['term']
        self.terms.append(term)
        self.emit('add-term', term)
        term.data.id = term.data.id[1:]
    on_add_term = command_from_methods2('graph/add-function-term', on_add_term, undo_add_term, redo=redo_add_term)

    def on_remove_term(self, state, term):
        if hasattr(term, 'data') and term.data.id.startswith('-'):
            raise StopCommand
        term.data.id = '-'+term.data.id
        state['term'] = term
    undo_remove_term = redo_add_term
    redo_remove_term = undo_add_term
    on_remove_term = command_from_methods2('graph/remove-function-term', on_remove_term, undo_remove_term, redo=redo_remove_term)
    
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

        ns = {}
        exec st in ns

        if 'move' in ns:
            self.move = ns['move']
        return ns['func']

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

from settings import DATADIR
registry = FunctionsRegistry(DATADIR+'data/functions')

import  keyword
import  wx
import  wx.stc  as  stc

if wx.Platform == '__WXMSW__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 10,
              'size2': 8,
             }
else:
    faces = { 'times': 'Times',
              'mono' : 'Courier',
              'helv' : 'Helvetica',
              'other': 'new century schoolbook',
              'size' : 10,
              'size2': 8,
             }

class PythonSTC(stc.StyledTextCtrl):

    def __init__(self, parent, ID,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0):
        stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)

        self.CmdKeyAssign(ord('B'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('N'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

        self.SetLexer(stc.STC_LEX_PYTHON)
        self.SetKeyWords(0, " ".join(keyword.kwlist))

#        self.SetProperty("fold", "1")
        self.SetProperty("tab.timmy.whinge.level", "1")
        self.SetMargins(0,0)

        self.SetViewWhiteSpace(False)
        #self.SetBufferedDraw(False)
        #self.SetViewEOL(True)
        #self.SetEOLMode(stc.STC_EOL_CRLF)
        #self.SetUseAntiAliasing(True)
        
        self.SetEdgeMode(stc.STC_EDGE_BACKGROUND)
        self.SetEdgeColumn(78)

        # Setup a margin to hold fold markers
        #self.SetFoldFlags(16)  ###  WHAT IS THIS VALUE?  WHAT ARE THE OTHER FLAGS?  DOES IT MATTER?
#        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
#        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
#        self.SetMarginSensitive(2, True)
#        self.SetMarginWidth(2, 12)

        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPressed)

        # Make some styles,  The lexer defines what each style is used for, we
        # just have to define what each style looks like.  This set is adapted from
        # Scintilla sample property files.

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(helv)s,size:%(size)d" % faces)
        self.StyleClearAll()  # Reset all to be like the default

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")

        # Python styles
        self.StyleSetSpec(stc.STC_P_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_P_COMMENTLINE, "fore:#007F00,face:%(other)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_P_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_P_STRING, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_P_CHARACTER, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_P_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_P_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_P_OPERATOR, "bold,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_P_IDENTIFIER, "fore:#000000,face:%(helv)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)
        self.SetCaretForeground("BLUE")

    def OnKeyPressed(self, event):
        if self.CallTipActive():
            self.CallTipCancel()
        key = event.KeyCode()

        if key == 32 and event.ControlDown():
            pos = self.GetCurrentPos()

            # Tips
            if event.ShiftDown():
                self.CallTipSetBackground("yellow")
                self.CallTipShow(pos, 'lots of of text: blah, blah, blah\n\n'
                                 'show some suff, maybe parameters..\n\n'
                                 'fubar(param1, param2)')
            # Code completion
            else:
                #lst = []
                #for x in range(50000):
                #    lst.append('%05d' % x)
                #st = " ".join(lst)
                #print len(st)
                #self.AutoCompShow(0, st)

                kw = keyword.kwlist[:]
                kw.append("zzzzzz?2")
                kw.append("aaaaa?2")
                kw.append("__init__?3")
                kw.append("zzaaaaa?2")
                kw.append("zzbaaaa?2")
                kw.append("this_is_a_longer_value")
                #kw.append("this_is_a_much_much_much_much_much_much_much_longer_value")

                kw.sort()  # Python sorts are case sensitive
                self.AutoCompSetIgnoreCase(False)  # so this needs to match

                # Images are specified with a appended "?type"
                for i in range(len(kw)):
                    if kw[i] in keyword.kwlist:
                        kw[i] = kw[i] + "?1"

                self.AutoCompShow(0, " ".join(kw))
        else:
            event.Skip()


    def OnUpdateUI(self, evt):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()

        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_P_OPERATOR:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_P_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)
            #pt = self.PointFromPosition(braceOpposite)
            #self.Refresh(True, wxRect(pt.x, pt.y, 5,5))
            #print pt
            #self.Refresh(False)


class PythonEditor(gui.Widget):
    def __init__(self, parent, **place):
        self._widget = PythonSTC(parent._widget, -1)
        gui.Widget.__init__(self, parent, **place)

        self._widget.Bind(wx.EVT_SET_FOCUS, self.evt_set_focus)
        self._widget.Bind(wx.EVT_KILL_FOCUS, self.evt_kill_focus)
        self._widget.Bind(wx.EVT_CHAR, self.evt_char)
        self._widget.Bind(wx.EVT_TEXT_ENTER, self.evt_enter)

    def evt_kill_focus(self, evt):
        if self._destroyed:
            return
        self.emit('kill-focus')

    def evt_char(self, evt):
        if self._destroyed:
            return
        self.emit('character', evt.GetKeyCode())
        evt.Skip()

    def evt_set_focus(self, evt):
        if self._destroyed:
            return
        self.emit('set-focus')
        evt.Skip()

    def evt_enter(self, evt):
        if self._destroyed:
            return
        self.emit('enter')

    def get_value(self): 
        if self._destroyed:
            return
        return self._widget.GetText()
    def set_value(self, val): 
        if self._destroyed:
            return
        self._widget.SetText(val)
    text = property(get_value, set_value)


class FunctionsWindow(gui.Window):
    def __init__(self):
        gui.Window.__init__(self, title='Functions', size=(500, 300))
        box = gui.Box(self, 'horizontal')

#        split = gui.Splitter(box, 'horizontal', stretch=1)
#        self.categories = gui.List(split)
        self.category = gui.List(box, model=RegModel(registry), stretch=1)
        self.category.connect('selection-changed', self.on_select_function)
        self.category.connect('item-activated', self.on_item_activated)

        rbox = gui.Box(box, 'vertical', stretch=2)

        toolbar = gui.Toolbar(rbox, stretch=0)
        toolbar.append(gui.Action('New', '', self.on_new, 'new.png'))
        toolbar.append(gui.Action('Delete', '', self.on_remove, 'remove.png'))
        toolbar.append(gui.Action('Save', '', self.on_save, 'save.png'))
        toolbar._widget.Realize()

        book = gui.Notebook(rbox)

        edit = gui.Box(book, 'vertical', page_label='edit')
        g = gui.Grid(edit, 2, 2, stretch=0, expand=True)
        g.layout.AddGrowableCol(1)
        gui.Label(g, 'Name', pos=(0,0))
        gui.Label(g, 'Parameters', pos=(1,0))
        self.name = gui.Text(g, pos=(0,1), expand=True)
        self.params = gui.Text(g, pos=(1,1), expand=True)

#        self.text = gui.Text(edit, multiline=True, stretch=1)
        self.text = PythonEditor(edit, stretch=1)

        extra = gui.Box(book, 'vertical', page_label='extra')
#        self.extra = gui.Text(extra, multiline=True, stretch=1)
        self.extra = PythonEditor(extra, stretch=1)

        self.functions = functions
        self.function = None

    def on_new(self):
        num = 0
        while 'function%d.function'%num in (f.filename.split('/')[-1] for f in registry):
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

    def on_item_activated(self, ind):
        self.emit('function-activated', self.category.model[ind])


if __name__ == '__main__':
    gui.Application().run(FunctionsWindow)
