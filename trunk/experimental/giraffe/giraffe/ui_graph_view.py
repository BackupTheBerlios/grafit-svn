import sys
import sets

from giraffe import Worksheet, Folder
from giraffe.graph import Style
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

        # Symbol
        self.symbol = gui.Frame(self, 'vertical', title='Symbol', stretch=0.)
        grid = self.symbol_grid = gui.Grid(self.symbol, 3, 3, expand=False)#, expand=True, stretch=1.)
        grid.layout.AddGrowableCol(2)

        # symbol type
        self.symbol = gui.PixmapChoice(grid, pos=(0,2))
        self.symbol.label = gui.Label(grid,  'Symbol', pos=(0,1))
        self.symbol.check = gui.Checkbox(grid, pos=(0,0))
        self.symbol.min_size = (10, self.symbol.min_size[1])
        for symbol in Style.symbols:
            self.symbol.append(symbol+'.png')
        self.symbol.value = 0
        self.symbol.connect('select', lambda value: self.on_select_property('symbol', value), True)

        # symbol color
        self.color = gui.PixmapChoice(grid, pos=(1,2))
        self.color.label = gui.Label(grid,  'Color', pos=(1,1))
        self.color.check = gui.Checkbox(grid, pos=(1,0))
        self.color.min_size = (10, self.color.min_size[1])
        for color in Style.colors:
            self.color.append(self.color.create_colored_bitmap((20, 10), color))
        self.color.value = 0
        self.color.connect('select', lambda value: self.on_select_property('color', value), True)

        # symbol size
        self.symbol_size = gui.Spin(grid, pos=(2,2))
        self.symbol_size.label = gui.Label(grid, 'Size', pos=(2,1))
        self.symbol_size.check = gui.Checkbox(grid, pos=(2,0))
        self.symbol_size.min_size = (10, self.symbol_size.min_size[1])
        self.symbol_size.value = 5
        self.symbol_size.connect('modified', lambda value: self.on_select_property('symbol_size', value), True)

        # Line
        self.line = gui.Frame(self, 'vertical', title='Line', stretch=0.)
        grid = self.line_grid = gui.Grid(self.line, 3, 3)#, expand=True, stretch=1.)
        grid.layout.AddGrowableCol(2)

        # Line type
        self.line_type = gui.Choice(grid, pos=(0,2))
        self.line_type.label = gui.Label(grid, 'Type', pos=(0,1))
        self.line_type.check = gui.Checkbox(grid, pos=(0,0))
        self.line_type.min_size = (10, self.line_type.min_size[1])
        for t in Style.line_types:
            self.line_type.append(t)
        self.line_type.value = 0
        self.line_type.connect('select', lambda value: self.on_select_property('line_type', value), True)

        # Line style
        self.line_style = gui.Choice(grid, pos=(1,2))
        self.line_style.label = gui.Label(grid,  'Style', pos=(1,1))
        self.line_style.check = gui.Checkbox(grid, pos=(1,0))
        self.line_style.min_size = (10, self.line_style.min_size[1])
        for p in Style.line_styles:
            self.line_style.append(p)
        self.line_style.value = 0
        self.line_style.connect('select', lambda value: self.on_select_property('line_style', value), True)

        # Line width
        self.line_width = gui.Spin(grid, pos=(2,2))
        self.line_width.label = gui.Label(grid, 'Width', pos=(2,1))
        self.line_width.check = gui.Checkbox(grid, pos=(2,0))
        self.line_width.min_size = (10, self.line_width.min_size[1])
        self.line_width.value = 1
        self.line_width.connect('modified', lambda value: self.on_select_property('line_width', value), True)

        self.settings_widgets = [self.symbol, self.color, self.symbol_size, 
                                 self.line_type, self.line_style, self.line_width]

        self.show_checks(False)

        self.symbol.prop = 'symbol'
        self.symbol_size.prop = 'symbol_size'
        self.color.prop = 'color'
        self.line_width.prop = 'line_width'
        self.line_type.prop = 'line_type'
        self.line_style.prop = 'line_style'

        b = gui.Box(self, 'horizontal', expand=True, stretch=0)
        gui.Label(b, 'Group', stretch=0)
        self.multi = gui.Choice(b, stretch=1)
        self.multi.append('identical')
        self.multi.append('series')
        self.multi.value = 0
        self.multi.connect('select', self.on_select_multi)


        maxminw = max([w.label._widget.GetBestSize()[0] for w in self.settings_widgets])
        for widget in self.settings_widgets:
            widget.check.connect('modified', lambda state, widget=widget: self.on_check(widget, state), True)
            widget.label.min_size = (maxminw, widget.label.min_size[1])


    def on_legend_selection(self):
        datasets = [self.view.legend.model[i] for i in self.view.legend.selection]

        style = datasets[0].style
        self.color.value = Style.colors.index(style.color)
        self.symbol.value = Style.symbols.index(style.symbol)
        self.symbol_size.value = style.symbol_size
        self.line_type.value = Style.line_types.index(style.line_type)
        self.line_style.value = Style.line_styles.index(style.line_style)
        self.line_width.value = style.line_width

        if len(datasets) > 1:
            if self.multi.value == 0: # identical
                self.show_checks(True)
                for control in self.settings_widgets:
                    control.check.state = all_the_same([getattr(d.style, control.prop) for d in datasets])
                    control.active = control.label.active = control.check.state

            elif self.multi.value == 1: # series
                self.show_checks(False)
                self.symbol_grid.layout.Show(self.color.check._widget)
                self.symbol_grid.layout.Layout()

                for control in self.settings_widgets:
                    control.active = control.label.active = control.check.state = False

                colors = [Style.colors.index(d.style.color) for d in datasets]
                c0 = colors[0]
                self.color.check.state = colors == [c % len(Style.colors) for c in range(c0, c0+len(colors))]
                self.color.active = self.color.label.active = self.color.check.state
        else:
            for control in self.settings_widgets:
                control.active = control.label.active = True
            self.show_checks(False)

    def on_select_multi(self, sel):
        self.on_legend_selection()

    def on_check(self, widget, state):
        widget.active = state
        widget.label.active = state
        self.on_select_property(widget.prop, widget.value)

    def show_checks(self, visible):
        for w in [self.symbol,self.color,self.symbol_size]:
            self.symbol_grid.layout.Show(w.check._widget, visible)
        for w in [self.line_type, self.line_style, self.line_width]:
            self.line_grid.layout.Show(w.check._widget, visible)
        self.symbol_grid.layout.Layout()
        self.line_grid.layout.Layout()

    def on_select_property(self, prop, value):
        datasets = [self.graph.datasets[s] for s in self.view.legend.selection]
        if len(datasets) == 1:
            setattr(datasets[0].style, prop, value)
        elif self.multi.value == 0:
            for d in datasets:
                setattr(d.style, prop, value)
        elif self.multi.value == 1:
            for i, d in enumerate(datasets):
                d.style.color = (value + i) % len(Style.colors)


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
