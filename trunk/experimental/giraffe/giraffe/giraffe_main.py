#!/usr/bin/env python
import os
import sys

DATADIR = os.path.normpath(os.path.dirname(os.path.realpath(os.path.abspath(__file__)))+'/../')+'/'
sys.path.append(DATADIR)
sys.path.append(DATADIR+'lib/')

print >>sys.stderr, "loading wx...",
import wx
print >>sys.stderr, "ok"

print >>sys.stderr, "loading giraffe...",
from giraffe import Project
from giraffe.ui_main import Application
print >>sys.stderr, "ok"

def main():
    print >>sys.stderr, "creating application...",
    p = Project()
    app = Application(p)
    print >>sys.stderr, "ok"
    app.run()

if __name__ == '__main__':
    main()
