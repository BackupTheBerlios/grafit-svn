import sys
import time

from numarray import *
from OpenGL.GL import *
from OpenGL.GLU import *

from giraffe.signals import HasSignals
from giraffe.item import Item, wrap_attribute, register_class

import ftgl

from giraffe.graph_render import makedata

sys.path.append('/home/daniel/grafit/functions')
sys.path.append('/home/daniel/grafit')
import hn

class Style(object):
    def __init__(self, color=(0,0,0,1)):
        self._line_width = 0
        self._color = color

    def set_line_width(self, val):
        self._line_width = val
    def get_line_width(self):
        return self._line_width
    line_width = property(get_line_width, set_line_width)

    def set_color(self, val):
        self._color = val
    def get_color(self):
        return self._color
    color = property(get_color, set_color)


default_style = Style()

def create_list_id(start=[100]):
    start[0] += 1
    return start[0]

class Dataset(object):
    def __init__(self, x=None, y=None, range=(None,None), style=default_style):
        self._style = Style()
        self._x = x
        self._y = y
        self._style.dataset = self

        self.id = create_list_id()

    def set_style(self, val):
        self._style.line_width = val.line_width
        self._style.color = val.color
    def get_style(self):
        return self._style
    style = property(get_style, set_style)

    def set_range(self, val):
        self._range.line_width = val.line_width
    def get_range(self):
        return self._range
    range = property(get_range, set_range)

    def set_x(self, val):
        self._x = val
    def get_x(self):
        return self._x
    x = property(get_x, set_x)

    def set_y(self, val):
        self._y = val
    def get_y(self):
        return self._y
    y = property(get_y, set_y)

    def paint(self):
        glCallList(self.id)

    def build_display_list(self):
        dx =  self.graph.res * (self.graph.xmax-self.graph.xmin)/self.graph.w
        dy =  self.graph.res * (self.graph.ymax-self.graph.ymin)/self.graph.h

        p = 0.5

        glNewList(1001, GL_COMPILE)
        glPushMatrix()
        glScale(self.graph.xscale_mm/self.graph.xscale_data, self.graph.yscale_mm/self.graph.yscale_data, 1.)

        glBegin(GL_QUADS)
        glVertex3d(-p, -p, 0)
        glVertex3d(-p, p, 0)
        glVertex3d(p, p, 0)
        glVertex3d(p, -p, 0)
        glEnd()
        glPopMatrix()
        glEndList()

        glNewList(1002, GL_COMPILE)
        glPushMatrix()
        glScale(self.graph.xscale_mm/self.graph.xscale_data, self.graph.yscale_mm/self.graph.yscale_data, 1.)
        glBegin(GL_POLYGON)
        n = 20
        for i in xrange(n):
            c = p*exp(i*2j*pi/n)
            glVertex(c.real, c.imag, 0)
        glEnd()
        glPopMatrix()

        glEndList()

        glNewList(self.id, GL_COMPILE)
        glColor4f(*self.style.color)
	print >>sys.stderr, 'makedata'
        makedata(asarray(self.x[:]), asarray(self.y[:]), 
                 self.graph.xmin, self.graph.xmax, self.graph.ymin, self.graph.ymax, 
                 GL_QUADS, [(0,0), (dx,0), (dx, dy), (0, dy)]  )
	print >>sys.stderr, '/makedata'
        glEndList()

class Grid(object):
    def __init__(self, orientation, plot):
        assert orientation in ['horizontal', 'vertical']
        self.orientation = orientation
        self.plot = plot

    def paint(self):
        if self.orientation == 'horizontal':
            self = self.plot
            glLoadIdentity()
            glPushMatrix()
            glTranslate(-1.+2.*self.marginl/self.w, -1.+2.*self.marginb/self.h, 0)
            glScalef(self.xscale_data, self.yscale_mm, 1.)
            glTranslate(-self.xmin, 0, 0)

            plot_height_mm = (self.h - self.marginb - self.margint)/self.res
            plot_width_mm = (self.w - self.marginr - self.marginl)/self.res

            glLineStipple (1, 0x4444) # dotted
            glEnable(GL_LINE_STIPPLE)
            glColor3f(0.3, 0.3, 0.3)
            glBegin(GL_LINES)
            for x in self.axis_bottom.tics(self.xmin, self.xmax):
                glVertex3f(x, 0.0, 0.0)
                glVertex3f(x, plot_height_mm, 0.0)
            glEnd()
            glDisable(GL_LINE_STIPPLE)
            glColor3f(0.0, 0.0, 0.0)

            glPopMatrix()
        elif self.orientation == 'vertical':
            self = self.plot
            glPushMatrix()
            glTranslate(-1.+2.*self.marginl/self.w, -1.+2.*self.marginb/self.h, 0)
            glScalef(self.xscale_mm, self.yscale_data, 1.)
            glTranslate(0, -self.ymin, 0)

            plot_height_mm = (self.h - self.marginb - self.margint)/self.res
            plot_width_mm = (self.w - self.marginr - self.marginl)/self.res

            glLineStipple (1, 0x4444) # dotted
            glEnable(GL_LINE_STIPPLE)
            glColor3f(0.3, 0.3, 0.3)
            glBegin(GL_LINES)
            for y in self.axis_left.tics(self.ymin, self.ymax):
                glVertex3f(0, y, 0.0)
                glVertex3f(plot_width_mm, y, 0.0)
            glEnd()
            glDisable(GL_LINE_STIPPLE)
            glColor3f(0.0, 0.0, 0.0)

            glPopMatrix()

class Axis(object):
    def __init__(self, position, plot):
        assert position in ['left', 'right', 'top', 'bottom'], "illegal value for position: %s" % position
        self.position = position
        self.plot = plot

    def paint(self):
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(-1., -1., 0.)         # starting at bottom left corner
        glScalef(self.plot.xscale_pixel, self.plot.yscale_pixel, 1.) # pixel scale

        glColor3f(0.0,0.0,0.0)      # black

        glBegin(GL_LINES)
        if self.position == 'bottom':
            glVertex3f(self.plot.marginl, self.plot.marginb, 0.0)
            glVertex3f(self.plot.w - self.plot.marginr, self.plot.marginb, 0.0)
        elif self.position == 'right':
            glVertex3f(self.plot.w - self.plot.marginr, self.plot.marginb, 0.0)
            glVertex3f(self.plot.w - self.plot.marginr, self.plot.h - self.plot.margint, 0.0)
        elif self.position == 'top':
            glVertex3f(self.plot.w - self.plot.marginr, self.plot.h - self.plot.margint, 0.0)
            glVertex3f(self.plot.marginl, self.plot.h - self.plot.margint, 0.0)
        elif self.position == 'left':
            glVertex3f(self.plot.marginl, self.plot.h - self.plot.margint, 0.0)
            glVertex3f(self.plot.marginl, self.plot.marginb, 0.0)
        glEnd()

        glPopMatrix()

        if self.position == 'bottom':
            glPushMatrix()
            glLoadIdentity()
            glTranslate(-1.+2.*self.plot.marginl/self.plot.w, -1.+2.*self.plot.marginb/self.plot.h, 0)
            glScalef(self.plot.xscale_data, self.plot.yscale_mm, 1.)
            glTranslate(-self.plot.xmin, 0, 0)

            glBegin(GL_LINES)
            for x in self.tics(self.plot.xmin, self.plot.xmax):
                glVertex3f(x, 0.0, 0.0)
                glVertex3f(x, 2, 0.0)
            glEnd()

            glPopMatrix()
 
        elif self.position == 'left':
            glPushMatrix()
            glTranslate(-1.+2.*self.plot.marginl/self.plot.w, -1.+2.*self.plot.marginb/self.plot.h, 0)
            glScalef(self.plot.xscale_mm, self.plot.yscale_data, 1.)
            glTranslate(0, -self.plot.ymin, 0)

            glBegin(GL_LINES)
            for y in self.tics(self.plot.ymin, self.plot.ymax):
                glVertex3f(0, y, 0.0)
                glVertex3f(2, y, 0.0)
            glEnd()

            glPopMatrix()
        self.paint_text()

    def paint_text(self):
        glLoadIdentity()
	print >>sys.stderr, 'arse'
        f = ftgl.FTGLPixmapFont('/home/daniel/giraffe/data/fonts/bitstream-vera/Vera.ttf')
	print >>sys.stderr, 'arses'
        h = int(2.6*self.plot.res)
        f.FaceSize(h)
        if self.position == 'bottom':
            for x in self.tics(self.plot.xmin, self.plot.xmax):
                glPushMatrix()
                glTranslate(-1.+2.*self.plot.marginl/self.plot.w, -1.+2.*self.plot.marginb/self.plot.h, 0)
                glScalef(self.plot.xscale_data, self.plot.yscale_mm, 1.)
                glTranslatef(-self.plot.xmin, 0, 0)
                
                w = f.Advance(str(x))
                glRasterPos2f(x-(self.plot.xscale_pixel/self.plot.xscale_data)*(w/2.), -3)
                f.Render(str(x))

                glPopMatrix()
        elif self.position == 'left':
            for y in self.tics(self.plot.ymin, self.plot.ymax):
                glPushMatrix()
                glTranslate(-1.+2.*self.plot.marginl/self.plot.w, -1.+2.*self.plot.marginb/self.plot.h, 0)
                glScalef(self.plot.xscale_mm, self.plot.yscale_data, 1.)
                
                glTranslatef(0, -self.plot.ymin, 0)

                w = f.Advance(str(y))
                glRasterPos2f(-2.-(self.plot.xscale_pixel/self.plot.xscale_mm)*w, 
                              y-(self.plot.xscale_pixel/self.plot.xscale_data)*(h*0.35277138/4.))
                f.Render(str(y))
                
                glPopMatrix()

 

    def tics(self, fr, to):
        # 5-8 major tics
        if fr == to:
            return [fr]
        exponent = floor(log10(to-fr)) - 1

        for interval in (1,5,2,4,6,7,8,9,3):
            interval = interval * (10**exponent)
            if fr%interval == 0:
                first = fr
            else:
                first = fr + (interval-fr%interval)
            rng = arange(first, to, interval)
            if 5 <= len(rng) <= 8:
                return rng

        exponent += 1
        for interval in (1,5,2,4,6,7,8,9,3):
            interval = interval * (10**exponent)
            if fr%interval == 0:
                first = fr
            else:
                first = fr + (interval-fr%interval)
            rng = arange(first, to, interval)
            if 5 <= len(rng) <= 8:
                return rng
        return []

# matrix_physical: starting at lower left corner of plot; units in mm
# matrix_data: starting at data (0, 0); units are data
# resolution: pixels per mm (but we _should not care about pixels_!)

# TODO:
# - convert drawing to use the above data
# - move drawing to Axis and Dataset classes
# - more generic mechanism for symbols, in pyrex if nescessary
class Graph(Item, HasSignals):
    def __init__(self, project, name=None, parent=None, location=None):
        Item.__init__(self, project, name, parent, location)
    
        # mouse rubberbanding coordinates
        self.sx = None
        self.px = None
        self.sy = None
        self.py = None

        self.buf =  False

        self.datasets = []

        x = arange(2, 6, 0.001)
        y = log10(hn.havriliak_negami(10.**x, 4, 1, 0.5, 1))

        d = Dataset(x, y)
        d.style.color =  (0.3, 0.4, 0.7, 0.8)
        d.graph = self
        self.datasets.append(d)

        self.datasets.append(Dataset(x = arange(100000.)/100000,
                                     y = sin(arange(100000.)/100000)))
        self.datasets[-1].style.color = (0.0, 0.1, 0.6, 0.8)
        self.datasets[-1].graph = self

        self.datasets.append(Dataset(x = arange(10000.)/1000,
                                     y = cos(arange(10000.)/1000)))
        self.datasets[-1].style.color = (0.4, 0.0, 0.1, 0.5)
        self.datasets[-1].graph = self

#        self.colors[2] = (0.3, 0.4, 0.7, 0.8)

        self.axis_top = Axis('top', self)
        self.axis_bottom = Axis('bottom', self)
        self.axis_right = Axis('right', self)
        self.axis_left = Axis('left', self)

        self.axes = [self.axis_bottom, self.axis_top, self.axis_right, self.axis_left]

        self.grid_h = Grid('horizontal', self)
        self.grid_v = Grid('vertical', self)

        self.set_range(0.0, 100.5)
        self.autoscale()

    def add(self, *args, **kwds):
        d = Dataset(*args, **kwds)
        self.datasets.append(d)
        d.graph = self

    def paint_frame(self):
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(-1., -1., 0.)         # starting at bottom left corner
        glScalef(self.xscale_pixel, self.yscale_pixel, 1.)

        glColor3f(1.0,1.0,1.0)      # black

        glBegin(GL_QUADS)
        glVertex3f(self.marginl, self.marginb, 0.0)
        glVertex3f(self.w - self.marginr, self.marginb, 0.0)
        glVertex3f(self.w - self.marginr, self.h - self.margint, 0.0)
        glVertex3f(self.marginl, self.h - self.margint, 0.0)
        glEnd()

        glPopMatrix()

    def paint_axes(self):

        self.paint_frame()

        for a in self.axes:
            a.paint()

        self.grid_h.paint()
        self.grid_v.paint()

        glPushMatrix()
        glLoadIdentity()
        self.initmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
        glTranslate(-1.+2.*self.marginl/self.w, -1.+2.*self.marginb/self.h, 0) # go to origin
        glScalef(self.xscale_data, self.yscale_data, 1) # scale to coordinates
        glTranslatef(-self.xmin, -self.ymin, 0) # go to (0, 0)
        self.projmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
        glPopMatrix()

    def set_data_scales(self):
        self.xscale_data = self.xscale_pixel * ((self.w-self.marginl-self.marginr)/(self.xmax-self.xmin))
        self.yscale_data = self.yscale_pixel * ((self.h-self.margint-self.marginb)/(self.ymax-self.ymin))

    def make_data_list(self):
        t = time.time()

        for d in self.datasets:
            d.build_display_list()

        print (time.time()-t), "seconds"

    def mouse_to_ident(self, xm, ym):
        realy = self.viewport[3] - ym - 1
        x, y, _ = gluUnProject(xm, realy, 0.0, self.mvmatrix, self.initmatrix, self.viewport)
        return x, y

    def mouse_to_real(self, xm, ym):
        realy = self.viewport[3] - ym - 1
        x, y, _ = gluUnProject(xm, realy, 0.0, self.mvmatrix, self.projmatrix, self.viewport)
        return x, y

    def autoscale(self):
        self.xmin = min(self.datasets[0].x)
        self.ymin = min(self.datasets[0].y)
        self.xmax = max(self.datasets[0].x)
        self.ymax = max(self.datasets[0].y)
        if hasattr(self, 'xscale_pixel'):
            self.set_data_scales()

    def set_range(self, fr, to):
        self.fr, self.to  = fr, to

    def zoom(self, xmin, xmax, ymin, ymax):
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.set_data_scales()

 
    def zoomout(self,x1, x2,x3, x4):
        a = (x2-x1)/(x4-x3)
        c = x1 - a*x3
        f1 = a*x1 + c
        f2 = a*x2 + c
        return min(f1, f2), max(f1, f2)

    def init(self):
    	print >>sys.stderr, 'init'
        glClearColor(252./256, 252./256, 252./256, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # enable transparency
        glEnable (GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glDisable(GL_DEPTH_TEST)

        glMatrixMode (GL_PROJECTION)
        glLoadIdentity ()

        self.mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        self.viewport = glGetIntegerv(GL_VIEWPORT)

    	print >>sys.stderr, 'init/'
        self.make_data_list()
    	print >>sys.stderr, '/init'
 
    def display(self, width, height):
    	print >>sys.stderr, 'display'

        gluOrtho2D (0, width, 0, height)
        if not self.buf:
            glClear(GL_COLOR_BUFFER_BIT)
            self.paint_axes()

            glPushMatrix()
            glLoadIdentity()

            x, _, _ = gluProject(self.fr, 0.0, 0.0, self.mvmatrix, self.projmatrix, self.viewport)
            x1, _ = self.mouse_to_ident(x, 0.)

            x, _, _ = gluProject(self.to, 0.0, 0.0, self.mvmatrix, self.projmatrix, self.viewport)
            x2, _ =  self.mouse_to_ident(x, 0.)

            lt = 1-2.*self.marginl/self.w
            rt = -1+2.*(self.w-self.marginr)/self.w
            bt = 1-2.*self.marginb/self.h
            tp = -1+2.*(self.h-self.margint)/self.h

            glClipPlane(GL_CLIP_PLANE0, [  1.,  0.,  0.,  min(lt, -x1) ])
            glClipPlane(GL_CLIP_PLANE1, [ -1.,  0.,  0.,  min(rt, x2) ])
            glClipPlane(GL_CLIP_PLANE2, [  0.,  1.,  0.,  bt ])
            glClipPlane(GL_CLIP_PLANE3, [  0., -1.,  0.,  tp ])

            glEnable(GL_CLIP_PLANE0)
            glEnable(GL_CLIP_PLANE1)
            glEnable(GL_CLIP_PLANE2)
            glEnable(GL_CLIP_PLANE3)

            glLoadMatrixd(self.projmatrix)
            for d in self.datasets:
                d.paint()

            glDisable(GL_CLIP_PLANE0)
            glDisable(GL_CLIP_PLANE1)
            glDisable(GL_CLIP_PLANE2)
            glDisable(GL_CLIP_PLANE3)

            glPopMatrix()
        else:
            glPushMatrix()
            glLoadIdentity()

            glColor3f(1.0,1.0,0.0)
            glLineStipple (1, 0x4444) # dotted
            glEnable(GL_LINE_STIPPLE)
            glLogicOp(GL_XOR)
            glEnable(GL_COLOR_LOGIC_OP)

            if (self.px, self.py) != (None, None):
                glBegin(GL_LINE_LOOP)
                glVertex3f(self.ix, self.iy, 0.0)
                glVertex3f(self.ix, self.py, 0.0)
                glVertex3f(self.px, self.py, 0.0)
                glVertex3f(self.px, self.iy, 0.0)
                glEnd()

            glBegin(GL_LINE_LOOP)
            glVertex3f(self.ix, self.iy, 0.0)
            glVertex3f(self.ix, self.sy, 0.0)
            glVertex3f(self.sx, self.sy, 0.0)
            glVertex3f(self.sx, self.iy, 0.0)
            glEnd()
            self.px, self.py = self.sx, self.sy

            glDisable(GL_LINE_STIPPLE)
            glDisable(GL_COLOR_LOGIC_OP)
            glPopMatrix()

    
    def reshape(self, width, height):
        # aspect ratio to keep 
        ratio = 4./3.

        # set width and height (in pixels)
        self.ww, self.hh = self.w, self.h = width, height
        if (1.*self.w) / self.h > ratio:
            self.ww = ratio*self.h
        else:
            self.hh = self.w/ratio

        self.excessh = height - self.hh
        self.excessw = width - self.ww
        self.w -= self.excessw

        # set margins (in pixels)
        self.marginb = int(self.h * 0.1) + self.excessh
        self.margint = int(self.h * 0.05)
        self.marginl = int(self.w * 0.1)
        self.marginr = int(self.w * 0.05)


        # resolution (in pixels/mm)
        self.res = self.w/100.

        # resize the viewport
        glViewport(0, 0, int(self.w), int(self.h))
        self.viewport = glGetIntegerv(GL_VIEWPORT)

        self.xscale_pixel = 2./self.w
        self.yscale_pixel = 2./self.h

        self.xscale_mm = self.xscale_pixel * self.res
        self.yscale_mm = self.yscale_pixel * self.res

        self.set_data_scales()

    def rubberband_begin(self, x, y):
        self.buf = True
        self.pixx, self.pixy = x, y

        # zooming box in identity coordinates
        self.ix, self.iy = self.mouse_to_ident(x, y)
        self.sx, self.sy = self.ix, self.iy

    def rubberband_active(self):
        return self.buf

    def rubberband_continue(self, x, y):
#        self.px, self.py = self.sx, self.sy
        self.sx, self.sy = self.mouse_to_ident(x, y)
        self.emit('redraw')

    def rubberband_end(self, x, y):
        self.rubberband_continue(x, y)
        self.buf = False
        self.px, self.py = None, None
        return self.pixx, self.pixy, x, y

    def button_press(self, x, y, button):
        if button in (1,3):
            self.rubberband_begin(x, y)
        if button == 2:
            self.haha = True
        else:
            self.haha = False
    
    def button_release(self, x, y, button):
        if button == 2:
            pass
#            self.autoscale()
#            self.make_data_list()
#            self.queue_draw()
        elif button == 1 or button == 3:
            zix, ziy, zfx, zfy = self.rubberband_end(x, y)

            zix, ziy = self.mouse_to_real(zix, ziy)
            zfx, zfy = self.mouse_to_real(zfx, zfy)

            _xmin, _xmax = min(zix, zfx), max(zix, zfx)
            _ymin, _ymax = min(zfy, ziy), max(zfy, ziy)

            if button == 3:
                xmin, xmax = self.zoomout(self.xmin, self.xmax, _xmin, _xmax)
                ymin, ymax = self.zoomout(self.ymin, self.ymax, _ymin, _ymax)
            else:
                xmin, xmax, ymin, ymax = _xmin, _xmax, _ymin, _ymax
            self.zoom(xmin, xmax, ymin, ymax)

            self.make_data_list()
            self.emit('redraw')

    
    def button_motion(self, x, y):
        if self.haha:
            ex, ey = self.mouse_to_real(x, y)
            x = arange(2, 6, 0.01)
            params = hn.havriliak_negami.move(10.**ex, 10.**ey, 4, 1, 0.5, 1)
            y = log10(hn.havriliak_negami(10.**x, *params))
            self.datasets[0].x = x
            self.datasets[0].y = y
            self.datasets[0].build_display_list()
            self.emit('redraw')
        elif self.rubberband_active():
            self.rubberband_continue(x, y)

    name = wrap_attribute('name')
    parent = wrap_attribute('parent')


register_class(Graph, 'graphs[name:S,id:S,parent:S]')

