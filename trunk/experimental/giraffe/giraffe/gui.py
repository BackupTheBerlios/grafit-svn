import wx

from giraffe.signals import HasSignals

class Button(HasSignals):
    def __init__(self, parent, text):
        self._widget = wx.Button(parent._widget, -1, text)
        self._widget.Bind(wx.EVT_BUTTON, self.on_clicked)
        parent._add(self)

    def on_clicked(self, evt):
        self.emit('clicked')

class Box(object):
    def __init__(self, parent, orientation):
        self._widget = wx.Panel(parent._widget, -1)
        if orientation == 'horizontal':
            self.layout = wx.BoxSizer(wx.HORIZONTAL)
        elif orientation == 'vertical':
            self.layout = wx.BoxSizer(wx.VERTICAL)
        else:
            raise NameError
        self._widget.SetSizer(self.layout)
        self.layout.SetSizeHints(self._widget)

    def _add(self, widget):
        self.layout.Add(widget._widget, 1, wx.EXPAND)
        self.layout.SetSizeHints(self._widget)

class List(HasSignals):
    def __init__(self, parent):
        self._widget = wx.ListCtrl(parent._widget, -1)
        parent._add(self)

