#!/usr/bin/env python2.4

import doctest
import os

red = '\x1b[1;31m'
green = '\x1b[1;32m'
default = '\x1b[0m'


def _test():
    for f in [fn for fn in os.listdir('.') if fn.endswith('.txt')]:
        print 'Testing', f,
        failed, total = doctest.testfile(f)
        if failed == 0:
            print green+'ok!, '+ str(total)+ ' tests passed' + default
        else:
            print red+str(failed), 'tests failed'+default

if __name__=='__main__':
    _test()
