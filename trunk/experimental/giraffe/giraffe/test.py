import sys
print >>sys.stderr, 'initializing...',
from base.arrays import *
print >>sys.stderr, 'a',
from base.items import Persistent
print >>sys.stderr, 'i',
from project import Project
print >>sys.stderr, 'p',
from worksheet import Worksheet
print >>sys.stderr, 'w',
from lib.ElementTree import dump
import time
print >>sys.stderr, 'e',

print >>sys.stderr, 'ok'

print >>sys.stderr, 'creating...',
project = Project()

data1 = Worksheet('data1', project)
for i in xrange(300):
    data1.add_column('A'+str(i))
    data1['A'+str(i)] = arange(190.)

print >>sys.stderr, 'ok'

print >>sys.stderr, 'saving...',
t = time.time()
project.filename = 'test.xml'
project.save()
print time.time()-t, 'seconds'
print >>sys.stderr, 'ok'

p2 = Project()
print >>sys.stderr, 'loading...',
t = time.time()
p2.load('test.xml')
print p2
print time.time()-t, 'seconds'
print >>sys.stderr, 'ok'

