import sys
sys.path.append('/home/daniel/giraffe')

import os
import wx
import wx.py

from giraffe.ui.shapes import PlotCanvas, Plot
from giraffe.common import identity
from giraffe.worksheet import Worksheet

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
    ID_WINDOW_LEFT1  = 5101
    ID_WINDOW_LEFT2  = 5102
    ID_WINDOW_BOTTOM = 5103


    def __init__(self, parent, project):
        wx.Panel.__init__(self, parent, -1)
        self.project = project

        # A window like a statusbar
        win = wx.SashLayoutWindow(self, self.ID_WINDOW_BOTTOM, wx.DefaultPosition, (200, 0), wx.NO_BORDER|wx.SW_3D)

        win.SetDefaultSize((1000, 30))
        win.SetOrientation(wx.LAYOUT_HORIZONTAL)
        win.SetAlignment(wx.LAYOUT_BOTTOM)
        win.SetSashVisible(wx.SASH_TOP, True)

        self.bottomWindow = win

        panel = wx.Panel(self.bottomWindow, -1)
        self.script_window = wx.py.shell.Shell(panel, -1)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.script_window, 1, wx.EXPAND)
        panel.SetAutoLayout(True)
        panel.SetSizer(box)

        # A window to the left of the client window
        win =  wx.SashLayoutWindow(self, self.ID_WINDOW_LEFT1, wx.DefaultPosition, (200, 30), wx.NO_BORDER|wx.SW_3D)

        win.SetDefaultSize((120, 1000))
        win.SetOrientation(wx.LAYOUT_VERTICAL)
        win.SetAlignment(wx.LAYOUT_LEFT)
        win.SetSashVisible(wx.SASH_RIGHT, True)
        self.leftWindow1 = win

        # Another window to the left of the client window
        win = wx.SashLayoutWindow(self, self.ID_WINDOW_LEFT2, wx.DefaultPosition, (200, 30), wx.NO_BORDER|wx.SW_3D)

        win.SetDefaultSize((120, 1000))
        win.SetOrientation(wx.LAYOUT_VERTICAL)
        win.SetAlignment(wx.LAYOUT_RIGHT)
        win.SetSashVisible(wx.SASH_LEFT, True)

        self.leftWindow2 = win

        win = wx.Panel(self.leftWindow1, -1)

        self.project_tree = ProjectTree(self, self.project)

        btn = wx.ToggleButton(win, 10011, "He", style=wx.BU_EXACTFIT)
        self.btn = btn
        self.Bind(wx.EVT_TOGGLEBUTTON, self.button_clicked, btn)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(btn, 0)
        box.Add(self.project_tree, 1, wx.EXPAND)

#        box.SetSizeHints(win)

        win.SetAutoLayout(True)
        win.SetSizer(box)

        # will occupy the space not used by the Layout Algorithm
        self.remainingSpace = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)

        self.graph = Plot()
        self.graphw = PlotCanvas(self.remainingSpace, self.graph)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.graphw, 1, wx.EXPAND)
        self.remainingSpace.SetSizer(box)

        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.OnSashDrag, id=self.ID_WINDOW_LEFT1)
        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.OnSashDrag, id=self.ID_WINDOW_LEFT2)
        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.OnSashDrag, id=self.ID_WINDOW_BOTTOM)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def button_clicked(self, event):
        if event.IsChecked():
            self.project_tree.Show()
            self.leftWindow1.SetDefaultSize((300, -1))
        else:
            self.project_tree.Hide()
#            self.leftWindow1.Fit()
            margin = self.leftWindow1.GetSize()[0] - self.leftWindow1.GetClientSize()[0]
            print margin
            self.leftWindow1.SetDefaultSize((self.btn.GetSize()[0]+margin, -1))
#            self.leftWindow1.SetDefaultSize((self.leftWindow1.GetMinimumSizeX(), -1))

        wx.LayoutAlgorithm().LayoutWindow(self, self.remainingSpace)
        self.remainingSpace.Refresh()


    def OnSashDrag(self, event):
        if event.GetDragStatus() == wx.SASH_STATUS_OUT_OF_RANGE:
            return

        id = event.GetId()

        if id == self.ID_WINDOW_LEFT1:
            self.leftWindow1.SetDefaultSize((event.GetDragRect().width, 1000))
        elif id == self.ID_WINDOW_LEFT2:
            self.leftWindow2.SetDefaultSize((event.GetDragRect().width, 1000))
        elif id == self.ID_WINDOW_BOTTOM:
            self.bottomWindow.SetDefaultSize((1000, event.GetDragRect().height))
        else:
            print id

        wx.LayoutAlgorithm().LayoutWindow(self, self.remainingSpace)
        self.remainingSpace.Refresh()

    def OnSize(self, event):
        wx.LayoutAlgorithm().LayoutWindow(self, self.remainingSpace)

if __name__ == '__main__':
    app = Application(None)
    app.MainLoop()
