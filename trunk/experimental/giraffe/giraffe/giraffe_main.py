#!/usr/bin/env python
import numarray._bytes,     numarray._ufuncBool,      numarray._ufuncInt32, numarray._ufuncUInt8
import numarray._chararray, numarray._ufuncComplex32, numarray._ufuncInt64, numarray.libnumarray
import numarray._conv,      numarray._ufuncComplex64, numarray._ufuncInt8,  numarray.memory
import numarray._ndarray,   numarray._ufuncFloat32,   numarray._ufuncUInt16
import numarray._numarray,  numarray._ufuncFloat64,   numarray._ufuncUInt32
import numarray._sort,      numarray._ufuncInt16,     numarray._ufuncUInt64
import os
import sys

#DATADIR = os.path.normpath(os.path.dirname(os.path.realpath(os.path.abspath(__file__)))+'/../')+'/'
#DATADIR='/home/daniel/giraffe'
#sys.path.append(DATADIR)
#sys.path.append(DATADIR+'lib/')

print >>sys.stderr, "loading wx...",
import wx
print >>sys.stderr, "ok"

print >>sys.stderr, "loading giraffe...",
from giraffe import Project
from giraffe.ui_main import Application, MainWindow
print >>sys.stderr, "ok"

def main():
    sys.stderr.write("creating application...")
    app = Application(MainWindow)
    print >>sys.stderr, "ok"
    app.run()

if __name__ == '__main__':
    main()
