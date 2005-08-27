from giraffe.arrays import *
from giraffe.signals import HasSignals
from giraffe.commands import command_from_methods2, command_from_methods
from giraffe.functions import MFunctionSum
from giraffe.project import wrap_attribute

from OpenGL.GL import *
from OpenGL.GLU import *

from giraffe.graph_render import *

class Style(HasSignals):
    def __init__(self, color=(0,0,0), symbol='square-f', symbol_size=8,line_type='none', line_style='solid', line_width=0):
        self._color = color
        self._symbol = symbol
        self._symbol_size = symbol_size

        self._line_type = line_type
        self._line_style = line_style
        self._line_width = line_width

    colors = []
    for r in range(0, 256, 64): 
        for g in range(0, 256, 64): 
            for b in range(0, 256, 64):
                colors.append((r,g,b))

    symbols = []
    for interior in ['o', 'f']:
        for symbol in ['circle', 'square', 'diamond', 'uptriangle', 
                      'downtriangle', 'lefttriangle', 'righttriangle']:
            symbols.append(symbol+'-'+interior)
    line_types = ['none', 'straight', 'bspline']
    line_styles = ['solid', 'dotted', 'dashed']

    def __repr__(self):
        return "Style(symbol='%s', color=%s, symbol_size=%d, " \
               "line_type='%s', line_style='%s', line_width=%d)" \
               % (self.symbol, str(self.color), self.symbol_size, 
                  self.line_type, self.line_style, self.line_width)

    def set_line_style(self, val):
        if isinstance(val, int):
            val = self.line_styles[val % len(self.line_styles)]
        self._line_style, old = val, self._line_style
        self.emit('modified', 'line_style', val, old)
    def get_line_style(self):
        return self._line_style
    line_style = property(get_line_style, set_line_style)


    def set_line_type(self, val):
        if isinstance(val, int):
            val = self.line_types[val % len(self.line_types)]
        self._line_type, old = val, self._line_type
        self.emit('modified', 'line_type', val, old)
    def get_line_type(self):
        return self._line_type
    line_type = property(get_line_type, set_line_type)

    def set_line_width(self, val):
        self._line_width, old = val, self._line_width
        self.emit('modified', 'line_width', val, old)
    def get_line_width(self):
        return self._line_width
    line_width = property(get_line_width, set_line_width)

    def set_symbol(self, val):
        if isinstance(val, int):
            val = self.symbols[val]
        self._symbol, old = val, self._symbol
        self.emit('modified', 'symbol', val, old)
    def get_symbol(self):
        return self._symbol
    symbol = property(get_symbol, set_symbol)

    def set_symbol_size(self, val):
        self._symbol_size, old = val, self._symbol_size
        self.emit('modified', 'symbol_size', val, old)
    def get_symbol_size(self):
        return self._symbol_size
    symbol_size = property(get_symbol_size, set_symbol_size)

    def set_color(self, val):
        if isinstance(val, int):
            val = self.colors[val % len(self.colors)]
        self._color, old = val, self._color
        self.emit('modified', 'color', val, old)
    def get_color(self):
        return self._color
    color = property(get_color, set_color)

default_style = Style()

class DrawWithStyle(HasSignals):
    def __init__(self, graph, data):

        self.graph, self.data = graph, data

        self.style = Style()

        try:
            c = self.data.color
            self.style.color = (c%256, (c//256)%256, (c//(256*256))%256)
        except ValueError:
            self.style.color = default_style.color
            self.data.color = '0'

        if self.data.size == 0:
            self.data.size = 6
        self.style.symbol_size = self.data.size

        if self.data.symbol == '':
            self.data.symbol = 'square-f'
        self.style.symbol = self.data.symbol

        if self.data.linestyle == '':
            self.data.linestyle = 'solid'
        self.style.line_style = self.data.linestyle

        if self.data.linetype == '':
            self.data.linetype = 'none'
        self.style.line_type = self.data.linetype

        self.style.line_width = self.data.linewidth
        
        self.style.connect('modified', self.on_style_modified)

    def change_style_do(self, item, value, old):
        if item == 'color':
            self.data.color = (self.style.color[0] + self.style.color[1]*256 + self.style.color[2]*256*256)
        elif item == 'symbol':
            self.data.symbol = self.style.symbol
        elif item == 'symbol_size':
            self.data.size = self.style.symbol_size
        elif item == 'line_type':
            self.data.linetype = self.style.line_type
        elif item == 'line_style':
            self.data.linestyle = self.style.line_style
        elif item == 'line_width':
            self.data.linewidth = self.style.line_width

        return [item, value, old]

    def change_style_redo(self, state):
        item, value, old = state
        setattr(self.style, item, value)

    def change_style_undo(self, state):
        item, value, old = state
        setattr(self.style, item, old)

    def change_style_combine(self, state, other):
#        print state, other
        return False

    change_style = command_from_methods('dataset-change-style', change_style_do, 
                                        change_style_undo, change_style_redo,
                                        combine=change_style_combine)

    def on_style_modified(self, item, value, old):
        self.change_style(item, value, old)
        self.emit('modified', self)

    def paint_symbols(self, x, y):
        if self.style.symbol != 'none' and self.style.symbol_size != 0:
            glColor4f(self.style.color[0]/256., self.style.color[1]/256., 
                      self.style.color[2]/256., 1.)
            gl2ps_PointSize(self.data.size)
            if self.data.size != 0:
                glPointSize(self.data.size)
#            x, y = self.graph.proj(x, y)
            xmin, ymin = self.graph.proj(self.graph.xmin, self.graph.ymin)
            xmax, ymax = self.graph.proj(self.graph.xmax, self.graph.ymax)
            render_symbols(x, y, self.style.symbol, self.style.symbol_size, xmin, xmax, ymin, ymax)

    def paint_lines(self, x, y):
        if len(x) == 0:
            return
        glColor4f(self.style.color[0]/256., self.style.color[1]/256., 
                  self.style.color[2]/256., 1.)

#        x = array([xi for (xi, yi) in zip(xx, yy) if xi is not nan and yi is not nan])
#        y = array([yi for (xi, yi) in zip(xx, yy) if xi is not nan and yi is not nan])
#        x, y = self.graph.proj(x, y)
        z = zeros(len(x))

        N = len(x)

        if self.style.line_style == 'dotted':
            glLineStipple (1, 0x4444)
            glEnable(GL_LINE_STIPPLE)
        elif self.style.line_style == 'dashed':
            glLineStipple (3, 0x4444)
            glEnable(GL_LINE_STIPPLE)
        elif self.style.line_style == 'solid':
            glDisable(GL_LINE_STIPPLE)

        if self.style.line_type == 'bspline':
            nurb = gluNewNurbsRenderer()
            gluNurbsProperty(nurb, GLU_AUTO_LOAD_MATRIX, GL_TRUE)
            gluNurbsProperty(nurb, GLU_SAMPLING_TOLERANCE, 5)
            gluBeginCurve(nurb)
            gluNurbsCurve(nurb,arange(3+N), transpose(array([x, y, z])), GL_MAP1_VERTEX_3)
            gluEndCurve(nurb)
        elif self.style.line_type == 'straight':
            xmin, ymin = self.graph.proj(self.graph.xmin, self.graph.ymin)
            xmax, ymax = self.graph.proj(self.graph.xmax, self.graph.ymax)
            render_lines(x, y, xmin, xmax, ymin, ymax)
#            glVertexPointerd(transpose(array([x, y, z])).tostring())
#            glEnable(GL_VERTEX_ARRAY)
#            glDrawArrays(GL_LINE_STRIP, 0, N)
#            glDisable(GL_VERTEX_ARRAY)

        glDisable(GL_LINE_STIPPLE)

class Dataset(DrawWithStyle):
    def __init__(self, graph, ind):
        self.graph, self.ind = graph, ind
        self.data = self.graph.data.datasets[ind]

        DrawWithStyle.__init__(self, graph, self.data)

        self.worksheet = self.graph.project.items[self.data.worksheet]
        self.x, self.y = self.worksheet[self.data.x], self.worksheet[self.data.y]

        self.xfrom, self.xto = -inf, inf
        self.recalculate()

    def connect_signals(self):
        self.x.connect('data-changed', self.on_data_changed)
        self.y.connect('data-changed', self.on_data_changed)

    def disconnect_signals(self):
        self.x.disconnect('data-changed', self.on_data_changed)
        self.y.disconnect('data-changed', self.on_data_changed)

    def on_data_changed(self):
        self.recalculate()
        self.emit('modified', self)

    def __repr__(self):
        return '<Dataset %s (#%d in graph "%s"), (%s, %s, %s)>' % (self.id, self.graph.datasets.index(self), self.graph.name,
                                                         self.worksheet.name, self.x.name, self.y.name)
    def recalculate(self):
        ind = [i for i in range(len(self.x)) if self.x[i]>= self.xfrom and self.x[i]<=self.xto]
        self.xx = asarray(self.x[ind])
        self.yy = asarray(self.y[ind])

    def set_range(self, _state, range):
        _state['old'] = self.xfrom, self.xto
        self.xfrom, self.xto = range
        self.recalculate()
        self.emit('modified', self)

    def undo_set_range(self, _state):
        self.xfrom, self.xto = _state['old']
        self.recalculate()
        self.emit('modified', self)

    def get_range(self):
        return self.xfrom, self.xto

    set_range = command_from_methods2('dataset-set-range', set_range, undo_set_range)

    range = property(get_range, set_range)


    def paint(self):
        xx, yy = self.graph.proj(self.xx, self.yy)
        self.paint_lines(xx, yy)
        self.paint_symbols(xx, yy)

    id = wrap_attribute('id')

    # this is nescessary! see graph.remove
    def __eq__(self, other):
        return self.id == other.id

    def set_worksheet(self, ws): self.data.worksheet = ws.id
    def get_worksheet(self): return self.graph.project.items[self.data.worksheet]

    def __str__(self):
        return self.x.worksheet.name+':'+self.y.name+'('+self.x.name+')'

class Nop:
    pass

class Function(DrawWithStyle):
    def __init__(self, graph, totalcolor=(0, 0, 155), termcolor=(0, 0, 0)):
        self.graph = graph
        self.data =  Nop()
        self.data.color = '0'
        self.data.size = '0'
        self.data.symbol = ''
        self.data.color = 0
        self.data.linestyle = ''
        self.data.linetype = ''
        self.data.linewidth = ''
#        self.data['color']
#self.graph.data.functions[ind]

        DrawWithStyle.__init__(self, graph, self.data)
        self.style._line_style = 'solid'
        self.style._line_type = 'straight'

        self.totalcolor, self.termcolor = totalcolor, termcolor

        self.func = MFunctionSum(self.graph.data.functions)

    def paint(self):
        npoints = 100
        if self.graph.xtype == 'log':
            x = 10**arange(log10(self.graph.xmin), log10(self.graph.xmax), 
                           (log10(self.graph.xmax/self.graph.xmin))/npoints)
        else:
            x = arange(self.graph.xmin, self.graph.xmax, 
                       (self.graph.xmax-self.graph.xmin)/npoints)

        self.style._color = self.termcolor
        if hasattr(self.func, 'terms'):
            for term in self.func.terms:
                if term.enabled:
                    y = term(x)
                    self.paint_lines(*self.graph.proj(x, y))

        self.style._color = self.totalcolor
        y = self.func(x)
        self.paint_lines(*self.graph.proj(x, y))

    def set_id(self, id): self.data.id = id
    def get_id(self): return self.data.id
    id = property(get_id, set_id)

    # this is necessary! see graph.remove
    def __eq__(self, other):
        return self.id == other.id


