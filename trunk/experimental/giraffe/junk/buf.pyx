cdef extern from "stdlib.h":
    void *malloc (int size)

cdef class Shrubbery:

    cdef int width, height
    cdef void *buf

    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.buf = malloc(100)

    def describe(self):
        print "This shrubbery is", self.width, \
            "by", self.height, "cubits."

    def __getreadbuffer__(self, int i, void **p):
        p[0] = self.buf + i

    def __getwritebuffer__(self, int i, void **p):
        p[0] = self.buf + i

    def __getsegcount__(self, int *p):
        p[0] = 1

    def __getcharbuffer__(self, int i, char **p):
        p[0] = <char *>self.buf + i
