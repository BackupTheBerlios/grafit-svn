# http://tman.3-wave.com/torrents.html

import sys
print  >>sys.stderr, "import wx...",
import  wx
print  >>sys.stderr, "ok"
import os

print  >>sys.stderr, "import shapes...",
from shapes import PlotCanvas, Plot
print  >>sys.stderr, "ok",

class RunDemoApp(wx.App):
    def __init__(self):
        self.name = 'name'
        wx.App.__init__(self, redirect=False)

    def OnInit(self):
        wx.Log_SetActiveTarget(wx.LogStderr())

        frame = wx.Frame(None, -1,  self.name, pos=(50,50), size=(200,100),
                        style=wx.DEFAULT_FRAME_STYLE)
        frame.CreateStatusBar()

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        item = menu.Append(-1, "E&xit\tAlt-X", "Exit demo")
        self.Bind(wx.EVT_MENU, self.OnButton, item)
        menuBar.Append(menu, "&File")

        frame.SetMenuBar(menuBar)
        frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        win = TestSashWindow(frame)

        frame.SetSize((640, 480))
        win.SetFocus()
        self.window = win
        frect = frame.GetRect()

        self.SetTopWindow(frame)
        self.frame = frame
        frame.Show(True)
        return True


    def OnButton(self, evt):
        self.frame.Close(True)


    def OnCloseFrame(self, evt):
        evt.Skip()

class TestSashWindow(wx.Panel):
    ID_WINDOW_LEFT1  = 5101
    ID_WINDOW_LEFT2  = 5102
    ID_WINDOW_BOTTOM = 5103


    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        # A window like a statusbar
        win = wx.SashLayoutWindow(self, self.ID_WINDOW_BOTTOM, wx.DefaultPosition, (200, 0), wx.NO_BORDER|wx.SW_3D)

        win.SetDefaultSize((1000, 30))
        win.SetOrientation(wx.LAYOUT_HORIZONTAL)
        win.SetAlignment(wx.LAYOUT_BOTTOM)
        win.SetSashVisible(wx.SASH_TOP, True)

        self.bottomWindow = win

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

#        self.textWindow = wx.TextCtrl(win, -1, "", wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.SUNKEN_BORDER)
        self.textWindow = wx.TreeCtrl(win, -1, style=wx.TR_DEFAULT_STYLE|wx.TR_EDIT_LABELS | wx.TR_HIDE_ROOT)
#        self.textWindow = wx.TreeCtrl(win, -1, style=wx.TR_DEFAULT_STYLE)
        self.textWindow.SetIndent(10)
        r1 = self.textWindow.AddRoot('Root item')
        r = self.textWindow.AppendItem(r1, 'Root item')
        self.textWindow.AppendItem(r, 'other item')
        self.textWindow.AppendItem(r, 'other item')
        r = self.textWindow.AppendItem(r1, 'Root item')
        self.textWindow.AppendItem(r, 'other item')
        self.textWindow.AppendItem(r, 'other item')
#        self.textWindow.SetValue("A window")

        btn = wx.ToggleButton(win, 10011, "He", style=wx.BU_EXACTFIT)
        self.btn = btn
        self.Bind(wx.EVT_TOGGLEBUTTON, self.button_clicked, btn)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(btn, 0)
        box.Add(self.textWindow, 1, wx.EXPAND)

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
            self.textWindow.Show()
            self.leftWindow1.SetDefaultSize((300, -1))
        else:
            self.textWindow.Hide()
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
    app = RunDemoApp()
    app.MainLoop()
