from OpenGL.GL import GL_COMPILE, GL_QUADS, GL_LINES
#from OpenGL.GLU import *
#from OpenGL.GLUT import *

cdef extern from "Numeric/arrayobject.h":

  struct PyArray_Descr:
    int type_num, elsize
    char type

  ctypedef class Numeric.ArrayType [object PyArrayObject]:
    cdef char *data
    cdef int nd
    cdef int *dimensions, *strides
    cdef object base
    cdef PyArray_Descr *descr
    cdef int flags

cdef extern from "GL/gl.h":

  void glVertex3f(float x, float y, float z)
  void glBegin(int mode)
  void glEnd()

def makedata(ArrayType sx, ArrayType sy, double dx, double dy):
    cdef int n, l
    cdef double x, y
    cdef double *xd, *yd

    xd = <double *>sx.data
    yd = <double *>sy.data

    glBegin(GL_QUADS)
    l = sx.dimensions[0]
    for n from 0 <= n < l:
        x = xd[n]
        y = yd[n]
        glVertex3f(x, y, 0)
        glVertex3f(x+dx, y, 0)
        glVertex3f(x+dx, y+dy, 0)
        glVertex3f(x, y+dy, 0)
    glEnd()
