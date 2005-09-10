import wx
from signals import HasSignals

class Container(HasSignals):
    def place(self, **kwds):
        return self, kwds

class Widget(HasSignals):
    def __init__(self, place, connect={}, **kwds):
        if place is None:
            self.parent = None
            placeargs = {}
        else:
            self.parent, placeargs = place
        if hasattr(self.parent, '_add'):
            self.parent._add(self, **placeargs)
        for signal, slot in connect.iteritems():
            self.connect(signal, slot)
        for k, v in kwds.iteritems():
            setattr(self, k, v)

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
        doc = """True if the control can be manipulated by the user. Disabled controls are typically
displayed in a different way, and do not respond to user actions."""
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

    def close(self):
        return self.Close()

class Window(wx.Frame, Widget, Container):
    def __init__(self, parent=None, connect={}, **kwds):
        wx.Frame.__init__(self, parent, -1)
        Widget.__init__(self, None, connect, **kwds)
        self.parent = parent

    title = property(lambda self: self.GetTitle(), lambda self, t: self.SetTitle(t))

class Dialog(wx.Dialog, Widget, Container):
    def __init__(self, parent=None, connect={}, **kwds):
        wx.Dialog.__init__(self, parent, -1, style=wx.THICK_FRAME)
        Widget.__init__(self, None, connect, **kwds)
        self.parent = parent

    def show(self, modal=False):
        if modal:
            return self.ShowModal()
        else:
            return Widget.show(self)
    title = property(lambda self: self.GetTitle(), lambda self, t: self.SetTitle(t))

class Box(Widget, Container, wx.Panel):
    def __init__(self, place, orientation='vertical', **kwds):
        wx.Panel.__init__(self, place[0], -1)
        Widget.__init__(self, place, **kwds)
        if orientation == 'horizontal':
            self.layout = wx.BoxSizer(wx.HORIZONTAL)
        elif orientation == 'vertical':
            self.layout = wx.BoxSizer(wx.VERTICAL)
        else:
            raise NameError
        self.SetAutoLayout(True)
        self.SetSizer(self.layout)

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
        self.layout.Add(widget, stretch, expand | wx.ADJUST_MINSIZE)
        self.layout.Layout()
        self.layout.Fit(self)

class Label(Widget, wx.StaticText):
    def __init__(self, place, text, **kwds):
        wx.StaticText.__init__(self, place[0], -1, text)
        Widget.__init__(self, place, **kwds)

class Image(Widget, wx.StaticBitmap):
    def __init__(self, place, image, **kwds):
        image = image.convert('RGB')
        wximg = wx.EmptyImage(image.size[0],image.size[1])
        wximg.SetData(image.tostring())
        bitmap = wximg.ConvertToBitmap()

        wx.StaticBitmap.__init__(self, place[0], -1, bitmap)
        Widget.__init__(self, place, **kwds)

class Button(Widget, wx.Button):
    def __init__(self, place, text, toggle=False, connect={}, **kwds):
        wx.Button.__init__(self, place[0], -1, text)
        Widget.__init__(self, place, connect, **kwds)

#        self.Bind(wx.EVT_LEFT_DCLICK, self.emitter('double-clicked'), True)
        self.Bind(wx.EVT_BUTTON, self.emitter('clicked'))

#    def on_toggled(self, evt):
#        self.emit('toggled', evt.IsChecked())

    def state():
        def fget(self): return self.GetValue()
        def fset(self, state): self.SetValue(state)
        return locals()
    state = property(**state())

    def text():
        doc = "Text to display inside the button"
        def fget(self): return self.GetLabel()
        def fset(self, text): self.SetLabel(text)
        return locals()
    text = property(**text())

class Text(Widget, wx.TextCtrl):
    def __init__(self, place, multiline=False, connect={}, **kwds):
        style = 0
        if multiline:
            style |= wx.TE_MULTILINE
        else:
            style |= wx.TE_PROCESS_ENTER
        wx.TextCtrl.__init__(self, place[0], -1, style=style)
        Widget.__init__(self, place, connect, **kwds)

    def get_value(self):
        return self.GetValue()
    def set_value(self, val):
        self.SetValue(val)
    text = property(get_value, set_value)

class Notebook(Widget, Container, wx.Notebook):
    def __init__(self, place, connect={}, **kwds):
        wx.Notebook.__init__(self, place[0], -1)
        Widget.__init__(self, place, connect, **kwds)

        # item images
        self.imagelist = wx.ImageList(16, 16)
        self.SetImageList(self.imagelist)
        self.pixmaps = {}

        self.pages = []


    def getpixmap(self, filename):
        if filename is None:
            return None
        if filename not in self.pixmaps:
            self.pixmaps[filename] = self.imagelist.Add(wx.Image(DATADIR+'data/images/'+filename).ConvertToBitmap())
        return self.pixmaps[filename]

    def _add(self, widget, label="", page_pixmap=None):
        self.AddPage(widget, label)
        if page_pixmap is not None:
            self.SetPageImage(self.GetPageCount()-1, self.getpixmap(page_pixmap))
        self.pages.append(widget)

    def active_page():
        def fget(self): return self.pages[self.GetSelection()]
        def fset(self, page): self.SetSelection(self.pages.index(page))
        return locals()
    active_page = property(**active_page())

    def delete(self, widget):
        self.DeletePage(self.pages.index(widget))
        self.pages.remove(widget)

    def select(self, widget):
        if widget in range(len(self.pages)):
            self.SetSelection(widget)
        elif widget in self.pages:
            self.SetSelection(self.pages.index(widget))
        else:
            raise NameError


