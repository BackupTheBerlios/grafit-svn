
import  wx
 
p = None

#---------------------------------------------------------------------------

class MySplitter(wx.SplitterWindow):
    def __init__(self, parent, ID, log):
        wx.SplitterWindow.__init__(self, parent, ID, style = wx.SP_3D)
        self.log = log
        
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnSashChanged)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.OnSashChanging)

    def OnSashChanged(self, evt):
        self.log.WriteText("sash changed to %s\n" % str(evt.GetSashPosition()))
        pos = p.GetSashPosition()
        p.SetSashPosition(pos + 10)

    def OnSashChanging(self, evt):
        self.log.WriteText("sash changing to %s\n" % str(evt.GetSashPosition()))
        # uncomment this to not allow the change
        #evt.SetSashPosition(-1)


#---------------------------------------------------------------------------

def runTest(frame, nb, log):
    splitter = MySplitter(nb, -1, log)

    p1 = wx.Window(splitter, -1)
    p1.SetBackgroundColour(wx.WHITE)
    wx.StaticText(p1, -1, "Panel One", (5,5))

    splitter2 = wx.SplitterWindow(splitter, -1)

    p2 = wx.Window(splitter2, -1)
    p2.SetBackgroundColour(wx.RED)
    global p 
    p=splitter2
    wx.StaticText(p2, -1, "Panel Two", (5,5))

    p3 = wx.Window(splitter2, -1)
    wx.StaticText(p3, -1, "Panel Three", (5,5))

    splitter.SetMinimumPaneSize(20)
    splitter.SplitVertically(p1, splitter2, 0)

    splitter2.SetMinimumPaneSize(20)
    splitter2.SplitVertically(p2, p3, 0)

    win = p3

    textWindow = wx.TextCtrl(win, -1, "", wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.SUNKEN_BORDER)
    textWindow.SetValue("A window")
    btn = wx.Button(win, -1, "He")

    box = wx.BoxSizer(wx.HORIZONTAL)
    box.Add(btn, 1, wx.EXPAND)
    box.Add(textWindow, 1, wx.EXPAND)

    box.SetSizeHints(win)
    win.SetSizer(box)
    win.Layout()
#        box.Fit(win)


    return splitter


#---------------------------------------------------------------------------


overview = """\
This class manages up to two subwindows. The current view can be split
into two programmatically (perhaps from a menu command), and unsplit
either programmatically or via the wx.SplitterWindow user interface.
"""

if __name__ == '__main__':
    import sys,os
    import run
    run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])

