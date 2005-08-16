#!/usr/bin/env python

# we need these lines for cx_Freeze to work on numarray!
import numarray._bytes,     numarray._ufuncBool,      numarray._ufuncInt32, numarray._ufuncUInt8
import numarray._chararray, numarray._ufuncComplex32, numarray._ufuncInt64, numarray.libnumarray
import numarray._conv,      numarray._ufuncComplex64, numarray._ufuncInt8,  numarray.memory
import numarray._ndarray,   numarray._ufuncFloat32,   numarray._ufuncUInt16
import numarray._numarray,  numarray._ufuncFloat64,   numarray._ufuncUInt32
import numarray._sort,      numarray._ufuncInt16,     numarray._ufuncUInt64

import os
import sys

from settings import DATADIR
print "Starting grafit, data directory is", DATADIR
sys.path.append(DATADIR)

import gui

def main():
    print >>sys.stderr, "creating application"
    app = gui.Application()
    app.splash()
    from giraffe.ui_main import MainWindow
    app.run(MainWindow)

if __name__ == '__main__':
    main()
