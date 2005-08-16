# A small C extension for the inner loop.
# with the rest in pure python, we can easily handle a few million points 
# (lines are even faster)

cdef extern from "math.h":
    double sin(double x)
    double cos(double y)
    int isnan(double x)

cdef extern from "numarray/libnumarray.h":
    ctypedef int maybelong
    cdef struct PyArray_Descr:
        int type_num # PyArray_TYPES
        int elsize   # bytes for 1 element
        char type    # One of "cb1silfdFD "  Object array not supported
        # function pointers omitted

    ctypedef class numarray._numarray._numarray [object PyArrayObject]:
        cdef char *data
        cdef int nd
        cdef maybelong *dimensions
        cdef maybelong *strides
        cdef object base
        cdef PyArray_Descr *descr
        cdef int flags

        # numarray extras
        cdef maybelong *_dimensions
        cdef maybelong *_strides
        cdef object _data         # object must meet buffer API
        cdef object _shadows      # ill-behaved original array.
        cdef int    nstrides      # elements in strides array
        cdef long   byteoffset    # offset into buffer where array data begins
        cdef long   bytestride    # basic seperation of elements in bytes
        cdef long   itemsize      # length of 1 element in bytes

        cdef char   byteorder     # NUM_BIG_ENDIAN, NUM_LITTLE_ENDIAN

        cdef char   _aligned      # test override flag
        cdef char   _contiguous   # test override flag

    ctypedef enum:
        NUM_UNCONVERTED # 0
        NUM_CONTIGUOUS  # 1
        NUM_NOTSWAPPED  # 2
        NUM_ALIGNED     # 4
        NUM_WRITABLE    # 8
        NUM_COPY        # 16
        NUM_C_ARRAY     #  = (NUM_CONTIGUOUS | NUM_ALIGNED | NUM_NOTSWAPPED)

    ctypedef enum NumarrayType:
        tAny
        tBool
        tInt8
        tUInt8
        tInt16
        tUInt16
        tInt32
        tUInt32
        tInt64
        tUInt64
        tFloat32
        tFloat64
        tComplex32
        tComplex64
        tObject                   # placeholder... does nothing
        tDefault = tFloat64
        tLong = tInt32,
        tMaxType

    void import_libnumarray()
 
    _numarray NA_InputArray (object, NumarrayType, int)
    void *NA_OFFSETDATA(_numarray)

import_libnumarray()

cdef extern from "GL/gl.h":

    void glVertex3d(double x, double y, double z)
    void glPointSize(double size)
    void glBegin(int mode)
    void glEnd()
    void glCallList(int id)
    void glEnable(int)
    void glPolygonMode(int, int)
    void glTranslated(double x, double y, double z)
    int GL_COMPILE, GL_QUADS, GL_LINES, GL_POLYGON, GL_TRIANGLES, GL_LINE_STRIP, GL_POINTS, GL_POINT_SMOOTH
    int GL_BACK, GL_LINE, GL_FRONT, GL_FILL


def render_symbols(_numarray sx, _numarray sy,  symbol, int size, 
                   double xmin, double xmax, double ymin, double ymax):
    cdef int n, m, l
    cdef double x, y, xnext, ynext
    cdef double *xd, *yd
    cdef int xbucket, ybucket
    cdef int xbucket_s, ybucket_s
    cdef int i
    cdef double xinterval, yinterval
    cdef double pi
    cdef int sym
    cdef double si

    si = size/5.

    pi = 3.14159265358979
    cdef double circlex[11], circley[11]

    for n from 0<=n<11:
        circlex[n] = cos(n*2*pi/10)*size
        circley[n] = sin(n*2*pi/10)*size

    if symbol == 'square-f' or symbol == 'square-o':
        sym = 1
        shape = GL_QUADS
    elif symbol == 'uptriangle-f' or symbol == 'uptriangle-o':
        sym = 2
        shape = GL_TRIANGLES
    elif symbol == 'circle-f':
        sym = 3
        shape = GL_POINTS
#        glPointSize(4)
        glEnable(GL_POINT_SMOOTH)
    elif symbol == 'diamond-f' or symbol == 'diamond-o':
        sym = 4
        shape = GL_QUADS
    elif symbol == 'circle-o':
        sym = -100
        shape = GL_LINES
    else:
        print 'unknown symbol', symbol
        return 0

    if symbol[-1] == 'f':
        glPolygonMode(GL_BACK, GL_FILL)
        glPolygonMode(GL_FRONT, GL_FILL)
    elif symbol[-1] == 'o':
        glPolygonMode(GL_BACK, GL_LINE)
        glPolygonMode(GL_FRONT, GL_LINE)

#    pi = 3.14159

    xbucket, ybucket = -1, -1

    xd = <double *>NA_OFFSETDATA(sx)
    yd = <double *>NA_OFFSETDATA(sy)

#    xinterval = (xmax-xmin)/1000.
#    yinterval = (ymax-ymin)/1000.

    l = sx.dimensions[0]


    # draw symbols
    glBegin(shape)
    for n from 0 <= n < l:
        x = xd[n]
        y = yd[n]
        if isnan(x) or isnan(y):
            continue

        # skip if outside limits
        if not (xmin-si/2 <= x <= xmax+si/2) or not (ymin-si/2 <= y <= ymax+si/2):
            continue

        # skip if we would land within 1/1000th of the graph from the previous point
#        xbucket_s = xbucket
#        ybucket_s = ybucket
#        xbucket = <int>((x-xmin)/xinterval)
#        ybucket = <int>((y-ymin)/yinterval)
#        if (xbucket == xbucket_s) and (ybucket == ybucket_s):
#            continue

        if sym == 1:
            glVertex3d(x-si/2, y-si/2, 0)
            glVertex3d(x+si/2, y-si/2, 0)
            glVertex3d(x+si/2, y+si/2, 0)
            glVertex3d(x-si/2, y+si/2, 0)
        elif sym == 2:
            glVertex3d(x-si/2, y-si/2, 0)
            glVertex3d(x+si/2, y-si/2, 0)
            glVertex3d(x, y+si/2, 0)
        elif sym == 3:
            glVertex3d(x, y, 0)
        elif sym == 4:
            glVertex3d(x-si/2, y, 0)
            glVertex3d(x, y-si/2, 0)
            glVertex3d(x+si/2, y, 0)
            glVertex3d(x, y+si/2, 0)
        elif sym == -100:
            for m from 0<=m<10:
                glVertex3d(x+circlex[m], y+circley[m], 0)
                glVertex3d(x+circlex[m+1], y+circley[m+1], 0)
            
    glEnd()

    return 1

def render_lines(_numarray sx, _numarray sy, double xmin, double xmax, double ymin, double ymax):
    cdef int n, l
    cdef double x, y, xnext, ynext
    cdef double *xd, *yd

    xd = <double *>NA_OFFSETDATA(sx)
    yd = <double *>NA_OFFSETDATA(sy)
    l = sx.dimensions[0]

    # draw lines
    glBegin(GL_LINES)
    for n from 0 <= n < l-1:
        x = xd[n]
        y = yd[n]
        xnext = xd[n+1]
        ynext = yd[n+1]

        if (x <= xmin and xnext <= xmin) or (y <= ymin and ynext <= ymin) or \
            (x >= xmax and xnext >= xmax) or (y >= ymax and ynext >= ymax):
            continue

        # skip if outside limits
#        if n < l-1:
#            xnext = xd[n-1]
#            ynext = yd[n-1]
#            if (x <= xmin and xnext <= xmin) or \
#               (x >= xmax and xnext >= xmax) or \
#               (y <= ymin and ynext <= ymin) or \
#               (y >= ymax and ynext >= ymax):
#                continue
#        else:
#            if not (xmin <= x <= xmax) or not (ymin <= y <= ymax):
#                continue
#
        # skip if we would land within 1/1000th of the graph from the previous point
#        xbucket_s = xbucket
#        ybucket_s = ybucket
#        xbucket = <int>((x-xmin)/xinterval)
#        ybucket = <int>((y-ymin)/yinterval)
#        if (xbucket == xbucket_s) and (ybucket == ybucket_s):
#            continue
        glVertex3d(x, y, 0.1)
        glVertex3d(xnext, ynext, 0.1)

    glEnd()
    return 1


