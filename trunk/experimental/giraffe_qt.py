import sys
import time

from qt import *
from qtgl import *

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
    def __init__(self,graph,parent=None, name=None):
        fmt = QGLFormat()
        fmt.setDepth(False)
        fmt.setAlpha(True)
        QGLWidget.__init__(self, fmt, parent, name)
        self.graph = graph

    def initializeGL(self):
        self.graph.init_view(self.size().width(), self.size().height())

    def resizeGL(self, w, h):
        self.graph.resize_view(w, h)

    def paintGL(self):
        self.graph.update_view()


    btns = {Qt.LeftButton: Mouse.Left, Qt.MidButton: Mouse.Middle, Qt.RightButton: Mouse.Right, 0:None}

    def mouseMoveEvent(self, e):
        self.graph.mouse_event(Mouse.Move, e.x(), e.y(), self.btns[e.button()])
    def mousePressEvent(self, e):
        self.graph.mouse_event(Mouse.Press, e.x(), e.y(), self.btns[e.button()])

    def mouseReleaseEvent(self, e):
        self.graph.mouse_event(Mouse.Release, e.x(), e.y(), self.btns[e.button()])


if __name__=='__main__':
    app=QApplication(sys.argv)
    g = glGraph()
    w = GLGraphWidget(g)
    app.setMainWidget(w)
    w.show()
    app.exec_loop()

