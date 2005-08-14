# mingui
# minimalist gui for python

import sys
import time
import weakref
import os

import wx
import wx.py
import wx.glcanvas
import wx.grid
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, ListCtrlSelectionManagerMix
from wx.lib.colourselect import ColourSelect, EVT_COLOURSELECT
from wx.lib.scrolledpanel import ScrolledPanel

from giraffe.signals import HasSignals
from giraffe.settings import DATADIR


###############################################################################
# Application                                                                 #
###############################################################################

class _xSplashScreen(wx.SplashScreen):
    """
    Create a splash screen widget.
    """
    def __init__(self):
        aBitmap = wx.Image(name = DATADIR+"data/images/logo.png").ConvertToBitmap()
        splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT #| wx.NO_BORDER
        splashDuration = 1000 # milliseconds
        splashCallback = None
        wx.SplashScreen.__init__(self, aBitmap, splashStyle, splashDuration, splashCallback)
        wx.Yield()

class _xApplication(wx.App):
    def __init__(self):
        wx.App.__init__(self, redirect=False)

    def run(self, mainwinclass, *args, **kwds):
        self.mainwin = mainwinclass(*args, **kwds)
        self.SetTopWindow(self.mainwin._widget)
        self.mainwin.show(all=True)

    def OnExit(self):
        pass

class Singleton(object):
    _state = {}
    def __new__(cls, *p, **k):
        self = object.__new__(cls, *p, **k)
        self.__dict__ = cls._state
        return self

class Application(Singleton):
    def __init__(self):
        self._app = _xApplication()

    def get_mainwin(self):
        return self._app.mainwin
    mainwin = property(get_mainwin)

    def run(self, mainwinclass, *args, **kwds):
        self._app.run(mainwinclass, *args, **kwds)
        return self._app.MainLoop()

    def splash(self):
        splash = _xSplashScreen()
        splash.Show()

def run(mainwinclass):
    Application().run(mainwinclass)


###############################################################################
# Widget                                                                      #
###############################################################################

class Widget(HasSignals):
    def __init__(self, parent, **kwds):
        if parent is not None:
            self.parent = parent #weakref.proxy(parent)
        else:
            self.parent = None
        if hasattr(parent, '_add'):
            parent._add(self, **kwds)
        self._destroyed = False

    def destroy(self):
        self.destroyed = True
        self._widget.Destroy()

    def show(self, s=True, all=True):
        if s:
            self._widget.Show(all)
        else:
            self._widget.Hide() 

    def hide(self):
#        pass        
        self._widget.Hide()

    def place(self, **kwds):
        return self, kwds

    def get_min_size(self): return self._widget.GetMinSize()
    def set_min_size(self, size): self._widget.SetMinSize(size)
    min_size = property(get_min_size, set_min_size)

    def get_active(self): return self._widget.IsEnabled()
    def set_active(self, value): self._widget.Enable(value)
    active = property(get_active, set_active)

    size = property(lambda self: tuple(self._widget.GetSize()),
                    lambda self, sz: self._widget.SetSize(sz))

    position = property(lambda self: tuple(self._widget.GetPosition()),
                        lambda self, po: self._widget.SetPosition(po))


# http://wiki.wxpython.org/index.cgi/_xProportionalSplitterWindow
class _xProportionalSplitter(wx.SplitterWindow):
    def __init__(self,parent, id = -1, proportion=0.33, size = wx.DefaultSize):
        wx.SplitterWindow.__init__(self,parent,id,wx.Point(0, 0),size,0)
        self.SetMinimumPaneSize(50) #the minimum size of a pane.
        self.proportion = proportion
        if not 0 < self.proportion < 1:
            raise ValueError, "proportion value for _xProportionalSplitter must be between 0 and 1."
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
        self._widget = _xProportionalSplitter(parent._widget, -1, proportion=proportion)
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

        
class Grid(Widget):
    """
    usage:
    ------
    >>> g = gui.Grid(parent, rows, columns, **place)
    >>> child = gui.Label('Text', pos=(row, col), span=(x, y), expand=True)
    """
    def __init__(self, parent, rows, columns, **place):
        self._widget = wx.Panel(parent._widget, -1)
        Widget.__init__(self, parent, **place)
        self.layout = wx.GridBagSizer(rows, columns)
        self.layout.SetEmptyCellSize((0,0))
        self._widget.SetSizer(self.layout)
#        self.layout.SetSizeHints(self._widget)
        self._widget.SetAutoLayout(True)

#        self._widget.Bind(wx.EVT_SIZE, self.OnSize)


    def _add(self, widget, pos, span=(1,1), expand=False):
        self.layout.Add(widget._widget, pos, span, flag=wx.EXPAND|wx.ALL)

#        self.layout.CalcMin()
#        self.layout.RecalcSizes()
#        self.layout.SetSizeHints(self._widget)
        self._widget.Fit()
##    def OnSize(self, evt):
#        print evt.GetSize()
#        if self._widget.GetAutoLayout():
#            self._widget.Layout()
#        evt.Skip()

class Spin(Widget):
    """
    usage:
    ------
    >>> spin = gui.Spin(parent, **place)
    >>> spin.value = 16
    >>> spin.value
    16

    signals:
    --------
    modified(value)
    """
    def __init__(self, parent, **place):
        self._widget = wx.SpinCtrl(parent._widget, -1)
        Widget.__init__(self, parent, **place) 
        self._widget.Bind(wx.EVT_SPINCTRL, self.on_spin)

    def get_value(self): return self._widget.GetValue()
    def set_value(self, val): self._widget.SetValue(val)
    value = property(get_value, set_value)

    def on_spin(self, event):
        self.emit('modified', self.value)

class Text(Widget):
    """
    usage:
    ------
    >>> t = gui.Text(parent, multiline=False, **place)
    >>> t.text = 'hello'
    >>> t.text
    'hello, world'

    signals:
    --------
    set-focus
    kill-focus
    character(keycode)
    """
    def __init__(self, parent, multiline=False, align='default', **place):
        style = 0
        if multiline:
            style |= wx.TE_MULTILINE 
	else:
            style |= wx.TE_PROCESS_ENTER
        if align != 'default':
            style |= {'left':wx.TE_LEFT, 'right':wx.TE_RIGHT, 'center':wx.TE_CENTRE}[align]
        self._widget = wx.TextCtrl(parent._widget, -1, style=style)
        Widget.__init__(self, parent, **place)
        self._widget.Bind(wx.EVT_SET_FOCUS, self.evt_set_focus)
        self._widget.Bind(wx.EVT_KILL_FOCUS, self.evt_kill_focus)
        self._widget.Bind(wx.EVT_CHAR, self.evt_char)
        self._widget.Bind(wx.EVT_TEXT_ENTER, self.evt_enter)

    def evt_kill_focus(self, evt):
        if self._destroyed:
            return
        self.emit('kill-focus')

    def evt_char(self, evt):
        if self._destroyed:
            return
        self.emit('character', evt.GetKeyCode())
        evt.Skip()

    def evt_set_focus(self, evt):
        if self._destroyed:
            return
        self.emit('set-focus')
        evt.Skip()

    def evt_enter(self, evt):
        if self._destroyed:
            return
        self.emit('enter')

    def get_value(self): 
        if self._destroyed:
            return
        return self._widget.GetValue()
    def set_value(self, val): 
        if self._destroyed:
            return
        self._widget.SetValue(val)
    text = property(get_value, set_value)

    
class Choice(Widget):
    def __init__(self, parent, **place):
        self._widget = wx.Choice(parent._widget, -1)
        Widget.__init__(self, parent, **place)
        self._widget.Bind(wx.EVT_CHOICE, self.on_choice)

    def append(self, s):
        self._widget.Append(s)

    def get_value(self): return self._widget.GetSelection()
    def set_value(self, sel): self._widget.SetSelection(sel)
    value = property(get_value, set_value)

    def on_choice(self, event):
        self.emit('select', self.value)


class xPopup(wx.PopupWindow):
    pass
#    def ProcessLeftDown(self, event):
#        self.lst.ProcessEvent(event)
#        return False


class PixmapChoice(Widget):
    def __init__(self, parent, **place):
#        bimp = wx.Image('../data/images/'+'arrow.png').ConvertToBitmap()
        bimp = self.create_colored_bitmap((30, 10), (100, 80, 120))
        self._widget = wx.BitmapButton(parent._widget, -1, bimp, style=wx.BU_EXACTFIT)
        Widget.__init__(self, parent, **place) 
        self.imagelist = wx.ImageList(20, 10)

        self._widget.Bind(wx.EVT_BUTTON, self.on_button)

        self.images = {}
        self.items = []

        self.down = False

    def create_colored_bitmap(self, size, rgb):
        dc = wx.MemoryDC()
        bmp = wx.EmptyBitmap(*size)
        dc.SelectObject(bmp)
        dc.BeginDrawing()
        dc.SetBackground(wx.Brush(wx.Colour(*rgb)))
        dc.Clear()
        dc.EndDrawing()

        return bmp

    def on_button(self, event):
        if self.down:
            self.on_kill_focus(None)
            return
        self.win = win = xPopup(self._widget, wx.SUNKEN_BORDER)
        lst = wx.ListCtrl(win, -1, size=(120, 220), style=wx.LC_SMALL_ICON)
        win.lst = lst
#        lst.InsertColumn(0, 'col')
#        lst.SetImageList(self.imagelist, wx.IMAGE_LIST_NORMAL)
        lst.SetImageList(self.imagelist, wx.IMAGE_LIST_SMALL)
        lst.SetItemSpacing(0, 1)
        for i, img in enumerate(self.items):
            lst.InsertImageItem(i, img)
        pos = self._widget.ClientToScreen( (0,0) )
        sz = self._widget.GetSize()
        win.Position(pos, (0,sz[1]))
        win.SetSize(lst.GetSize())
        win.Show(True)
#        win.Popup()
        lst.SetFocus()
        lst.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_sel)
        self._widget.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)
        self.down = True
        self._selection = -1

    def on_sel(self, event):
        i = event.GetIndex()
        bitmap = self.images[self.items[i]]
        self._widget.SetBitmapLabel(bitmap)
        wx.CallAfter(self.win.Destroy)
        self.down = False
        self._selection = i
        self.emit('select', i)

    def set_selection(self, idx):
        bitmap = self.images[self.items[idx]]
        self._selection = idx
        self._widget.SetBitmapLabel(bitmap)
    def get_selection(self):
        return self._selection
    value = property(get_selection, set_selection)

    def on_kill_focus(self, event):
        try:
            self.win.Destroy()
            self.down = False
        except wx.PyDeadObjectError:
            pass

    def append(self, bitmap):
        if isinstance(bitmap, basestring):
            bitmap = wx.Image(DATADIR+'data/images/'+bitmap).ConvertToBitmap()
        id = self.imagelist.Add(bitmap)
        self.images[id] = bitmap
        self.items.append(id)

class ColorSelect(Widget):
    def __init__(self, parent, **place):
        self._widget = ColourSelect(parent._widget, -1, size=(100, 10))
        Widget.__init__(self, parent, **place)

class Frame(Widget):
    def __init__(self, parent, orientation, title='', **kwds):
        self._widget = wx.Panel(parent._widget, -1)
        self._box = wx.StaticBox(self._widget, -1, title)
        Widget.__init__(self, parent, **kwds)
        if orientation == 'horizontal':
            self.layout = wx.StaticBoxSizer(self._box, wx.HORIZONTAL)
        elif orientation == 'vertical':
            self.layout = wx.StaticBoxSizer(self._box, wx.VERTICAL)
        else:
            raise NameError
        self._widget.SetSizer(self.layout)
        self._widget.SetAutoLayout(True)

    def _add(self, widget, expand=True, stretch=1.0):
#        widget._widget.Reparent(self.parent._widget)
        if expand:
            expand = wx.EXPAND
        else:
            expand = 0
        self.layout.Add(widget._widget, stretch, wx.EXPAND)
#        self.layout.SetSizeHints(self._widget)
#        self._widget.Layout()

class Scrolled(Widget):
    def __init__(self, parent, **place):
        self._widget = ScrolledPanel(parent._widget, -1, style=wx.SUNKEN_BORDER)
        Widget.__init__(self, parent, **place)

        self.layout = wx.BoxSizer(wx.VERTICAL)
        self._widget.SetSizer(self.layout)
        self._widget.SetAutoLayout(True)
        self._widget.SetupScrolling()

    def _add(self, widget):
        self.layout.Add(widget._widget, 1., wx.EXPAND)
#        self.layout.SetSizeHints(self._widget)



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
#        self.layout.SetSizeHints(self._widget)



class Checkbox(Widget):
    """ A a labelled box which by default is either on (checkmark is visible) 
        or off (no checkmark). 
    """
    def __init__(self, parent, **place):
        self._widget = wx.CheckBox(parent._widget, -1)
        Widget.__init__(self, parent, **place)

        self._widget.Bind(wx.EVT_CHECKBOX, self.on_event)

    def get_state(self):
        return self._widget.GetValue()
    def set_state(self, state):
        self._widget.SetValue(state)
    state = property(get_state, set_state)

    def on_event(self, event):
        self.emit('modified', self.state)

class Progressbar(Widget):
    def __init__(self, parent, **place):
        self._widget = wx.Gauge(parent._widget, -1, 100)
        Widget.__init__(self, parent, **place)

    def set_value(self, value): self._widget.SetValue(value); wx.Yield()
    def get_value(self): return self._widget.GetValue()
    value = property(get_value, set_value)

    def set_range(self, range): self._widget.SetRange(range)
    def get_range(self): return self._widget.GetRange()
    range = property(get_range, set_range)

class Button(Widget):
    def __init__(self, parent, text, toggle=False, **kwds):
        if toggle:
            self._widget = wx.ToggleButton(parent._widget, -1, text)
            self._widget.Bind(wx.EVT_TOGGLEBUTTON, self.on_toggled)
        else:
            self._widget = wx.Button(parent._widget, -1, text)
            self._widget.Bind(wx.EVT_BUTTON, self.on_clicked)

        Widget.__init__(self, parent, **kwds)

        self._widget.Bind(wx.EVT_LEFT_DCLICK, self.OnMouse)

    def OnMouse(self, evt):
        self.emit('double-clicked')

    def on_clicked(self, evt):
        self.emit('clicked')

    def on_toggled(self, evt):
        self.emit('toggled', evt.IsChecked())

    def get_state(self):
        return self._widget.GetValue()
    def set_state(self, state):
        self._widget.SetValue(state)
    state = property(get_state, set_state)

    text = property(lambda self: self._widget.GetLabel(), lambda self, t: self._widget.SetLabel(t))


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


#1. In the OnBeginDrag method, the line:
#
#      sel_item, flags = self.tree.HitTest(event.GetPoint()) 
#
#does not work because of a problem with event.GetPoint(). This can be replaced with the following:
#
## Get the Mouse Position on the Screen 
#(windowx, windowy) = wx.wxGetMousePosition() 
## Translate the Mouse's Screen Position to the Mouse's Control Position 
#(x, y) = self.tree.ScreenToClientXY(windowx, windowy) 
## Now use the tree's HitTest method to find out about the potential drop target for the current mouse position 
#(sel_item, flags) = self.tree.HitTest((x, y))

#http://wiki.wxpython.org/index.cgi/TreeControls
#http://wiki.wxpython.org/index.cgi/TreeCtrlDnD
#http://wiki.wxpython.org/index.cgi/LongRunningTasks

class _xDropTarget(wx.DropTarget):
    def __init__(self, window):
        wx.DropTarget.__init__(self)
        self.window = window

    def OnDrop(self, x, y):
        return self.window.OnRequestDrop(x, y)

    def OnData(self, x, y, d):
        if self.GetData():
            self.window.AddItem(x, y)
        return d

    def OnDragOver(self, x, y, d):
        return self.window.OnHover(x, y)

def create_wx_data_object(formats, data=None):
    compobj = wx.DataObjectComposite()
    indivi = []

    for format in formats:
        if format == 'filename':
            obj = wx.FileDataObject()
            if data:
                for filename in data.get_data(format):
                    obj.AddFile(filename)
        elif format == 'text':
            obj = wx.TextDataObject()
            if data:
                obj.SetText(data.get_data(format))
        else:
            obj = wx.CustomDataObject(wx.CustomDataFormat(format))
            if data:
                obj.SetData(data.get_data(format))
        compobj.Add(obj)
        indivi.append(obj)

    return compobj, indivi

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

        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.on_begin_drag)


    def on_begin_drag(self, event):
        data = self.lst.emit('drag-begin', event.GetIndex())
        if len(data) != 1:
#            event.Deny()
            return

        dropSource = wx.DropSource(self)
        data, _ = create_wx_data_object(data[0].supported_formats, data[0])
        dropSource.SetData(data)
        result = dropSource.DoDragDrop(wx.Drag_AllowMove)

        event.Allow()

    def OnHover(self, x, y):
        """
        Override this to perform an action when a drag action is
        hovering over the widget.
        """
        item, flags = self.HitTest(wx.Point(x, y))
        if not (flags & wx.LIST_HITTEST_ONITEM):
            item = -1

        result = self.lst.emit('drop-hover', item)
        if 'move' in result:
            return wx.DragMove
        elif 'copy' in result:
            return wx.DragCopy
        else:
            return wx.DragNone

    def OnRequestDrop(self, x, y):
        item, flags = self.HitTest(wx.Point(x, y))
        if not (flags & wx.LIST_HITTEST_ONITEM):
            item = -1

        result = self.lst.emit('drop-ask', item)
        if True in result:
            return True
        else:
            return False

    def AddItem(self, x, y):
        item, flags = self.HitTest(wx.Point(x, y))
        print >>sys.stderr, item, flags

        for obj in self.lst.dropobjs:
            if obj.GetFormat() == wx.DataFormat(wx.DF_UNICODETEXT):
                format, data = 'text', obj.GetText()
                if len(data):
                    obj.SetData('')
                    break
            elif obj.GetFormat() == wx.DataFormat(wx.DF_FILENAME):
                format, data = 'filename', obj.GetFilenames()
                if len(data):
                    obj.SetData('')
                    break
            else:
                if obj.GetDataSize() > 0:
                    format, data = obj.GetFormat().GetId(), obj.GetDataHere()
                    if data is not None:
                        obj.SetData('')
                        break

        result = self.lst.emit('dropped', item, format, data)

    def getpixmap(self, filename):
        if filename is None:
            return None
        if filename not in self.pixmaps:
            self.pixmaps[filename] = self.imagelist.Add(wx.Image(DATADIR+'data/images/'+filename).ConvertToBitmap())
        return self.pixmaps[filename]

    def OnGetItemText(self, item, col):
        if hasattr(self.lst.model, 'get'):
            return str(self.lst.model.get(item, self.lst.columns[col]))
        else:
            if col == 0:
                return str(self.lst.model[item])
            else:
                raise AttributeError

    def OnGetItemImage(self, item):
        if hasattr(self.lst.model, 'get_image'):
            return self.getpixmap(self.lst.model.get_image(item))


class List(Widget):
    def __init__(self, parent, model=None, columns=None, headers=False, editable=False, **kwds):
        flags = wx.LC_REPORT|wx.LC_VIRTUAL|wx.BORDER_SUNKEN
        if not headers:
            flags |= wx.LC_NO_HEADER
        if editable:
            flags |= wx.LC_EDIT_LABELS

        self._widget = _xListCtrl(self, parent._widget, -1, style=flags)
        Widget.__init__(self, parent, **kwds)

        if model is None:
            model = ListModel()

        if columns is None:
            columns = [None]

        self.selection = []

        self._columns = columns
        self._model = model
        if hasattr(self._model, 'connect'):
            self._model.connect('modified', self.update)

        self.update()

        self._widget.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_item_activated)
        for event in (wx.EVT_LIST_ITEM_SELECTED, wx.EVT_LIST_ITEM_DESELECTED, wx.EVT_LIST_ITEM_FOCUSED):
            self._widget.Bind(event, self.on_update_selection)

        self.can_drop = False
        self.drop_formats = []

        self._widget.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)

    def on_right_click(self, evt):
        item, flags = self._widget.HitTest(evt.GetPosition())
        if not (flags & wx.LIST_HITTEST_ONITEM):
            item = -1
        self.emit('right-click', item)
        evt.Skip()

    def enable_drop(self, formats):
        self.can_drop = True
        self.formats = formats
        self.setup_drop()

    def setup_drop(self):
        target = _xDropTarget(self._widget)
        composite, self.dropobjs = create_wx_data_object(self.formats)
        target.SetDataObject(composite)
        self._widget.SetDropTarget(target)

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

        try:
            selection = self._widget.getSelection()
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

    def set_model(self, model):
        if model is None:
            model = ListModel()
        self._model = model
        if hasattr(self._model, 'connect'):
            self._model.connect('modified', self.update)
        self.update()
    def get_model(self):
        return self._model
    model = property(get_model, set_model)

    def setsel(self, sel):
        for item in sel:
            self._widget.SetItemState(item, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

    def update(self):
        self._widget.Freeze()
        sel = self.selection
        self._widget.ClearAll()
        self._widget.SetItemCount(len(self.model))
        for num, name in enumerate(self.columns):
            self._widget.InsertColumn(num, str(name))
        self.selection = sel
        for item in sel:
            self._widget.SetItemState(item, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
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

    def AddItem(self, x, y):
        item, flags = self.HitTest(wx.Point(x, y))

        try:
            items = self.tree.items + self.tree.roots
            item = items[[i._nodeid for i in items].index(item)]
        except ValueError:
            return


        for obj in self.tree.dropobjs:
            if obj.GetFormat() == wx.DataFormat(wx.DF_UNICODETEXT):
                format, data = 'text', obj.GetText()
                if len(data):
                    obj.SetData('')
                    break
            elif obj.GetFormat() == wx.DataFormat(wx.DF_FILENAME):
                format, data = 'filename', obj.GetFilenames()
                if len(data):
                    obj.SetData('')
                    break
            else:
                if obj.GetDataSize() > 0:
                    format, data = obj.GetFormat().GetId(), obj.GetDataHere()
                    if data is not None:
                        obj.SetData('')
                        break

        result = self.tree.emit('dropped', item, format, data)


class Tree(Widget):
    def __init__(self, parent, **place):
        self._widget = _xTreeCtrl(self, parent._widget)
        Widget.__init__(self, parent, **place)
        self.roots = []
        self.items = []

        self._widget.SetIndent(10)

        self.imagelist = wx.ImageList(16, 16)
        self._widget.SetImageList(self.imagelist)
        self.pixmaps = {}

        self._widget.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
        self._widget.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.on_label_edit)

        self._widget.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_expand)
        self._widget.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.on_collapse)

        self.tree = self._widget
        self.selection = None

    def on_sel_changed(self, evt):
        from itertools import chain
        for item in chain(self.items, self.roots):
            if self._widget.IsSelected(item._nodeid):
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
        node._nodeid = self._widget.AppendItem(parent._nodeid, str(node), 
                                               self.getpixmap(node.get_pixmap()))
        self.items.append(node)
        for child in node:
            self._add_node_and_children(node, child)
        self._widget.Expand(node._nodeid)

    def on_node_modified(self):
        self._widget.DeleteAllItems()
        self.items = []
        for root in self.roots:
            root._nodeid = self._widget.AddRoot(str(root), self.getpixmap(root.get_pixmap()))
            for node in root:
                self._add_node_and_children(root, node)
            self._widget.Expand(root._nodeid)
        if self.selection is not None:
            self._widget.SelectItem(self.selection._nodeid)


    def clear(self):
        self._widget.DeleteAllItems()
        self.roots = []
        self.items = []

    def enable_drop(self, formats):
        self.can_drop = True
        self.formats = formats
        self.setup_drop()

    def setup_drop(self):
        target = _xDropTarget(self._widget)
        composite, self.dropobjs = create_wx_data_object(self.formats)
        target.SetDataObject(composite)
        self._widget.SetDropTarget(target)



class Label(Widget):
    def __init__(self, parent, text, *args, **kwds):
        self._widget = wx.StaticText(parent._widget, -1, text)
        Widget.__init__(self, parent, *args, **kwds)

    text = property(lambda self: self._widget.GetLabel(), lambda self, t: self._widget.SetLabel(t))


# stuff for tool panels and main window
# long and ugly but it works nicely

class ToolPanel(Widget):
    def __init__(self, parent, position, *args, **kwds):
        self._widget = _xToolPanel(parent, position)
        Widget.__init__(self, parent, *args, **kwds)

    def _add(self, widget, page_label='', page_pixmap=''):
        if hasattr(widget._widget, 'Reparent'):
            widget._widget.Reparent(self._widget.panel)
        self._widget.add_page(page_label, page_pixmap, widget)

    def open(self, id):
        self._widget.open(id)

    def close(self, id=None):
        self._widget.close(id)

class _xToolPanel(wx.SashLayoutWindow):
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

        self.panel.SetSizer(self.box)
        self.panel.SetAutoLayout(True)

        self.contents = []
        self.buttons = []
        self.last_width = 180
        self.last_height = 120

    def create_colored_bitmap(self, size, rgb):
        dc = wx.MemoryDC()
        bmp = wx.EmptyBitmap(*size)
        dc.SelectObject(bmp)
        dc.BeginDrawing()
        dc.SetBackground(wx.Brush(wx.Colour(*rgb)))
        dc.Clear()
        dc.EndDrawing()

        return bmp

    def add_page(self, text, pixmap, widget):
        bimp = wx.Image(DATADIR+"data/images/"+pixmap).ConvertToBitmap()

        # create an empty bitmap
        dc = wx.MemoryDC()
        w, h = dc.GetTextExtent(text)
        wb, hb = bimp.GetSize()
        bmp = wx.EmptyBitmap(w + wb, max([h, hb]))
        bmp.SetMaskColour(self.GetBackgroundColour())
        dc.SelectObject(bmp)

        # draw bitmap and text
        dc.BeginDrawing()
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.SetFont(self.GetFont())
        dc.DrawBitmap(bimp, 0, 0, True)
        dc.DrawText(text, wb+5, 0)
        dc.EndDrawing()

        # rotate if nescessary
        if self.position in ['left', 'right']:
            bmp = bmp.ConvertToImage().Rotate90(False).ConvertToBitmap()

        ind = len(self.contents)

        btn = wx.NewId()
        self.toolbar.AddCheckTool(btn, bmp, bmp)#, "New")
        x, y = self.toolbar.GetToolBitmapSize()
	xb, yb = bmp.GetSize()
	self.toolbar.SetToolBitmapSize((max(x, xb), max(y, yb)))

        self.contentbox.Add(widget._widget, 1, wx.EXPAND)
        widget.hide()
        self.contentbox.Layout()

        widget._id = len(self.contents)
        self.contents.append(widget)
        self.buttons.append(btn)

        if self.position in ['left', 'right']:
            margin = self.GetEdgeMargin(wx.SASH_RIGHT)
            self.SetDefaultSize((self.toolbar.GetSize()[0] + margin, -1))
        else:
            margin = self.GetEdgeMargin(wx.SASH_TOP)
            self.SetDefaultSize((-1, self.toolbar.GetSize()[1] + margin))

    def open(self, id):
        if hasattr(id, '_id'):
            id = id._id
        for i, btn in enumerate(self.buttons):
            self.toolbar.ToggleTool(btn, i==id)

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
        if hasattr(id, '_id'):
            id = id._id
        if id is not None:
            self.contentbox.Hide(self.contents[id]._widget)
        self.contentbox.Layout()

        for i, btn in enumerate(self.buttons):
            self.toolbar.ToggleTool(btn, False)

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
        self._widget = _xMainPanel(parent._widget)
        Widget.__init__(self, parent, **place)
        self.bottom_panel = self._widget.bottom_panel
        self.left_panel = self._widget.left_panel
        self.right_panel = self._widget.right_panel

    def _add(self, widget, expand=True, stretch=1.0):
        if hasattr(widget._widget, 'Reparent'):
            widget._widget.Reparent(self._widget.remainingSpace)
        if expand:
            expand = wx.EXPAND
        else:
            expand = 0
        self._widget.main_box.Add(widget._widget, stretch, wx.EXPAND)
#        self._widget.main_box.SetSizeHints(widget._widget)


class _xMainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.bottom_panel = ToolPanel(self, 'bottom')
        self.right_panel = ToolPanel(self, 'right')
        self.left_panel = ToolPanel(self, 'left')

        # will occupy the space not used by the Layout Algorithm
        self.remainingSpace = wx.Panel(self, -1)#, style=wx.CLIP_CHILDREN)#, style=wx.SUNKEN_BORDER)

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
        action = self.tools[event.GetId()]
        if action.type == 'check':
            action(event.IsChecked())
        else:
            action()

    def append(self, action):
        if action is None:
            self._widget.AddSeparator()
        else:
            if action.pixmap is not None:
                bitmap = wx.Image(DATADIR+'data/images/'+action.pixmap).ConvertToBitmap()
            else:
                bitmap = None
            id = wx.NewId()
            if action.type == 'check':
                self._widget.AddCheckTool(id, bitmap, bitmap, action.name, action.desc)
            elif action.type == 'radio':
                self._widget.AddRadioTool(id, bitmap, bitmap, action.name, action.desc)
            else:
                self._widget.AddSimpleTool(id, bitmap, action.name, action.desc)
            self.tools[id] = action
            
            x, y = self._widget.GetToolBitmapSize()
            xb, yb = bitmap.GetSize()
            self._widget.SetToolBitmapSize((max(x, xb), max(y, yb)))
            action.upd.append([self._widget, id])

    def _add(self, child, **place):
        self._widget.AddControl(child._widget)
 

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
    def __init__(self, menubar=None, name=None):
        self._menu = wx.Menu()
        self.menubar = menubar
        self.name = name
        self.items = {}
        self._menu.Bind(wx.EVT_MENU, self.on_menu)
        if menubar is not None:
            menubar._widget.Append(self._menu, name)

    def append(self, action):
        if action is None:
            self._menu.AppendSeparator()
        else:
            id = wx.NewId()
            self.items[id] = action
            if action.accel is not None:
                name = action.name + '\t' + action.accel
            else:
                name = action.name
            if action.desc is not None:
                help = action.desc
            else:
                help = ''
#            self._menu.Append(id, name, help)
            item = wx.MenuItem(self._menu, id, name, help)
            if action.pixmap is not None:
                item.SetBitmap(wx.Image(DATADIR+'data/images/'+action.pixmap).ConvertToBitmap())
            self._menu.AppendItem(item)
    
            if self.menubar is not None:
                self.menubar.items[id] = action

    def on_menu(self, event):
        self.items[event.GetId()]()
        
###############################################################################
# top level window                                                            #
###############################################################################

class Window(Widget):
    def __init__(self, position=(50,50), size=(640,480), title='', statusbar=False):
        self._widget = wx.Frame(None, -1,  title, pos=position, size=size,
                                style=wx.DEFAULT_FRAME_STYLE)
        if statusbar:
            self._widget.CreateStatusBar()

        Widget.__init__(self, None)
        self.title = title
        self._widget.Bind(wx.EVT_CLOSE, self.on_close)
        icon = wx.EmptyIcon()
        icon.LoadFile(DATADIR+'install/grafit.ico', wx.BITMAP_TYPE_ICO)
        icon.CopyFromBitmap(wx.Image(DATADIR+'install/grafit16x16.png').ConvertToBitmap())
        self._widget.SetIcon(icon)

    title = property(lambda self: self._widget.GetTitle(), lambda self, t: self._widget.SetTitle(t))

    def set_status(self, t):
        sb = self._widget.GetStatusBar()
        sb.SetStatusText(t,0 )
        sb.Update()
        wx.Yield()
    status = property(lambda self: self._widget.GetStatusBar().GetStatusText(), 
                      set_status)

    def _add(self, child, **place):
        if isinstance(child, Toolbar):
            self._widget.SetToolBar(child._widget)
        elif isinstance(child, Menubar):
            self._widget.SetMenuBar(child._widget)
#        else:
#            Widget._add(self, child, **place)

    def close(self):
        self._widget.Close(True)

    def on_close(self, evt):
        ret = self.emit('close')
        if sum(bool(r) for r in ret) == len(ret):
            evt.Skip()

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
        self._widget = wx.glcanvas.GLCanvas(parent._widget, -1)#, attribList =[wx.glcanvas.WX_GL_DOUBLEBUFFER])
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
        btn = {wx.MOUSE_BTN_LEFT:1, wx.MOUSE_BTN_MIDDLE:2, wx.MOUSE_BTN_RIGHT:3}[evt.GetButton()]
        self.emit('button-pressed', x, y, btn)

    def OnMouseUp(self, evt):
        self._widget.ReleaseMouse()
        x, y = evt.GetPosition()
        btn = {wx.MOUSE_BTN_LEFT:1, wx.MOUSE_BTN_MIDDLE:2, wx.MOUSE_BTN_RIGHT:3}[evt.GetButton()]
        self.emit('button-released', x, y, btn)

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
            self.pixmaps[filename] = self.imagelist.Add(wx.Image(DATADIR+'data/images/'+filename).ConvertToBitmap())
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

class _xTableData(wx.grid.PyGridTableBase):
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

    def SetValue(self, row, col, value):
        self.data.set_data(col, row, value)

    def label_edited(self, column, name):
        if hasattr(self.data, 'label_edited'):
            self.data.label_edited(column, name)        

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
        self._widget = _xGrid(parent._widget, data)
        Widget.__init__(self, parent, **place)

class _xLabelEditor(wx.TextCtrl, HasSignals):
    def __init__(self, parent, column):
        wx.TextCtrl.__init__(self, parent, -1, parent.GetTable().data.get_column_name(column), 
                             style=wx.TE_PROCESS_ENTER|wx.TE_CENTRE)
        self.parent, self.column = parent, column
        self.destroyed = False

        rect = parent.CellToRect(0, column)
        self.SetSize((rect[2], parent.GetColLabelSize()))
        self.SetPosition(parent.CalcScrolledPosition(parent.GetRowLabelSize()+rect[0], 0))
        self.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.Bind(wx.EVT_TEXT_ENTER, self.on_enter)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

        self.SetFocus()

    def on_enter(self, evt):
        self.parent.GetTable().label_edited(self.column, self.GetValue())
        if not self.destroyed:
            self.destroyed = True
            self.Destroy()

    def on_kill_focus(self, evt):
        if not self.destroyed:
            self.destroyed = True
            self.Destroy()

class _xGrid(wx.grid.Grid):
    def __init__(self, parent, data):
        wx.grid.Grid.__init__(self, parent, -1)

        self.SetLabelFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.SetDefaultRowSize(20, False)

        table = _xTableData(data)

        # The second parameter means that the grid is to take ownership of the
        # table and will destroy it when done.  Otherwise you would need to keep
        # a reference to it and call it's Destroy method later.
        self.SetTable(table, True)

        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnRightDown)  
#        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)    
        self.Bind(wx.grid.EVT_GRID_RANGE_SELECT, self.OnRangeSelect)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.OnLabelLeftClick)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.OnLabelLeftDClick)

    def OnLabelLeftDClick(self, evt):
        evt.Skip()
        if evt.GetRow() != -1:
            return
        if hasattr(self.GetTable().data, 'label_edited'):
            self.edit = _xLabelEditor(self, evt.GetCol())

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


class Action(HasSignals):
    def __init__(self, name, desc, call, pixmap=None, accel=None, type='simple'):
        self.name, self.desc, self.call, self.pixmap, self.accel = name, desc, call, pixmap, accel
        self.type = type

        self._state = False
        self.upd = []

    def get_state(self):
        return self._state
    def set_state(self, state):
        self._state = state
        for w, id in self.upd:
            w.ToggleTool(id, state)
    state = property(get_state, set_state)

    def __call__(self, *args, **kwds):
        return self.call(*args, **kwds)
