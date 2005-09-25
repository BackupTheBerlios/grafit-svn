import os.path

import wx

import PIL.Image
from signals import HasSignals

class Container(HasSignals):
    def place(self, **kwds):
        return self, kwds

def _pil_to_wxbitmap(image):
    wi = wx.EmptyImage(image.size[0], image.size[1])
    wi.SetData(image.convert('RGB').tostring())
    wi.SetAlphaData(image.convert('RGBA').tostring()[3::4])
    return wi.ConvertToBitmap()
 
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

class Label(Widget, wx.StaticText):
    def __init__(self, place, text, **kwds):
        wx.StaticText.__init__(self, place[0], -1, text)
        Widget.__init__(self, place, **kwds)

class Image(Widget, wx.StaticBitmap):
    def __init__(self, place, image, **kwds):
#        image = image.convert('RGB')
#        wximg = wx.EmptyImage(image.size[0],image.size[1])
#        wximg.SetData(image.tostring())
#        bitmap = wximg.ConvertToBitmap()
        bitmap = _pil_to_wxbitmap(image)

        wx.StaticBitmap.__init__(self, place[0], -1, bitmap)
        Widget.__init__(self, place, **kwds)

class Button(Widget, wx.Button, wx.ToggleButton):
    def __init__(self, place, text, toggle=False, connect={}, **kwds):

        if toggle:
            wxbase = wx.ToggleButton
        else:
            wxbase = wx.Button

#        class _Button(Widget, wxbase):
#            pass
#        self.__class__ = _Button

        wxbase.__init__(self, place[0], -1, text)
        Widget.__init__(self, place, connect, **kwds)

#        self.Bind(wx.EVT_LEFT_DCLICK, self.emitter('double-clicked'), True)
        self.Bind(wx.EVT_BUTTON, self.emitter('clicked'))
        self.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggled)

    def on_toggled(self, evt):
        self.emit('toggled', evt.IsChecked())

    def toggled():
        doc = "Whether a toggle button is on or not"
        def fget(self): return self.GetValue()
        def fset(self, state): self.SetValue(state)
        return locals()
    toggled = property(**toggled())

    def text():
        doc = "Text to display inside the button"
        def fget(self): return self.GetLabel()
        def fset(self, text): self.SetLabel(text)
        return locals()
    text = property(**text())

class Singleton(object):
    _state = {}
    def __new__(cls, *p, **k):
        self = object.__new__(cls, *p, **k)
        self.__dict__ = cls._state
        return self

class Application(Singleton):
    def __init__(self):
        if not hasattr(self, '_app'):
            self._app = wx.App(redirect=False)

    def run(self, mainwin):
        self.mainwin = mainwin
        self._app.SetTopWindow(self.mainwin)
        self.mainwin.show()
        return self._app.MainLoop()

app = Application()

def run(mainwinclass):
    Application().run(mainwinclass)
