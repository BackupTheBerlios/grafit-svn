import wx
from giraffe.signals import HasSignals


class Widget(HasSignals):
    def __init__(self, parent, **place):
        self.parent = parent
        if hasattr(self.parent, '_add'):
            self.parent._add(self, **place)

    def destroy(self):
        self.Destroy()

    def show(self, s=True, all=True):
        if s:
            self.Show(all)
        else:
            self.Hide() 

    def hide(self):
        self.Hide()

    def get_min_size(self): return self.GetMinSize()
    def set_min_size(self, size): self.SetMinSize(size)
    min_size = property(get_min_size, set_min_size)

    def get_active(self): return self.IsEnabled()
    def set_active(self, value): self.Enable(value)
    active = property(get_active, set_active)

    size = property(lambda self: tuple(self.GetSize()),
                    lambda self, sz: self.SetSize(sz))

    position = property(lambda self: tuple(self.GetPosition()),
                        lambda self, po: self.SetPosition(po))

class Window(wx.Frame, Widget):
    def __init__(self):
        wx.Frame.__init__(self, None, -1)
        Widget.__init__(self, None)


class Box(Widget):
    def __init__(self, parent, orientation, **kwds):
        self = wx.Panel(parent, -1)
        Widget.__init__(self, parent, **kwds)
        if orientation == 'horizontal':
            self.layout = wx.BoxSizer(wx.HORIZONTAL)
        elif orientation == 'vertical':
            self.layout = wx.BoxSizer(wx.VERTICAL)
        else:
            raise NameError
        self.SetSizer(self.layout)
        self.SetAutoLayout(True)

    def _add(self, widget, expand=True, stretch=1.0):
        if expand:
            expand = wx.EXPAND
        else:
            expand = 0
        self.layout.Add(widget, stretch, wx.EXPAND)
#        self.layout.SetSizeHints(self)



class Button(Widget, wx.Button):
    def __init__(self, parent, text, toggle=False, **place):
        wx.Button.__init__(self, parent, -1, text)
        Widget.__init__(self, parent, **place)

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
