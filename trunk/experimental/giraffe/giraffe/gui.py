import wx
from  wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

import sys
sys.path.append('..')
sys.path.append('../lib')
from giraffe.signals import HasSignals

class Widget(HasSignals):
    def __init__(self, parent, **kwds):
        if hasattr(parent, '_add'):
            parent._add(self, **kwds)

    def show(self):
        self._widget.Show()

    def show_all(self):
        self._widget.Show(True)

    def hide(self):
        self._widget.Hide()

class Box(Widget):
    def __init__(self, parent, orientation, **kwds):
        if parent is None:
            self._widget = wx.Panel(None, -1)
        else:
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

class CustomWxApp(wx.App):
    def __init__(self, mainwinclass, *args, **kwds):
        self.mainwinclass = mainwinclass
        self.initargs, self.initkwds = args, kwds
        wx.App.__init__(self, redirect=False)

    def OnInit(self):
        self.mainwin = self.mainwinclass(*self.initargs, **self.initkwds)
        self.SetTopWindow(self.mainwin._widget)
        self.mainwin.show_all()
        return True

class Application(object):
    def __init__(self, mainwinclass, *args, **kwds):
        self._app = CustomWxApp(mainwinclass, *args, **kwds)

    def get_mainwin(self):
        return self._app.mainwin
    mainwin = property(get_mainwin)

    def run(self):
        return self._app.MainLoop()

class Window(Widget):
    def __init__(self, position=None, size=None, **kwds):
        self._widget = wx.Frame(None, -1,  'grafit', pos=position, size=size,
                                style=wx.DEFAULT_FRAME_STYLE)
        Widget.__init__(self, None, **kwds)

class Button(Widget):
    def __init__(self, parent, text, **kwds):
        self._widget = wx.Button(parent._widget, -1, text)
        Widget.__init__(self, parent, **kwds)
        self._widget.Bind(wx.EVT_BUTTON, self.on_clicked)

    def on_clicked(self, evt):
        self.emit('clicked')

class ListModel(HasSignals):
    def __init__(self):
        self.items = []
        
    # list model interface
    def get(self, row, column):
        return str(self.items[row])

    def __len__(self):
        return len(self.items)

    # behave as a sequence
    def append(self, item):
        self.items.append(item)
        self.emit('modified')

    def __setitem__(self, key, value):
        self.items[key] = value
        self.emit('modified')

    def __getitem__(self, key):
        return self.items[key]

class _CustomListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, lst, *args, **kwds):
        wx.ListCtrl.__init__(self, *args, **kwds)
        ListCtrlAutoWidthMixin.__init__(self)
        self.lst = lst

    def OnGetItemText(self, item, col):
        return self.lst.model.get(item, self.lst.columns[col])

class List(Widget):
    def __init__(self, parent, model=None, columns=None, headers=False, editable=False, **kwds):
        flags = wx.LC_REPORT|wx.LC_VIRTUAL|wx.BORDER_SUNKEN
        if not headers:
            flags |= wx.LC_NO_HEADER
        if editable:
            flags |= wx.LC_EDIT_LABELS

        self._widget = _CustomListCtrl(self, parent._widget, -1, style=flags)
        Widget.__init__(self, parent, **kwds)

        if model is None:
            model = ListModel()

        if columns is None:
            columns = [None]

        self._columns = columns
        self._model = model
        self._model.connect('modified', self.update)

        self.update()

        self._widget.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)
        for event in (wx.EVT_LIST_ITEM_SELECTED, wx.EVT_LIST_ITEM_DESELECTED, wx.EVT_LIST_ITEM_FOCUSED):
            self._widget.Bind(event, self.on_update_selection)

        self.selection = []

    def on_item_activated(self, event):
        self.emit('item-activated', event.m_itemIndex)

    def on_update_selection(self, event):
        # we can't update the selection here since if the event is ITEM_FOCUSED
        # the selection hasn't been updated yet
        wx.CallAfter(self.update_selection)
        event.Skip()

    def update_selection(self):
        # we have to work around the fact that a virtual ListCtrl does _not_
        # send ITEM_SELECTED or ITEM_DESELECTED events when multiple items
        # are selected / deselected
        selection = []

        item = -1
        while True:
            item = self._widget.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if item == -1:
                break
            selection.append(item)

        if selection != self.selection:
            self.selection = selection
            self.emit('selection-changed')

    def set_columns(self, columns):
        self._columns = columns
        self.update()
    def get_columns(self):
        return self._columns
    columns = property(get_columns, set_columns)
    
    def set_model(self, model):
        if model is None:
            model = ListModel()
        self._model = model
        self._model.connect('modified', self.update)
        self.update()
    def get_model(self):
        return self._model
    model = property(get_model, set_model)

    def update(self):
        self._widget.ClearAll()
        self._widget.SetItemCount(len(self.model))
        for num, name in enumerate(self.columns):
            self._widget.InsertColumn(num, str(name))


class Label(Widget):
    def __init__(self, parent, text, **kwds):
        self._widget = wx.StaticText(parent._widget, -1, text)
        Widget.__init__(self, parent, **kwds)

if __name__ == '__main__':
    app = Application(Window)
    app.run()
