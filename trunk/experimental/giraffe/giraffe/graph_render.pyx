# A small C extension for the inner loop.
# with the rest in pure python, we can easily handle a few million points 
# (lines are even faster)

cdef extern from "math.h":
    double sin(double x)
    double cos(double y)

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

cdef extern from "GL/glu.h":

    void gluDisk(void* quad, double inner, double outer, int slices, int loops)
    void* gluNewQuadric()


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


def makedata(_numarray sx, _numarray sy,  
             double xmin, double xmax, double ymin, double ymax, 
             double dx, double dy, symbol):
#             shape, vertices):
    cdef int n, m, l
    cdef double x, y
    cdef double *xd, *yd
    cdef int xbucket, ybucket
    cdef int xbucket_s, ybucket_s
    cdef int i
    cdef double xinterval, yinterval
    cdef double pi
    cdef int sym
    cdef void *quad


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
        shape = -1
        print 'j'
        quad = gluNewQuadric()
        print 'k'
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

    xinterval = (xmax-xmin)/1000.
    yinterval = (ymax-ymin)/1000.

#        glVertex3d(x-xmin, y-ymin, 0.)
#        glVertex3d(x-xmin+sin(i*2*pi/m)*dx, y-ymin+cos(i*2*pi/m)*dy, 0.)
#        glVertex3d(x-xmin+sin((i+1)*2*pi/m)*dx, y-ymin+cos((i+1)*2*pi/m)*dy, 0.)
#    

    l = sx.dimensions[0]
    if shape != -1:
        glBegin(shape)
    for n from 0 <= n < l:
        x = xd[n]
        y = yd[n]

        # skip if outside limits
        if not (xmin <= x <= xmax) or not (ymin <= y <= ymax):
            continue

        # skip if we would land within 1/1000th of the graph from the previous point
        xbucket_s = xbucket
        ybucket_s = ybucket
        xbucket = <int>((x-xmin)/xinterval)
        ybucket = <int>((y-ymin)/yinterval)
        if (xbucket == xbucket_s) and (ybucket == ybucket_s):
            continue

#        for i from 0 <= i < m:
        if sym == 1:
            glVertex3d(x-xmin-dx/2, y-ymin-dy/2, 0)
            glVertex3d(x-xmin+dx/2, y-ymin-dy/2, 0)
            glVertex3d(x-xmin+dx/2, y-ymin+dy/2, 0)
            glVertex3d(x-xmin-dx/2, y-ymin+dy/2, 0)
        elif sym == 2:
            glVertex3d(x-xmin-dx/2, y-ymin-dy/2, 0)
            glVertex3d(x-xmin+dx/2, y-ymin-dy/2, 0)
            glVertex3d(x-xmin, y-ymin+dy/2, 0)
        elif sym == 3:
            glVertex3d(x-xmin, y-ymin, 0)
        elif sym == 4:
            glVertex3d(x-xmin-dx/2, y-ymin, 0)
            glVertex3d(x-xmin, y-ymin-dy/2, 0)
            glVertex3d(x-xmin+dx/2, y-ymin, 0)
            glVertex3d(x-xmin, y-ymin+dy/2, 0)
        elif sym == -100:
            gluDisk(quad, 1, 3, 10, 10)
            


#        for v in vertices:
#            glVertex3d(x-xmin+v[0], y-ymin+v[1], 0.)
    if shape != -1:
        glEnd()

        
    glBegin(GL_LINE_STRIP)
    for n from 0 <= n < l:
        x = xd[n]
        y = yd[n]
        # skip if outside limits
        if not (xmin <= x <= xmax) or not (ymin <= y <= ymax):
            continue

        # skip if we would land within 1/1000th of the graph from the previous point
        xbucket_s = xbucket
        ybucket_s = ybucket
        xbucket = <int>((x-xmin)/xinterval)
        ybucket = <int>((y-ymin)/yinterval)
        if (xbucket == xbucket_s) and (ybucket == ybucket_s):
            continue
        glVertex3d(x-xmin, y-ymin, 0)

    glEnd()
    return 1
