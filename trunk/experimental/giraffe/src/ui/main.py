import sys
sys.path.append('/home/daniel/giraffe')

import os
import new
import wx
import wx.py
import wx.lib.buttons

from giraffe.ui.shapes import PlotCanvas, Plot
from giraffe.common import identity
from giraffe.worksheet import Worksheet


class Splash(wx.SplashScreen):
    def __init__(self):
        bmp = wx.Image("/home/daniel/grafit/pixmaps/logo.png").ConvertToBitmap()
        wx.SplashScreen.__init__(self, bmp,
                                 wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
                                 3000, None, -1)
#        self.Bind(wx.EVT_CLOSE, self.OnClose)

#    def OnClose(self, evt):
#        self.Hide()
#        frame = wxPythonDemo(None, "wxPython: (A Demonstration)")
#        frame.Show()
#        evt.Skip()  # Make sure the default handler runs too...

class PanelToolbar(wx.ToolBar):
    def __init__(self, parent):
        wx.ToolBar.__init__(self, parent)

class ToolPanel(wx.SashLayoutWindow):
    def __init__(self, parent, position):
        wx.SashLayoutWindow.__init__(self, parent, -1, 
                                     wx.DefaultPosition, (200, 30),
                                     wx.NO_BORDER|wx.SW_3D)
        self.parent = parent
        self.position = position
        if position in ['top', 'bottom']:
            self.SetDefaultSize((1000, 12))
        else:
            self.SetDefaultSize((12, 1000))

        data = { 'left' : (wx.LAYOUT_VERTICAL, wx.LAYOUT_LEFT, wx.SASH_RIGHT, wx.VERTICAL, wx.HORIZONTAL),
                 'right' : (wx.LAYOUT_VERTICAL, wx.LAYOUT_RIGHT, wx.SASH_LEFT, wx.VERTICAL, wx.HORIZONTAL), 
                 'top' : (wx.LAYOUT_HORIZONTAL, wx.LAYOUT_TOP, wx.SASH_BOTTOM, wx.HORIZONTAL, wx.VERTICAL), 
                 'bottom' : (wx.LAYOUT_HORIZONTAL, wx.LAYOUT_BOTTOM, wx.SASH_TOP, wx.HORIZONTAL, wx.VERTICAL) }
        d_orientation, d_alignment, d_showsash, d_btnbox, d_mainbox = data[position]

        self.SetOrientation(d_orientation)
        self.SetAlignment(d_alignment)
        self.SetSashVisible(d_showsash, True)

        self.panel = wx.Panel(self, -1)
        self.btnbox = wx.BoxSizer(d_btnbox)
        self.contentbox = wx.BoxSizer(d_mainbox)
        self.box = wx.BoxSizer(d_mainbox)
        if position in ['top', 'left']:
            self.box.Add(self.btnbox, 0)
            self.box.Add(self.contentbox, 1, wx.EXPAND)
        else:
            self.box.Add(self.contentbox, 1, wx.EXPAND)
            self.box.Add(self.btnbox, 0)

        self.panel.SetAutoLayout(True)
        self.panel.SetSizer(self.box)

        self.contents = []
        self.buttons = []
        self.last_width = 120
        self.last_height = 120

    def add_page(self, widget):
        bmp = wx.Bitmap("graph.xpm", wx.BITMAP_TYPE_XPM)
        ind = len(self.contents)

        btn = wx.lib.buttons.GenBitmapToggleButton(self.panel, -1, bmp, style=wx.BU_EXACTFIT)
        btn.SetBezelWidth(1)
        btn.Bind(wx.EVT_BUTTON, self.button_clicked(ind))
        self.btnbox.Add(btn, 0)
        self.contentbox.Add(widget, 1, wx.EXPAND)
        widget.Hide()
        self.contentbox.Layout()

        self.contents.append(widget)
        self.buttons.append(btn)

        if self.position in ['left', 'right']:
            margin = self.GetEdgeMargin(wx.SASH_RIGHT)
            self.SetDefaultSize((self.buttons[0].GetSize()[0] + margin, -1))
        else:
            margin = self.GetEdgeMargin(wx.SASH_TOP)
            self.SetDefaultSize((-1, self.buttons[0].GetSize()[1] + margin))


    def open(self, id):
        for i, widget in enumerate(self.contents):
            if i != id:
                self.contentbox.Hide(widget)
        for i, btn in enumerate(self.buttons):
            if i != id:
                btn.SetToggle(False)
        self.contentbox.Show(self.contents[id])
        self.contentbox.Layout()
        if self.position in ['left', 'right']:
            self.SetDefaultSize((self.last_width, -1))
        else:
            self.SetDefaultSize((-1, self.last_height))

        wx.LayoutAlgorithm().LayoutWindow(self.parent, self.parent.remainingSpace)
        self.parent.remainingSpace.Refresh()

    def close(self, id=None):
        if id is not None:
            self.contentbox.Hide(self.contents[id])
        self.contentbox.Layout()
        if self.position in ['left', 'right']:
            self.last_width = self.GetSize()[0]
            margin = self.GetEdgeMargin(wx.SASH_RIGHT)
            self.SetDefaultSize((self.buttons[0].GetSize()[0] + margin, -1))
        else:
            self.last_height = self.GetSize()[1]
            margin = self.GetEdgeMargin(wx.SASH_TOP)
            self.SetDefaultSize((-1, self.buttons[0].GetSize()[1] + margin))

        wx.LayoutAlgorithm().LayoutWindow(self.parent, self.parent.remainingSpace)
        self.parent.remainingSpace.Refresh()
 
    def button_clicked(self, id):
        def button_clicked_callback(self, event):
            if event.GetIsDown():
                self.open(id)
            else:
                self.close(id)
        return new.instancemethod(button_clicked_callback, self, self.__class__)

class ProjectTree(wx.TreeCtrl):
    def __init__(self, parent, project): 
        wx.TreeCtrl.__init__(self, parent, -1, 
                             style=wx.TR_DEFAULT_STYLE|wx.TR_EDIT_LABELS)
        self.SetIndent(10)
        self.project = project
        self.project.connect('add-item', self.on_add_item)

        self.root  = self.AddRoot('Project')
        self.items = {}

    def on_add_item(self, item):
        self.items[item.id] = self.AppendItem(self.root, item.name)


class Application(wx.App):
    def __init__(self, project):
        self.name = 'name'
        self.project = project
        wx.App.__init__(self, redirect=False)


    def OnInit(self):
        wx.Log_SetActiveTarget(wx.LogStderr())
#        s = Splash()
#        s.Show()

        frame = wx.Frame(None, -1,  self.name, pos=(50,50), size=(200,100),
                        style=wx.DEFAULT_FRAME_STYLE)
        frame.CreateStatusBar()

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        item = menu.Append(-1, "New Workshee (test)", "Test new worksheet")
        self.Bind(wx.EVT_MENU, self.OnNewWs, item)
        item = menu.Append(-1, "E&xit\tAlt-X", "Exit demo")
        self.Bind(wx.EVT_MENU, self.OnButton, item)
        menuBar.Append(menu, "&File")

        frame.SetMenuBar(menuBar)
        frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        win = MainWindow(frame, self.project)

        frame.SetSize((640, 480))
        win.SetFocus()
        self.window = win
        frect = frame.GetRect()

        self.SetTopWindow(frame)
        self.frame = frame
        frame.Show(True)
        return True

    def OnNewWs(self, evt):
        ws = Worksheet('test', self.project)

    def OnButton(self, evt):
        self.frame.Close(True)

    def OnCloseFrame(self, evt):
        evt.Skip()

    def run(self):
        self.MainLoop()

class MainWindow(wx.Panel):
    ID_WINDOW_LEFT2  = 5102
    ID_WINDOW_BOTTOM = 5103

    def __init__(self, parent, project):
        wx.Panel.__init__(self, parent, -1)
        self.project = project

        # A window like a statusbar
#        win = wx.SashLayoutWindow(self, self.ID_WINDOW_BOTTOM, wx.DefaultPosition, (200, 0), wx.NO_BORDER|wx.SW_3D)
##
#        win.SetDefaultSize((1000, 30))
#        win.SetOrientation(wx.LAYOUT_HORIZONTAL)
#        win.SetAlignment(wx.LAYOUT_BOTTOM)
#        win.SetSashVisible(wx.SASH_TOP, True)
#
#        self.bottom_panel = win
#
        self.bottom_panel = ToolPanel(self, 'bottom')
        self.script_window = wx.py.shell.Shell(self.bottom_panel.panel, -1, introText='Welcome to giraffe')
        self.bottom_panel.add_page(self.script_window)
        self.script_window.zoom(-1)
#        box = wx.BoxSizer(wx.VERTICAL)
#        box.Add(self.script_window, 1, wx.EXPAND)
#        panel.SetAutoLayout(True)
#        panel.SetSizer(box)
#

        self.right_panel = ToolPanel(self, 'right')
    
        # the left panel
        self.left_panel = ToolPanel(self, 'left')
        self.project_tree = ProjectTree(self.left_panel.panel, self.project)
        self.left_panel.add_page(self.project_tree)

        self.pikou = wx.py.shell.Shell(self.left_panel.panel, -1, introText='Welcome to giraffe')
        self.left_panel.add_page(self.pikou)


        # will occupy the space not used by the Layout Algorithm
        self.remainingSpace = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)

        self.graph = Plot()
        self.graphw = PlotCanvas(self.remainingSpace, self.graph)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.graphw, 1, wx.EXPAND)
        self.remainingSpace.SetSizer(box)

        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.OnSashDrag, id=self.left_panel.GetId())
        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.OnSashDrag, id=self.right_panel.GetId())
        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.OnSashDrag, id=self.bottom_panel.GetId())
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSashDrag(self, event):
        if event.GetDragStatus() == wx.SASH_STATUS_OUT_OF_RANGE:
            return

        id = event.GetId()

        if id == self.left_panel.GetId():
            self.left_panel.SetDefaultSize((event.GetDragRect().width, 1000))
        elif id == self.right_panel.GetId():
            self.right_panel.SetDefaultSize((event.GetDragRect().width, 1000))
        elif id == self.bottom_panel.GetId():
            self.bottom_panel.SetDefaultSize((1000, event.GetDragRect().height))
        else:
            print id

        wx.LayoutAlgorithm().LayoutWindow(self, self.remainingSpace)
        self.remainingSpace.Refresh()

    def OnSize(self, event):
        wx.LayoutAlgorithm().LayoutWindow(self, self.remainingSpace)

if __name__ == '__main__':
    app = Application(None)
    app.MainLoop()
