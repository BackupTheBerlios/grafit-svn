import  wx
import wx                  # This module uses the new wx namespace
import sys, os

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
        frame.Show(True)
        frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        win = TestSashWindow(frame)

        frame.SetSize((640, 480))
        win.SetFocus()
        self.window = win
        frect = frame.GetRect()

        self.SetTopWindow(frame)
        self.frame = frame
        return True


    def OnButton(self, evt):
        self.frame.Close(True)


    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.window.ShutdownDemo()
        evt.Skip()


#----------------------------------------------------------------------------


def main(argv):
    app = RunDemoApp()
    app.MainLoop()



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

        textWindow = wx.TextCtrl(win, -1, "", wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.SUNKEN_BORDER)
        textWindow.SetValue("A window")
        btn = wx.Button(win, -1, "He")

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(btn, 0)
        box.Add(textWindow, 1, wx.EXPAND)

#        box.SetSizeHints(win)

        win.SetAutoLayout(True)
        win.SetSizer(box)

        # will occupy the space not used by the Layout Algorithm
        self.remainingSpace = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)

        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.OnSashDrag, id=self.ID_WINDOW_LEFT1)
        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.OnSashDrag, id=self.ID_WINDOW_LEFT2)
        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.OnSashDrag, id=self.ID_WINDOW_BOTTOM)
        self.Bind(wx.EVT_SIZE, self.OnSize)


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

#---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys,os
    main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])
