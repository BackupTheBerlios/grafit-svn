import sys
import os
import new

import wx
import wx.xrc

from giraffe import Graph, Worksheet, Folder, Project
from giraffe.signals import HasSignals
from giraffe.commands import undo, redo, command_list
from giraffe.ui_graph_view import GraphView, GraphDataPanel
from giraffe.ui_worksheet_view import WorksheetView
from giraffe.ui_panels import ProjectExplorer, ScriptWindow

class Cancel(Exception):
    pass

class ToolPanel(wx.SashLayoutWindow):
    """The areas on the left, top and bottom of the window holding tabs."""

    def __init__(self, parent, position):
        """`position` is one of 'left', 'right', 'top' or 'bottom'"""

        wx.SashLayoutWindow.__init__(self, parent, -1, wx.DefaultPosition,
                                     (200, 30), wx.NO_BORDER|wx.SW_3D)

        self.parent = parent
        self.position = position

        if position in ['top', 'bottom']:
            self.SetDefaultSize((1000, 12))
        else:
            self.SetDefaultSize((12, 1000))

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

        self.contentbox.Add(widget, 1, wx.EXPAND)
        widget.Hide()
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
                self.contentbox.Hide(widget)

        self.contentbox.Show(self.contents[id]) 
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
            self.contentbox.Hide(self.contents[id])
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


class Application(wx.App):
    def __init__(self):
        self.name = 'Grafit'
        wx.App.__init__(self, redirect=False)

    def on_undo(self, event):
        undo()

    def on_redo(self, event):
        redo()

    def OnInit(self):
        wx.Log_SetActiveTarget(wx.LogStderr())

        # splash screen ###########################################################################
        s = wx.SplashScreen(wx.Image("/home/daniel/grafit/pixmaps/logo.png").ConvertToBitmap(),
                            wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT, 3000, None, -1)
        s.Show()

        sys.stderr.write('.')
        resource = wx.xrc.XmlResource('resources.xrc')

        sys.stderr.write('.')

        # frame ###################################################################################
        self.frame = frame = wx.Frame(None, -1,  self.name, pos=(50,50), size=(200,100),
                        style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(frame)

        frame.CreateStatusBar()

        sys.stderr.write('.')

        # toolbar #################################################################################
        buttons = [
            ('stock_undo', 'Undo', 'Undo the last action', self.on_undo),
            ('stock_redo', 'Redo', 'Redo the last action that was undone', self.on_redo),
            None,
            ('worksheet', 'New worksheet', 'Create a new worksheet', self.on_new_worksheet),
            ('graph', 'New graph', 'Create a new graph', self.on_new_graph),
        ] 

        tb = frame.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)
        for data in buttons:
            if data is None:
                tb.AddSeparator()
            else:
                image, help_s, help_l, callback = data
                bitmap = wx.Image('/home/daniel/giraffe/data/images/'+image+'.png').ConvertToBitmap()
                tool = tb.AddSimpleTool(-1, bitmap, help_s, help_l)
                tb.Bind(wx.EVT_TOOL, callback, id=tool.GetId())
            
        # menu bar ################################################################################
        sys.stderr.write('.')

        frame.SetMenuBar(resource.LoadMenuBar('menubar'))

        menuitems = [
            ('project-new', self.on_project_new),
            ('project-open', self.on_project_open),
            ('project-save', self.on_project_save),
            ('project-saveas', self.on_project_saveas),
            ('project-quit', self.OnButton),
            ('object-new-folder', self.on_new_folder),
            ('object-new-worksheet', self.on_new_worksheet),
            ('object-new-graph', self.on_new_graph), 
        ]

        for id, func in menuitems:
            self.Bind(wx.EVT_MENU, func, id=wx.xrc.XRCID(id))

        sys.stderr.write('.')

        # events
        frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)

        self.main = MainPanel(frame)
        self.main.SetFocus()

        frame.SetSize((640, 480))
        frame.Show(True)
        return True

    def on_new_worksheet(self, evt):
        ws = self.main.project.new(Worksheet, None, self.main.project.here)
        ws.a = [1,2,3]
        ws.other = 2*ws.a

    def on_project_open(self, evt=None):
        try:
            if self.main.project.modified and self.ask_savechanges():
                self.on_project_save()

            dlg = wx.FileDialog(self.frame, message="Choose a file", defaultDir=os.getcwd(), 
                                defaultFile="", wildcard="All Files|*.*|Projects|*.mk", style=wx.OPEN | wx.CHANGE_DIR)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPaths()[0]
                self.main.close_project()
                self.main.open_project(Project(str(path)))
            dlg.Destroy()
        except Cancel:
            return

    def ask_savechanges(self):
        dlg = wx.MessageDialog(self.frame, 'Save <b>changes?</b>', 'Save?',
                               wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            return True
        elif result == wx.ID_NO:
            return False
        elif result == wx.ID_CANCEL:
            raise Cancel
        dlg.Destroy()

    def on_project_saveas(self, evt=None):
        try:
            dlg = wx.FileDialog(self.frame, message="Choose a file", defaultDir=os.getcwd(), 
                                defaultFile="", wildcard="All Files|*.*|Projects|*.mk", style=wx.SAVE | wx.CHANGE_DIR)
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPaths()[0]
                self.main.project.saveto(path)
                self.main.open_project(Project(str(path)))
            dlg.Destroy()
        except Cancel:
            return

    def on_project_save(self, evt=None):
        try:
            if self.main.project.filename is not None:
                self.main.project.commit()
            else:
                self.on_project_saveas()
        except Cancel:
            return

    def on_project_new(self, evt=None):
        try:
            if self.main.project.modified and self.ask_savechanges():
                self.on_project_save()
            self.main.close_project()
            self.main.open_project(Project())
        except Cancel:
            return
            
    def on_new_graph(self, evt):
        g = self.main.project.new(Graph, None, self.main.project.here)

    def on_new_folder(self, evt):
        self.main.project.new(Folder, None, self.main.project.here)

    def OnButton(self, evt):
        self.frame.Close(True)

    def OnCloseFrame(self, evt):
        evt.Skip()

    def run(self):
        self.MainLoop()

class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.view = None
        self.active = None

        self.bottom_panel = ToolPanel(self, 'bottom')
        self.right_panel = ToolPanel(self, 'right')
        self.left_panel = ToolPanel(self, 'left')

        # bottom panel
        self.script_window = ScriptWindow(self.bottom_panel.panel)
        sys.stderr.write('.')
        self.bottom_panel.add_page('Script', 'console.png', self.script_window)
        self.script_window.locals['mainwin'] = self

        # the left panel
        self.explorer = ProjectExplorer(self.left_panel.panel)
        sys.stderr.write('.')
        self.explorer.connect('activate-object', self.show_object)
        self.left_panel.add_page('Project', 'stock_navigator.png', self.explorer)

        # the right panel
#        self.graph_data_panel = GraphDataPanel(self.right_panel.panel)
#        self.right_panel.add_page('Data', 'worksheet.png', self.graph_data_panel._widget)

        # will occupy the space not used by the Layout Algorithm
        self.remainingSpace = wx.Panel(self, -1, style=wx.SUNKEN_BORDER)

        self.main_box = wx.BoxSizer(wx.VERTICAL)
        self.remainingSpace.SetSizer(self.main_box)

        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.on_sash_drag, id=self.left_panel.GetId())
        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.on_sash_drag, id=self.right_panel.GetId())
        self.Bind(wx.EVT_SASH_DRAGGED_RANGE, self.on_sash_drag, id=self.bottom_panel.GetId())
        self.Bind(wx.EVT_SIZE, self.on_size)

    def open_project(self, project):
        self.project = project
        for panel in (self.script_window, self.explorer):
            panel.connect_project(self.project)
        self.project.connect('remove-item', self.on_project_remove_item)
        command_list.clear()

    def close_project(self):
        for panel in (self.script_window, self.explorer, ):
            panel.disconnect_project()
        self.project.disconnect('remove-item', self.on_project_remove_item)

    def on_project_remove_item(self, obj):
        if obj == self.active:
            self.show_object(None)

    def show_object(self, obj):
        if self.view is not None:
            self.main_box.Remove(self.view)
            self.view.Destroy()

        if isinstance(obj, Graph):
            self.view =  GraphView(self.remainingSpace, obj)
            self.active = obj
        elif isinstance(obj, Worksheet):
            self.view = WorksheetView(self.remainingSpace, obj)
            self.active = obj
        elif obj is None:
            self.view = None
            self.active = None
        else:
            raise TypeError

        if self.view is not None:
            self.main_box.Add(self.view, 1, wx.EXPAND)

        self.remainingSpace.Layout()

    # wx stuff

    def on_sash_drag(self, event):
        if event.GetDragStatus() == wx.SASH_STATUS_OUT_OF_RANGE:
            return

        id = event.GetId()

        if id == self.left_panel.GetId():
            self.left_panel.SetDefaultSize((event.GetDragRect().width, 1000))
        elif id == self.right_panel.GetId():
            self.right_panel.SetDefaultSize((event.GetDragRect().width, 1000))
        elif id == self.bottom_panel.GetId():
            self.bottom_panel.SetDefaultSize((1000, event.GetDragRect().height))

        wx.LayoutAlgorithm().LayoutWindow(self, self.remainingSpace)
        self.remainingSpace.Refresh()

    def on_size(self, event):
        wx.LayoutAlgorithm().LayoutWindow(self, self.remainingSpace)
