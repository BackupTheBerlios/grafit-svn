import sys
import time

from qt import Qt, QApplication
from qtgl import QGLWidget

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

class GLGraphWidget(QGLWidget):
    def __init__(self,graph,parent=None):
        QGLWidget.__init__(self, parent)
        self.graph = graph
    
    # gl events
    def initializeGL(self):
        self.graph.init_view(self.size().width(), self.size().height())

    def resizeGL(self, w, h):
        self.graph.resize_view(w, h)

    def paintGL(self):
        self.graph.update_view()

    # mouse events
    qtbtns = { Qt.LeftButton: Mouse.Left, 
               Qt.MidButton: Mouse.Middle, 
               Qt.RightButton: Mouse.Right, 
               0: None }

    def mousePressEvent(self, e):
        self.graph.mouse_event(Mouse.Press, e.x(), e.y(), self.qtbtns[e.button()])

    def mouseMoveEvent(self, e):
        self.graph.mouse_event(Mouse.Move, e.x(), e.y(), self.qtbtns[e.button()])

    def mouseReleaseEvent(self, e):
        self.graph.mouse_event(Mouse.Release, e.x(), e.y(), self.qtbtns[e.button()])


if __name__=='__main__':
    app=QApplication(sys.argv)
    g = glGraph()
    w = GLGraphWidget(g)
    g.widget= w
    w.show()
    app.setMainWidget(w)
    app.exec_loop()

