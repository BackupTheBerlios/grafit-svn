#!/usr/bin/env python

import sys
#import time

import wx
import wx.glcanvas

from giraffe import Worksheet, Folder
from giraffe.signals import HasSignals

class GraphView(wx.glcanvas.GLCanvas):
    def __init__(self, parent, graph):
        wx.glcanvas.GLCanvas.__init__(self, parent, -1)
        self.init = False

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
        for event in (wx.EVT_LEFT_DOWN, wx.EVT_MIDDLE_DOWN, wx.EVT_RIGHT_DOWN):
            self.Bind(event, self.OnMouseDown)
        for event in (wx.EVT_LEFT_UP, wx.EVT_MIDDLE_UP, wx.EVT_RIGHT_UP):
            self.Bind(event, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)

        self.graph = graph
        self.graph.connect('redraw', self.redraw)
        self.SetCursor(wx.CROSS_CURSOR)

    def redraw(self):
        self.Refresh(False)

    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.

    def InitGL(self):
        self.graph.init()
        self.SwapBuffers()

    def OnSize(self, event):
        self.graph.reshape(*event.GetSize())

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent()
        if not self.init:
            self.InitGL()
            self.init = True
        self.graph.display(*self.GetSize())
        self.SwapBuffers()

    def OnMouseDown(self, evt):
        self.CaptureMouse()
        x, y = evt.GetPosition()
        btn = evt.GetButton()
        if btn is wx.MOUSE_BTN_LEFT:
            self.graph.button_press(x, y, 1)
        elif btn is wx.MOUSE_BTN_RIGHT:
            self.graph.button_press(x, y, 3)
        elif btn is wx.MOUSE_BTN_MIDDLE:
            self.graph.button_press(x, y, 2)

    def OnMouseUp(self, evt):
        self.ReleaseMouse()
        x, y = evt.GetPosition()
        btn = evt.GetButton()
        if btn is wx.MOUSE_BTN_LEFT:
            self.graph.button_release(x, y, 1)
        elif btn is wx.MOUSE_BTN_RIGHT:
            self.graph.button_release(x, y, 3)
        elif btn is wx.MOUSE_BTN_MIDDLE:
            self.graph.button_release(x, y, 2)

    def OnMouseMotion(self, evt):
        if evt.Dragging():
            x, y = evt.GetPosition()
            self.graph.button_motion(x, y)


from giraffe import gui

class FolderListModel(HasSignals):
    def __init__(self, folder):
        self.folder = folder
        self.update()
        self.folder.project.connect(['add-item', 'remove-item'], self.update)

    def update(self, item=None):
        self.contents = [o for o in self.folder.contents() 
                           if isinstance(o, (Folder, Worksheet))]
        self.emit('modified')

    # ListModel protocol
    def get(self, row, column):
        return self.contents[row].name + '/'*isinstance(self.contents[row], Folder)

    def __len__(self):
        return len(self.contents)

class GraphDataPanel(gui.Box):
    def __init__(self, parent):
        # wrapper for wx parent widget
        class k: pass
        k = k()
        k.__dict__.update({'_widget': parent })

        gui.Box.__init__(self, k, 'vertical')

        # create widgets 
        btnbox = gui.Box(self, 'horizontal', stretch=0)
        button = gui.Button(btnbox, 'add', stretch=0)
        button.connect('clicked', self.on_add)

        gui.Label(self, 'Worksheet', stretch=0)
        self.worksheet_list = gui.List(self)
        self.worksheet_list.model.append('arse')

        gui.Label(self, 'X column', stretch=0)
        self.x_list = gui.List(self)
        self.x_list.columns = ['vame', 'vavel']
        self.x_list.model.append('arse')

        gui.Label(self, 'Y column', stretch=0)
        self.y_list = gui.List(self)

        self.project = None
        self.folder = None

    def set_current_folder(self, folder):
        self.folder = folder
        self.worksheet_list.model = FolderListModel(folder)

    def on_add(self):
        print '1'

    def connect_project(self, project):
        self.project = project
        self.worksheet_list.model = FolderListModel(self.project.top)

    def disconnect_project(self):
        self.worksheet_list.model = None
        self.project = None

    def on_open(self):
        self.set_current_folder(self.project.here)
