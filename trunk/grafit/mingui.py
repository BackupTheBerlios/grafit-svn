import os.path

import PIL.Image

import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, ListCtrlSelectionManagerMix
from wx.lib.splitter import MultiSplitterWindow
from wx.html import HtmlWindow

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
#        image = image.convert('RGB')
#        wximg = wx.EmptyImage(image.size[0],image.size[1])
#        wximg.SetData(image.tostring())
#        bitmap = wximg.ConvertToBitmap()
        bitmap = _pil_to_wxbitmap(image)

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


    def getpixmap(self, image):
        if image not in self.pixmaps:
            self.pixmaps[image] = self.imagelist.Add(_pil_to_wxbitmap(images[image][16,16]))
        return self.pixmaps[image]

    def _add(self, widget, label="", image=None):
        self.AddPage(widget, label)
        if image is not None:
            self.SetPageImage(self.GetPageCount()-1, self.getpixmap(image))
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

class DirImageProvider(object):
    def __init__(self, dir):
        self.dir = dir
        files = [os.path.join(dir, f) for f in os.listdir(dir)
                                       if os.path.isfile(os.path.join(dir, f))]
        ids = [os.path.splitext(os.path.basename(f))[0] for f in files]
        self.ids = dict(zip(ids, files))

    def provide(self, id):
        if id in self.ids:
            return PIL.Image.open(self.ids[id])
        else:
            return None


class ImageCatalog(Singleton):
    def __init__(self):
        if not hasattr(self, 'images'):
            self.images = {}
            self.providers = []

    def __getitem__(self, id):
        if id not in self.images:
            for p in self.providers:
                img = p.provide(id)
                if img is not None:
                    self.register(id, img)
        return self.images[id]

    def register(self, id, image):
        self.images.setdefault(id, {})[image.size] = image

    def register_dir(self, dir):
        self.providers.append(DirImageProvider(dir))

images = ImageCatalog()

class ListData(HasSignals):
    def __init__(self):
        self.items = []
        
    # list data interface
    def get(self, row, column):
        r = self.items[row]
        try:
            return str(r[column])
        except (IndexError, TypeError):
            return str(r)

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


class _xListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin, ListCtrlSelectionManagerMix):
    def __init__(self, lst, *args, **kwds):
        wx.ListCtrl.__init__(self, *args, **kwds)
        ListCtrlAutoWidthMixin.__init__(self)
        ListCtrlSelectionManagerMix.__init__(self)
        self.lst = lst

        # item images
        self.imagelist = wx.ImageList(16, 16)
        self.SetImageList(self.imagelist, wx.IMAGE_LIST_NORMAL)
        self.SetImageList(self.imagelist, wx.IMAGE_LIST_SMALL)
        self.pixmaps = {}

    def getpixmap(self, filename):
        if filename is None:
            return None
        if isinstance(filename, wx.Bitmap):
            if id(filename) not in self.pixmaps:
                self.pixmaps[id(filename)] = self.imagelist.Add(filename)
            filename = id(filename)
        if filename not in self.pixmaps:
            self.pixmaps[filename] = self.imagelist.Add(wx.Image(DATADIR+'data/images/'+filename).ConvertToBitmap())
        return self.pixmaps[filename]

    def OnGetItemText(self, item, col):
        if hasattr(self.lst.data, 'get'):
            return str(self.lst.data.get(item, self.lst.columns[col]))
        else:
            if col == 0:
                return str(self.lst.data[item])
            else:
                raise AttributeError

    def OnGetItemImage(self, item):
        if hasattr(self.lst.data, 'get_image'):
            return self.getpixmap(self.lst.data.get_image(item))


class List(Widget, _xListCtrl):
    def __init__(self, place, data=None, columns=None, headers=False, editable=False, 
                 connect={}, **kwds):
        flags = wx.LC_REPORT|wx.LC_VIRTUAL|wx.BORDER_SUNKEN
        if not headers:
            flags |= wx.LC_NO_HEADER
        if editable:
            flags |= wx.LC_EDIT_LABELS

        _xListCtrl.__init__(self, self, place[0], -1, style=flags)
        Widget.__init__(self, place, connect, **kwds)

        if data is None:
            data = ListData()

        if columns is None:
            columns = [None]

        self.selection = []

        self._columns = columns
        self._data = data
        if hasattr(self._data, 'connect'):
            self._data.connect('modified', self.update)

        self.update()

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)
        for event in (wx.EVT_LIST_ITEM_SELECTED, wx.EVT_LIST_ITEM_DESELECTED, wx.EVT_LIST_ITEM_FOCUSED):
            self.Bind(event, self.on_update_selection)

        self.can_drop = False
        self.drop_formats = []

        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)

    def on_right_click(self, evt):
        item, flags = self.HitTest(evt.GetPosition())
        if not (flags & wx.LIST_HITTEST_ONITEM):
            item = -1
        self.emit('right-click', item)
        evt.Skip()

    def on_item_activated(self, event):
        self.emit('item-activated', self.data[event.m_itemIndex])

    def on_update_selection(self, event):
        # we can't update the selection here since if the event is ITEM_FOCUSED
        # the selection hasn't been updated yet
        wx.CallAfter(self.update_selection)
        event.Skip()

    def update_selection(self):
        # we have to work around the fact that a virtual ListCtrl does _not_
        # send ITEM_SELECTED or ITEM_DESELECTED events when multiple items
        # are selected / deselected

        try:
            selection = self.getSelection()
        except wx.PyDeadObjectError:
            return
        if selection != self.selection:
            self.selection = selection
            self.emit('selection-changed')

    def set_columns(self, columns):
        self._columns = columns
        self.update()
    def get_columns(self):
        return self._columns
    columns = property(get_columns, set_columns)

    def set_data(self, data):
        if data is None:
            data = ListData()
        self._data = data
        if hasattr(self._data, 'connect'):
            self._data.connect('modified', self.update)
        self.update()
    def get_data(self):
        return self._data
    data = property(get_data, set_data)

    def setsel(self, sel):
        for item in sel:
            self.SetItemState(item, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

    def update(self):
        self.Freeze()
        sel = self.selection
        self.ClearAll()
        self.SetItemCount(len(self.data))
        for num, name in enumerate(self.columns):
            self.InsertColumn(num, str(name))
        self.selection = sel
        for item in sel:
            self.SetItemState(item, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        self.resizeLastColumn(-1)
        self.Thaw()

class Splitter(Widget, Container, MultiSplitterWindow):
    def __init__(self, place, orientation, **kwds):
        self.orientation = orientation
        MultiSplitterWindow.__init__(self, place[0], style=wx.SP_LIVE_UPDATE)
        Widget.__init__(self, place, **kwds)
        self.SetOrientation({'horizontal':wx.HORIZONTAL, 'vertical':wx.VERTICAL}[orientation])

    def _add(self, widget, width=-1, stretch=0):
        widget._stretch = stretch
        if width == -1:
            width = widget.GetBestSize()[self.orientation=='vertical']
        self.AppendWindow(widget, width)

    def _OnMouse(self, evt):
        evt.ShiftDown = lambda: True
        return MultiSplitterWindow._OnMouse(self, evt)

    def _SizeSizeWindows(self):
        total_window_w = self.GetClientSize()[self.orientation == 'vertical'] \
                         - 2*self._GetBorderSize() - self._GetSashSize()*(len(self._windows)-1)

        for win, sash in zip(self._windows, self._sashes):
            if win._stretch == 0:
                total_window_w -= sash

        total_stretch = sum(w._stretch for w in self._windows)

        for i, win in enumerate(self._windows):
            if win._stretch != 0:
                self._sashes[i] = total_window_w*win._stretch/total_stretch

        MultiSplitterWindow._SizeWindows(self)

    _SizeWindows = _SizeSizeWindows

def _pil_to_wxbitmap(image):
    wi = wx.EmptyImage(image.size[0], image.size[1])
    wi.SetData(image.convert('RGB').tostring())
    wi.SetAlphaData(image.convert('RGBA').tostring()[3::4])
    return wi.ConvertToBitmap()
    
class TreeNode(HasSignals):
    def __init__(self):
        self.children = []

    def __iter__(self):
        return iter(self.children)
    
    def __str__(self):
        return 'TreeNode'

    def get_pixmap(self):
        return None

    def append(self, child):
        self.children.append(child)
        child.connect('modified', self.on_child_modified)
        self.emit('modified')

    def on_child_modified(self):
        self.emit('modified')

class _xTreeCtrl(wx.TreeCtrl):
    def __init__(self, tree, parent):
        wx.TreeCtrl.__init__(self, parent, -1, style=wx.TR_DEFAULT_STYLE|wx.TR_EDIT_LABELS|wx.SUNKEN_BORDER)
        self.tree = tree

    def OnHover(self, x, y):
        """
        Override this to perform an action when a drag action is
        hovering over the widget.
        """
        item, flags = self.HitTest(wx.Point(x, y))
#        if not (flags & wx.TREE_HITTEST_ONITEM):
#            item = -1
        try:
            items = self.tree.items + self.tree.roots
            item = items[[i._nodeid for i in items].index(item)]
        except ValueError:
            return wx.DragNone

        result = self.tree.emit('drop-hover', item)
        if 'move' in result:
            return wx.DragMove
        elif 'copy' in result:
            return wx.DragCopy
        else:
            return wx.DragNone

    def OnRequestDrop(self, x, y):
        item, flags = self.HitTest(wx.Point(x, y))
#        if not (flags & wx.LIST_HITTEST_ONITEM):
#            item = -1
        try:
            items = self.tree.items + self.tree.roots
            item = items[[i._nodeid for i in items].index(item)]
        except ValueError:
            return False

        result = self.tree.emit('drop-ask', item)
        if True in result:
            return True
        else:
            return False

    def AddItem(self, x, y, data):
        item, flags = self.HitTest(wx.Point(x, y))

        try:
            items = self.tree.items + self.tree.roots
            item = items[[i._nodeid for i in items].index(item)]
        except ValueError:
            return

        result = self.tree.emit('dropped', item, data)


class Tree(Widget, _xTreeCtrl):

    def __init__(self, place, **kwds):
        _xTreeCtrl.__init__(self, self, place[0])
        Widget.__init__(self, place, **kwds)
        self.roots = []
        self.items = []

        self.SetIndent(10)

        self.imagelist = wx.ImageList(16, 16)
        self.SetImageList(self.imagelist)
        self.pixmaps = {}

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.on_label_edit)

        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_expand)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.on_collapse)

        self.tree = self
        self.selection = None

    def on_sel_changed(self, evt):
        from itertools import chain
        for item in chain(self.items, self.roots):
            if self.IsSelected(item._nodeid):
                self.emit('selected', item)
                self.selection = item
                return
        self.selection = None

    def on_label_edit(self, evt):
        item = self.id_to_item(evt.GetItem())
        label = evt.GetLabel()
        if hasattr(item, 'rename') and label != '' and item.rename(label):
            evt.Veto()

    def on_expand(self, evt):
        item = self.id_to_item(evt.GetItem())
        if hasattr(item, 'open'):
            item.open()

    def on_collapse(self, evt):
        item = self.id_to_item(evt.GetItem())
        if hasattr(item, 'close'):
            item.close()

    def id_to_item(self, id):
        items = self.items + self.roots
        return items[[i._nodeid for i in items].index(id)]

    def getpixmap(self, filename):
        if filename is None:
            return None
        if filename not in self.pixmaps:
            self.pixmaps[filename] = self.imagelist.Add(wx.Image(DATADIR+'data/images/'+filename).ConvertToBitmap())
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
        node._nodeid = self.AppendItem(parent._nodeid, str(node))#, self.getpixmap(node.get_pixmap()))
        self.items.append(node)
        for child in node:
            self._add_node_and_children(node, child)
        self.Expand(node._nodeid)

    def on_node_modified(self):
        self.DeleteAllItems()
        self.items = []
        for root in self.roots:
            root._nodeid = self.AddRoot(str(root))#, self.getpixmap(root.get_pixmap()))
            for node in root:
                self._add_node_and_children(root, node)
            self.Expand(root._nodeid)
        if self.selection is not None:
            self.SelectItem(self.selection._nodeid)


    def clear(self):
        self.DeleteAllItems()
        self.roots = []
        self.items = []

    def enable_drop(self, formats):
        self.can_drop = True
        self.formats = formats
        target = _xDropTarget(self)
        self.composite = create_wx_data_object(self.formats)
        target.SetDataObject(self.composite)
        self.SetDropTarget(target)
        target.formats = formats

class Html(Widget, HtmlWindow):
    def __init__(self, place, connect={}, **kwds):
        HtmlWindow.__init__(self, place[0], -1)
        Widget.__init__(self, place, connect, **kwds)
        self.SetStandardFonts()

            
app = Application()

def run(mainwinclass):
    Application().run(mainwinclass)
