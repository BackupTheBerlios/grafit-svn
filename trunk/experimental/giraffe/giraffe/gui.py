import sys
import weakref
import wx
import wx.py
import wx.glcanvas
import wx.grid
from  wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

import sys
sys.path.append('..')
sys.path.append('../lib')
from giraffe.signals import HasSignals

# this module absolutely needs documentation!

#class Pixmap(object):
#    def __init__(self, name):
#        self.name = name
#        self._bitmap = wx.Image('../data/images/'+name).ConvertToBitmap()

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
        if parent is not None:
            self.parent = weakref.proxy(parent)
        else:
            self.parent = None
        if hasattr(parent, '_add'):
            parent._add(self, **kwds)

    def show(self):
        self._widget.Show()

    def show_all(self):
        self._widget.Show(True)

    def hide(self):
        self._widget.Hide()

# http://wiki.wxpython.org/index.cgi/ProportionalSplitterWindow
class ProportionalSplitter(wx.SplitterWindow):
        def __init__(self,parent, id = -1, proportion=0.33, size = wx.DefaultSize):
                wx.SplitterWindow.__init__(self,parent,id,wx.Point(0, 0),size,0)
                self.SetMinimumPaneSize(50) #the minimum size of a pane.
                self.proportion = proportion
                if not 0 < self.proportion < 1:
                        raise ValueError, "proportion value for ProportionalSplitter must be between 0 and 1."
                self.ResetSash()
                self.Bind(wx.EVT_SIZE, self.OnReSize)
                self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnSashChanged, id=id)
                ##hack to set sizes on first paint event
                self.Bind(wx.EVT_PAINT, self.OnPaint)
                self.firstpaint = True

        def SplitHorizontally(self, win1, win2):
                if self.GetParent() is None: return False
                return wx.SplitterWindow.SplitHorizontally(self, win1, win2,
                        int(round(self.GetParent().GetSize().GetHeight() * self.proportion)))

        def SplitVertically(self, win1, win2):
                if self.GetParent() is None: return False
                return wx.SplitterWindow.SplitVertically(self, win1, win2,
                        int(round(self.GetParent().GetSize().GetWidth() * self.proportion)))

        def GetExpectedSashPosition(self):
                if self.GetSplitMode() == wx.SPLIT_HORIZONTAL:
                        tot = max(self.GetMinimumPaneSize(),self.GetParent().GetClientSize().height)
                else:
                        tot = max(self.GetMinimumPaneSize(),self.GetParent().GetClientSize().width)
                return int(round(tot * self.proportion))

        def ResetSash(self):
                self.SetSashPosition(self.GetExpectedSashPosition())

        def OnReSize(self, event):
                "Window has been resized, so we need to adjust the sash based on self.proportion."
                self.ResetSash()
                event.Skip()

        def OnSashChanged(self, event):
                "We'll change self.proportion now based on where user dragged the sash."
                pos = float(self.GetSashPosition())
                if self.GetSplitMode() == wx.SPLIT_HORIZONTAL:
                        tot = max(self.GetMinimumPaneSize(),self.GetParent().GetClientSize().height)
                else:
                        tot = max(self.GetMinimumPaneSize(),self.GetParent().GetClientSize().width)
                self.proportion = pos / tot
                event.Skip()

        def OnPaint(self,event):
                if self.firstpaint:
                        if self.GetSashPosition() != self.GetExpectedSashPosition():
                                self.ResetSash()
                        self.firstpaint = False
                event.Skip()

class Splitter(Widget):
    def __init__(self, parent, orientation, proportion=0.33, **place):
        self._widget = ProportionalSplitter(parent._widget, -1, proportion=proportion)
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

    def get_image(self, row):
        return None

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

    def index(self, value):
        return self.items.index(value)

class xListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, lst, *args, **kwds):
        wx.ListCtrl.__init__(self, *args, **kwds)
        ListCtrlAutoWidthMixin.__init__(self)
        self.lst = lst

        # item images
        self.imagelist = wx.ImageList(16, 16)
        self.SetImageList(self.imagelist, wx.IMAGE_LIST_NORMAL)
        self.SetImageList(self.imagelist, wx.IMAGE_LIST_SMALL)
        self.pixmaps = {}

    def getpixmap(self, filename):
        if filename is None:
            return None
        if filename not in self.pixmaps:
            self.pixmaps[filename] = self.imagelist.Add(wx.Image('../data/images/'+filename).ConvertToBitmap())
        return self.pixmaps[filename]

    def OnGetItemText(self, item, col):
        return self.lst.model.get(item, self.lst.columns[col])

    def OnGetItemImage(self, item):
        return self.getpixmap(self.lst.model.get_image(item))


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

        self.selection = []

        self._columns = columns
        self._model = model
        self._model.connect('modified', self.update)

        self.update()

        self._widget.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)
        for event in (wx.EVT_LIST_ITEM_SELECTED, wx.EVT_LIST_ITEM_DESELECTED, wx.EVT_LIST_ITEM_FOCUSED):
            self._widget.Bind(event, self.on_update_selection)


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
        try:
            while True:
                item = self._widget.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
                if item == -1:
                    break
                selection.append(item)
        except wx.PyDeadObjectError:
            pass

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
        self._widget.Freeze()
        sel = self.selection
        self._widget.ClearAll()
        self._widget.SetItemCount(len(self.model))
        for num, name in enumerate(self.columns):
            self._widget.InsertColumn(num, str(name))
        self.selection = sel
        for item in sel:
            self._widget.SetItemState(item, wx.LIST_STATE_SELECTED, wx.LIST_MASK_STATE)
        self._widget.resizeLastColumn(-1)
        self._widget.Thaw()


class TreeNode(HasSignals):
    def __init__(self):
        self.children = []

    def __iter__(self):
        return iter(self.children)
    
    def __str__(self):
        return 'TreeNode'

    def get_pixmap(self):
        return 'stock_folder.png'

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
        self.roots = []
        self.items = []

        self._widget.SetIndent(10)

        self.imagelist = wx.ImageList(16, 16)
        self._widget.SetImageList(self.imagelist)
        self.pixmaps = {}

        self._widget.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)

        self.selection = None

    def on_sel_changed(self, evt):
        from itertools import chain
        for item in chain(self.items, self.roots):
            if self._widget.IsSelected(item._nodeid):
                self.emit('selected', item)
                self.selection = item
                return
        self.selection = None


    def getpixmap(self, filename):
        if filename is None:
            return None
        if filename not in self.pixmaps:
            self.pixmaps[filename] = self.imagelist.Add(wx.Image('../data/images/'+filename).ConvertToBitmap())
        return self.pixmaps[filename]

    def append(self, node):
        self.roots.append(node)
        node.connect('modified', self.on_node_modified)
        self.on_node_modified()

    def remove(self, node):
        self.roots.remove(node)
        node.disconnect('modified', self.on_node_modified)
        self.on_node_modified()

    def _add_node_and_children(self, parent, node):
        node._nodeid = self._widget.AppendItem(parent._nodeid, str(node), 
                                               self.getpixmap(node.get_pixmap()))
        self._widget.Expand(node._nodeid)
        self.items.append(node)
        for child in node:
            self._add_node_and_children(node, child)

    def on_node_modified(self):
        self._widget.DeleteAllItems()
        self.items = []
        for root in self.roots:
            root._nodeid = self._widget.AddRoot(str(root), self.getpixmap(root.get_pixmap()))
            for node in root:
                self._add_node_and_children(root, node)
            self._widget.Expand(root._nodeid)

    def clear(self):
        self._widget.DeleteAllItems()
        self.roots = []
        self.items = []


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
                                  style=d_toolbar|wx.SUNKEN_BORDER|wx.TB_3DBUTTONS)
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
        self.toolbar.AddCheckTool(btn, bmp, bmp)#, "New")

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

class Toolbar(Widget):
    def __init__(self, parent, **place):
        self._widget = wx.ToolBar(parent._widget,
                                  style=wx.SUNKEN_BORDER|wx.TB_FLAT)
        Widget.__init__(self, parent, **place)
        self._widget.Bind(wx.EVT_TOOL, self.on_tool)
        self.tools = {}

    def on_tool(self, event):
        self.tools[event.GetId()]()

    def append(self, action):
        if action is None:
            self._widget.AddSeparator()
        else:
            bitmap = wx.Image('/home/daniel/giraffe/data/images/'+action.pixmap).ConvertToBitmap()
            id = wx.NewId()
            self._widget.AddSimpleTool(id, bitmap, action.name, action.desc)
            self.tools[id] = action

class Menubar(Widget):
    def __init__(self, parent, **place):
        self._widget = wx.MenuBar()
        self.frame = parent
        Widget.__init__(self, parent, **place)
        self.frame._widget.Bind(wx.EVT_MENU, self.on_menu)
        self.items = {}

    def on_menu(self, event):
        self.items[event.GetId()]()

class Menu(object):
    def __init__(self, menubar, name):
        self._menu = wx.Menu()
        self.menubar = menubar
        self.name = name
#        self.items = {} # wxid: action
        self._menu.Bind(wx.EVT_MENU, self.on_menu)
        menubar._widget.Append(self._menu, name)

    def append(self, action):
        if action is None:
            self._menu.AppendSeparator()
        else:
            id = wx.NewId()
            self._menu.Append(id, action.name)
            self.menubar.items[id] = action
    def on_menu(self, event):
        self.items[event.GetId()]()

class Window(Widget):
    def __init__(self, position=(50,50), size=(640,480), statusbar=False):
        self._widget = wx.Frame(None, -1,  'grafit', pos=position, size=size,
                                style=wx.DEFAULT_FRAME_STYLE)
        if statusbar:
            self._widget.CreateStatusBar()

        Widget.__init__(self, None)

    def _add(self, child, **place):
        if isinstance(child, Toolbar):
            self._widget.SetToolBar(child._widget)
        elif isinstance(child, Menubar):
            self._widget.SetMenuBar(child._widget)
#        else:
#            Widget._add(self, child, **place)

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


class OpenGLWidget(Widget):
    def __init__(self, parent, **place):
        self._widget = wx.glcanvas.GLCanvas(parent._widget, -1)
        Widget.__init__(self, parent, **place)

        self.init = False

        self._widget.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self._widget.Bind(wx.EVT_SIZE, self.OnSize)
        self._widget.Bind(wx.EVT_PAINT, self.OnPaint)
        
        for event in (wx.EVT_LEFT_DOWN, wx.EVT_MIDDLE_DOWN, wx.EVT_RIGHT_DOWN):
            self._widget.Bind(event, self.OnMouseDown)
        for event in (wx.EVT_LEFT_UP, wx.EVT_MIDDLE_UP, wx.EVT_RIGHT_UP):
            self._widget.Bind(event, self.OnMouseUp)
        self._widget.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self._lastsize = (-1, -1)

#        self.SetCursor(wx.CROSS_CURSOR)

    def redraw(self):
        self._widget.Refresh(False)

    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.

    def InitGL(self):
        self.emit('initialize-gl')
        self._widget.SwapBuffers()

    def OnSize(self, event):
#        self.emit('resize-gl', *event.GetSize())
        pass

    def OnPaint(self, event):
        dc = wx.PaintDC(self._widget)
        self._widget.SetCurrent()
        if not self.init:
            self.InitGL()
            self.init = True
        size = self._widget.GetSize()
        if size[0] <= 0 or size[1] <= 0:
            return
        if self._lastsize != size:
            self.emit('resize-gl', *size)
            self._lastsize = size
        self.emit('paint-gl', *size)
        self._widget.SwapBuffers()

    def OnMouseDown(self, evt):
        self._widget.CaptureMouse()
        x, y = evt.GetPosition()
        btn = evt.GetButton()
        if btn is wx.MOUSE_BTN_LEFT:
            self.emit('button-pressed', x, y, 1)
        elif btn is wx.MOUSE_BTN_RIGHT:
            self.emit('button-pressed', x, y, 3)
        elif btn is wx.MOUSE_BTN_MIDDLE:
            self.emit('button-pressed', x, y, 2)

    def OnMouseUp(self, evt):
        self._widget.ReleaseMouse()
        x, y = evt.GetPosition()
        btn = evt.GetButton()
        if btn is wx.MOUSE_BTN_LEFT:
            self.emit('button-released', x, y, 1)
        elif btn is wx.MOUSE_BTN_RIGHT:
            self.emit('button-released', x, y, 3)
        elif btn is wx.MOUSE_BTN_MIDDLE:
            self.emit('button-released', x, y, 2)

    def OnMouseMotion(self, evt):
        if evt.Dragging():
            x, y = evt.GetPosition()
            self.emit('mouse-moved', x, y)


class Notebook(Widget):
    def __init__(self, parent, **place):
        self._widget = wx.Notebook(parent._widget, -1)
        Widget.__init__(self, parent, **place)

        # item images
        self.imagelist = wx.ImageList(16, 16)
        self._widget.SetImageList(self.imagelist)
        self.pixmaps = {}

        self.pages = []

    def getpixmap(self, filename):
        if filename is None:
            return None
        if filename not in self.pixmaps:
            self.pixmaps[filename] = self.imagelist.Add(wx.Image('../data/images/'+filename).ConvertToBitmap())
        return self.pixmaps[filename]

    def _add(self, widget, page_label, page_pixmap=None):
        self._widget.AddPage(widget._widget, page_label)
        if page_pixmap is not None:
            self._widget.SetPageImage(self._widget.GetPageCount()-1, self.getpixmap(page_pixmap))
        self.pages.append(widget)

    def on_page_changed(self, evt):
        self.emit('page-changed', self.pages[evt.GetSelection()])
        evt.Skip()

    def delete(self, widget):
        self._widget.DeletePage(self.pages.index(widget))
        self.pages.remove(widget)

    def select(self, widget):
        if widget in range(len(self.pages)):
            self._widget.SetSelection(widget)
        elif widget in self.pages:
            self._widget.SetSelection(self.pages.index(widget))
        else:
            raise NameError

class TableData(wx.grid.PyGridTableBase):
    def __init__(self, data):
        wx.grid.PyGridTableBase.__init__(self)
        self.data = data
        self.data.connect('modified', self.ResetView)

        self.normal_attr = wx.grid.GridCellAttr()
        self.normal_attr.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

    def GetNumberRows(self):
        return self.data.get_n_rows()

    def GetNumberCols(self):
        return self.data.get_n_columns()

#    def IsEmptyCell(self, row, col):
#        return self.get_data(col, row) is None

    def GetValue(self, row, col):
        return self.data.get_data(col, row)

#    def SetValue(self, row, col, value):
#        self.worksheet[col][row] = float(value)

    def ResetView(self, view=None):
        """
        Reset the grid view. Call this to update the grid 
        if rows and columns have been added or deleted
        """
        if view is None:
            view = self.GetView()
        
        view.BeginBatch()
        
        for current, new, delmsg, addmsg in [
            (self._rows, self.GetNumberRows(), 
             wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, self.GetNumberCols(), 
             wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED, wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED), ]:
            
            if new < current:
                msg = wx.grid.GridTableMessage(self, delmsg, new, current-new)
                view.ProcessTableMessage(msg)
            elif new > current:
                msg = wx.grid.GridTableMessage(self, addmsg, new-current)
                view.ProcessTableMessage(msg)
                self.UpdateValues(view)

        view.EndBatch()

        self._rows = self.GetNumberRows()
        self._cols = self.GetNumberCols()

        # update the scrollbars and the displayed part of the grid
        view.AdjustScrollbars()
        view.ForceRefresh()

    def UpdateValues(self, view):
        """Update all displayed values"""
        # This sends an event to the grid table to update all of the values
        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        view.ProcessTableMessage(msg)

    def GetColLabelValue(self, col):
        return self.data.get_column_name(col)

    def GetRowLabelValue(self, row):
        return self.data.get_row_name(row)

class Table(Widget):
    def __init__(self, parent, data, **place):
        self._widget = xGrid(parent._widget, data)
        Widget.__init__(self, parent, **place)

class xGrid(wx.grid.Grid):
    def __init__(self, parent, data):
        wx.grid.Grid.__init__(self, parent, -1)

        self.SetLabelFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.SetDefaultRowSize(20, False)

        table = TableData(data)

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(table, True)

        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnRightDown)  
#        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)    
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

    def OnMouseWheel(self, evt):
        evt.Skip()

    def OnLabelLeftClick(self, evt):
#        pass
        evt.Skip()
        
    def OnRangeSelect(self, evt):
#        print evt, type(evt)
#        if evt.Selecting():
#            print >>sys.stderr, (evt.GetTopLeftCoords(), evt.GetBottomRightCoords())
        evt.Skip()

    def OnKeyDown(self, evt):
        if evt.KeyCode() != wx.WXK_RETURN:
            evt.Skip()
            return
        if evt.ControlDown():   # the edit control needs this key
            evt.Skip()
            return

        self.DisableCellEditControl()

        if not self.MoveCursorDown(True): 
            # add a new row
            self.GetTable().worksheet[self.GetGridCursorCol()][self.GetTable().GetNumberRows()] = nan


    def OnRightDown(self, event):
        pass

class Action(object):
    def __init__(self, name, desc, call, pixmap=None, accel=None):
        self.name, self.desc, self.call, self.pixmap, self.accel = name, desc, call, pixmap, accel

    def __call__(self, *args, **kwds):
        return self.call(*args, **kwds)
