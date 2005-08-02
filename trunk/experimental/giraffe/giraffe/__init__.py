from giraffe.project import Project, Folder
from giraffe.worksheet import Worksheet
from giraffe.graph import Graph

from giraffe.commands import undo, redo

import os
import sys
import settings

DATADIR = os.path.normpath(os.path.abspath(os.path.dirname(sys.argv[0]))+'/../') + '/'
settings = settings.Settings(DATADIR+'grafit.cfg')
