import sys
import time
print >>sys.stderr, "import graph"
import string

from giraffe.arrays import *
from OpenGL.GL import *
from OpenGL.GLU import *

from giraffe.signals import HasSignals
from giraffe.project import Item, wrap_attribute, register_class, create_id
from giraffe.commands import command_from_methods
from giraffe.functions import MFunctionSum

from ftgl import FTGLPixmapFont
from gl2ps import *

from giraffe.graph_render import render

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
            gl2psPointSize(self.data.size)
            if self.data.size != 0:
                glPointSize(self.data.size)
#            x, y = self.graph.proj(x, y)
            render(x, y, self.style.symbol, self.style.symbol_size)

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
            glVertexPointerd(transpose(array([x, y, z])))
            glEnable(GL_VERTEX_ARRAY)
            glDrawArrays(GL_LINE_STRIP, 0, N)
            glDisable(GL_VERTEX_ARRAY)

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

        self.x.connect('data-changed', self.on_data_changed)
        self.y.connect('data-changed', self.on_data_changed)

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

    def set_range(self, range):
        self.xfrom, self.xto = range
        self.recalculate()
        self.emit('modified', self)

    def get_range(self):
        return self.xfrom, self.xto

    range = property(get_range, set_range)

    def paint(self):
        xx, yy = self.graph.proj(self.xx, self.yy)
        self.paint_lines(xx, yy)
        self.paint_symbols(xx, yy)

    def set_id(self, id): self.data.id = id
    def get_id(self): return self.data.id
    id = property(get_id, set_id)

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
    def __init__(self, graph):
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

        self.func = MFunctionSum(self.graph.data.functions)

    def paint(self):
        npoints = 100
        if self.graph.xtype == 'log':
            x = 10**arange(log10(self.graph.xmin), log10(self.graph.xmax), 
                           (log10(self.graph.xmax/self.graph.xmin))/npoints)
        else:
            x = arange(self.graph.xmin, self.graph.xmax, 
                       (self.graph.xmax-self.graph.xmin)/npoints)

        self.style._color = (0,0,0)
        for term in self.func.terms:
            if term.enabled:
                y = term(x)
                self.paint_lines(*self.graph.proj(x, y))

        self.style._color = (0, 0, 155)
        y = self.func(x)
        self.paint_lines(*self.graph.proj(x, y))

    def set_id(self, id): self.data.id = id
    def get_id(self): return self.data.id
    id = property(get_id, set_id)

    # this is necessary! see graph.remove
    def __eq__(self, other):
        return self.id == other.id

class Grid(object):
    def __init__(self, orientation, plot):
        assert orientation in ['horizontal', 'vertical']
        self.orientation = orientation
        self.plot = plot

    def paint(self):
        if self.orientation == 'horizontal':
            glLineStipple (1, 0x4444) # dotted
            glEnable(GL_LINE_STIPPLE)
            if self.plot.ps:
                gl2psEnable(GL2PS_LINE_STIPPLE)
                gl2psLineWidth(0.01)
            glColor3f(0.3, 0.3, 0.3)
            glBegin(GL_LINES)
            for x in self.plot.axis_bottom.tics(self.plot.xmin, self.plot.xmax)[0]:
                x, _ = self.plot.proj(x, 0)
                glVertex3d(x, 0.0, 0.0)
                glVertex3d(x, self.plot.plot_height, 0.0)
            glEnd()
            if self.plot.ps:
                gl2psDisable(GL2PS_LINE_STIPPLE)
                gl2psLineWidth(0.1)
            glDisable(GL_LINE_STIPPLE)

        elif self.orientation == 'vertical':
            glLineStipple (1, 0x4444) # dotted
            glEnable(GL_LINE_STIPPLE)
            if self.plot.ps:
                gl2psEnable(GL2PS_LINE_STIPPLE)
                gl2psLineWidth(0.01)
            glColor3f(0.3, 0.3, 0.3)
            glBegin(GL_LINES)
            for y in self.plot.axis_left.tics(self.plot.ymin, self.plot.ymax)[0]:
                _, y = self.plot.proj(0, y)
                glVertex3d(0, y, 0.0)
                glVertex3d(self.plot.plot_width, y, 0.0)
            glEnd()
            glDisable(GL_LINE_STIPPLE)
            if self.plot.ps:
                gl2psDisable(GL2PS_LINE_STIPPLE)
                gl2psLineWidth(0.1)

from settings import DATADIR
FONTFILE = DATADIR+'/data/fonts/bitstream-vera/VeraSe.ttf'
AXISFONT = FTGLPixmapFont(FONTFILE)

class Axis(object):
    def __init__(self, position, plot):
        self.position = position
        self.plot = plot
        self.font = AXISFONT

    def transform(self, data):
        if self.position in ['bottom', 'top'] and self.plot.xtype == 'log':
            return log10(data)
        if self.position in ['left', 'right'] and self.plot.ytype == 'log':
            return log10(data)
        return data

    def invtransform(self, data):
        if self.position in ['bottom', 'top'] and self.plot.xtype == 'log':
            return 10**data
        if self.position in ['left', 'right'] and self.plot.ytype == 'log':
            return 10**data
        return data

    def paint(self):
        glColor3d(0.87, 0.85, 0.83) # background color
        if self.position == 'bottom':
            glRectd(-self.plot.marginl, -self.plot.marginb, 
                    self.plot.width_mm-self.plot.marginl, 0)
        elif self.position == 'right':
            glRectd(self.plot.plot_width, -self.plot.marginb,
                    self.plot.width_mm-self.plot.marginl, self.plot.height_mm-self.plot.marginb)
        elif self.position == 'top':
            glRectd(-self.plot.marginl, self.plot.height_mm-self.plot.marginb,
                    self.plot.width_mm-self.plot.marginl, self.plot.plot_height)
        elif self.position == 'left':
            glRectd(-self.plot.marginl, self.plot.height_mm-self.plot.marginb,
                    0, 0)

        glColor3d(0.0, 0.0, 0.0) # axis color

        # Axis lines
        glBegin(GL_LINES)
        if self.position == 'bottom':
            glVertex3d(0., 0., 0.)
            glVertex3d(self.plot.plot_width, 0., 0.0)
        elif self.position == 'right':
            glVertex3d(self.plot.plot_width, 0., 0.)
            glVertex3d(self.plot.plot_width, self.plot.plot_height, 0.0)
        elif self.position == 'top':
            glVertex3d(0., self.plot.plot_height, 0.)
            glVertex3d(self.plot.plot_width, self.plot.plot_height, 0.0)
        elif self.position == 'left':
            glVertex3d(0., 0., 0.)
            glVertex3d(0., self.plot.plot_height, 0.0)
        glEnd()

        # Tics
        if self.position == 'bottom':
            major, minor = self.tics(self.plot.xmin, self.plot.xmax)
            glBegin(GL_LINES)
            for x in major:
                x, _ = self.plot.proj(x, 0)
                glVertex3d(x, 0, 0)
                glVertex3d(x, 2, 0)
            for x in minor:
                x, _ = self.plot.proj(x, 0)
                glVertex3d(x, 0, 0)
                glVertex3d(x, 1, 0)
            glEnd()

        elif self.position == 'left':
            major, minor = self.tics(self.plot.ymin, self.plot.ymax)
            glBegin(GL_LINES)
            for y in major:
                _, y = self.plot.proj(0, y)
                glVertex3d(0, y, 0)
                glVertex3d(2, y, 0)
            for y in minor:
                _, y = self.plot.proj(0, y)
                glVertex3d(0, y, 0)
                glVertex3d(1, y, 0)
            glEnd()

        self.paint_text()

    def paint_text(self):
        h = int(2.6*self.plot.res)
        self.font.FaceSize(h)
        if self.position == 'bottom':
            for x in self.tics(self.plot.xmin, self.plot.xmax)[0]:
                st = '%g'%x
                xm, _ = self.plot.proj(x, 0.)
                w = self.font.Advance(st)
                glRasterPos2d(xm - (w/2)/self.plot.res, -4)
                if self.plot.ps:
                    gl2psText(st, "Times-Roman", h)
                else:
                    self.font.Render(st)
        elif self.position == 'left':
            for y in self.tics(self.plot.ymin, self.plot.ymax)[0]:
                st = '%g'%y
                _, ym = self.plot.proj(0., y)
                w = self.font.Advance(st)
                glRasterPos2d(-w/self.plot.res - 2, ym - (h/2)/self.plot.res)
                if self.plot.ps:
                    gl2psText(st, "TimesRoman", h)
                else:
                    self.font.Render(st)

    def tics(self, fr, to):
        if (self.position in ['right', 'left'] and self.plot.ytype == 'log') or\
           (self.position in ['bottom', 'top'] and self.plot.xtype == 'log'):
            return self.logtics(fr, to)
        else:
            return self.lintics(fr, to)


    def logtics(self, fr, to):
        if fr <= 0 or to <= 0:
            return [], []
        if fr == to:
            return [fr], []

        bottom = floor(log10(fr))
        top = ceil(log10(to))

        major = 10**arange(bottom, top+1)
        minor = array([])
        major = array([n for n in major if fr<=n<=to])
        return major, minor

    def lintics(self, fr, to):
        # 3-8 major tics
        if fr == to:
            return [fr], []
        exponent = floor(log10(to-fr)) - 1

        for interval in (1,5,2):#,4,6,7,8,9,3):
            interval = interval * (10**exponent)
            if fr%interval == 0:
                first = fr
            else:
                first = fr + (interval-fr%interval)
            first -= interval
            rng = arange(first, to, interval)
            if 4 <= len(rng) <= 8:
                minor = []
                for n in rng:
                    minor.extend(arange(n, n+interval, interval/5))
                rng = array([n for n in rng if fr<=n<=to])
                minor = array([n for n in minor if fr<=n<=to])
                return rng, minor
#
        exponent += 1
        for interval in (1,5,2):#,4,6,7,8,9,3):
            interval = interval * (10**exponent)
            if fr%interval == 0:
                first = fr
            else:
                first = fr + (interval-fr%interval)
            first -= interval
            rng = arange(first, to, interval)
            if 4 <= len(rng) <= 8:
#                print 'from %f to %f:'%(fr, to), rng
                minor = []
                for n in rng:
                    minor.extend(arange(n, n+interval, interval/5))
                rng = array([n for n in rng if fr<=n<=to])
                minor = array([n for n in minor if fr<=n<=to])
                return rng, minor
        print "cannot tick", fr, to, len(rng)
        return []

class Graph(Item, HasSignals):
    def __init__(self, project, name=None, parent=None, location=None):
        Item.__init__(self, project, name, parent, location)
    
        # mouse rubberbanding coordinates
        self.sx = None
        self.px = None
        self.sy = None
        self.py = None

        self.buf =  False
        self.selected_datasets = []

        self.mode = 'arrow'

        self.datasets = []
        if location is not None:
            for i in range(len(self.data.datasets)):
                if not self.data.datasets[i].id.startswith('-'):
                    d = Dataset(self, i)
                    self.datasets.append(d)
                    d.connect('modified', self.on_dataset_modified)

        self.functions = []
#        if location is not None:
#            for i in range(len(self.data.functions)):
#                if not self.data.functions[i].id.startswith('-'):
#                    f = Function(self, i)
#                    self.functions.append(f)
#                    f.connect('modified', self.on_dataset_modified)
#                    f.func.connect('modified', self.on_dataset_modified)

        self.ps = False

        self.axis_top = Axis('top', self)
        self.axis_bottom = Axis('bottom', self)
        self.axis_right = Axis('right', self)
        self.axis_left = Axis('left', self)

        self.axes = [self.axis_bottom, self.axis_top, self.axis_right, self.axis_left]

        self.grid_h = Grid('horizontal', self)
        self.grid_v = Grid('vertical', self)

        self.set_range(0.0, 100.5)
        if location is None:
            self.xmin, self.ymin = 0,0  
            self.ymax, self.xmax = 10, 10
        self.newf()

        if self.xtype == '':
            self.xtype = 'linear'
        if self.ytype == '':
            self.ytype = 'linear'
        self.selected_function = None

    default_name_prefix = 'graph'

    def get_xmin(self): 
        try: return float(self._zoom.split()[0])
        except IndexError: return 0.0
    def get_xmax(self): 
        try: return float(self._zoom.split()[1])
        except IndexError: return 1.0
    def get_ymin(self): 
        try: return float(self._zoom.split()[2])
        except IndexError: return 0.0
    def get_ymax(self): 
        try: return float(self._zoom.split()[3])
        except IndexError: return 1.0
    def set_xmin(self, value): self._zoom = ' '.join([str(f) for f in [value, self.xmax, self.ymin, self.ymax]])
    def set_xmax(self, value): self._zoom = ' '.join([str(f) for f in [self.xmin, value, self.ymin, self.ymax]])
    def set_ymin(self, value): self._zoom = ' '.join([str(f) for f in [self.xmin, self.xmax, value, self.ymax]])
    def set_ymax(self, value): self._zoom = ' '.join([str(f) for f in [self.xmin, self.xmax, self.ymin, value]])
    xmin = property(get_xmin, set_xmin)
    xmax = property(get_xmax, set_xmax)
    ymin = property(get_ymin, set_ymin)
    ymax = property(get_ymax, set_ymax)

    def set_xtype(self, tp):
        if tp == 'log' and (self.xmin <= 0 or self.xmax <= 0):
            return
        self._xtype = tp
        self.emit('redraw')
    def get_xtype(self):
        return self._xtype
    xtype = property(get_xtype, set_xtype)

    def set_ytype(self, tp):
        if tp == 'log' and (self.ymin <= 0 or self.ymax <= 0):
            return
        self._ytype = tp
        self.emit('redraw')
    def get_ytype(self):
        return self._ytype
    ytype = property(get_ytype, set_ytype)

    def __repr__(self):
        return '<Graph %s%s>' % (self.name, '(deleted)'*self.id.startswith('-'))

    def newf(self):
#        ind = self.data.functions.append(id=create_id())
        f = Function(self)
        f.connect('modified', self.on_dataset_modified)
        f.func.connect('modified', self.on_dataset_modified)
        self.functions.append(f)
        self.emit('add-function', f)
        return f

    # add and remove datasets

    def add(self, x, y):
        ind = self.data.datasets.append(worksheet=x.worksheet.id, id=create_id(), 
                                        x=x.name.encode('utf-8'), y=y.name.encode('utf-8'))

        d = Dataset(self, ind)
        self.datasets.append(d)


        pos = len(self.datasets)-1
        print 'added dataset, index %d, position %d' % (ind, pos)

        d.connect('modified', self.on_dataset_modified)
        self.on_dataset_modified(d)
        self.emit('add-dataset', d)

        return pos

    def undo_add(self, pos):
        d = self.datasets[pos]
        print 'undoing addition of dataset, index %d, position %d' % (d.ind, pos)
        del self.datasets[pos]
        d.disconnect('modified', self.on_dataset_modified)
        self.emit('remove-dataset', d)
        self.emit('redraw')
        self.data.datasets.delete(d.ind)

    add = command_from_methods('graph_add_dataset', add, undo_add)

    def remove(self, dataset):
        # we can do this even if `dataset` is a different object
        # than the one in self.datasets, if they have the same id
        # (see Dataset.__eq__)
        ind = self.datasets.index(dataset)
        print 'removing dataset, index %d, position %d' % (dataset.ind, ind)
        dataset.id = '-'+dataset.id
        self.datasets.remove(dataset)
        try:
            dataset.disconnect('modified', self.on_dataset_modified)
        except NameError:
            pass
        self.emit('remove-dataset', dataset)
        self.emit('redraw')
        return (dataset.ind, ind), None

    def undo_remove(self, data):
        ind, pos = data
        print 'undoing removal of dataset, index %d, position %d' % (ind, pos)
        dataset = Dataset(self, ind)
        dataset.id = dataset.id[1:]
        self.on_dataset_modified(dataset)
        self.datasets.insert(pos, dataset)
        dataset.connect('modified', self.on_dataset_modified)
        self.emit('add-dataset', dataset)
        self.emit('redraw')

    remove = command_from_methods('graph_remove_dataset', remove, undo_remove)

    def on_dataset_modified(self, d=None):
        self.emit('redraw')

    def paint_axes(self):
        for a in self.axes:
            a.paint()

        self.grid_h.paint()
        self.grid_v.paint()

    def proj(self, x, y):
        x, xmin, xmax = map(self.axis_bottom.transform, (x, self.xmin, self.xmax))
        y, ymin, ymax = map(self.axis_left.transform, (y, self.ymin, self.ymax))

        px = self.plot_width * (x-xmin)/(xmax-xmin)
        py = self.plot_height * (y-ymin)/(ymax-ymin)

        return px, py

    def invproj(self, x, y):
        xmin, xmax = map(self.axis_bottom.transform, (self.xmin, self.xmax))
        ymin, ymax = map(self.axis_left.transform, (self.ymin, self.ymax))

        px = x*(xmax-xmin)/self.plot_width + xmin
        py = y*(ymax-ymin)/self.plot_height + ymin

        return self.axis_bottom.invtransform(px), self.axis_left.invtransform(py)

    def mouse_to_ident(self, xm, ym):
        x = (xm / self.res) - self.marginl
        y = ((self.h-ym) / self.res) - self.marginb
        return x, y

    def mouse_to_real(self, xm, ym):
        x, y = self.mouse_to_ident(xm, ym)
        return self.invproj(x, y)

    def autoscale(self):
        if len(self.datasets):
            self.zoom(
                array(self.datasets[0].x).min(),
                array(self.datasets[0].y).min(),
                array(self.datasets[0].x).max(),
                array(self.datasets[0].y).max())

    def set_range(self, fr, to):
        self.fr, self.to  = fr, to

    #####################
    # zoom command      #
    #####################

    def zoom_do(self, xmin, xmax, ymin, ymax):
        eps = 1e-24
        old = (self.xmin, self.xmax, self.ymin, self.ymax)
        if abs(xmin-xmax)<=eps or abs(ymin-ymax)<=eps:
            return
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        new = (xmin, xmax, ymin, ymax)
        return [new, old]

    def zoom_redo(self, state):
        new, old = state
        self.xmin, self.xmax, self.ymin, self.ymax = new
        self.emit('redraw')

    def zoom_undo(self, state):
        new, old = state
        self.xmin, self.xmax, self.ymin, self.ymax = old
        self.emit('redraw')

    def zoom_combine(self, state, other):
        return False

    zoom = command_from_methods('graph-zoom', zoom_do, zoom_undo, zoom_redo, combine=zoom_combine)

 
    def zoomout(self,x1, x2,x3, x4):
        a = (x2-x1)/(x4-x3)
        c = x1 - a*x3
        f1 = a*x1 + c
        f2 = a*x2 + c
        return min(f1, f2), max(f1, f2)

    def init(self):
        glClearColor(252./256, 252./256, 252./256, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

#        # enable transparency
#        glEnable (GL_BLEND)
#        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glDisable(GL_DEPTH_TEST)
        glShadeModel(GL_FLAT)

        glMatrixMode (GL_PROJECTION)
        glLoadIdentity ()

    def display(self, width=-1, height=-1):
        if width == -1 and height == -1:
            width, height = self.last_width, self.last_height
        else:
            self.last_width, self.last_height = width, height

        if not self.buf:
            t = time.time()
            glClear(GL_COLOR_BUFFER_BIT)
            for d in self.datasets:
                d.paint()
            for f in self.functions:
                f.paint()

            self.paint_axes()
            print >>sys.stderr, time.time()-t, "seconds"
        else:
            glColor3f(1.0,1.0,0.0)
            glLineStipple (1, 0x4444) # dotted
            if self.ps:
                gl2psEnable(GL2PS_LINE_STIPPLE)
            else:
                glEnable(GL_LINE_STIPPLE)
            glLogicOp(GL_XOR)
            glEnable(GL_COLOR_LOGIC_OP)

            if (self.px, self.py) != (None, None):
                glBegin(GL_LINE_LOOP)
                glVertex3d(self.ix, self.iy, 0.0)
                glVertex3d(self.ix, self.py, 0.0)
                glVertex3d(self.px, self.py, 0.0)
                glVertex3d(self.px, self.iy, 0.0)
                glEnd()

            glBegin(GL_LINE_LOOP)
            glVertex3d(self.ix, self.iy, 0.0)
            glVertex3d(self.ix, self.sy, 0.0)
            glVertex3d(self.sx, self.sy, 0.0)
            glVertex3d(self.sx, self.iy, 0.0)
            glEnd()
            self.px, self.py = self.sx, self.sy

            if self.ps:
                gl2psDisable(GL2PS_LINE_STIPPLE)
            else:
                glDisable(GL_LINE_STIPPLE)
            glDisable(GL_COLOR_LOGIC_OP)

    
    def reshape(self, width, height):
        self._shape = (width, height)

#        # aspect ratio to keep 
#        ratio = 4./3.

        # set width and height (in pixels)
        self.ww, self.hh = self.w, self.h = width, height

        # resolution (in pixels/mm)
        self.res = self.w/100.

        self.width_mm = self.w / self.res
        self.height_mm = self.h / self.res

#        if (1.*self.w) / self.h > ratio:
#            self.ww = ratio*self.h
#        else:
#            self.hh = self.w/ratio

#        self.excessh = height - self.hh
#        self.excessw = width - self.ww
#        self.w -= self.excessw

        # set margins 
        self.marginb = self.height_mm * 0.1
        self.margint = self.height_mm * 0.05
        self.marginl = self.width_mm * 0.15
        self.marginr = self.width_mm * 0.05

        self.plot_width = self.width_mm - self.marginl - self.marginr
        self.plot_height = self.height_mm - self.margint - self.marginb

        # resize the viewport
        glViewport(0, 0, int(self.w), int(self.h))
        self.viewport = glGetIntegerv(GL_VIEWPORT)

        self.xscale_pixel = 2./self.w
        self.yscale_pixel = 2./self.h

        self.xscale_mm = self.xscale_pixel * self.res
        self.yscale_mm = self.yscale_pixel * self.res

        self.reset_matrix()

    def reset_matrix(self):
        """Reset the matrix at the bottom left corner of the graph with scale in mm"""
        glLoadIdentity()
        glTranslated(-1.+2.*self.marginl/self.width_mm, 
                     -1.+2.*self.marginb/self.height_mm, 0) # go to corner
        glScaled(2./self.width_mm, 2./self.height_mm, 1) # scale is mm

    def rubberband_begin(self, x, y):
        self.buf = True
        self.pixx, self.pixy = x, y

        # zooming box in identity coordinates
        self.ix, self.iy = self.mouse_to_ident(x, y)
        self.sx, self.sy = self.ix, self.iy

    def rubberband_active(self):
        return self.buf

    def rubberband_continue(self, x, y):
        self.sx, self.sy = self.mouse_to_ident(x, y)
        self.emit('redraw')

    def rubberband_end(self, x, y):
        self.rubberband_continue(x, y)
        self.buf = False
        self.px, self.py = None, None
        return self.pixx, self.pixy, x, y

    def export_ascii(self, f):
        gl2psBeginPage("Title", "Producer", 
                       self.viewport,
                       GL2PS_EPS, GL2PS_NO_SORT, GL2PS_NONE,
                       GL_RGBA, -1,
                       0,
                       0, 0, 0,
                       21055000, f,
                       "arxi.eps")
        self.ps = True
#        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.display()
        self.ps = False

        gl2psEndPage()

    def button_press(self, x, y, button=None):
        if self.mode == 'zoom':
            if button in (1,3):
                self.rubberband_begin(x, y)
            if button == 2:
                self.haha = True
            else:
                self.haha = False
        elif self.mode == 'range':
            if button is None:
                button = self.__button
            else:
                self.__button = button

            x, y = self.mouse_to_real(x, y)
            for d in self.selected_datasets:
                if button == 1:
                    d.range = (x, d.range[1])
                elif button == 3:
                    d.range = (d.range[0], x)
                elif button == 2:
                    d.range = (-inf, inf)
        elif self.mode == 'hand':
            if self.selected_function is not None:
                self.selected_function.set_reg(False)
                self.selected_function.move(*self.mouse_to_real(x, y))
                self.emit('redraw')
        elif self.mode == 's-reader':
            self.emit('status-message', '%f, %f' % self.mouse_to_real(x, y))

     
    def button_release(self, x, y, button):
        if self.mode == 'zoom':
            if button == 2:
                self.autoscale()
                self.emit('redraw')
            elif button == 1 or button == 3:
                zix, ziy, zfx, zfy = self.rubberband_end(x, y)

                zix, ziy = self.mouse_to_real(zix, ziy)
                zfx, zfy = self.mouse_to_real(zfx, zfy)

                _xmin, _xmax = min(zix, zfx), max(zix, zfx)
                _ymin, _ymax = min(zfy, ziy), max(zfy, ziy)

                if button == 3:
                    _xmin, _xmax = self.axis_bottom.transform(_xmin), self.axis_bottom.transform(_xmax)
                    _ymin, _ymax = self.axis_left.transform(_ymin), self.axis_left.transform(_ymax)

                    xmin, xmax = self.zoomout(self.axis_bottom.transform(self.xmin), 
                                              self.axis_bottom.transform(self.xmax), _xmin, _xmax)
                    ymin, ymax = self.zoomout(self.axis_left.transform(self.ymin), 
                                              self.axis_left.transform(self.ymax), _ymin, _ymax)

                    xmin, xmax = self.axis_bottom.invtransform(xmin), self.axis_bottom.invtransform(xmax)
                    ymin, ymax = self.axis_left.invtransform(ymin), self.axis_left.invtransform(ymax)
                else:
                    xmin, xmax, ymin, ymax = _xmin, _xmax, _ymin, _ymax
                self.zoom(xmin, xmax, ymin, ymax)
                self.emit('redraw')
        elif self.mode == 'hand':
            if self.selected_function is not None:
                self.selected_function.set_reg(True)
                self.selected_function.move(*self.mouse_to_real(x, y))
                self.emit('redraw')
        
    def button_motion(self, x, y):
        if self.mode == 'zoom':
            self.rubberband_continue(x, y)
        elif self.mode in ['range', 's-reader', 'd-reader']:
            self.button_press(x, y)
        elif self.mode == 'hand':
            if self.selected_function is not None:
                self.selected_function.move(*self.mouse_to_real(x, y))
                self.emit('redraw')
 
    name = wrap_attribute('name')
    parent = wrap_attribute('parent')
    _xtype = wrap_attribute('xtype')
    _ytype = wrap_attribute('ytype')
    _zoom = wrap_attribute('zoom')

desc="""
graphs [
    name:S, id:S, parent:S, zoom:S, xtype:S, ytype:S,
    datasets [
        id:S, worksheet:S, x:S, y:S,
        symbol:S, color:I, size:I, linetype:S,
        linestyle:S, linewidth:I,
        xfrom:D, xto:D 
    ],
    functions [
        id:S, func:S, name:S,
        params:S, lock:S, use:I
    ]
]
"""

for w in string.whitespace:
    desc = desc.replace(w, '')

register_class(Graph, desc)
