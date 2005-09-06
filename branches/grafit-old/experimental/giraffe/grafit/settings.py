import os
import sys
import ConfigParser

class Settings(object):
    def __init__(self, filename):
        self.filename = filename
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.filename)

    def write(self):
        self.config.write(open(self.filename, 'w'))

    def set(self, section, key, value):
        if section not in self.config.sections():
            self.config.add_section(section)
        self.config.set(section, key, value)
        self.write()

    def get(self, section, key):
        return self.config.get(section, key)

DATADIR = os.path.normpath(os.path.abspath(os.path.dirname(sys.argv[0]))+'/../') + '/'
settings = Settings(DATADIR+'grafit.cfg')
