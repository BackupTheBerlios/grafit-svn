import sys
import sets

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

def all_the_same(sequence):
    return len(sets.Set(sequence)) == 1

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
        self.toolbar.append(gui.Action('Arrow', '', object, 'arrow.png', type='radio'))
        self.toolbar.append(gui.Action('Hand', '', object, 'hand.png', type='radio'))
        self.toolbar.append(gui.Action('Zoom', '', object, 'zoom.png', type='radio'))
        self.toolbar.append(gui.Action('Range', '', object, 'range.png', type='radio'))
        self.toolbar.append(gui.Action('Data reader', '', object, 'dreader.png', type='radio'))
        self.toolbar.append(gui.Action('Screen reader', '', object, 'sreader.png', type='radio'))

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

        self.style = GraphStylePanel(self.graph, self, self.panel.right_panel, page_label='Style', page_pixmap='style.png')
        self.axes = gui.Box(self.panel.right_panel, 'horizontal', page_label='Axes', page_pixmap='axes.png')
        self.fit = gui.Box(self.panel.right_panel, 'horizontal', page_label='Fit', page_pixmap='function.png')

    def on_legend_select(self):
        self.style.on_legend_selection()

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


###############################################################################
# style panel                                                                  #
###############################################################################

class GraphStylePanel(gui.Box):
    def __init__(self, graph, view, parent, **place):
        gui.Box.__init__(self, parent, 'vertical', **place)

        self.graph = graph
        self.view = view

        labels = []

        # Symbol
        self.symbol = gui.Frame(self, 'vertical', title='Symbol', stretch=0.)
        grid = self.symbol_grid = gui.Grid(self.symbol, 3, 3, expand=False)#, expand=True, stretch=1.)
        grid.layout.AddGrowableCol(2)

        # symbol type
        labels.append(gui.Label(grid,  'Symbol', pos=(0,1)))
        self.shape = gui.PixmapChoice(grid, pos=(0,2))
        self.shape.check = gui.Checkbox(grid, pos=(0,0))
        self.shape.check.connect('modified', lambda state: self.on_check(self.shape, state), True)
        self.shape.min_size = (10, self.shape.min_size[1])
#        self.shapes = ['uptriangle-f', 'square-f', 'circle-f', 'diamond-f']
        self.shapes = []
        for interior in ['o', 'f']:
            for shape in ['circle', 'square', 'diamond', 'uptriangle', 
                          'downtriangle', 'lefttriangle', 'righttriangle']:
                self.shape.append(shape+'-'+interior+'.png')
                self.shapes.append(shape+'-'+interior)
        self.shape.selection = 0
        self.shape.connect('select', self.on_select_shape)

        # symbol color
        labels.append(gui.Label(grid,  'Color', pos=(1,1)))
        self.color = gui.PixmapChoice(grid, pos=(1,2))
        self.color.check = gui.Checkbox(grid, pos=(1,0))
        self.color.min_size = (10, self.color.min_size[1])
        self.colors = []
        for r in range(0, 256, 64):
            for g in range(0, 256, 64):
                for b in range(0, 256, 64):
                    self.color.append(self.color.create_colored_bitmap((20, 10), (r, g, b)))
                    self.colors.append((r,g,b))
        self.color.selection = 0
        self.color.connect('select', self.on_select_color)

        # symbol size
        labels.append(gui.Label(grid, 'Size', pos=(2,1)))

        self.size = gui.Spin(grid, pos=(2,2))
        self.size.check = gui.Checkbox(grid, pos=(2,0))
        self.size.min_size = (10, self.size.min_size[1])
        self.size.connect('modified', self.on_select_size)
        self.size.value = 5

        # Line
        self.line = gui.Frame(self, 'vertical', title='Line', stretch=0.)
        grid = self.line_grid = gui.Grid(self.line, 3, 3)#, expand=True, stretch=1.)
        grid.layout.AddGrowableCol(2)

        # Line type
        labels.append(gui.Label(grid, 'Type', pos=(0,1)))
        self.line_type = gui.Choice(grid, pos=(0,2))
        self.line_type.check = gui.Checkbox(grid, pos=(0,0))
        self.line_type.min_size = (10, self.line_type.min_size[1])
        self.linetypes = []
        for shape in ['none', 'straight', 'bspline']:
            self.line_type.append(shape)
            self.linetypes.append(shape)
        self.line_type.selection = 0
        self.line_type.connect('select', self.on_select_line_type)

        # Line style
        labels.append(gui.Label(grid,  'Style', pos=(1,1)))
        self.line_style = gui.Choice(grid, pos=(1,2))
        self.line_style.check = gui.Checkbox(grid, pos=(1,0))
        self.line_style.min_size = (10, self.line_style.min_size[1])
        self.linestyles = []
        for p in ['solid', 'dashed', 'dotted',]:
            self.line_style.append(p)
            self.linestyles.append(p)
        self.line_style.selection = 0
        self.line_style.connect('select', self.on_select_line_style)

        # Line width
        labels.append(gui.Label(grid, 'Width', pos=(2,1)))
        self.line_width = gui.Spin(grid, pos=(2,2))
        self.line_width.check = gui.Checkbox(grid, pos=(2,0))
        self.line_width.min_size = (10, self.line_width.min_size[1])
        self.line_width.value = 1
        self.line_width.connect('modified', self.on_select_line_width)

        self.settings_widgets = [self.shape, self.color, self.size, 
                                 self.line_type, self.line_style, self.line_width]

        self.hide_checks()

        b = gui.Box(self, 'horizontal', expand=True, stretch=0)
        labels.append(gui.Label(b, 'Group', stretch=0))
        self.multi = gui.Choice(b, stretch=1)
        self.multi.append('identical')
        self.multi.append('series')
        self.multi.selection = 0
        self.multi.connect('select', self.on_select_multi)

        maxminw = max([l._widget.GetBestSize()[0] for l in labels])
        for l in labels:
            l.min_size = (maxminw, l.min_size[1])

    def on_legend_selection(self):
        datasets = [self.view.legend.model[i] for i in self.view.legend.selection]

        style = datasets[0].style
        self.color.selection = self.colors.index(style.color)
        self.shape.selection = self.shapes.index(style.symbol)
        self.size.value = style.symbol_size
        self.line_type.selection = self.linetypes.index(style.line_type)
        self.line_style.selection = self.linestyles.index(style.line_style)
        self.line_width.value = style.line_width

        if len(datasets) > 1:
            self.show_checks()

            if self.multi.selection == 0: # identical
                self.color.check.state =  all_the_same([self.colors.index(d.style.color) for d in datasets])
                self.shape.check.state = all_the_same([d.style.symbol for d in datasets])
                self.size.check.state = all_the_same([d.style.symbol_size for d in datasets])

                self.line_type.check.state = all_the_same([d.style.line_type for d in datasets])
                self.line_style.check.state = all_the_same([d.style.line_style for d in datasets])
                self.line_width.check.state = all_the_same([d.style.line_width for d in datasets])

                for control in [self.color, self.shape, self.size, 
                                self.line_type, self.line_style, self.line_width]:
                    control.active = control.check.state

            elif self.multi.selection == 1: # series
                colors = [self.colors.index(d.style.color) for d in datasets]
                c0 = colors[0]
                self.color.check.state = colors == [c % len(self.colors) for c in range(c0, c0+len(colors))]
        else:
            self.hide_checks()

    def on_select_multi(self, sel):
        self.on_legend_selection()

    def on_check(self, widget, state):
        print widget, state

    def hide_checks(self):
        for w in [self.shape,self.color,self.size]:
            self.symbol_grid.layout.Hide(w.check._widget)
        for w in [self.line_type, self.line_style, self.line_width]:
            self.line_grid.layout.Hide(w.check._widget)
        self.symbol_grid.layout.Layout()
        self.line_grid.layout.Layout()

    def show_checks(self):
        for w in [self.shape,self.color,self.size]:
            self.symbol_grid.layout.Show(w.check._widget)
        for w in [self.line_type, self.line_style, self.line_width]:
            self.line_grid.layout.Show(w.check._widget)
        self.symbol_grid.layout.Layout()
        self.line_grid.layout.Layout()

    def on_select_color(self, ind):
        for d in [self.graph.datasets[s] for s in self.view.legend.selection]:
            d.style.color = self.colors[ind]

    def on_select_shape(self, ind):
        for d in [self.graph.datasets[s] for s in self.view.legend.selection]:
            d.style.symbol = self.shapes[ind]

    def on_select_size(self, size):
        for d in [self.graph.datasets[s] for s in self.view.legend.selection]:
            d.style.symbol_size = size

    def on_select_line_type(self, ind):
        for d in [self.graph.datasets[s] for s in self.view.legend.selection]:
            d.style.line_type = self.linetypes[ind]

    def on_select_line_style(self, ind):
        for d in [self.graph.datasets[s] for s in self.view.legend.selection]:
            d.style.line_style = self.linestyles[ind]

    def on_select_line_width(self, width):
        for d in [self.graph.datasets[s] for s in self.view.legend.selection]:
            d.style.line_width = width


###############################################################################
# data panel                                                                  #
###############################################################################

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


class GraphDataPanel(gui.Box):
    def __init__(self, graph, view, parent, **place):
        gui.Box.__init__(self, parent, 'vertical', **place)

        self.graph = graph
        self.view = view

        self.project = graph.project
        self.folder = None

        self.toolbar = gui.Toolbar(self, stretch=0)
        self.toolbar.append(gui.Action('Add', 'Add datasets to the graph', 
                                       self.on_add, 'add.png'))
        self.toolbar.append(gui.Action('Remove', 'Remove datasets from the graph', 
                                       self.on_remove, 'remove.png'))

        gui.Label(self, 'Worksheet', stretch=0)
        self.worksheet_list = gui.List(self, editable=False, 
                                       model=WorksheetListModel(self.project.top))
#        self.worksheet_list.connect('item-activated', self.on_wslist_activated)
        self.worksheet_list.connect('selection-changed', self.on_wslist_select)

        gui.Label(self, 'X column', stretch=0)
        self.x_list = gui.List(self, model=ColumnListModel())

        gui.Label(self, 'Y column', stretch=0)
        self.y_list = gui.List(self, model=ColumnListModel())

#    def on_wslist_activated(self, ind):
#        print 'activated:', self.worksheet_list.model[ind]

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
