import sys
import time
import re
print >>sys.stderr, "import graph"
import string

from giraffe.arrays import *
from OpenGL.GL import *
from OpenGL.GLU import *

from giraffe.signals import HasSignals
from giraffe.project import Item, wrap_attribute, register_class, create_id
from giraffe.commands import command_from_methods, command_from_methods2, StopCommand
from giraffe.functions import MFunctionSum

from ftgl import FTGLPixmapFont
from gl2ps import *

from giraffe.graph_render import render_symbols, render_lines

def cut(st, delim):
    pieces = st.split(delim)
    pieces_fixed = []

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
            gl2psPointSize(self.data.size)
            if self.data.size != 0:
                glPointSize(self.data.size)
#            x, y = self.graph.proj(x, y)
            render_symbols(x, y, self.style.symbol, self.style.symbol_size)

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
            render_lines(x, y)
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

import mathtextg as mathtext
import numarray.mlab as mlab

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
#        glColor3d(0.87, 0.85, 0.83) # background color
#        glColor3d(*[c/255. for c in (245, 222, 179)])
        glColor3d(1, 1, 1)
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
        self.paint_title()

    def paint_title(self):
        if self.position == 'bottom':
            st = r'frequency [Hz]'
            facesize = int(3.*self.plot.res)
            x = self.plot.plot_width/2
            y = -9
            self.render_text(st, facesize, x, y, align_x='center', align_y='bottom')

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


    # Text objects are split into chunks, which are fragments
    # that have the same size and the same type (normal, tex, ...)

    # The render_text_chunk_xxx functions return the size of the
    # text fragment and a renderer. The renderer must be called
    # with the position (lower left corner) of the fragment, 
    # to render the text

    def render_text_chunk_normal(self, text, size):
        """Render a text chunk using normal text"""
        self.font.FaceSize(size)
        w, h = self.font.Advance(text), self.font.LineHeight()
        def renderer(x, y):
            self.font.FaceSize(size)
            glRasterPos2d(x, y)
            self.font.Render(text)
        return w, h, renderer

    def render_text_chunk_tex(self, text, size):
        """Render a text chunk using mathtext"""
        w, h, origin, fonts = mathtext.math_parse_s_ft2font(text, 72, size)
        def renderer(x, y):
            glRasterPos2d(x, y-origin/self.plot.res)
            w, h, imgstr = fonts[0].image_as_str()
            N = w*h
            Xall = zeros((N,len(fonts)), typecode=UInt8)

            for i, f in enumerate(fonts):
                w, h, imgstr = f.image_as_str()
                Xall[:,i] = fromstring(imgstr, UInt8)

            Xs = mlab.max(Xall, 1)
            Xs.shape = (h, w)

            pa = zeros(shape=(h,w,4), typecode=UInt8)
            rgb = (0.2, 0.2, 0.)

            pa[:,:,0] = int(rgb[0]*255)
            pa[:,:,1] = int(rgb[1]*255)
            pa[:,:,2] = int(rgb[2]*255)
            pa[:,:,3] = Xs[::-1]

            glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, pa.tostring())

        return w, h, renderer

    def render_text(self, text, size, x, y, align_x='center', align_y='center'):
        if self.plot.ps:
            return 0, 0
        else:
            chunks = cut(text, '$')

            renderers = []
            widths = []
            heights = []
            for chunk, tex in chunks:
                if tex:
                    w, h, renderer = self.render_text_chunk_tex('$'+chunk+'$', int(size*1.3))
                else:
                    w, h, renderer = self.render_text_chunk_normal(chunk, size)

                renderers.append(renderer)
                widths.append(w)
                heights.append(h)

            totalw = sum(widths)
            totalh = max(heights)

            if align_x == 'left':
                pass
            elif align_x == 'right':
                x -= totalw/self.plot.res
            elif align_x == 'center':
                x -= (totalw/2)/self.plot.res

            if align_y == 'top':
                ys = [y+(totalh-h)/self.plot.res for h in heights]
            elif align_y == 'bottom':
                ys = [y for h in heights]
            elif align_y == 'center':
                ys = [y+(totalh-h/2.)/self.plot.res for h in heights]

            for rend, pos, y in zip(renderers, [0]+list(cumsum(widths)/self.plot.res)[:-1], ys):
                rend(x+pos, y)

    def paint_text(self):
        facesize = int(3.*self.plot.res)

        if self.position == 'bottom':
            tics = self.tics(self.plot.xmin, self.plot.xmax)[0]
            for x in tics:
#                if x > 100:
                st = self.totex(x)
#                else:
#                    st = r'%g$\tt{\Delta\epsilon \tt{ab}cde_\infty}$ass'%x
                xm, _ = self.plot.proj(x, 0.)
                self.render_text(st, facesize, xm, -5, 'center', 'bottom')
        elif self.position == 'left':
            for y in self.tics(self.plot.ymin, self.plot.ymax)[0]:
#                if y > 100:
                st = self.totex(y)
#                else:
#                st = '%g'%y
                _, ym = self.plot.proj(0., y)
                self.render_text(st, facesize, -2, ym, 'right', 'center')
 
#                if self.plot.ps:
#                    w = self.font.Advance(st)
#                else:
#                    w, t, fts = mathtext.math_parse_s_ft2font(st, 72, facesize)

#                glRasterPos2d(rasterx, rastery)
#                psx, psy = self.graph.invproj()

#                if self.plot.ps:
##                    gl2psText(st, "Times-Roman", h)
#                    
#                    width, height, pswriter = mathtext.math_parse_s_ps(st, 72, facesize)
#                    thetext = pswriter.getvalue()
#                    ps = """gsave
#%f %f translate
#%f rotate
#%s
#grestore
#""" % (xm*self.plot.res, 0, 0, thetext)
#                    print >>sys.stderr, ps
#
#                elif 0:
#                    self.font.Render(st)
#                else:
#                    tw, th, fts = mathtext.math_parse_s_ft2font(st, 75, facesize)
#                    w, h, imgstr = fts[0].image_as_str()
#                    N = w*h
#                    Xall = zeros((N,len(fts)), typecode=UInt8)
#
#                    for i, f in enumerate(fts):
#                        w, h, imgstr = f.image_as_str()
#                        Xall[:,i] = fromstring(imgstr, UInt8)
#
#                    Xs = mlab.max(Xall, 1)
#                    Xs.shape = (h, w)
#
#                    pa = zeros(shape=(h,w,4), typecode=UInt8)
#                    rgb = [0., 0., 0.]
#
#                    pa[:,:,0] = int(rgb[0]*255)
#                    pa[:,:,1] = int(rgb[1]*255)
#                    pa[:,:,2] = int(rgb[2]*255)
#                    pa[:,:,3] = Xs[::-1]
#
#                    glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, pa.tostring())
#
#        elif self.position == 'left':
#            for y in self.tics(self.plot.ymin, self.plot.ymax)[0]:
#                st = '%g'%y
#                _, ym = self.plot.proj(0., y)
#                w = self.font.Advance(st)
#                glRasterPos2d(-w/self.plot.res - 2, ym - (h/2)/self.plot.res)
#                if self.plot.ps:
#                    gl2psText(st, "TimesRoman", h)
#                else:
#                    self.font.Render(st)

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

class Graph(Item, HasSignals):
    def __init__(self, project, name=None, parent=None, location=None):
        Item.__init__(self, project, name, parent, location)
    
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
        glEnable (GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

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
            glLogicOp(GL_XOR)
            glEnable(GL_COLOR_LOGIC_OP)
            for o in self.objects:
                o.redraw()
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
        self.marginb = self.height_mm * 0.15
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

    def export_ascii(self, f):
        gl2psBeginPage("Title", "Producer", 
                       self.viewport,
                       GL2PS_EPS, GL2PS_SIMPLE_SORT, GL2PS_NONE,
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
                self.buf = True
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
                self.buf = True
                self._movefunc.show(*self.mouse_to_real(x, y))
                self.emit('redraw')
        elif self.mode == 's-reader':
            self.buf = True
            self.cross.show(*self.mouse_to_ident(x, y))
            self.emit('redraw')
            self.emit('status-message', '%f, %f' % self.mouse_to_real(x, y))

     
    def button_release(self, x, y, button):
        if self.mode == 'zoom':
            if button == 2:
                self.autoscale()
                self.emit('redraw')
            elif button == 1 or button == 3:
                self.rubberband.hide()
                self.emit('redraw')
                self.buf = False

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
                self.emit('redraw')
        elif self.mode == 'hand':
            if self.selected_function is not None:
                self.selected_function.set_reg(True)
                self.selected_function.move(*self.mouse_to_real(x, y))
                del self.objects[-1]
                self.buf = False
                self.emit('redraw')
        elif self.mode == 's-reader':
            self.cross.hide()
            self.emit('redraw')
            self.buf = False
        
    def button_motion(self, x, y):
        if self.mode == 'zoom':
            self.rubberband.move(self.ix, self.iy, *self.mouse_to_ident(x, y))
            self.emit('redraw')
        elif self.mode in ['range', 'd-reader']:
            self.button_press(x, y)
        elif self.mode == 'hand':
            if self.selected_function is not None:
                self.selected_function.move(*self.mouse_to_real(x, y))
                self._movefunc.move(*self.mouse_to_real(x, y))
                self.emit('redraw')
        elif self.mode == 's-reader':
            self.cross.move(*self.mouse_to_ident(x, y))
            self.emit('redraw')
            self.emit('status-message', '%f, %f' % self.mouse_to_real(x, y))
 
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


#basepath = '/usr/share/matplotlib/'
#type42 = [os.path.join(basepath, name) + '.ttf' for name in bakoma_fonts]
#type42.append('/usr/share/matplotlib/cmr10.ttf')
#type42.append('/usr/share/matplotlib/cmex10.ttf')
#type42.append('/usr/share/matplotlib/cmmi10.ttf')
#type42.append('/usr/share/matplotlib/cmsy10.ttf')
#type42.append('/usr/share/matplotlib/cmtt10.ttf')


#for font in type42:
#    print "%%BeginFont: "+FT2Font(str(font)).postscript_name
#    print encodeTTFasPS(font)
#    print "%%EndFont"

