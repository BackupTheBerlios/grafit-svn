import sys
import time
import re
#print >>sys.stderr, "import graph"
import string
import tempfile

from giraffe.arrays import *
from OpenGL.GL import *
from OpenGL.GLU import *

from giraffe.signals import HasSignals
from giraffe.project import Item, wrap_attribute, register_class, create_id
from giraffe.commands import command_from_methods, command_from_methods2, StopCommand
from giraffe.functions import MFunctionSum

#from gl2ps import *
from giraffe.graph_render import *

from giraffe.graph_render import render_symbols, render_lines

from settings import DATADIR

#FONTFILE = DATADIR+'/data/fonts/bitstream-vera/VeraSe.ttf'
FONTFILE = DATADIR+'/data/fonts/bitstream-vera/Vera.ttf'

import mathtextg as mathtext
import numarray.mlab as mlab
import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw

def cut(st, delim):
    pieces = st.split(delim)
    pieces_fixed = []
    if st == '':
        return []

    pieces_fixed.append(pieces[0])

    for p, q in (pieces[n:n+2] for n in range(len(pieces)-1)):
        if (len(p) - len(p.rstrip('\\'))) % 2:
            # has an odd number of trailing backslashes
            pieces_fixed[-1] += delim+q
        else:
            pieces_fixed.append(q)
    if pieces_fixed[0] == '':
        initial = True
        del pieces_fixed[0]
    else: 
        initial = False

    if pieces_fixed[-1] == '':
        del pieces_fixed[-1]

    return zip(pieces_fixed, [bool(x%2)^initial for x in range(len(pieces_fixed))])

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

class XorDraw(object):
    def __init__(self, graph):
        self.graph = graph
        self.coords = None
        self.previous = None
        self.need_redraw = False

    def draw(self, *coords):
        raise NotImplementedError

    def show(self, *pos):
        self.coords = pos
        self.previous = None
        self.need_redraw = True

    def hide(self):
        self.need_redraw = True
        self.coords = None

    def move(self, *pos):
        if not self.need_redraw:
            self.previous = self.coords
        self.coords = pos
        self.need_redraw = True

    def redraw(self):
        if self.need_redraw:
            if self.previous is not None:
                self.draw(*self.previous)
            if self.coords is not None:
                self.draw(*self.coords)
            self.need_redraw = False

class Handle(object):
    def __init__(self, graph, obj, posx, posy):
        self.graph, self.posx, self.posy = graph, posx, posy
        self.obj = obj
        self.graph.connect('display', self.update)

    def update(self):
        self.x, self.y = self.graph.pos2x(self.posx)[0], self.graph.pos2y(self.posy)[0]
        self.p, self.q = self.graph.pos2x(self.posx)[1], self.graph.pos2y(self.posy)[1]
        self.obj.emit('modified')

    def move(self, x, y):
        self.posx, self.posy = self.graph.x2pos(x, self.p), self.graph.y2pos(y, self.q)
        self.update()

    def draw(self):
        glColor3f(0, 0, 1) # blue
        glBegin(GL_LINE_LOOP)
        glVertex3d(self.x-1, self.y-1, 0.0)
        glVertex3d(self.x+1, self.y-1, 0.0)
        glVertex3d(self.x+1, self.y+1, 0.0)
        glVertex3d(self.x-1, self.y+1, 0.0)
        glEnd()

        glColor3f(.7, .2, 0)
        if self.p == 'x':
            glBegin(GL_LINES)
            glVertex3d(self.x, self.y-1, 0)
            glVertex3d(self.x, self.y+1, 0)
            glEnd()
        if self.q == 'y':
            glBegin(GL_LINES)
            glVertex3d(self.x-1, self.y, 0)
            glVertex3d(self.x+1, self.y, 0)
            glEnd()


    def hittest(self, x, y):
        if not hasattr(self, 'x'):
            return False
        return self.x-1<=x<= self.x+1 and self.y-1<=y<=self.y+1


class GraphObject(HasSignals):
    def __init__(self, graph):
        self.graph = graph
        self.handles = []

    def draw(self):
        raise NotImplementedError

    def draw_handles(self):
        for h in self.handles:
            h.draw()

    def begin(self, x, y):
        print >>sys.stderr, self, 'begin', x, y

    def cont(self, x, y):
        print >>sys.stderr, self, 'cont', x, y

    def end(self, x, y):
        print >>sys.stderr, self, 'end', x, y

    def hittest(self, x, y):
        for i, h in enumerate(self.handles):
            if h.hittest(x, y):
                self._active_handle = h
                return True
        self._active_handle = None
        return False

class Line(GraphObject):
    def __init__(self, graph):
        GraphObject.__init__(self, graph)
        self.handles.append(Handle(graph, self, '0%', '0%'))
        self.handles.append(Handle(graph, self, '0%', '0%'))

    def draw(self):
        glColor3f(.3, .5, .7)
        glBegin(GL_LINES)
        glVertex3d(self.handles[0].x, self.handles[0].y, 0)
        glVertex3d(self.handles[1].x, self.handles[1].y, 0)
        glEnd()

    def begin(self, x, y):
        self.handles[0].update()
        self.handles[1].update()
        self.handles[0].move(x, y)
        self.handles[1].move(x, y)
        self._active_handle = self.handles[1]

    def get_x1(self): return self.handles[0].posx
    def set_x1(self, value): self.handles[0].posx = value; self.graph.emit('redraw')
    _x1 = property(get_x1, set_x1)

    def get_y1(self): return self.handles[0].posy
    def set_y1(self, value): self.handles[0].posy = value; self.graph.emit('redraw')
    _y1 = property(get_y1, set_y1)

    def get_x2(self): return self.handles[1].posx
    def set_x2(self, value): self.handles[1].posx = value; self.graph.emit('redraw')
    _x2 = property(get_x2, set_x2)

    def get_y2(self): return self.handles[1].posy
    def set_y2(self, value): self.handles[1].posy = value; self.graph.emit('redraw')
    _y2 = property(get_y2, set_y2)


class Text(GraphObject):
    def __init__(self, graph):
        GraphObject.__init__(self, graph)
        self.handles.append(Handle(graph, self, '0%', '0%'))
        self._text = 'text object\nwith $new$line'

    def draw(self):
        facesize = 12
        self.graph.textpainter.render_text(self.text, facesize, 
                                           self.handles[0].x, self.handles[0].y,
                                           align_x='bottom', align_y='left')

    def get_text(self): return self._text
    def set_text(self, value): self._text = value; self.emit('modified'); self.graph.emit('redraw')
    text = property(get_text, set_text)

    def begin(self, x, y):
        self.handles[0].update()
        self.handles[0].move(x, y)
        self._active_handle = self.handles[0]

class Move(XorDraw):
    def __init__(self, obj):
        XorDraw.__init__(self, obj.graph)
        self.obj = obj

    def draw(self, x, y):
        self.obj._active_handle.move(x, y)
        self.obj.draw_handles()
        self.obj.draw()

class Rubberband(XorDraw):
    def __init__(self, graph):
        XorDraw.__init__(self, graph)

    def draw(self, ix, iy, sx, sy):
        glColor3f(1.0,1.0,0.0) # blue
        glLineStipple (1, 0x4444) # dotted
        glEnable(GL_LINE_STIPPLE)

        glBegin(GL_LINE_LOOP)
        glVertex3d(ix, iy, 0.0)
        glVertex3d(ix, sy, 0.0)
        glVertex3d(sx, sy, 0.0)
        glVertex3d(sx, iy, 0.0)
        glEnd()

        glDisable(GL_LINE_STIPPLE)

class Cross(XorDraw):
    def __init__(self, graph):
        XorDraw.__init__(self, graph)

    def draw(self, x, y):
        glColor3f(1.0,0.5,1.0)
        glBegin(GL_LINES)
        glVertex3d(x-15, y, 0)
        glVertex3d(x+15, y, 0)

        glVertex3d(x, y-15, 0)
        glVertex3d(x, y+15, 0)
        glEnd()

class DrawFunction(XorDraw):
    def __init__(self, graph, function):
        XorDraw.__init__(self, graph)
        self.f = Function(self.graph, totalcolor=(55, 255, 255))
        self.f.func = function

    def draw(self, x, y):
        self.f.func.move(x, y)
        self.f.paint()


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
                gl2ps_Enable(GL2PS__LINE_STIPPLE)
                gl2ps_LineWidth(0.01)
            glColor3f(0.3, 0.3, 0.3)
            glBegin(GL_LINES)
            for x in self.plot.axis_bottom.tics(self.plot.xmin, self.plot.xmax)[0]:
                x, _ = self.plot.proj(x, 0)
                glVertex3d(x, 0.0, 0.0)
                glVertex3d(x, self.plot.plot_height, 0.0)
            glEnd()
            if self.plot.ps:
                gl2ps_Disable(GL2PS__LINE_STIPPLE)
                gl2ps_LineWidth(0.1)
            glDisable(GL_LINE_STIPPLE)

        elif self.orientation == 'vertical':
            glLineStipple (1, 0x4444) # dotted
            glEnable(GL_LINE_STIPPLE)
            if self.plot.ps:
                gl2ps_Enable(GL2PS__LINE_STIPPLE)
                gl2ps_LineWidth(0.01)
            glColor3f(0.3, 0.3, 0.3)
            glBegin(GL_LINES)
            for y in self.plot.axis_left.tics(self.plot.ymin, self.plot.ymax)[0]:
                _, y = self.plot.proj(0, y)
                glVertex3d(0, y, 0.0)
                glVertex3d(self.plot.plot_width, y, 0.0)
            glEnd()
            glDisable(GL_LINE_STIPPLE)
            if self.plot.ps:
                gl2ps_Disable(GL2PS__LINE_STIPPLE)
                gl2ps_LineWidth(0.1)

class Axis(object):
    def __init__(self, position, plot):
        self.position = position
        self.plot = plot
#        self.font = AXISFONT

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
        glColor3d(0.0, 0.0, 0.0) # axis color

        # Axis lines
        w, h = self.plot.plot_width, self.plot.plot_height
        p1, p2 = {'bottom': ((0, 0, 0), (w, 0, 0)),
                  'right':  ((w, 0, 0), (w, h, 0)),
                  'top':    ((0, h, 0), (w, h, 0)),
                  'left':   ((0, 0, 0), (0, h, 0)) } [self.position]
        glBegin(GL_LINES)
        glVertex3d(*p1)
        glVertex3d(*p2)
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
        self.paint_title()

    def paint_title(self):
        facesize = int(3.*self.plot.res)
        if self.position == 'bottom':
            self.plot.textpainter.render_text(self.plot.xtitle, facesize, 
                                              self.plot.plot_width/2, -5,
                                              align_x='center', align_y='top')
        elif self.position == 'left':
            self.plot.textpainter.render_text(self.plot.ytitle, facesize, 
                                              -5-self.plot.ticw, self.plot.plot_height/2, 
                                              align_x='right', align_y='center', orientation='v')


    rexp = re.compile(r'([-?\d\.]+)e([\+\-])(\d+)')

    def totex(self, num, sci=False):
#        if sci:
#            st = "%e"%num
#        else:
        st = "%g"%num
        match = self.rexp.match(st)
        if match is not None:
            mant = match.group(1)
            if mant == '1':
                mant = ''
                cdot = ''
            elif mant == '-1':
                mant = '-'
                cdot = ''
            else:
                cdot = r' \cdot '

            exp = str(int(match.group(3)))

            sign = match.group(2)
            if sign == '+':
                sign = ''
            return r'$%s%s10^{%s%s}$' % (mant, cdot, sign, exp)
        return r'$%s$' % st

    def paint_text(self):
        facesize = int(3.*self.plot.res)

        if self.position == 'bottom':
            tics = self.tics(self.plot.xmin, self.plot.xmax)[0]
            for x in tics:
                st = self.totex(x)
                xm, _ = self.plot.proj(x, 0.)
                self.plot.textpainter.render_text(st, facesize, xm, -5, 'center', 'bottom')
        elif self.position == 'left':
            for y in self.tics(self.plot.ymin, self.plot.ymax)[0]:
                st = self.totex(y)
                _, ym = self.plot.proj(0., y)
                self.plot.textpainter.render_text(st, facesize, -2, ym, 'right', 'center')
 
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
        top = ceil(log10(to)) + 1

        r = 1
        l = 100
        while l>8:
            major = 10**arange(bottom, top, r)
            minor = array([])
            major = array([n for n in major if fr<=n<=to])
            l = len(major)
            r += 1
        return major, minor

    def lintics(self, fr, to):
        # 3-8 major tics
        if fr == to:
            return [fr], []

        exponent = floor(log10(to-fr)) - 1

        for exponent in (exponent, exponent+1):
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

        print "cannot tick", fr, to, len(rng)
        return []

class TextPainter(object):
    def __init__(self, graph):
        self.plot = graph

    #########################################################################
    # Rendering text                                                        #
    #########################################################################

    # Text objects are split into chunks, which are fragments
    # that have the same size and the same type (normal, tex, ...)

    # The render_text_chunk_xxx functions return the size of the
    # text fragment and a renderer. The renderer must be called
    # with the position (lower left corner) of the fragment, 
    # to render the text

    def render_text_chunk_symbol(self, text, size, orientation='h'):
        def renderer(x, y):
            xmin, ymin = self.plot.proj(self.plot.xmin, self.plot.ymin)
            xmax, ymax = self.plot.proj(self.plot.xmax, self.plot.ymax)
            render_symbols(array([x]), array([y]),
                           'square-f', 15, 
                           xmin, xmax, ymin, ymax)

        return 15, 15, 0, renderer

    def render_text_chunk_normal(self, text, size, orientation='h'):
        fonte = PIL.ImageFont.FreeTypeFont(FONTFILE, size) 
        w, h = fonte.getsize(text)
        _, origin = fonte.getmetrics()
        if orientation == 'v': 
            ww, hh, angle = h, w, 90.0
        else: 
            ww, hh, angle = w, h, 0.0

        def renderer(x, y):
            if self.plot.ps:
                glRasterPos2d(x, y)
                font = FT2Font(str(FONTFILE))
                fontname = font.postscript_name
                gl2ps_TextOpt(text, fontname, size, GL2PS__TEXT_BL, angle)
            else:
                image = PIL.Image.new('L', (w, h), 255)
                PIL.ImageDraw.Draw(image).text((0, 0), text, font=fonte)
                image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
                if orientation == 'v':
                    image = image.transpose(PIL.Image.ROTATE_270)
                glRasterPos2d(x, y)
#                ww, wh = image.size
                glDrawPixels(ww, hh, GL_LUMINANCE, GL_UNSIGNED_BYTE, image.tostring())

        return ww, hh, origin, renderer

    def render_text_chunk_tex(self, text, size, orientation='h'):
        """Render a text chunk using mathtext"""
        if self.plot.ps:
            w, h, _, pswriter = mathtext.math_parse_s_ps(text, 72, size)
            _, _, origin, _ = mathtext.math_parse_s_ft2font(text, 72, size) #FIXME
        else:
            w, h, origin, fonts = mathtext.math_parse_s_ft2font(text, 72, size)
#        print >>sys.stderr, w, h, origin, text, self.plot.res, self.plot.ps
        if orientation == 'v': 
            ww, hh, angle = h, w, 90
        else: 
            ww, hh, angle = w, h, 0
        def renderer(x, y):
            if self.plot.ps:
                text = pswriter.getvalue()
                ps = "gsave\n%f %f translate\n%f rotate\n%s\ngrestore\n" \
                    % ((self.plot.marginl+x)*self.plot.res, 
                       (self.plot.marginb+y)*self.plot.res, angle, text)
                self.plot.pstext.append(ps)
            else:
                glRasterPos2d(x, y)
                w, h, imgstr = fonts[0].image_as_str()
                N = w*h
                Xall = zeros((N,len(fonts)), typecode=UInt8)

                for i, f in enumerate(fonts):
                    if orientation == 'v':
                        f.horiz_image_to_vert_image()
                    w, h, imgstr = f.image_as_str()
                    Xall[:,i] = fromstring(imgstr, UInt8)

                Xs = mlab.max(Xall, 1)
                Xs.shape = (h, w)

                pa = zeros(shape=(h,w,4), typecode=UInt8)
                rgb = (0., 0., 0.)
                pa[:,:,0] = int(rgb[0]*255)
                pa[:,:,1] = int(rgb[1]*255)
                pa[:,:,2] = int(rgb[2]*255)
                pa[:,:,3] = Xs[::-1]

                glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, pa.tostring())

        return ww, hh, origin, renderer

    def render_text(self, text, size, x, y, align_x='center', align_y='center', 
                    orientation='h', measure_only=False):
        if not '\n' in text:
            return self.render_text_line(text, size, x, y, align_x, align_y, orientation, measure_only)

        lines = text.splitlines()

        heights = []
        widths = []

        for line in lines:
            w, h = self.render_text_line(line, size, x, y, align_x, align_y, orientation, measure_only=True)
            heights.append(h)
            widths.append(w)

        if orientation == 'h':
            totalh = sum(heights)
            totalw = max(widths)
        elif orientation=='v':
            totalh = max(heights)
            totalw = sum(widths)

        for line, off in zip(lines, [0]+list(cumsum(heights))[:-1]):
            self.render_text_line(line, size, x, y-off, align_x, align_y, orientation)

    def render_text_line(self, text, size, x, y, align_x='center', align_y='center', 
                    orientation='h', measure_only=False):
        if text == '':
            return 0, 0

        # split text into chunks
        chunks = cut(text, '$')

        renderers = []
        widths = []
        heights = []
        origins = []
        for chunk, tex in chunks:
            if tex:
                w, h, origin, renderer = self.render_text_chunk_tex('$'+chunk+'$', int(size*1.3), orientation)
                renderers.append(renderer)
                widths.append(w)
                heights.append(h)
                origins.append(origin)
            else:
                chunks2 = cut(chunk, '@')
                for chunk2, at in chunks2:
                    if at:
                        w, h, origin, renderer = self.render_text_chunk_symbol(chunk2, size, orientation)
                    else:
                        w, h, origin, renderer = self.render_text_chunk_normal(chunk2, size, orientation)
                    renderers.append(renderer)
                    widths.append(w)
                    heights.append(h)
                    origins.append(origin)

        #####################################################################
        #                                    ________        _____          #
        #             ___                   | |      |      |     |         #
        #     ___    |   |    ^           __|_|___ _o|      |     |         #
        #    |   |___|   |    |          |    |   |         |_____|         #
        #    |___|___|___|  totalh     __|____|__o|         |     |   ^     #
        #    |o__|   |o__|    |       |       |  |          |     | origin  #
        #        |o__|        v       |_______|_o|          |o____|   v     #
        #                                                                   #
        #####################################################################

        # compute offsets for each chunk and total size 
        if orientation == 'h':
            hb = max(origins)
            ht = max(h-o for h, o in zip(heights, origins))
            totalw, totalh = sum(widths), hb+ht
            offsets = [hb-o for o in origins]
        elif orientation == 'v':
            hb = max(origins)
            ht = max(h-o for h, o in zip(widths, origins))
            totalw, totalh = hb+ht, sum(heights)
            if self.plot.ps:
                offsets = [ht-v-totalw for v in (h-o for h, o in zip(widths, origins))]
            else:
                offsets = [v-ht for v in (h-o for h, o in zip(widths, origins))]

        if measure_only:
            # return width and height of text, in mm
            return totalw/self.plot.res, totalh/self.plot.res

        # alignment (no change = bottom left)
        if align_x == 'right': 
            x -= totalw/self.plot.res
        elif align_x == 'center': 
            x -= (totalw/2)/self.plot.res

        if align_y == 'top': 
            y -= totalh/self.plot.res
        elif align_y == 'center': 
            y -= (totalh/2)/self.plot.res

        # render chunks
        if orientation == 'h':
            for rend, pos, off in zip(renderers, [0]+list(cumsum(widths)/self.plot.res)[:-1], offsets):
                rend(x+pos, y+off/self.plot.res)
        elif orientation == 'v':
            for rend, pos, off in zip(renderers, [0]+list(cumsum(heights)/self.plot.res)[:-1], offsets):
                rend(x-off/self.plot.res, y+pos)



class Graph(Item, HasSignals):
    def __init__(self, project, name=None, parent=None, location=None):
        Item.__init__(self, project, name, parent, location)
    
        self.paint_xor_objects =  False
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

        self.axes = [self.axis_top, self.axis_right, self.axis_bottom, self.axis_left]

        self.grid_h = Grid('horizontal', self)
        self.grid_v = Grid('vertical', self)

        self.set_range(0.0, 100.5)
        if location is None:
            self.xmin, self.ymin = 0,0  
            self.ymax, self.xmax = 10, 10
        self.newf()

        if self.xtype == '':
            self._xtype = 'linear'
        if self.ytype == '':
            self._ytype = 'linear'
        self.selected_function = None

        self.rubberband = Rubberband(self)
        self.cross = Cross(self)

        self.objects = [self.rubberband, self.cross]
        self.textpainter = TextPainter(self)

        self.graph_objects = []
        self.graph_objects.append(Text(self))
        self.dragobj = None

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


    # axis scales

    def set_xtype(self, _state, tp):
        if tp == 'log' and (self.xmin <= 0 or self.xmax <= 0):
            raise StopCommand
        _state['old'] = self._xtype
        self._xtype = tp
        self.emit('redraw')

    def undo_set_xtype(self, _state):
        self._xtype = _state['old']
        self.emit('redraw')

    set_xtype = command_from_methods2('graph-set-xaxis-scale', set_xtype, undo_set_xtype)

    def get_xtype(self):
        return self._xtype

    xtype = property(get_xtype, set_xtype)

    def set_ytype(self, _state, tp):
        if tp == 'log' and (self.xmin <= 0 or self.xmax <= 0):
            raise StopCommand
        _state['old'] = self._ytype
        self._ytype = tp
        self.emit('redraw')

    def undo_set_ytype(self, _state):
        self._ytype = _state['old']
        self.emit('redraw')

    set_ytype = command_from_methods2('graph-set-xaxis-scale', set_ytype, undo_set_ytype)

    def get_ytype(self):
        return self._ytype

    ytype = property(get_ytype, set_ytype)


    def set_xtitle(self, title):
        self._xtitle = title
    def get_xtitle(self):
        return self._xtitle
    xtitle = property(get_xtitle, set_xtitle)

    def set_ytitle(self, title):
        self._ytitle = title
    def get_ytitle(self):
        return self._ytitle
    ytitle = property(get_ytitle, set_ytitle)

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

    def add(self, state, x, y):
        ind = self.data.datasets.append(worksheet=x.worksheet.id, id=create_id(), 
                                        x=x.name.encode('utf-8'), y=y.name.encode('utf-8'))

        d = Dataset(self, ind)
        self.datasets.append(d)


        pos = len(self.datasets)-1
        print 'added dataset, index %d, position %d' % (ind, pos)

        d.connect('modified', self.on_dataset_modified)
        self.on_dataset_modified(d)
        self.emit('add-dataset', d)

        state['pos'] = pos

        return pos

    def undo_add(self, state):
        pos = state['pos']

        d = self.datasets[pos]
        print 'undoing addition of dataset, index %d, position %d' % (d.ind, pos)
        del self.datasets[pos]
        d.disconnect('modified', self.on_dataset_modified)
        self.emit('remove-dataset', d)
        self.emit('redraw')
        self.data.datasets.delete(d.ind)

    add = command_from_methods2('graph_add_dataset', add, undo_add)

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

    def pos2y(self, pos):
        if pos.endswith('%'):
            return float(pos[:-1])*self.plot_height/100., '%'
        elif pos.endswith('y'):
            return self.proj(self.ymin, float(pos[:-1]))[1], 'y'
        elif pos.endswith('mm'):
            return float(pos[:-2]), 'mm'
        else:
            return float(pos), 'mm'

    def pos2x(self, pos):
        if pos.endswith('%'):
            return float(pos[:-1])*self.plot_width/100., '%'
        elif pos.endswith('x'):
            return self.proj(float(pos[:-1]), self.xmin)[0], 'x'
        elif pos.endswith('mm'):
            return float(pos[:-2]), 'mm'
        else:
            return float(pos), 'mm'

    def x2pos(self, x, typ):
        if typ=='%':
            return str(x*100./self.plot_width)+'%'
        elif typ=='x':
            return str(self.invproj(x, 0)[0])+'x'
        elif typ=='mm':
            return str(x)+'mm'

    def y2pos(self, y, typ):
        if typ=='%':
            return str(y*100./self.plot_height)+'%'
        elif typ=='y':
            return str(self.invproj(0, y)[1])+'y'
        elif typ=='mm':
            return str(y)+'mm'

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
        y = ((self.height_pixels-ym) / self.res) - self.marginb
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
#        self.reshape()
        return [new, old]

    def zoom_redo(self, state):
        new, old = state
        self.xmin, self.xmax, self.ymin, self.ymax = new
        self.reshape()
        self.emit('redraw')

    def zoom_undo(self, state):
        new, old = state
        self.xmin, self.xmax, self.ymin, self.ymax = old
        self.reshape()
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

        # enable transparency
        glEnable (GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glDisable(GL_DEPTH_TEST)
        glShadeModel(GL_FLAT)

        # we need this to render pil fonts properly
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glPixelStorei(GL_PACK_ALIGNMENT, 1)

    def display(self, width=-1, height=-1):
        self.emit('display')
        if width == -1 and height == -1:
            width, height = self.last_width, self.last_height
        else:
            self.last_width, self.last_height = width, height

        if not self.paint_xor_objects:
            t = time.time()
            glClear(GL_COLOR_BUFFER_BIT)

            # set up clipping
            glClipPlane(GL_CLIP_PLANE0, [  1,  0,  0,  0 ])
            glClipPlane(GL_CLIP_PLANE1, [ -1,  0,  0,  self.plot_width ])
            glClipPlane(GL_CLIP_PLANE2, [  0,  1,  0,  0 ])
            glClipPlane(GL_CLIP_PLANE3, [  0, -1,  0,  self.plot_height ])
            for plane in [GL_CLIP_PLANE0, GL_CLIP_PLANE1, 
                          GL_CLIP_PLANE2, GL_CLIP_PLANE3]:
                glEnable(plane)

            for d in self.datasets:
                d.paint()
            for f in self.functions:
                f.paint()

            for plane in [GL_CLIP_PLANE0, GL_CLIP_PLANE1, 
                          GL_CLIP_PLANE2, GL_CLIP_PLANE3]:
                glDisable(plane)

            self.paint_axes()
            for o in self.graph_objects:
                o.draw_handles()
                o.draw()

#            self.pixels = glReadPixels(0, 0, self.width_pixels, self.height_pixels, GL_RGBA, GL_UNSIGNED_BYTE)
#            print pixels
#            print >>sys.stderr, time.time()-t, "seconds"
        else:
#            glClear(GL_COLOR_BUFFER_BIT)
#            if self.pixels is not None:
#                glRasterPos2d(-self.marginl, -self.marginb)
#                glDrawPixels(self.width_pixels, self.height_pixels, GL_RGBA, GL_UNSIGNED_BYTE, self.pixels)
            glLogicOp(GL_XOR)
            glEnable(GL_COLOR_LOGIC_OP)
            for o in self.objects:
                o.redraw()
            glDisable(GL_COLOR_LOGIC_OP)

    def reshape(self, width=-1, height=-1):
        if width == -1 and height == -1:
            width, height = self.last_width, self.last_height
        else:
            self.last_width, self.last_height = width, height

        # resolution (in pixels/mm)
        # diagonal of the window is 15cm
        self.res = sqrt(width*width+height*height)/150.

        # set width and height
        self.width_pixels, self.height_pixels = width, height
        self.width_mm = width / self.res
        self.height_mm = height / self.res

        # measure titles
        facesize = int(3.*self.res)
        if self.xtitle != '':
            _, tith = self.textpainter.render_text(self.xtitle, facesize, 0, 0, 
                                                   measure_only=True)
        else:
            tith=0

        if self.ytitle != '':
            titw, _ = self.textpainter.render_text(self.ytitle, facesize, 0, 0, 
                                                 measure_only=True, orientation='v')
        else:
            titw=0

        # measure tick labels
        self.ticw = max(self.textpainter.render_text(self.axis_left.totex(y), 
                                                     facesize, 0, 0, measure_only=True)[0] 
                        for y in self.axis_left.tics(self.ymin, self.ymax)[0]) # :-)
        self.tich = max(self.textpainter.render_text(self.axis_bottom.totex(x), 
                                                     facesize, 0, 0, measure_only=True)[1] 
                        for x in self.axis_bottom.tics(self.xmin, self.xmax)[0])


        # set margins 
        self.marginb = tith + self.tich + 6
        self.margint = self.height_mm * 0.03
        self.marginl = titw + self.ticw + 6
        self.marginr = self.width_mm * 0.03

        self.plot_width = self.width_mm - self.marginl - self.marginr
        self.plot_height = self.height_mm - self.margint - self.marginb

        # resize the viewport
        glViewport(0, 0, int(width), int(height))
        self.viewport = glGetIntegerv(GL_VIEWPORT)

        # set opengl projection matrix with the origin
        # at the bottom left corner # of the graph 
        # and scale in mm
        glMatrixMode (GL_PROJECTION)
        glLoadIdentity()
        glTranslated(-1.+2.*self.marginl/self.width_mm, 
                     -1.+2.*self.marginb/self.height_mm, 0)
        glScaled(2./self.width_mm, 2./self.height_mm, 1)


    def export_ascii(self, outfile):

        d = tempfile.mkdtemp()
        filename = self.name + '.eps'
        f = open(d+'/'+filename, 'wb')

        # mathtext is not rendered directly
        self.pstext = []

#        gl2psBeginPage("Title", "Producer", self.viewport,
#                       GL2PS__EPS, GL2PS__SIMPLE_SORT, GL2PS__NONE,
#                       GL_RGBA, -1, 0, 0, 0, 0, 21055000, f, filename)

        gl2ps_BeginPage("Title", "Producer", self.viewport, f, filename)
        self.ps = True
        self.display()
        self.ps = False

        gl2ps_EndPage()
        f.close()

        f = open(d+'/'+filename, 'rb')
        for line in f:
            if line == '%%EndProlog\n':
                # insert encoded mathtext fonts
                # at the end of the prolog
                type42 = []
                type42.append(FONTFILE)
                type42.append('/usr/share/matplotlib/cmr10.ttf')
                type42.append('/usr/share/matplotlib/cmex10.ttf')
                type42.append('/usr/share/matplotlib/cmmi10.ttf')
                type42.append('/usr/share/matplotlib/cmsy10.ttf')
                type42.append('/usr/share/matplotlib/cmtt10.ttf')
                for font in type42:
                    print >>outfile, "%%BeginFont: "+FT2Font(str(font)).postscript_name
                    print >>outfile, encodeTTFasPS(font)
                    print >>outfile, "%%EndFont"
                outfile.write(line)
            elif line == 'showpage\n':
                # insert mathtext chunks
                # at the end of the file
                outfile.write(''.join(self.pstext))
                outfile.write(line)
            else:
                # copy lines
                outfile.write(line)
        f.close()

    def button_press(self, x, y, button=None):
        if self.mode == 'zoom':
            if button in (1,3):
                self.paint_xor_objects = True
                self.pixx, self.pixy = x, y
                self.ix, self.iy = self.mouse_to_ident(x, y)
                self.rubberband.show(self.ix, self.iy, self.ix, self.iy)
                self.emit('redraw')
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
#                self.emit('redraw')
                self._movefunc = DrawFunction(self, self.selected_function)
                self.objects.append(self._movefunc)
                self.paint_xor_objects = True
                self._movefunc.show(*self.mouse_to_real(x, y))
                self.emit('redraw')
        elif self.mode == 's-reader':
            self.paint_xor_objects = True
            self.cross.show(*self.mouse_to_ident(x, y))
            self.emit('redraw')
            self.emit('status-message', '%f, %f' % self.mouse_to_real(x, y))
        elif self.mode == 'arrow':
            x, y = self.mouse_to_ident(x, y)
            for o in self.graph_objects:
                if o.hittest(x, y):
                    self.dragobj = o
                    self.dragobj_xor = Move(self.dragobj)
                    self.objects.append(self.dragobj_xor)
                    self.paint_xor_objects = True
                    self.dragobj_xor.show(x, y)
                    self.emit('redraw')
                    self.emit('request-cursor', 'none')
                    break
            else:
                self.emit('request-cursor', 'arrow')
        elif self.mode in ('draw-line', 'draw-text'):
            xi, yi = self.mouse_to_ident(x, y)
            createobj = {'draw-line': Line, 'draw-text': Text}[self.mode](self)
            createobj.begin(xi, yi)
            self.dragobj = createobj
            self.dragobj_xor = Move(self.dragobj)
            self.objects.append(self.dragobj_xor)
            self.paint_xor_objects = True
            self.dragobj_xor.show(xi, yi)
            self.graph_objects.append(createobj)
            self.mode = 'arrow'
            self.emit('redraw')
            self.emit('request-cursor', 'arrow')
      
    def button_doubleclick(self, x, y, button):
        if self.mode == 'arrow' and button == 1:
            x, y = self.mouse_to_ident(x, y)
            for o in self.graph_objects:
                if o.hittest(x, y):
                    self.emit('object-doubleclicked', o)
                    break
     
    def button_release(self, x, y, button):
        if self.mode == 'zoom':
            if button == 2:
                self.autoscale()
                self.emit('redraw')
            elif button == 1 or button == 3:
                self.rubberband.hide()
                self.emit('redraw')
                self.paint_xor_objects = False

                zix, ziy = self.mouse_to_real(self.pixx, self.pixy)
                zfx, zfy = self.mouse_to_real(x, y)

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
                self.reshape()
                self.emit('redraw')
        elif self.mode == 'hand':
            if self.selected_function is not None:
                self.selected_function.set_reg(True)
                self.selected_function.move(*self.mouse_to_real(x, y))
                del self.objects[-1]
                self.paint_xor_objects = False
                self.emit('redraw')
        elif self.mode == 's-reader':
            self.cross.hide()
            self.emit('redraw')
            self.paint_xor_objects = False

        elif self.mode == 'arrow':
            if self.dragobj is not None:
                self.dragobj = None
                self.dragobj_xor.hide()
                self.emit('redraw')
                self.objects.remove(self.dragobj_xor)
                self.paint_xor_objects = False
        
    def button_motion(self, x, y, dragging):
        if self.mode == 'zoom' and dragging:
            self.rubberband.move(self.ix, self.iy, *self.mouse_to_ident(x, y))
            self.emit('redraw')
        elif self.mode in ['range', 'd-reader'] and dragging:
            self.button_press(x, y)
        elif self.mode == 'hand' and dragging:
            if self.selected_function is not None:
                self.selected_function.move(*self.mouse_to_real(x, y))
                self._movefunc.move(*self.mouse_to_real(x, y))
                self.emit('redraw')
        elif self.mode == 's-reader' and dragging:
            self.cross.move(*self.mouse_to_ident(x, y))
            self.emit('redraw')
            self.emit('status-message', '%f, %f' % self.mouse_to_real(x, y))
        elif self.mode == 'arrow':
            if not hasattr(self, 'res'):
                # not initialized yet, do nothing
                return
            x, y = self.mouse_to_ident(x, y)
            if self.dragobj is not None: # drag a handle on an object
                self.dragobj_xor.move(x, y)
                self.emit('redraw')
                self.emit('request-cursor', 'none')
            else: # look for handles
                for o in self.graph_objects:
                    if o.hittest(x, y):
                        self.emit('request-cursor', 'hand')
                        break
                else:
                    self.emit('request-cursor', 'arrow')
     
    name = wrap_attribute('name')
    parent = wrap_attribute('parent')
    _xtype = wrap_attribute('xtype')
    _ytype = wrap_attribute('ytype')
    _xtitle = wrap_attribute('xtitle')
    _ytitle = wrap_attribute('ytitle')
    _zoom = wrap_attribute('zoom')

desc="""
graphs [
    name:S, id:S, parent:S, zoom:S, 
    xtype:S, ytype:S, xtitle:S, ytitle:S,
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


import os
import binascii
from matplotlib.mathtext import math_parse_s_ps, bakoma_fonts
from matplotlib.ft2font import FT2Font

def encodeTTFasPS(fontfile):
    """
    Encode a TrueType font file for embedding in a PS file.
    """
    font = file(fontfile, 'rb')
    hexdata, data = [], font.read(65520)
    b2a_hex = binascii.b2a_hex
    while data:
        hexdata.append('<%s>\n' %
                       '\n'.join([b2a_hex(data[j:j+36]).upper()
                                  for j in range(0, len(data), 36)]) )
        data  = font.read(65520)

    hexdata = ''.join(hexdata)[:-2] + '00>'
    font    = FT2Font(str(fontfile))

    headtab  = font.get_sfnt_table('head')
    version  = '%d.%d' % headtab['version']
    revision = '%d.%d' % headtab['fontRevision']

    dictsize = 8
    fontname = font.postscript_name
    encoding = 'StandardEncoding'
    fontbbox = '[%d %d %d %d]' % font.bbox

    posttab  = font.get_sfnt_table('post')
    minmemory= posttab['minMemType42']
    maxmemory= posttab['maxMemType42']

    infosize = 7
    sfnt     = font.get_sfnt()
    notice   = sfnt[(1,0,0,0)]
    family   = sfnt[(1,0,0,1)]
    fullname = sfnt[(1,0,0,4)]
    iversion = sfnt[(1,0,0,5)]
    fixpitch = str(bool(posttab['isFixedPitch'])).lower()
    ulinepos = posttab['underlinePosition']
    ulinethk = posttab['underlineThickness']
    italicang= '(%d.%d)' % posttab['italicAngle']

    numglyphs = font.num_glyphs
    glyphs = []
    for j in range(numglyphs):
        glyphs.append('/%s %d def' % (font.get_glyph_name(j), j))
        if j != 0 and j%4 == 0:
            glyphs.append('\n')
        else:
            glyphs.append(' ')
    glyphs = ''.join(glyphs)
    data = ['%%!PS-TrueType-%(version)s-%(revision)s\n' % locals()]
    if maxmemory:
        data.append('%%%%VMusage: %(minmemory)d %(maxmemory)d' % locals())
    data.append("""%(dictsize)d dict begin
/FontName /%(fontname)s def
/FontMatrix [1 0 0 1 0 0] def
/FontType 42 def
/Encoding %(encoding)s def
/FontBBox %(fontbbox)s def
/PaintType 0 def
/FontInfo %(infosize)d dict dup begin
/Notice (%(notice)s) def
/FamilyName (%(family)s) def
/FullName (%(fullname)s) def
/version (%(iversion)s) def
/isFixedPitch %(fixpitch)s def
/UnderlinePosition %(ulinepos)s def
/UnderlineThickness %(ulinethk)s def
end readonly def
/sfnts [
%(hexdata)s
] def
/CharStrings %(numglyphs)d dict dup begin
%(glyphs)s
end readonly def
FontName currentdict end definefont pop""" % locals())
    return ''.join(data)

