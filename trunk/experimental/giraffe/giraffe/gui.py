import sys
import wx
import wx.py
from  wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

import sys
sys.path.append('..')
sys.path.append('../lib')
from giraffe.signals import HasSignals

# this module absolutely needs documentation!

class xApplication(wx.App):
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
        self._app = xApplication(mainwinclass, *args, **kwds)

    def get_mainwin(self):
        return self._app.mainwin
    mainwin = property(get_mainwin)

    def run(self):
        return self._app.MainLoop()

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

class Splitter(Widget):
    def __init__(self, parent, orientation, **place):
        self._widget = wx.SplitterWindow(parent._widget, -1)
        Widget.__init__(self, parent, **place)
        self.first = None
        self.second = None
        self.orientation = orientation

    def _add(self, widget):
        if self.first is None:
            self.first = widget
        elif self.second is None:
            self.second = widget
            if self.orientation == 'horizontal':
                self._widget.SplitHorizontally(self.first._widget, self.second._widget)
            elif self.orientation == 'vertical':
                self._widget.SplitVertically(self.first._widget, self.second._widget)
        else:
            raise NameError, 'TODO'
        

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
        self._widget.SetAutoLayout(True)

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

    def __delitem__(self, key):
        del self.items[key]
        self.emit('modified')

class xListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
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

        self._widget = xListCtrl(self, parent._widget, -1, style=flags)
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


class TreeNode(HasSignals):
    def __init__(self):
        self.children = []

    def __iter__(self):
        return iter(self.children)
    
    def __str__(self):
        return 'TreeNode'

    def append(self, child):
        self.children.append(child)
        child.connect('modified', self.on_child_modified)
        self.emit('modified')

    def on_child_modified(self):
        self.emit('modified')

class Tree(Widget):
    def __init__(self, parent, **place):
        self._widget = wx.TreeCtrl(parent._widget, -1,
                                   style=wx.TR_DEFAULT_STYLE|wx.TR_EDIT_LABELS|wx.SUNKEN_BORDER)
        Widget.__init__(self, parent, **place)
        self._widget.SetIndent(10)
        self.roots = []

    def append(self, node):
        self.roots.append(node)
        node.connect('modified', self.on_node_modified)
        self.on_node_modified()

    def remove(self, node):
        self.roots.remove(node)
        node.disconnect('modified', self.on_node_modified)
        self.on_node_modified()

    def _add_node_and_children(self, parent, node):
        self._widget.AppendItem(parent._nodeid, str(node))
        for child in node:
            self._add_node_and_children(node, child)

    def on_node_modified(self):
        self._widget.DeleteAllItems()
        for root in self.roots:
            root._nodeid = self._widget.AddRoot(str(root))
            for node in root:
                self._add_node_and_children(root, node)

    def clear(self):
        self._widget.DeleteAllItems()
        self.roots = []





class Label(Widget):
    def __init__(self, parent, text, **kwds):
        self._widget = wx.StaticText(parent._widget, -1, text)
        Widget.__init__(self, parent, **kwds)


# stuff for tool panels and main window
# long and ugly but it works nicely

class ToolPanel(Widget):
    def __init__(self, parent, position, *args, **kwds):
        self._widget = xToolPanel(parent, position)
        Widget.__init__(self, parent, *args, **kwds)

    def _add(self, widget, page_label='', page_pixmap=''):
        widget._widget.Reparent(self._widget.panel)
        self._widget.add_page(page_label, page_pixmap, widget)

class xToolPanel(wx.SashLayoutWindow):
    """The areas on the left, top and bottom of the window holding tabs."""

    def __init__(self, parent, position):
        """`position` is one of 'left', 'right', 'top' or 'bottom'"""

        wx.SashLayoutWindow.__init__(self, parent, -1, wx.DefaultPosition,
                                     (200, 30), wx.NO_BORDER|wx.SW_3D)

        self.parent = parent
        self.position = position

        if position in ['top', 'bottom']:
            self.SetDefaultSize((1000, 0))
        else:
            self.SetDefaultSize((0, 1000))

        data = { 
            'left' : (wx.LAYOUT_VERTICAL, wx.LAYOUT_LEFT, wx.SASH_RIGHT,
                    wx.VERTICAL, wx.HORIZONTAL, wx.TB_VERTICAL),
            'right' : (wx.LAYOUT_VERTICAL, wx.LAYOUT_RIGHT, wx.SASH_LEFT, 
                    wx.VERTICAL, wx.HORIZONTAL, wx.TB_VERTICAL),
            'top' : (wx.LAYOUT_HORIZONTAL, wx.LAYOUT_TOP, wx.SASH_BOTTOM, 
                    wx.HORIZONTAL, wx.VERTICAL, wx.TB_HORIZONTAL),
            'bottom' : (wx.LAYOUT_HORIZONTAL, wx.LAYOUT_BOTTOM, wx.SASH_TOP, 
                        wx.HORIZONTAL, wx.VERTICAL, wx.TB_HORIZONTAL) }

        d_orientation, d_alignment, d_showsash, d_btnbox, d_mainbox, d_toolbar = data[position]

        self.SetOrientation(d_orientation)
        self.SetAlignment(d_alignment)
        self.SetSashVisible(d_showsash, True)

        self.panel = wx.Panel(self, -1)
        self.btnbox = wx.BoxSizer(d_btnbox)
        self.contentbox = wx.BoxSizer(d_mainbox)
        self.box = wx.BoxSizer(d_mainbox)
        if position in ['top', 'left']:
            self.box.Add(self.btnbox, 0, wx.EXPAND)
            self.box.Add(self.contentbox, 1, wx.EXPAND)
        else:
            self.box.Add(self.contentbox, 1, wx.EXPAND)
            self.box.Add(self.btnbox, 0, wx.EXPAND)

        self.toolbar = wx.ToolBar(self.panel, -1, 
                                  style=d_toolbar |wx.TB_3DBUTTONS)
#                                  |wx.SUNKEN_BORDER|wx.TB_3DBUTTONS)
        self.btnbox.Add(self.toolbar, 1)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_toolbar)

        self.panel.SetAutoLayout(True)
        self.panel.SetSizer(self.box)
        self.panel.SetAutoLayout(True)

        self.contents = []
        self.buttons = []
        self.last_width = 180
        self.last_height = 120

    def add_page(self, text, pixmap, widget):
        bimp = wx.Image("../data/images/"+pixmap).ConvertToBitmap()

        # create an empty bitmap
        dc = wx.MemoryDC()
        w, h = dc.GetTextExtent(text)
        wb, hb = bimp.GetSize()
        bmp = wx.EmptyBitmap(w + wb, max([h, hb]))
        dc.SelectObject(bmp)

        # draw bitmap and text
        dc.BeginDrawing()
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.SetFont(self.GetFont())
        dc.DrawBitmap(bimp, 0, 0, True)
        dc.DrawText(text, wb+5, 0)
        dc.EndDrawing()
        bmp.SetMaskColour(self.GetBackgroundColour())

        # rotate if nescessary
        if self.position in ['left', 'right']:
            bmp = bmp.ConvertToImage().Rotate90(False).ConvertToBitmap()

        ind = len(self.contents)

        btn = wx.NewId()
        self.toolbar.AddCheckTool(btn, bmp, bmp, "New", "Long help for 'New'")

        self.contentbox.Add(widget._widget, 1, wx.EXPAND)
        widget.hide()
        self.contentbox.Layout()

        self.contents.append(widget)
        self.buttons.append(btn)

        if self.position in ['left', 'right']:
            margin = self.GetEdgeMargin(wx.SASH_RIGHT)
            self.SetDefaultSize((self.toolbar.GetSize()[0] + margin, -1))
        else:
            margin = self.GetEdgeMargin(wx.SASH_TOP)
            self.SetDefaultSize((-1, self.toolbar.GetSize()[1] + margin))

    def open(self, id):
        for i, btn in enumerate(self.buttons):
            if i != id:
                self.toolbar.ToggleTool(btn, False)

        for i, widget in enumerate(self.contents):
            if i != id:
                self.contentbox.Hide(widget._widget)

        self.contentbox.Show(self.contents[id]._widget) 
        if hasattr(self.contents[id], 'on_open'):
            self.contents[id].on_open()

        if self.position in ['left', 'right']:
            self.SetDefaultSize((self.last_width, -1))
        else:
            self.SetDefaultSize((-1, self.last_height))

        self.contentbox.Layout()
        wx.LayoutAlgorithm().LayoutWindow(self.parent, self.parent.remainingSpace)
        self.parent.remainingSpace.Refresh()

    def close(self, id=None):
        if id is not None:
            self.contentbox.Hide(self.contents[id]._widget)
        self.contentbox.Layout()
        if self.position in ['left', 'right']:
            self.last_width = self.GetSize()[0]
            margin = self.GetEdgeMargin(wx.SASH_RIGHT)
            self.SetDefaultSize((self.toolbar.GetSize()[0] + margin, -1))
        else:
            self.last_height = self.GetSize()[1]
            margin = self.GetEdgeMargin(wx.SASH_TOP)
            self.SetDefaultSize((-1, self.toolbar.GetSize()[1] + margin))

        wx.LayoutAlgorithm().LayoutWindow(self.parent, self.parent.remainingSpace)
        self.parent.remainingSpace.Refresh()

    def on_toolbar(self, event):
        num = self.buttons.index(event.GetId())
        if self.toolbar.GetToolState(self.buttons[num]):
            self.open(num)
        else:
            self.close(num)

class MainPanel(Widget):
    def __init__(self, parent, **place):
        self._widget = xMainPanel(parent._widget)
        Widget.__init__(self, parent, **place)
        self.bottom_panel = self._widget.bottom_panel
        self.left_panel = self._widget.left_panel
        self.right_panel = self._widget.right_panel

    def _add(self, widget, expand=True, stretch=1.0):
        widget._widget.Reparent(self._widget.remainingSpace)
        if expand:
            expand = wx.EXPAND
        else:
            expand = 0
        self._widget.main_box.Add(widget._widget, stretch, wx.EXPAND)
        self._widget.main_box.SetSizeHints(widget._widget)


class xMainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.bottom_panel = ToolPanel(self, 'bottom')
        self.right_panel = ToolPanel(self, 'right')
        self.left_panel = ToolPanel(self, 'left')

        # will occupy the space not used by the Layout Algorithm
        self.remainingSpace = wx.Panel(self, -1)#, style=wx.SUNKEN_BORDER)

        self.main_box = wx.BoxSizer(wx.VERTICAL)
        self.remainingSpace.SetSizer(self.main_box)
        self.remainingSpace.SetAutoLayout(True)

        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.on_sash_drag, id=self.left_panel._widget.GetId())
        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.on_sash_drag, id=self.right_panel._widget.GetId())
        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.on_sash_drag, id=self.bottom_panel._widget.GetId())
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_sash_drag(self, event):
        if event.GetDragStatus() == wx.SASH_STATUS_OUT_OF_RANGE:
            return

        id = event.GetId()

        if id == self.left_panel._widget.GetId():
            self.left_panel._widget.SetDefaultSize((event.GetDragRect().width, 1000))
        elif id == self.right_panel._widget.GetId():
            self.right_panel._widget.SetDefaultSize((event.GetDragRect().width, 1000))
        elif id == self.bottom_panel._widget.GetId():
            self.bottom_panel._widget.SetDefaultSize((1000, event.GetDragRect().height))

        wx.LayoutAlgorithm().LayoutWindow(self, self.remainingSpace)
        self.remainingSpace.Refresh()

    def on_size(self, event):
        wx.LayoutAlgorithm().LayoutWindow(self, self.remainingSpace)


class Window(Widget):
    def __init__(self, position=(50,50), size=(640,480), menubar=False, statusbar=False, toolbar=False, 
                 panels = '', **kwds):
        self._widget = wx.Frame(None, -1,  'grafit', pos=position, size=size,
                                style=wx.DEFAULT_FRAME_STYLE)
        if toolbar:
            self._widget.CreateToolBar()
            tb = self._widget.GetToolBar()
            bitmap = wx.Image('/home/daniel/giraffe/data/images/console.png').ConvertToBitmap()
            tool = tb.AddSimpleTool(-1, bitmap, 'help_s',' help_l')
        if statusbar:
            self._widget.CreateStatusBar()

        if menubar:
            menubar = wx.MenuBar()
            menu = wx.Menu()
            menu.Append(-1, 'S&trint')
            menubar.Append(menu, '&Spring')
            self._widget.SetMenuBar(menubar)
        Widget.__init__(self, None, **kwds)

        self.main = xMainPanel(self._widget)
        if 'b' in panels:
            self.bottom_panel = self.main.bottom_panel
        if 'l' in panels:
            self.left_panel = self.main.left_panel
        if 'r' in panels:
            self.right_panel = self.main.right_panel

    def _add(self, widget, expand=True, stretch=1.0):
        widget._widget.Reparent(self.main.remainingSpace)
        if expand:
            expand = wx.EXPAND
        else:
            expand = 0
        self.main.main_box.Add(widget._widget, stretch, wx.EXPAND)
        self.main.main_box.SetSizeHints(widget._widget)

class Shell(Widget):
    def __init__(self, parent, locals, **kwds):
        self._widget = wx.py.shell.Shell(parent._widget, -1, locals=locals)
        Widget.__init__(self, parent, **kwds)
        self._widget.setLocalShell()
        self._widget.zoom(-1)

    def run(self, cmd):
        return self._widget.push(cmd)

    def prompt(self):
        return self._widget.prompt()

    def clear(self):
        return self._widget.clear()


class Notebook(Widget):
    def __init__(self, parent, **place):
        self._widget = wx.Notebook(parent._widget, -1)
        Widget.__init__(self, parent, **place)
        self.ass = wx.Button(self._widget.GetParent(), -1, 'x')
        self.ass.SetSize((25, 25))
        self.ass.SetPosition((300, 0))
        self.ass.Bind(wx.EVT_BUTTON, self.on_x_button)
        self.il = wx.ImageList(16, 16)
        self.wsidx = self.il.Add(wx.Image('../data/images/worksheet.png').ConvertToBitmap())
        self._widget.SetImageList(self.il)
        self._widget.Bind(wx.EVT_SIZE, self.on_resized)

    def _add(self, widget, page_label):
        self._widget.AddPage(widget._widget, page_label)
        self._widget.SetPageImage(self._widget.GetPageCount()-1, self.wsidx)

    def on_resized(self, event):
        self.ass.SetPosition((event.GetSize()[0] - 25, 0))
        event.Skip()

    def on_x_button(self, event):
        print 'x clicked'
