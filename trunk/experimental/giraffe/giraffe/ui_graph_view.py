import sys
import sets

from giraffe import Worksheet, Folder
from giraffe.graph import Style
from giraffe.signals import HasSignals

from giraffe import gui
from giraffe.arrays import nan

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
        self.graph.connect('add-function', self.on_modified)
        self.graph.connect('remove-dataset', self.on_modified)

    def on_modified(self, dataset):
        self.emit('modified')

    def get(self, row, column): return str(self[row])
    def get_image(self, row): return None
    def __len__(self): return len(self.graph.datasets) #+ len(self.graph.functions)
    def __getitem__(self, row): 
#        if row < len(self.graph.datasets):
            return self.graph.datasets[row]
#        else:
#            return self.graph.functions[row-len(self.graph.datasets)]

class GraphView(gui.Box):
    def __init__(self, parent, graph, **place):
        gui.Box.__init__(self, parent, 'vertical', **place)
        self.graph = graph

        tbbox = gui.Box(self, 'horizontal', stretch=0)

        def set_graph_mode(mode):
            def _set(): self.graph.mode = mode
            return _set

        self.toolbar = gui.Toolbar(tbbox, stretch=1)
        self.toolbar.append(gui.Action('Arrow', '', set_graph_mode('arrow'), 'arrow.png', type='radio'))
        self.toolbar.append(gui.Action('Hand', '', set_graph_mode('hand'), 'hand.png', type='radio'))
        self.toolbar.append(gui.Action('Zoom', '', set_graph_mode('zoom'), 'zoom.png', type='radio'))
        self.toolbar.append(gui.Action('Range', '', set_graph_mode('range'), 'range.png', type='radio'))
        self.toolbar.append(gui.Action('Data reader', '', set_graph_mode('d-reader'), 'dreader.png', type='radio'))
        self.toolbar.append(gui.Action('Screen reader', '', set_graph_mode('s-reader'), 'sreader.png', type='radio'))

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
        self.style = GraphStylePanel(self.graph, self, self.panel.right_panel, 
                                     page_label='Style', page_pixmap='style.png')
        self.axes = GraphAxesPanel(self.graph, self, self.panel.right_panel, 
                                   page_label='Axes', page_pixmap='axes.png')
        self.fit = GraphFunctionsPanel(self.graph.functions[0].func, self.graph, 
                                       self.panel.right_panel,
                                       page_label='Fit', page_pixmap='function.png')

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


class GraphAxesPanel(gui.Box):
    def __init__(self, graph, view, parent, **place):
        gui.Box.__init__(self, parent, "vertical", **place)
        self.graph, self.view = graph, view

        xframe = gui.Frame(self, 'vertical', title='X axis', stretch=0.)
        grid = gui.Grid(xframe, 4, 2, expand=False)
        grid.layout.AddGrowableCol(1)
        gui.Label(grid, 'Title', pos=(0,0))
        x_title = gui.Text(grid, pos=(0,1))
        gui.Label(grid, 'From', pos=(1,0))
        x_from = gui.Text(grid, pos=(1,1))
        gui.Label(grid, 'To', pos=(2,0))
        x_to = gui.Text(grid, pos=(2,1))
        gui.Label(grid, 'Type', pos=(3,0))
        x_type = self.x_type = gui.Choice(grid, pos=(3,1))
        x_type.append('Linear')
        x_type.append('Logarithmic')
        x_type.value = ['linear', 'log'].index(self.graph.xtype)
        x_type.connect('select', lambda value: self.on_set_xtype(value), True)

        yframe = gui.Frame(self, 'vertical', title='Y axis', stretch=0.)
        grid = gui.Grid(yframe, 4, 2, expand=False)
        grid.layout.AddGrowableCol(1)
        gui.Label(grid, 'Title', pos=(0,0))
        y_title = gui.Text(grid, pos=(0,1))
        gui.Label(grid, 'From', pos=(1,0))
        y_from = gui.Text(grid, pos=(1,1))
        gui.Label(grid, 'To', pos=(2,0))
        y_to = gui.Text(grid, pos=(2,1))
        gui.Label(grid, 'Type', pos=(3,0))
        y_type = self.y_type = gui.Choice(grid, pos=(3,1))
        y_type.append('Linear')
        y_type.append('Logarithmic')
        y_type.value = ['linear', 'log'].index(self.graph.ytype)
        y_type.connect('select', lambda value: self.on_set_ytype(value), True)

        for w in [x_title, x_from, x_to, x_type, y_title, y_from, y_to, y_type]:
            w.min_size = (10, w.min_size[1])
        
    def on_set_xtype(self, value):
        self.graph.xtype = ['linear', 'log'][value]
        self.x_type.value = ['linear', 'log'].index(self.graph.xtype)

    def on_set_ytype(self, value):
        self.graph.ytype = ['linear', 'log'][value]
        self.y_type.value = ['linear', 'log'].index(self.graph.xtype)

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
        self.graph.selected_datasets = datasets

        if len(datasets) == 0:
            return

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
        gui.Label(self, 'Worksheet', stretch=0)
        self.toolbar.append(gui.Action('Add', 'Add datasets to the graph', 
                                       self.on_add, 'add.png'))
        self.toolbar.append(gui.Action('Remove', 'Remove datasets from the graph', 
                                       self.on_remove, 'remove.png'))

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

from functions import *

def efloat(f):
    try:
        return float(f)
    except:
        return nan

class GraphFunctionsPanel(gui.Box):
    def __init__(self, func, graph, parent, **place):
        gui.Box.__init__(self, parent, 'vertical', **place)
        self.toolbar = gui.Toolbar(self, stretch=0)

        self.scroll = gui.Scrolled(self)
        self.box = gui.Box(self.scroll, 'vertical')
        self.toolbar.append(gui.Action('Add term', '', self.do_add, 'function.png'))
        self.toolbar.append(gui.Action('Fit properties', '', self.do_configure, 'properties.png'))
        self.toolbar.append(gui.Action('Fit', '', self.do_fit, 'manibela.png'))
        self.toolbar.append(gui.Action('Save parameters', '', 
                            self.do_fit, 'pencil.png'))


        self.set_function(func)
        self.graph = graph

    def do_configure(self):
        pass

    def do_fit(self):
        data = self.graph.selected_datasets[0]
        self.function.fit(data.x, data.y, None, 50)
        for t in self.function.terms:
            for i, txt in enumerate(t._text):
                txt.text = str(t.parameters[i])
        self.function.emit('modified')

    def clear(self):
        pass

    def do_add(self):
        f = FunctionsWindow()
        f.connect('function-activated', self.on_function_activated)
        f.show()
        print >>sys.stderr, 'done'

    def set_function(self, f):
        self.function = f
        self.function.connect('add-term', self.on_add_term)
        self.function.connect('remove-term', self.on_remove_term)
        self.clear()
        for term in self.function:
            self.on_add_term(term)

    def on_add_term(self, term):
        box = gui.Box(self.box, 'vertical', expand=True, stretch=0)
        bpx = gui.Box(box, 'horizontal', expand=True, stretch=0)
        term._butt = gui.Button(bpx, term.name, toggle=True)
        term._butt.connect('toggled', lambda on: self.on_toggled(term, on), True)
        t = gui.Toolbar(bpx, expand=False, stretch=0)
        t.append(gui.Action('x', '', lambda checked: self.on_use(term, checked), 'down.png', type='check'))
        t.append(gui.Action('x', '', lambda: self.on_close(term), 'close.png'))

        term._box = box
        self.create_parambox(term)
        if sum((hasattr(t, '_butt') and t._butt.state) for t in self.function.terms) == 0:
            self.function.terms[0]._butt.state = True
            self.graph.selected_function = self.function.terms[0]

    def on_toggled(self, term, on):
        if sum(t._butt.state for t in self.function.terms) == 0:
            term._butt.state = True
            self.graph.selected_function = term
        else:
            for t in self.function.terms:
                t._butt.state = False
            term._butt.state = True
            self.graph.selected_function = term
        print >>sys.stderr, term

    def create_parambox(self, term):
        parambox = gui.Grid(term._box, len(term.parameters), 3, expand=True)
        parambox.layout.AddGrowableCol(1)
        term._text = []
        for n, par in enumerate(term.function.parameters):
            gui.Label(parambox, par, pos=(n, 0))
            text = gui.Text(parambox, pos=(n, 1))
            text.connect('character', lambda char: self.on_activate(term, n, char), True)
            text.connect('kill-focus', lambda: self.on_activate(term, n), True)
            text.text = str(term.parameters[n])
            term._text.append(text)
            gui.Checkbox(parambox, pos=(n, 2))
        term._parambox = parambox
        self._widget.Fit()

    def on_activate(self, term, n, char=13):
        if char != 13:
            return
        for t in self.function.terms:
            t.parameters = [efloat(txt.text) for txt in t._text]
            for i, txt in enumerate(t._text):
                txt.text = str(t.parameters[i])
        self.function.emit('modified')

    def delete_parambox(self, term):
        term._parambox._widget.Close()
        term._parambox._widget.Destroy()
        term._parambox = None
        self._widget.Fit()
 
    def on_remove_term(self, term):
        term._box._widget.Close()
        term._box._widget.Destroy()
        
    def on_function_activated(self, f):
        self.function.add(f.name, 'foo')

    def on_close(self, f):
        self.function.remove(self.function.terms.index(f))
        if len(self.function.terms) != 0 and sum(t._butt.state for t in self.function.terms) == 0:
            self.function.terms[0]._butt.state = True
            self.graph.selected_function = self.function.terms[0]

    def on_use(self, f, isit):
        if isit:
            if f._parambox is None:
                self.create_parambox(f)
        else:
            self.delete_parambox(f)
        print f, isit
        print f.function.name
        print f.function.parameters
        print f.name
        print f.parameters
        print self.function(1)
