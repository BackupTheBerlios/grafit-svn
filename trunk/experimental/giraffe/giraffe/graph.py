import sys
import time

#from numarray import *
from giraffe.arrays import *
from OpenGL.GL import *
from OpenGL.GLU import *

from giraffe.signals import HasSignals
from giraffe.project import Item, wrap_attribute, register_class, create_id
from giraffe.commands import command_from_methods

import ftgl
from gl2ps import *

from giraffe.graph_render import render

class Style(HasSignals):
    def __init__(self, color=(0,0,0), symbol='square-f'):
        self._line_width = 0
        self._color = color
        self._symbol = symbol

    def set_line_width(self, val):
        self._line_width = val
        self.emit('modified')
    def get_line_width(self):
        return self._line_width
    line_width = property(get_line_width, set_line_width)

    def set_symbol(self, val):
        self._symbol = val
        self.emit('modified')
    def get_symbol(self):
        return self._symbol
    symbol = property(get_symbol, set_symbol)

    def set_color(self, val):
        self._color = val
        self.emit('modified')
    def get_color(self):
        return self._color
    color = property(get_color, set_color)

default_style = Style()


class Dataset(HasSignals):
    def __init__(self, graph, ind):
        self.graph, self.ind = graph, ind
        self.data = self.graph.data.datasets[ind]

        self.worksheet = self.graph.project.items[self.data.worksheet]
        self.x, self.y = self.worksheet[self.data.x], self.worksheet[self.data.y]

        self.x.connect('data-changed', self.on_data_changed)
        self.y.connect('data-changed', self.on_data_changed)

        self.style = Style()

        try:
            c = self.data.color
            self.style.color = (c%256, (c//256)%256, (c//(256*256))%256)
        except ValueError:
            self.style.color = default_style.color
            self.data.color = '0'

        self.style.size = self.data.size

        if self.data.symbol == '':
            self.data.symbol = 'square-f'
        self.style.symbol = self.data.symbol
        
        self.style.connect('modified', self.on_style_modified)

    def set_id(self, id): self.data.id = id
    def get_id(self): return self.data.id
    id = property(get_id, set_id)

    def set_worksheet(self, ws): self.data.worksheet = ws.id
    def get_worksheet(self): return self.graph.project.items[self.data.worksheet]

    def paint(self):
        res, xmin, xmax, ymin, ymax, width, height = self.paintdata
        gl2psPointSize(self.data.size)
        dx =  res * (xmax-xmin)/width * self.style.size / 5.
        dy =  res * (ymax-ymin)/height * self.style.size / 5.
        glColor4f(self.style.color[0]/256., self.style.color[1]/256., 
                  self.style.color[2]/256., 1.)
        x = asarray(self.x[:])
        y = asarray(self.y[:])

        x = array([xi for (xi, yi) in zip(x, y) if xi is not nan and yi is not nan])
        y = array([yi for (xi, yi) in zip(x, y) if xi is not nan and yi is not nan])
        z = zeros(len(x))

        x = array([1,2,3,4,5])
        y = array([1,2,3,4,5])
        z = array([0,0,0,0,0])

        glMap1f(GL_MAP1_VERTEX_3, 0., 1., array([x-xmin, y-ymin, z]))
        glEnable(GL_MAP1_VERTEX_3)
#        glBegin(GL_LINE_STRIP)
#        for i in xrange(100):
#            print i/100.
#            glEvalCoord1f(i/100.)
#        glEnd()
        glMapGrid1f(100, 0.0, 1.0)
        glEvalMesh1(GL_LINE, 0, 100)
        glDisable(GL_MAP1_VERTEX_3)
#        render(x, y, xmin, xmax, ymin, ymax, dx, dy, self.style.symbol)

    def build_display_list(self, res, xmin, xmax, ymin, ymax, width, height):
        self.paintdata = (res, xmin, xmax, ymin, ymax, width, height)

    def on_data_changed(self):
        self.emit('modified', self)

    def on_style_modified(self):
        self.data.color = (self.style.color[0] + self.style.color[1]*256 + 
                           self.style.color[2]*256*256)
        self.data.symbol = self.style.symbol
        self.data.size = self.style.size
        self.emit('modified', self)

    def __str__(self):
        return self.x.worksheet.name+':'+self.y.name+'('+self.x.name+')'

    # this is nescessary! see graph.remove
    def __eq__(self, other):
        return self.id == other.id


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
            glTranslate(-1.+2.*self.marginl/self.w, 
                        -1.+2.*self.marginb/self.h, 0)
            glScaled(self.xscale_data, self.yscale_mm, 1.)
#            glTranslate(-self.xmin, 0, 0)

            plot_height_mm = (self.h - self.marginb - self.margint)/self.res
            plot_width_mm = (self.w - self.marginr - self.marginl)/self.res

            glLineStipple (1, 0x4444) # dotted
            glEnable(GL_LINE_STIPPLE)
            if self.ps:
                gl2psEnable(GL2PS_LINE_STIPPLE)
                gl2psLineWidth(0.01)
            glColor3f(0.3, 0.3, 0.3)
            glBegin(GL_LINES)
            for x in self.axis_bottom.tics(self.xmin, self.xmax)[0]:
                glVertex3d(x-self.xmin, 0.0, 0.0)
                glVertex3d(x-self.xmin, plot_height_mm, 0.0)
            glEnd()
            if self.ps:
                gl2psDisable(GL2PS_LINE_STIPPLE)
                gl2psLineWidth(0.1)
            glDisable(GL_LINE_STIPPLE)
            glColor3f(0.0, 0.0, 0.0)

            glPopMatrix()
        elif self.orientation == 'vertical':
            self = self.plot
            glPushMatrix()
            glTranslate(-1.+2.*self.marginl/self.w, 
                        -1.+2.*self.marginb/self.h, 0)
            glScaled(self.xscale_mm, self.yscale_data, 1.)
#            glTranslate(0, -self.ymin, 0)

            plot_height_mm = (self.h - self.marginb - self.margint)/self.res
            plot_width_mm = (self.w - self.marginr - self.marginl)/self.res

            glLineStipple (1, 0x4444) # dotted
            glEnable(GL_LINE_STIPPLE)
            if self.ps:
                gl2psEnable(GL2PS_LINE_STIPPLE)
                gl2psLineWidth(0.01)
            glColor3f(0.3, 0.3, 0.3)
            glBegin(GL_LINES)
            for y in self.axis_left.tics(self.ymin, self.ymax)[0]:
                glVertex3d(0, y-self.ymin, 0.0)
                glVertex3d(plot_width_mm, y-self.ymin, 0.0)
            glEnd()
            glDisable(GL_LINE_STIPPLE)
            if self.ps:
                gl2psDisable(GL2PS_LINE_STIPPLE)
                gl2psLineWidth(0.1)
            glColor3f(0.0, 0.0, 0.0)

            glPopMatrix()

FONTFILE = '/home/daniel/giraffe/data/fonts/bitstream-vera/VeraSe.ttf'
AXISFONT = ftgl.FTGLPixmapFont(FONTFILE)

class Axis(object):
    def __init__(self, position, plot):
        self.position = position
        self.plot = plot
        self.font = AXISFONT

    def paint(self):
        glPushMatrix()
        glLoadIdentity()
        glTranslated(-1., -1., 0.)         # starting at bottom left corner
        glScaled(self.plot.xscale_pixel, self.plot.yscale_pixel, 1.) # pixel scale

        glColor3f(0.0,0.0,0.0) # axis color

        # Axis lines
        glBegin(GL_LINES)
        if self.position == 'bottom':
            glVertex3d(self.plot.marginl, self.plot.marginb, 0.0)
            glVertex3d(self.plot.w - self.plot.marginr, self.plot.marginb, 0.0)
        elif self.position == 'right':
            glVertex3d(self.plot.w - self.plot.marginr, self.plot.marginb, 0.0)
            glVertex3d(self.plot.w - self.plot.marginr, self.plot.h - self.plot.margint, 0.0)
        elif self.position == 'top':
            glVertex3d(self.plot.w - self.plot.marginr, self.plot.h - self.plot.margint, 0.0)
            glVertex3d(self.plot.marginl, self.plot.h - self.plot.margint, 0.0)
        elif self.position == 'left':
            glVertex3d(self.plot.marginl, self.plot.h - self.plot.margint, 0.0)
            glVertex3d(self.plot.marginl, self.plot.marginb, 0.0)
        glEnd()

        glPopMatrix()

        if self.position == 'bottom':
            glPushMatrix()
            glLoadIdentity()
            glTranslate(-1.+2.*self.plot.marginl/self.plot.w, -1.+2.*self.plot.marginb/self.plot.h, 0)
            glScaled(self.plot.xscale_data, self.plot.yscale_mm, 1.)
#            glTranslate(-self.plot.xmin, 0, 0)

            glBegin(GL_LINES)
            major, minor = self.tics(self.plot.xmin, self.plot.xmax)

            for x in major:
                glVertex3d(x-self.plot.xmin, 0.0, 0.0)
                glVertex3d(x-self.plot.xmin, 2, 0.0)
            for x in minor:
                glVertex3d(x-self.plot.xmin, 0.0, 0.0)
                glVertex3d(x-self.plot.xmin, 1, 0.0)
            glEnd()

            glPopMatrix()
 
        elif self.position == 'left':
            glPushMatrix()
            glTranslate(-1.+2.*self.plot.marginl/self.plot.w, -1.+2.*self.plot.marginb/self.plot.h, 0)
            glScaled(self.plot.xscale_mm, self.plot.yscale_data, 1.)
#            glTranslate(0, -self.plot.ymin, 0)

            glBegin(GL_LINES)
            major, minor = self.tics(self.plot.ymin, self.plot.ymax)
            for y in major:
                glVertex3d(0, y-self.plot.ymin, 0.0)
                glVertex3d(2, y-self.plot.ymin, 0.0)
            for y in minor:
                glVertex3d(0, y-self.plot.ymin, 0.0)
                glVertex3d(1, y-self.plot.ymin, 0.0)
            glEnd()

            glPopMatrix()
        self.paint_text()

    def paint_text(self):
        glLoadIdentity()
        h = int(2.6*self.plot.res)
        self.font.FaceSize(h)
        if self.position == 'bottom':
            for x in self.tics(self.plot.xmin, self.plot.xmax)[0]:
                glPushMatrix()
                glTranslate(-1.+2.*self.plot.marginl/self.plot.w, -1.+2.*self.plot.marginb/self.plot.h, 0)
                glScaled(self.plot.xscale_data, self.plot.yscale_mm, 1.)
#                glTranslated(-self.plot.xmin, 0, 0)
                
                w = self.font.Advance(str(x))
                glRasterPos2d(x-self.plot.xmin,#-(self.plot.xscale_pixel/self.plot.xscale_data)*(w/2.), 
                              -3)
                if self.plot.ps:
                    gl2psText(str(x), "Times-Roman", h)
                else:
                    self.font.Render(str(x))
#                print str(x)

                glPopMatrix()
        elif self.position == 'left':
            for y in self.tics(self.plot.ymin, self.plot.ymax)[0]:
                glPushMatrix()
                glTranslate(-1.+2.*self.plot.marginl/self.plot.w, -1.+2.*self.plot.marginb/self.plot.h, 0)
                glScaled(self.plot.xscale_mm, self.plot.yscale_data, 1.)
                
#                glTranslated(0, -self.plot.ymin, 0)

                w = self.font.Advance(str(y))
                glRasterPos2d(-2.-(self.plot.xscale_pixel/self.plot.xscale_mm)*w, 
                              y-self.plot.ymin)#-(self.plot.xscale_pixel/self.plot.xscale_data)*(h*0.35277138/4.))
                if self.plot.ps:
                    gl2psText(str(y), "TimesRoman", h)
                else:
                    self.font.Render(str(y))
#                print str(y)
                
                glPopMatrix()

    def tics(self, fr, to):
        # 3-8 major tics
        if fr == to:
            return [fr]
        exponent = floor(log10(to-fr)) - 1

        for interval in (1,5,2):#,4,6,7,8,9,3):
            interval = interval * (10**exponent)
            if fr%interval == 0:
                first = fr
            else:
                first = fr + (interval-fr%interval)
            rng = arange(first, to, interval)
            if 3 <= len(rng) <= 8:
                minor = []
                for n in rng:
                    minor.extend(arange(n, n+interval, interval/5))

                return rng, minor
#
        exponent += 1
        for interval in (1,5,2):#,4,6,7,8,9,3):
            interval = interval * (10**exponent)
            if fr%interval == 0:
                first = fr
            else:
                first = fr + (interval-fr%interval)
            rng = arange(first, to, interval)
            if 3 <= len(rng) <= 8:
#                print 'from %f to %f:'%(fr, to), rng
                minor = []
                for n in rng:
                    minor.extend(arange(n, n+interval, interval/5))

                return rng, minor
        print "cannot tick", fr, to, len(rng)
        return []

# matrix_physical: starting at lower left corner of plot; units in mm
# matrix_data: starting at data (0, 0); units are data
# resolution: pixels per mm (but we _should not care about pixels_!)

# TODO:
# - convert drawing to use the above data
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
        if location is not None:
            for i in range(len(self.data.datasets)):
                if not self.data.datasets[i].id.startswith('-'):
                    d = Dataset(self, i)
                    self.datasets.append(d)
                    d.connect('modified', self.on_dataset_modified)

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
#        self.autoscale()

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

    def __repr__(self):
        return '<Graph %s%s>' % (self.name, '(deleted)'*self.id.startswith('-'))


    # add and remove datasets

    def add(self, x, y):
        ind = self.data.datasets.append(worksheet=x.worksheet.id, id=create_id(), 
                                        x=x.name.encode('utf-8'), y=y.name.encode('utf-8'))
        d = Dataset(self, ind)
        self.datasets.append(d)
        d.connect('modified', self.on_dataset_modified)
        self.on_dataset_modified(d)
        self.emit('add-dataset', d)
        return ind

    def undo_add(self, ind):
        d = self.datasets[ind]
        del self.datasets[ind]
        d.disconnect('modified', self.on_dataset_modified)
        self.emit('remove-dataset', d)
        self.emit('redraw')
        self.data.datasets.delete(ind)

    add = command_from_methods('graph_add_dataset', add, undo_add)

    def remove(self, dataset):
        # we can do this even if `dataset` is a different object
        # than the one in self.datasets, if they have the same id
        # (see Dataset.__eq__)
        ind = self.datasets.index(dataset)
        dataset.id = '-'+dataset.id
        self.datasets.remove(dataset)
        dataset.disconnect('modified', self.on_dataset_modified)
        self.emit('remove-dataset', dataset)
        self.emit('redraw')
        return (dataset, ind), None

    def undo_remove(self, data):
        dataset, ind = data
        dataset.id = dataset.id[1:]
        self.datasets.insert(ind, dataset)
        dataset.connect('modified', self.on_dataset_modified)
        self.emit('add-dataset', dataset)
        self.emit('redraw')

    remove = command_from_methods('graph_remove_dataset', remove, undo_remove)



    def on_dataset_modified(self, d):
        d.build_display_list(self.res, self.xmin, self.xmax, self.ymin, self.ymax, self.w, self.h)
        self.emit('redraw')

    def paint_frame(self):
        glPushMatrix()
        glLoadIdentity()
        glTranslated(-1., -1., 0.)         # starting at bottom left corner
        glScaled(self.xscale_pixel, self.yscale_pixel, 1.)

        glColor3f(1.0,1.0,1.0)      # black

        glBegin(GL_QUADS)
        glVertex3d(self.marginl, self.marginb, 0.0)
        glVertex3d(self.w - self.marginr, self.marginb, 0.0)
        glVertex3d(self.w - self.marginr, self.h - self.margint, 0.0)
        glVertex3d(self.marginl, self.h - self.margint, 0.0)
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
        glScaled(self.xscale_data, self.yscale_data, 1) # scale to coordinates
        self.projmatrix0 = glGetDoublev(GL_PROJECTION_MATRIX)
        glTranslated(-self.xmin, -self.ymin, 0) # go to (0, 0)
        self.projmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
        glPopMatrix()

    def set_data_scales(self):
        self.xscale_data = self.xscale_pixel * ((self.w-self.marginl-self.marginr)/(self.xmax-self.xmin))
        self.yscale_data = self.yscale_pixel * ((self.h-self.margint-self.marginb)/(self.ymax-self.ymin))

    def make_data_list(self):
        t = time.time()

        for d in self.datasets:
            d.build_display_list(self.res, self.xmin, self.xmax, self.ymin, self.ymax, self.w, self.h)

#        print (time.time()-t), "seconds"

    def mouse_to_ident(self, xm, ym):
        realy = self.viewport[3] - ym - 1
        x, y, _ = gluUnProject(xm, realy, 0.0, self.mvmatrix, self.initmatrix, self.viewport)
        return x, y

    def mouse_to_real(self, xm, ym):
        realy = self.viewport[3] - ym - 1
        x, y, _ = gluUnProject(xm, realy, 0.0, self.mvmatrix, self.projmatrix, self.viewport)
        return x, y

    def autoscale(self):
        if len(self.datasets):
            self.xmin = array(self.datasets[0].x).min()
            self.ymin = array(self.datasets[0].y).min()
            self.xmax = array(self.datasets[0].x).max()
            self.ymax = array(self.datasets[0].y).max()
            if hasattr(self, 'xscale_pixel'):
                self.set_data_scales()

    def set_range(self, fr, to):
        self.fr, self.to  = fr, to

    def zoom(self, xmin, xmax, ymin, ymax):
        eps = 1e-24
        if abs(xmin-xmax)<=eps or abs(ymin-ymax)<=eps:
            return
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.set_data_scales()
 
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
#        glEnable (GL_BLEND)
#        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glDisable(GL_DEPTH_TEST)
        glShadeModel(GL_FLAT)

        glMatrixMode (GL_PROJECTION)
        glLoadIdentity ()

        self.mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        self.viewport = glGetIntegerv(GL_VIEWPORT)

        self.dl = False

    def display(self, width=-1, height=-1):
        if width == -1 and height == -1:
            width, height = self.last_width, self.last_height
        else:
            self.last_width, self.last_height = width, height

        if not self.dl:
            self.make_data_list()
            self.dl = True

        gluOrtho2D (0, width, 0, height)
        if not self.buf:
            glClear(GL_COLOR_BUFFER_BIT)
            self.paint_axes()

            glPushMatrix()
            glLoadIdentity()
            glLoadMatrixd(self.projmatrix0)
            for d in self.datasets:
                d.paint()
            glPopMatrix()
        else:
            glPushMatrix()
            glLoadIdentity()

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
            glPopMatrix()

    
    def reshape(self, width, height):
        self._shape = (width, height)
        # aspect ratio to keep 
        ratio = 4./3.

        # set width and height (in pixels)
        self.ww, self.hh = self.w, self.h = width, height
#        if (1.*self.w) / self.h > ratio:
#            self.ww = ratio*self.h
#        else:
#            self.hh = self.w/ratio

#        self.excessh = height - self.hh
#        self.excessw = width - self.ww
#        self.w -= self.excessw

        # set margins (in pixels)
        self.marginb = int(self.h * 0.1)# + self.excessh
        self.margint = int(self.h * 0.05)
        self.marginl = int(self.w * 0.15)
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
 
    def button_release(self, x, y, button):
        if button == 2:

#GLint gl2psBeginPage( const char *title, const char *producer,
#                      GLint viewport[4],
#                      GLint format, GLint sort, GLint options, 
#                      GLint colormode, GLint colorsize, 
#                      GL2PSrgba *colortable, 
#                      GLint nr, GLint ng, GLint nb, 
#                      GLint buffersize, FILE *stream,
#                      const char *filename )

#
#            print >>sys.stderr, "exporting...",
#            f = file('arxi.eps', 'w')
#            gl2psBeginPage("Title", "Producer", 
#                           self.viewport,
#                           GL2PS_EPS, GL2PS_NO_SORT, GL2PS_NONE,
#                           GL_RGBA, -1,
#                           0,
#                           0, 0, 0,
#                           21055000, f,
#                           "arxi.eps")
#            self.ps = True
#            glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
#            self.display()
#            self.ps = False
#
#            gl2psEndPage()
#            f.close()
#            print >>sys.stderr, "done"
                           
            self.autoscale()
            self.make_data_list()
            self.emit('redraw')
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
#        if self.haha:
#            ex, ey = self.mouse_to_real(x, y)
#            x = arange(2, 6, 0.01)
#            params = hn.havriliak_negami.move(10.**ex, 10.**ey, 4, 1, 0.5, 1)
#            y = log10(hn.havriliak_negami(10.**x, *params))
#            self.datasets[0].x = x
#            self.datasets[0].y = y
#            self.datasets[0].build_display_list()
#            self.emit('redraw')
#        elif self.rubberband_active():
            self.rubberband_continue(x, y)

    name = wrap_attribute('name')
    parent = wrap_attribute('parent')
    _zoom = wrap_attribute('zoom')


register_class(Graph,
'graphs[name:S,id:S,parent:S,zoom:S,datasets[id:S,worksheet:S,x:S,y:S,symbol:S,color:I,size:I,linetype:S,linestyle:S,linewidth:I]]')
