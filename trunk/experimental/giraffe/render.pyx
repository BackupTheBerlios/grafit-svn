# A small C extension for the inner loop.
# with the rest in pure python, we can easily handle a few million points 
# (lines are even faster)

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
    int GL_COMPILE, GL_QUADS, GL_LINES


def makedata(ArrayType sx, ArrayType sy, double dx, double dy, 
             double xmin, double xmax, double ymin, double ymax):
    cdef int n, l
    cdef double x, y
    cdef double *xd, *yd
    cdef int xbucket, ybucket
    cdef int xbucket_s, ybucket_s
    cdef double xinterval, yinterval

    xbucket, ybucket = -1, -1

    xd = <double *>sx.data
    yd = <double *>sy.data

    xinterval = (xmax-xmin)/1000.
    yinterval = (ymax-ymin)/1000.

    l = sx.dimensions[0]
    glBegin(GL_QUADS)
    for n from 0 <= n < l:
        x = xd[n]
        y = yd[n]

        # skip if outside limits
        if not (xmin <= x <= xmax):
            continue

        # skip if we would land within 1/1000th of the graph from the previous point
        xbucket_s = xbucket
        ybucket_s = ybucket
        xbucket = <int>((x-xmin)/xinterval)
        ybucket = <int>((y-ymin)/yinterval)
        if (xbucket == xbucket_s) and (ybucket == ybucket_s):
            continue

        glVertex3f(x, y, 0)
#        glTranslate()
        glVertex3f(x+dx, y, 0)
        glVertex3f(x+dx, y+dy, 0)
        glVertex3f(x, y+dy, 0)
    glEnd()
