import sys
print >>sys.stderr, 'importing...',

from arrays import *
from items import Persistent
from project import Project
from worksheet import Worksheet
from lib.ElementTree import dump

print >>sys.stderr, 'ok'

print >>sys.stderr, 'creating...',
project = Project()

data1 = Worksheet('data1', project)
for i in xrange(100):
    data1.add_column('A'+str(i))
    data1['A'+str(i)] = arange(190.)

print >>sys.stderr, 'ok'

print >>sys.stderr, 'saving...',
project.filename = 'test.xml'
project.save()
print >>sys.stderr, 'ok'

p2 = Project()
print >>sys.stderr, 'loading...',
p2.load('test.xml')
print >>sys.stderr, 'ok'

