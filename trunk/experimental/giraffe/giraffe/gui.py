import wx
from  wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

from giraffe.signals import HasSignals

class Widget(HasSignals):
    def __init__(self, parent, **kwds):
        if hasattr(parent, '_add'):
            parent._add(self, **kwds)

class Box(Widget):
    def __init__(self, parent, orientation, **kwds):
        self._widget = wx.Panel(parent._widget, -1)
        Widget.__init__(self, parent, **kwds)
        if orientation == 'horizontal':
            self.layout = wx.BoxSizer(wx.HORIZONTAL)
        elif orientation == 'vertical':
            self.layout = wx.BoxSizer(wx.VERTICAL)
        else:
            raise NameError
        self._widget.SetSizer(self.layout)

    def _add(self, widget, expand=True, stretch=1.0):
        if expand:
            expand = wx.EXPAND
        else:
            expand = 0
        self.layout.Add(widget._widget, stretch, wx.EXPAND)
        self.layout.SetSizeHints(self._widget)
 
class Button(Widget):
    def __init__(self, parent, text, **kwds):
        self._widget = wx.Button(parent._widget, -1, text)
        Widget.__init__(self, parent, **kwds)
        self._widget.Bind(wx.EVT_BUTTON, self.on_clicked)

    def on_clicked(self, evt):
        self.emit('clicked')

class ListData(object):
    def get(self, row, column):
        return 'ass'

    def __len__(self):
        return 3

class VListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, lst, *args, **kwds):
        wx.ListCtrl.__init__(self, *args, **kwds)
        ListCtrlAutoWidthMixin.__init__(self)
        self.lst

    def OnGetItemText(self, item, col):
        return self.lst.model.get(self, row, self.lst.columns[column])

class ListModel(object):
    def get(self, row, column):
        return str(row) + '^' + str(column)

    def __len__(self):
        return 20

class List(Widget):
    def __init__(self, parent, model=None, columns=[], **kwds):
        self._widget = VListCtrl(parent._widget, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_NO_HEADER)
        Widget.__init__(self, parent, **kwds)

        self.model = model
        self.columns = columns
        if model is None:
            model = ListModel()

        self.update()

    def add_column(self, name):
        self.columns.append(name)

    def update(self):
        self._widget.ClearAll()
        for num, name in enumerate(self.columns):
            self._widget.InsertColumn(num, name)
        self._widget.SetItemCount(len(self.model))

class Label(Widget):
    def __init__(self, parent, text, **kwds):
        self._widget = wx.StaticText(parent._widget, -1, text)
        Widget.__init__(self, parent, **kwds)
