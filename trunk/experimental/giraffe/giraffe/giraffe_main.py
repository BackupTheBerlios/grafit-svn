#!/usr/bin/env python
import psyco ; psyco.full()

import os
import sys

DATADIR = os.path.normpath(os.path.dirname(os.path.realpath(os.path.abspath(__file__)))+'/../')+'/'
sys.path.append(DATADIR)

from giraffe import Project
from giraffe.ui.main import Application

def main():
    p = Project()
    app = Application(p)
    app.run()

if __name__ == '__main__':
    main()
