#!/usr/bin/env python

import sys
#import time

import wx
import wx.glcanvas

from giraffe import Worksheet, Folder

#from Numeric import *

#from OpenGL.GL import *
#from OpenGL.GLU import *
#from lib import ftgl

#from render import makedata

#sys.path.append('/home/daniel/grafit/functions')
#sys.path.append('/home/daniel/grafit')
#import hn

#from base.signals import HasSignals
#from giraffe.graph import Graph

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

class GraphDataPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        # create widgets 
        sizer = wx.BoxSizer(wx.VERTICAL)

#        buttons = wx.BoxSizer(wx.HORIZONTAL)
        class k: pass
        k = k()
        k.__dict__.update({'_widget': self })

        box = gui.Box(k, 'vertical')
        sizer.Add(box._widget, 1, wx.EXPAND)
        button = gui.Button(box, 'add')
        worksheet_list = gui.List(box)

#
#        button = gui.Button(k, 'add')
#        buttons.Add(button._widget, 0, wx.EXPAND)
#        sizer.Add(buttons, 0, wx.EXPAND)
#
#        sizer.Add(wx.StaticText(self, -1, 'Worksheet'), 0, wx.EXPAND)
#        self.worksheet_list = wx.ListCtrl(self, -1, style= wx.LC_LIST|wx.BORDER_SUNKEN|wx.LC_HRULES)
#        sizer.Add(self.worksheet_list, 1, wx.EXPAND)
#
#        sizer.Add(wx.StaticText(self, -1, 'X column'), 0, wx.EXPAND)
#        self.x_list = wx.ListCtrl(self, -1, style= wx.LC_LIST|wx.BORDER_SUNKEN|wx.LC_HRULES)
#        sizer.Add(self.x_list, 1, wx.EXPAND)
#
#        sizer.Add(wx.StaticText(self, -1, 'Y column'), 0, wx.EXPAND)
#        self.y_list = wx.ListCtrl(self, -1, style= wx.LC_LIST|wx.BORDER_SUNKEN|wx.LC_HRULES)
#        sizer.Add(self.y_list, 1, wx.EXPAND)
#
        self.SetSizer(sizer)
        sizer.SetSizeHints(self)

        self.project = None
        self.folder = None

    def set_current_folder(self, folder):
        self.folder = folder
        self.worksheet_list.ClearAll()

        for item in folder.contents():
            if isinstance(item, Worksheet):
                self.worksheet_list.InsertStringItem(0, item.name)
            elif isinstance(item, Folder):
                self.worksheet_list.InsertStringItem(0, item.name+'/')

    def on_project_changed(self, item):
        if item.parent == self.folder:
            self.set_current_folder(self.folder)

    def connect_project(self, project):
        return
        self.project = project
        self.project.connect('add-item', self.on_project_changed)
        self.project.connect('remove-item', self.on_project_changed)

    def disconnect_project(self):
        return
        self.project = None
        self.project.disconnect('add-item', self.on_project_changed)
        self.project.disconnect('remove-item', self.on_project_changed)

    def on_open(self):
        return
        self.set_current_folder(self.project.here)
