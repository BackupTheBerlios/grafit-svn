#!/usr/bin/env python

import sys
#import time

import wx
import wx.glcanvas

from giraffe import Worksheet, Folder
from giraffe.signals import HasSignals

from giraffe import gui

def intersection (ml):
    """Intersection of lists"""
    tmp = {}
    for l in ml:
        for x in l:
            z = tmp.get(x, [])
            z.append(1)
            tmp[x] = z
    rslt = []
    for k,v in tmp.items():
        if len(v) == len(ml):
            rslt.append(k)
    return rslt

class LegendModel(HasSignals):
    def __init__(self, graph):
        self.graph = graph
        self.graph.connect('add-dataset', self.on_modified)
        self.graph.connect('remove-dataset', self.on_modified)

    def on_modified(self, dataset):
        self.emit('modified')

    def get(self, row, column): return str(self.graph.datasets[row])
    def get_image(self, row): return None
    def __len__(self): return len(self.graph.datasets)
    def __getitem__(self, row): return self.graph.datasets[row]


class GraphView(gui.Box):
    def __init__(self, parent, graph, **place):
        gui.Box.__init__(self, parent, 'vertical', **place)
        self.graph = graph

        tbbox = gui.Box(self, 'horizontal', stretch=0)

        self.toolbar = gui.Toolbar(tbbox, stretch=1)
        self.toolbar.append(gui.Action('Arrow', '', object, 'arrow.png'))
        self.toolbar.append(gui.Action('Hand', '', object, 'hand.png'))
        self.toolbar.append(gui.Action('Zoom', '', object, 'zoom.png'))
        self.toolbar.append(gui.Action('Range', '', object, 'range.png'))
        self.toolbar.append(gui.Action('Data reader', '', object, 'dreader.png'))
        self.toolbar.append(gui.Action('Screen reader', '', object, 'sreader.png'))

        self.closebar = gui.Toolbar(tbbox, stretch=0)
        self.closebar.append(gui.Action('Close', 'Close this worksheet', 
                                       self.on_close, 'close.png'))

        self.panel = gui.MainPanel(self)
        self.box = gui.Splitter(self.panel, 'vertical', proportion=0.8)
        self.glwidget = gui.OpenGLWidget(self.box)

        self.glwidget.connect('initialize-gl', self.graph.init)
        self.glwidget.connect('resize-gl', self.graph.reshape)
        self.glwidget.connect('paint-gl', self.graph.display)

        self.glwidget.connect('button-pressed', self.graph.button_press)
        self.glwidget.connect('button-released', self.graph.button_release)
        self.glwidget.connect('mouse-moved', self.graph.button_motion)

        self.graph.connect('redraw', self.glwidget.redraw)

        self.legend = gui.List(self.box, model=LegendModel(self.graph))#, stretch=0)


        self.legend.connect('selection-changed', self.on_legend_select)
        self.graphdata = GraphDataPanel(self.graph, self, self.panel.right_panel, 
                                        page_label='Data', page_pixmap='worksheet.png')
        self.graphdata.connect_project(self.graph.project)

        self.style = GraphStylePanel(self.graph, self, self.panel.right_panel, page_label='Style', page_pixmap='style.png')
        self.axes = gui.Box(self.panel.right_panel, 'horizontal', page_label='Axes', page_pixmap='axes.png')
        self.fit = gui.Box(self.panel.right_panel, 'horizontal', page_label='Fit', page_pixmap='function.png')

    def on_legend_select(self):
        self.style.color.selection = self.style.colors.index([self.legend.model[i] for i in self.legend.selection][0].style.color)

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

class WorksheetListModel(HasSignals):
    def __init__(self, folder):
        self.folder = folder
        self.update()
        self.folder.project.connect(['add-item', 'remove-item'], self.update)

    def update(self, item=None):
        self.contents = [o for o in self.folder.contents() 
                           if isinstance(o, (Worksheet))]
        self.emit('modified')

    # ListModel protocol
    def get(self, row, column): return self.contents[row].name + '/'*isinstance(self.contents[row], Folder)
    def get_image(self, row): return 'worksheet.png'
    def __len__(self): return len(self.contents)
    def __getitem__(self, row): return self.contents[row]

class ColumnListModel(HasSignals):
    def __init__(self):
        self.worksheets = []
        self.colnames = []

    def set_worksheets(self, worksheets):
        self.worksheets = worksheets
        self.colnames = intersection([w.column_names for w in worksheets])
        self.emit('modified')

    def get(self, row, column): return self.colnames[row]
    def get_image(self, row): return None
    def __len__(self): return len(self.colnames)
    def __getitem__(self, row): return self.colnames[row]

class GraphStylePanel(gui.Box):
    def __init__(self, graph, view, parent, **place):
        gui.Box.__init__(self, parent, 'vertical', **place)

        self.graph = graph
        self.view = view

        self.symbol = gui.Frame(self, 'vertical', title='Symbol', stretch=0.)
        grid = gui.Grid(self.symbol, 3, 3, expand=False)#, expand=True, stretch=1.)

        labels = []

        labels.append(gui.Label(grid,  'Symbol', pos=(0,1)))
        c = gui.PixmapChoice(grid, pos=(0,2))
        c.min_size = (10, c.min_size[1])
        for shape in ['circle', 'square']:
            for interior in ['o', 'f']:
                c.append(shape+'-'+interior+'.png')

        labels.append(gui.Label(grid,  'Color', pos=(1,1)))
        c = gui.PixmapChoice(grid, pos=(1,2))
        c.min_size = (10, c.min_size[1])
        self.colors = []
        for r in range(0, 256, 64):
            for g in range(0, 256, 64):
                for b in range(0, 256, 64):
                    c.append(c.create_colored_bitmap((20, 10), (r, g, b)))
                    self.colors.append((r/256.,g/256.,b/256., 1.0))
        c.connect('select', self.on_select_color)

        labels.append(gui.Label(grid, 'Size', pos=(2,1)))

        c = gui.Spin(grid, pos=(2,2))
        c.min_size = (10, c.min_size[1])

        b = gui.Checkbox(grid, pos=(0,0))
        grid.layout.Hide(b._widget)
        b = gui.Checkbox(grid, pos=(1,0))
        grid.layout.Hide(b._widget)
        b = gui.Checkbox(grid, pos=(2,0))
        grid.layout.Hide(b._widget)

        grid.layout.AddGrowableCol(2)

        # Line
        self.line = gui.Frame(self, 'vertical', title='Line', stretch=0.)
        grid = gui.Grid(self.line, 3, 3)#, expand=True, stretch=1.)
        grid.layout.AddGrowableCol(2)

        # Line type
        labels.append(gui.Label(grid, 'Type', pos=(0,1)))
        b = gui.Checkbox(grid, pos=(0,0))
        grid.layout.Hide(b._widget)
        self.line_type = gui.Choice(grid, pos=(0,2))
        self.line_type.min_size = (10, self.line_type.min_size[1])
        for shape in ['none', 'straight', 'spline']:
            self.line_type.append(shape)

        # Line style
        labels.append(gui.Label(grid,  'Style', pos=(1,1)))
        b = gui.Checkbox(grid, pos=(1,0))
        grid.layout.Hide(b._widget)
        self.line_style = self.color = gui.Choice(grid, pos=(1,2))
        self.line_style.min_size = (10, self.line_style.min_size[1])
        for p in ['solid', 'dash', 'dot',]:
            self.line_style.append(p)

        # Line width
        labels.append(gui.Label(grid, 'Width', pos=(2,1)))
        b = gui.Checkbox(grid, pos=(2,0))
        grid.layout.Hide(b._widget)
        self.line_width = gui.Spin(grid, pos=(2,2))
        self.line_width.min_size = (10, self.line_width.min_size[1])

        maxminw = max([l.min_size[0] for l in labels])
        for l in labels:
            l.min_size = (maxminw, l.min_size[1])


        b = gui.Box(self, 'horizontal', expand=False, stretch=0)
        gui.Label(b, 'Group', stretch=1)
        self.multi = gui.Choice(b, stretch=2)
        self.multi.append('identical')
        self.multi.append('series')

    def on_select_color(self, ind):
        for d in [self.graph.datasets[s] for s in self.view.legend.selection]:
            d.style.color = self.colors[ind]
        self.graph.emit('redraw')



class GraphDataPanel(gui.Box):
    def __init__(self, graph, view, parent, **place):
        gui.Box.__init__(self, parent, 'vertical', **place)

        self.graph = graph
        self.view = view

        # create widgets 
#        btnbox = gui.Box(self, 'horizontal', stretch=0)
#        button = gui.Button(btnbox, 'add', stretch=0)
        self.toolbar = gui.Toolbar(self, stretch=0)
        self.toolbar.append(gui.Action('Add', 'Add datasets to the graph', 
                                       self.on_add, 'add.png'))
        self.toolbar.append(gui.Action('Remove', 'Remove datasets from the graph', 
                                       self.on_remove, 'remove.png'))
#        button.connect('clicked', self.on_add)

        gui.Label(self, 'Worksheet', stretch=0)
        self.worksheet_list = gui.List(self, editable=False)
        self.worksheet_list.connect('item-activated', self.on_wslist_activated)
        self.worksheet_list.connect('selection-changed', self.on_wslist_select)

        gui.Label(self, 'X column', stretch=0)
        self.x_list = gui.List(self, model=ColumnListModel())

        gui.Label(self, 'Y column', stretch=0)
        self.y_list = gui.List(self, model=ColumnListModel())

        self.project = None
        self.folder = None

    def on_wslist_activated(self, ind):
        print 'activated:', self.worksheet_list.model[ind]

    def on_wslist_select(self):
        selection = [self.worksheet_list.model[ind] for ind in self.worksheet_list.selection]
        self.x_list.model.set_worksheets(selection)
        self.y_list.model.set_worksheets(selection)

    def set_current_folder(self, folder):
        self.folder = folder
        self.worksheet_list.model = WorksheetListModel(folder)

    def on_add(self):
        for ws in self.worksheet_list.selection:
            worksheet = self.worksheet_list.model[ws]
            for x in self.x_list.selection:
                for y in self.y_list.selection:
                    self.graph.add(worksheet[x], worksheet[y])

    def on_remove(self):
        for d in [self.graph.datasets[s] for s in self.view.legend.selection]:
            self.graph.remove(d)

    def connect_project(self, project):
        self.project = project
        self.worksheet_list.model = WorksheetListModel(self.project.top)

    def disconnect_project(self):
        self.worksheet_list.model = None
        self.project = None

    def on_open(self):
        #`self.set_current_folder(self.project.here)
        pass
