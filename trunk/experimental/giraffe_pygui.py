import sys
import time
import math

from GUI import Window, Task, application
from GUI.GL import GLView
from OpenGL import GL



class Mouse:
    Left, Right, Middle = range(3)
    Press, Release, Move = range(3)

class Key:
    Shift, Ctrl, Alt = range(3)

class Direction:
    Left, Right, Top, Bottom = range(4)

class Coordinates:
    Pixel, Data, Physical = range(3)

from giraffe import glGraph


class Mouse:
    Left, Right, Middle = range(3)
    Press, Release, Move = range(3)

class Key:
    Shift, Ctrl, Alt = range(3)

class Direction:
    Left, Right, Top, Bottom = range(4)

class Coordinates:
    Pixel, Data, Physical = range(3)


class GLGraphWidget(GLView):
    def __init__(self, graph, *args, **kwds):
        GLView.__init__(self, *args, **kwds)
        self.graph = graph

    def render(self):
        self.graph.update_view()

    def viewport_changed(self):
        self.graph.resize_view(self.width, self.height)

    def init_context(self):
        self.graph.init_view(self.width, self.height)
#
#    btns = {Qt.LeftButton: Mouse.Left, Qt.MidButton: Mouse.Middle, Qt.RightButton: Mouse.Right, 0:None}
#
#    def mouseMoveEvent(self, e):
#        self.graph.mouse_event(Mouse.Move, e.x(), e.y(), self.btns[e.button()])
#    def mousePressEvent(self, e):
#        self.graph.mouse_event(Mouse.Press, e.x(), e.y(), self.btns[e.button()])
#
#    def mouseReleaseEvent(self, e):
#        self.graph.mouse_event(Mouse.Release, e.x(), e.y(), self.btns[e.button()])

#    def mouse_down(self,event, *args, **kwds):
#        print dir(event)
#        print args, kwds

#        for event in self.track_mouse():
            

##############################################################################
g = glGraph()
view = GLGraphWidget(g, size = (300, 300))
win = Window(title = "Gears")
win.place(view, sticky = "nsew")
view.become_target()
win.shrink_wrap()
win.show()

application().run()


#    app=QApplication(sys.argv)
#    g = glGraph()
#    app.setMainWidget(g.win)
#    g.win.show()
#    app.exec_loop()

