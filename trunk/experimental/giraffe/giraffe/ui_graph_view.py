#!/usr/bin/env python

import sys
#import time

import wx
import wx.glcanvas

from giraffe import Worksheet, Folder
from giraffe.signals import HasSignals

from giraffe import gui

class GraphView(gui.Box):
    def __init__(self, parent, graph, **place):
        gui.Box.__init__(self, parent, 'vertical', **place)
        self.graph = graph

        tbbox = gui.Box(self, 'horizontal', stretch=0)

        self.toolbar = gui.Toolbar(tbbox, stretch=1)
        self.toolbar.append(gui.Action('New column', 'Create a new column', 
                                       self.on_new_column, 'stock_insert-columns.png'))

        self.closebar = gui.Toolbar(tbbox, stretch=0)
        self.closebar.append(gui.Action('Close', 'Close this worksheet', 
                                       self.on_close, 'remove.png'))

        self.panel = gui.MainPanel(self)
        self.box = gui.Box(self.panel, 'horizontal')
        self.glwidget = gui.OpenGLWidget(self.box)

        self.glwidget.connect('initialize-gl', self.graph.init)
        self.glwidget.connect('resize-gl', self.graph.reshape)
        self.glwidget.connect('paint-gl', self.graph.display)

        self.glwidget.connect('button-pressed', self.graph.button_press)
        self.glwidget.connect('button-released', self.graph.button_release)
        self.glwidget.connect('mouse-moved', self.graph.button_motion)

        self.graph.connect('redraw', self.glwidget.redraw)

        self.legend = gui.List(self.box, stretch=0)
        self.legend.model.append('pis10sv_e1(f)')

        self.graphdata = GraphDataPanel(self.panel.right_panel, page_label='Data', page_pixmap='worksheet.png')

    def on_new_column(self):
        pass

    def on_close(self):
        self.glwidget.disconnect('initialize-gl', self.graph.init)
        self.glwidget.disconnect('resize-gl', self.graph.reshape)
        self.glwidget.disconnect('paint-gl', self.graph.display)

        self.glwidget.disconnect('button-pressed', self.graph.button_press)
        self.glwidget.disconnect('button-released', self.graph.button_release)
        self.glwidget.disconnect('mouse-moved', self.graph.button_motion)

        self.graph.disconnect('redraw', self.glwidget.redraw)

        self.parent.delete(self)

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
    def __init__(self, parent, **place):
        gui.Box.__init__(self, parent, 'vertical', **place)

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
        #`self.set_current_folder(self.project.here)
        pass
