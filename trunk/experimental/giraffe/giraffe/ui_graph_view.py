#!/usr/bin/env python

import sys
#import time

import wx
import wx.glcanvas

from giraffe import Worksheet, Folder
from giraffe.signals import HasSignals

from giraffe import gui

class GraphView(gui.Box):
    def __init__(self, parent, graph):
        gui.Box.__init__(self, parent, 'horizontal')
        self.graph = graph
        self.glwidget = gui.OpenGLWidget(self)

        self.glwidget.connect('initialize-gl', self.graph.init)
        self.glwidget.connect('resize-gl', self.graph.reshape)
        self.glwidget.connect('paint-gl', self.graph.display)

        self.glwidget.connect('button-pressed', self.graph.button_press)
        self.glwidget.connect('button-released', self.graph.button_release)
        self.glwidget.connect('mouse-moved', self.graph.button_motion)

        self.graph.connect('redraw', self.glwidget.redraw)

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

    def __getitem__(self, row):
        return self.contents[row]

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
        self.worksheet_list = gui.List(self, editable=False)
        self.worksheet_list.connect('item-activated', self.on_wslist_activated)
        self.worksheet_list.connect('selection-changed', self.on_wslist_select)

        gui.Label(self, 'X column', stretch=0)
        self.x_list = gui.List(self)
        self.x_list.columns = ['vame', 'vavel']
        self.x_list.model.append('arse')

        gui.Label(self, 'Y column', stretch=0)
        self.y_list = gui.List(self)

        self.project = None
        self.folder = None

    def on_wslist_activated(self, ind):
        print 'activated:', self.worksheet_list.model[ind]

    def on_wslist_select(self):
        print 'selection:', [self.worksheet_list.model[ind] for ind in self.worksheet_list.selection]

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
