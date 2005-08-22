from giraffe.signals import HasSignals
from giraffe.settings import DATADIR

from OpenGL.GL import *
from OpenGL.GLU import *

from math import sqrt
import sys

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
        self.dragstart = None

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

    def testpoint(self, x3, y3):
        x1, x2 = self.handles[0].x, self.handles[1].x
        y1, y2 = self.handles[0].y, self.handles[1].y
        u = ((x3-x1)*(x2-x1) + (y3-y1)*(y2-y1)) / ((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))
        x = x1 + u*(x2-x1)
        y = y1 + u*(y2-y1)
        dd = (x3-x)*(x3-x) + (y3-y)*(y3-y)
        h = dd<=1
        if h:
            self.dragstart = x3, y3
        else:
            self.dragstart = None
        return h

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

    def get_x1(self): return self.handles[0].posx
    def set_x1(self, value): self.handles[0].posx = value; self.graph.emit('redraw')
    _x1 = property(get_x1, set_x1)

    def get_y1(self): return self.handles[0].posy
    def set_y1(self, value): self.handles[0].posy = value; self.graph.emit('redraw')
    _y1 = property(get_y1, set_y1)

    def testpoint(self, x, y):
        h = self.hittest(x, y)
        if h:
            self.dragstart = x, y
        else:
            self.dragstart = None
        return h 


class Move(XorDraw):
    def __init__(self, obj):
        XorDraw.__init__(self, obj.graph)
        self.obj = obj

    def draw(self, x, y):
        if self.obj.dragstart:
            x0, y0 = self.obj.dragstart
            for h in self.obj.handles:
                h.move(h.x+x-x0, h.y+y-y0)
                self.obj.dragstart = x, y
        else:
            self.obj._active_handle.move(x, y)
#        self.obj.draw_handles()
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


