#!/usr/bin/env python2.4

import doctest

red = '\x1b[31m'
green = '\x1b[32m'
default = '\x1b[0m'


def _test():
    failed, total =  doctest.testfile('new.txt')
    if failed == 0:
        print green+'ok!, '+ str(total)+ ' tests passed' + default
    else:
        print red+str(failed), 'tests failed'+default

if __name__=='__main__':
    _test()
