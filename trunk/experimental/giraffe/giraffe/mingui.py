import wx
from signals import HasSignals

class Container(HasSignals):
    def place(self, **kwds):
        return self, kwds

class Widget(HasSignals):
    def __init__(self, place):
        if place is None:
            self.parent = None
            placeargs = {}
        else:
            self.parent, placeargs = place
        if hasattr(self.parent, '_add'):
            self.parent._add(self, **placeargs)

    def destroy(self):
        self.Destroy()

    def show(self): self.visible = True
    def hide(self): self.visible = False

    def visible():
        doc = ""
        def fget(self): return self.IsShown()
        def fset(self, vis):
            if vis:
                self.Show(True)
            else:
                self.Hide()
        return locals()
    visible = property(**visible())

    def enabled():
        doc = ""
        def fget(self): return self.IsEnabled()
        def fset(self, value): self.Enable(value)
        return locals()
    enabled = property(**enabled())

    def size():
        doc = ""
        def fget(self): return tuple(self.GetSize())
        def fset(self, sz): self.SetSize(sz)
        return locals()
    size = property(**size())

    def position():
        doc = ""
        def fget(self): return tuple(self.GetPosition())
        def fset(self, po): self.SetPosition(po)
        return locals()
    position = property(**position())

class Window(wx.Frame, Widget, Container):
    def __init__(self):
        wx.Frame.__init__(self, None, -1)
        Widget.__init__(self, None)


class Box(Widget, Container, wx.Panel):
    def __init__(self, place, orientation='vertical'):
        wx.Panel.__init__(self, place[0], -1)
        Widget.__init__(self, place)
        if orientation == 'horizontal':
            self.layout = wx.BoxSizer(wx.HORIZONTAL)
        elif orientation == 'vertical':
            self.layout = wx.BoxSizer(wx.VERTICAL)
        else:
            raise NameError
        self.SetSizer(self.layout)
        self.SetAutoLayout(True)

    def __getitem__(self, key):
        return self.GetChildren()[key]

    def __iter__(self):
        for item in self.GetChildren():
            yield item

    def _add(self, widget, expand=True, stretch=1.0):
        if expand:
            expand = wx.EXPAND
        else:
            expand = 0
        self.layout.Add(widget, stretch, wx.EXPAND)
        self.layout.Layout()

class Button(Widget, wx.Button):
    def __init__(self, place, text, toggle=False):
        wx.Button.__init__(self, place[0], -1, text)
        Widget.__init__(self, place)

        self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouse)
        self.Bind(wx.EVT_BUTTON, self.on_clicked)

    def OnMouse(self, evt):
        self.emit('double-clicked')

    def on_clicked(self, evt):
        self.emit('clicked')

    def on_toggled(self, evt):
        self.emit('toggled', evt.IsChecked())

    def get_state(self):
        return self.GetValue()
    def set_state(self, state):
        self.SetValue(state)
    state = property(get_state, set_state)

    text = property(lambda self: self.GetLabel(), lambda self, t: self.SetLabel(t))
