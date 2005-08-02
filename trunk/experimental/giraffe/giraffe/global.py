import os
import sys
import settings

DATADIR = os.path.normpath(os.path.abspath(os.path.dirname(sys.argv[0]))+'/../') + '/'
settings = settings.Settings(DATADIR+'grafit.cfg')
